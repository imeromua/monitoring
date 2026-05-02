from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from app.db.base import get_db
from app.api.deps import require_admin, get_redis
from app.models.user import User, UserRole
from app.models.user import User

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users = (await db.execute(select(User))).scalars().all()
    return [
        {"id": u.id, "telegram_id": u.telegram_id, "full_name": u.full_name,
         "role": u.role, "is_active": u.is_active}
        for u in users
    ]


@router.post("")
async def create_user(
    telegram_id: int,
    full_name: str,
    role: UserRole = UserRole.worker,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = User(telegram_id=telegram_id, full_name=full_name, role=role, is_active=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "telegram_id": user.telegram_id}


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    is_active: bool | None = None,
    role: UserRole | None = None,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if is_active is not None:
        user.is_active = is_active
        if not is_active:
            await redis.set(f"blocked:{user.telegram_id}", "1")
        else:
            await redis.delete(f"blocked:{user.telegram_id}")

    if role is not None:
        user.role = role

    await db.commit()
    return {"status": "updated", "user_id": user_id}
