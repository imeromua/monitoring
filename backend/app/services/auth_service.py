import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qsl
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.user import User


def verify_telegram_init_data(init_data: str) -> dict | None:
    """
    Перевірка підпису Telegram WebApp initData за HMAC-SHA256.
    Повертає словник з даними користувача або None при невалідному підписі.
    """
    parsed = dict(parse_qsl(unquote(init_data), keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        settings.BOT_TOKEN.encode(),
        hashlib.sha256,
    ).digest()

    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        return None

    user_data = json.loads(parsed.get("user", "{}"))
    return user_data


def create_access_token(telegram_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(telegram_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


async def get_or_create_user(db: AsyncSession, telegram_id: int, full_name: str) -> User | None:
    """
    Superadmin визначається з .env. Решта — з БД.
    Повертає None якщо користувача немає в системі або він заблокований.
    """
    if telegram_id == settings.SUPERADMIN_TELEGRAM_ID:
        return User(
            telegram_id=telegram_id,
            full_name=full_name,
            role="admin",
            is_active=True,
        )

    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return None

    return user
