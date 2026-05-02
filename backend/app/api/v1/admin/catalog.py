import re
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import pandas as pd
import io

from app.db.base import get_db
from app.api.deps import require_admin, get_redis
from app.models.user import User
from app.models.product import Product
from app.models.category import Category, CategoryLevel
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from typing import List

router = APIRouter(prefix="/admin/catalog", tags=["admin"])

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ARTICLE_RE = re.compile(r'^\d{8}$')


async def _get_or_create_category(db: AsyncSession, name: str) -> int:
    """Повертає id категорії за назвою. Створює якщо не існує (level=group)."""
    name = name.strip()
    result = await db.execute(
        select(Category).where(Category.name.ilike(name))
    )
    cat = result.scalar_one_or_none()
    if cat:
        return cat.id
    new_cat = Category(name=name, level=CategoryLevel.group, sort_order=0)
    db.add(new_cat)
    await db.flush()  # отримуємо id без commit
    return new_cat.id


@router.post("/upload")
async def upload_catalog(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    """
    Завантажує .xlsx файл з колонками: Категорія, Артикул, Назва.
    Стратегія: UPSERT за article_id. Відсутні позиції позначаються is_archived=True.
    Артикул — ровно 8 цифр.
    """
    if file.size and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="Файл занадто великий (макс. 10МБ)")

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Потрібний файл .xlsx")

    content = await file.read()
    df = pd.read_excel(io.BytesIO(content), dtype=str)

    # Нормалізація назв колонок
    df.columns = [c.strip().lower() for c in df.columns]

    # Підтримка українських назв колонок
    col_map = {
        "категорія": "category",
        "артикул": "article",
        "назва": "name",
        "category": "category",
        "article": "article",
        "article_id": "article",
        "name": "name",
    }
    df.rename(columns=col_map, inplace=True)

    required_cols = {"category", "article", "name"}
    missing = required_cols - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Відсутні колонки: {missing}. Очікується: Категорія, Артикул, Назва"
        )

    df = df.dropna(subset=["article", "name", "category"])

    # Валідація артикулів
    invalid = df[~df["article"].str.match(r'^\d{8}$')]
    if not invalid.empty:
        bad = invalid["article"].tolist()[:5]
        raise HTTPException(
            status_code=400,
            detail=f"Невірні артикули (потрібно ровно 8 цифр): {bad}"
        )

    uploaded_articles = set(df["article"].tolist())
    upserted = 0

    from sqlalchemy.dialects.postgresql import insert

    records = []
    for _, row in df.iterrows():
        category_id = await _get_or_create_category(db, str(row["category"]))
        records.append({
            "article_id": str(row["article"]),
            "name": str(row["name"]).strip(),
            "category_id": category_id,
            "is_archived": False,
        })

    if records:
        stmt = insert(Product).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["article_id"],
            set_={
                "name": stmt.excluded.name,
                "category_id": stmt.excluded.category_id,
                "is_archived": False,
            }
        )
        await db.execute(stmt)
        upserted = len(records)

    # Архівація видалених позицій
    await db.execute(
        update(Product)
        .where(Product.article_id.notin_(uploaded_articles))
        .values(is_archived=True)
    )

    await db.commit()
    await redis.delete("catalog:full")

    return {"status": "ok", "upserted": upserted}

# --- Products CRUD ---

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Product))
    return result.scalars().all()

@router.post("/products", response_model=ProductResponse)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    # Check if article_id already exists
    existing = await db.execute(select(Product).where(Product.article_id == product_in.article_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Товар з таким артикулом вже існує")
        
    new_product = Product(**product_in.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    await redis.delete("catalog:full")
    return new_product

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не знайдено")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    await redis.delete("catalog:full")
    return product

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не знайдено")

    await db.delete(product)
    await db.commit()
    await redis.delete("catalog:full")
    return {"status": "ok"}

# --- Categories CRUD ---

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Category).order_by(Category.sort_order))
    return result.scalars().all()

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    new_category = Category(**category_in.model_dump())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    await redis.delete("catalog:full")
    return new_category

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категорію не знайдено")

    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    await redis.delete("catalog:full")
    return category

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категорію не знайдено")

    await db.delete(category)
    await db.commit()
    await redis.delete("catalog:full")
    return {"status": "ok"}
