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

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(
                    User.telegram_id == telegram_id,
                )
            )
            user = result.scalar_one_or_none()

            # Якщо це Superadmin і його немає в БД — створюємо
            if not user and telegram_id == settings.SUPERADMIN_TELEGRAM_ID:
                user = User(
                    telegram_id=telegram_id,
                    full_name=event.from_user.full_name,
                    role="admin",
                    is_active=True,
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

        if not user or not user.is_active:
            await event.answer(
                "⛔ У вас немає доступу до системи.\n"
                "Зверніться до адміністратора."
            )
            return

        data["is_authorized"] = True
        data["db_user"] = user
        return await handler(event, data)
