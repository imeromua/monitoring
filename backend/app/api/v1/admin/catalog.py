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

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


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
    if file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="Файл занадто великий (макс. 10МБ)")

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Потрібний файл .xlsx")

    content = await file.read()
    df = pd.read_excel(io.BytesIO(content), dtype=str)

    required_cols = {"article_id", "name", "category_id"}
    if not required_cols.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Відсутні колонки: {required_cols - set(df.columns)}")

    uploaded_articles = set(df["article_id"].dropna().tolist())
    upserted = 0

    from sqlalchemy.dialects.postgresql import insert

    records = []
    for _, row in df.iterrows():
        weight_label = row.get("weight_label")
        if pd.isna(weight_label):
            weight_label = None
            
        records.append({
            "article_id": str(row["article_id"]),
            "name": str(row["name"]),
            "weight_label": str(weight_label) if weight_label else None,
            "category_id": int(row["category_id"]),
            "is_archived": False
        })

    if records:
        stmt = insert(Product).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['article_id'],
            set_={
                'name': stmt.excluded.name,
                'weight_label': stmt.excluded.weight_label,
                'category_id': stmt.excluded.category_id,
                'is_archived': False
            }
        )
        await db.execute(stmt)
        upserted = len(records)

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
