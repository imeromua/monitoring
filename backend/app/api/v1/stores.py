from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.store import Store
from app.models.user import User

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("")
async def get_stores(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stores = (await db.execute(select(Store).where(Store.is_active == True))).scalars().all()
    return [{"id": s.id, "name": s.name, "address": s.address, "logo_url": s.logo_url} for s in stores]
