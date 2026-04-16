from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import io
import redis.asyncio as aioredis

from app.db.base import get_db
from app.api.deps import require_admin, get_redis
from app.models.user import User
from app.models.product import Product
from app.models.category import Category

router = APIRouter(prefix="/admin/catalog", tags=["admin"])


@router.post("/upload")
async def upload_catalog(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    """
    Завантажує .xlsx файл з колонками: article_id, name, weight_label, category_id.
    Стратегія: UPSERT за article_id. Відсутні позиції позначаються is_archived=True.
    """
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Потрібний файл .xlsx")

    content = await file.read()
    df = pd.read_excel(io.BytesIO(content), dtype=str)

    required_cols = {"article_id", "name", "category_id"}
    if not required_cols.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Відсутні колонки: {required_cols - set(df.columns)}")

    uploaded_articles = set(df["article_id"].dropna().tolist())
    upserted = 0

    for _, row in df.iterrows():
        from sqlalchemy import select
        result = await db.execute(select(Product).where(Product.article_id == row["article_id"]))
        product = result.scalar_one_or_none()

        if product:
            product.name = row["name"]
            product.weight_label = row.get("weight_label")
            product.category_id = int(row["category_id"])
            product.is_archived = False
        else:
            product = Product(
                article_id=row["article_id"],
                name=row["name"],
                weight_label=row.get("weight_label"),
                category_id=int(row["category_id"]),
            )
            db.add(product)
        upserted += 1

    # Архівація видалених позицій
    from sqlalchemy import update
    await db.execute(
        update(Product)
        .where(Product.article_id.notin_(uploaded_articles))
        .values(is_archived=True)
    )

    await db.commit()

    # Інвалідація кешу каталогу
    await redis.delete("catalog:full")

    return {"status": "ok", "upserted": upserted}
