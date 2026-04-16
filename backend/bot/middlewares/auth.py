from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.models.user import User
from app.config import settings


class AuthMiddleware(BaseMiddleware):
    """
    Перевіряє чи має користувач доступ до системи.
    Superadmin — з .env, решта — з БД.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        telegram_id = event.from_user.id

        if telegram_id == settings.SUPERADMIN_TELEGRAM_ID:
            data["is_authorized"] = True
            return await handler(event, data)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(
                    User.telegram_id == telegram_id,
                    User.is_active == True,
                )
            )
            user = result.scalar_one_or_none()

        if not user:
            await event.answer(
                "⛔ У вас немає доступу до системи.\n"
                "Зверніться до адміністратора."
            )
            return

        data["is_authorized"] = True
        data["db_user"] = user
        return await handler(event, data)
