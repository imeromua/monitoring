from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.api.deps import require_admin
from app.models.store import Store
from app.models.user import User

router = APIRouter(prefix="/admin/stores", tags=["admin"])


@router.post("")
async def create_store(
    name: str,
    address: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    store = Store(name=name, address=address)
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return {"id": store.id, "name": store.name}


@router.patch("/{store_id}/archive")
async def archive_store(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не знайдено")
    store.is_active = False
    await db.commit()
    return {"status": "archived", "store_id": store_id}
