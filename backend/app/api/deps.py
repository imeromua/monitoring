from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from app.db.base import get_db
from app.config import settings
from app.services.auth_service import decode_token
from app.models.user import User

bearerScheme = HTTPBearer()


from app.db.redis import get_redis_client

async def get_redis():
    client = get_redis_client()
    try:
        yield client
    finally:
        # При використанні ConnectionPool закривати клієнт не обов'язково на кожен запит,
        # але для чистоти коду ми просто повертаємо його в пул.
        pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearerScheme),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалідний токен")

    telegram_id_str = payload.get("sub")
    if not telegram_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалідний токен: відсутній sub")
    
    telegram_id = int(telegram_id_str)

    # Перевірка Redis Blacklist
    is_blocked = await redis.get(f"blocked:{telegram_id}")
    if is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Користувача заблоковано")

    # Знаходимо користувача в БД
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ заборонено")

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("admin",):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Потрібні права адміністратора")
    return current_user
