from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis
import json

from app.db.base import get_db
from app.api.deps import get_current_user, get_redis
from app.models.category import Category
from app.models.product import Product
from app.schemas.catalog import CatalogResponse, CategorySchema, ProductSchema
from app.models.user import User

router = APIRouter(prefix="/catalog", tags=["catalog"])

CATALOG_CACHE_KEY = "catalog:full"
CATALOG_CACHE_TTL = 3600  # 1 година


@router.get("", response_model=CatalogResponse)
async def get_catalog(
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    cached = await redis.get(CATALOG_CACHE_KEY)
    if cached:
        return CatalogResponse(**json.loads(cached))

    cats = (await db.execute(select(Category).order_by(Category.sort_order))).scalars().all()
    prods = (await db.execute(select(Product).where(Product.is_archived == False))).scalars().all()

    response = CatalogResponse(
        categories=[CategorySchema.model_validate(c) for c in cats],
        products=[ProductSchema.model_validate(p) for p in prods],
    )

    await redis.set(CATALOG_CACHE_KEY, response.model_dump_json(), ex=CATALOG_CACHE_TTL)
    return response
