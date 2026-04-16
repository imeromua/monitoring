from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.auth import TelegramAuthRequest, TokenResponse
from app.services.auth_service import verify_telegram_init_data, create_access_token, get_or_create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/verify", response_model=TokenResponse)
async def verify_auth(payload: TelegramAuthRequest, db: AsyncSession = Depends(get_db)):
    user_data = verify_telegram_init_data(payload.init_data)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалідні дані Telegram")

    telegram_id = user_data.get("id")
    full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()

    user = await get_or_create_user(db, telegram_id, full_name)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ заборонено")

    token = create_access_token(telegram_id=telegram_id, role=user.role)
    return TokenResponse(access_token=token, role=user.role)
