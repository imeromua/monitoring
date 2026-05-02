from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

router = Router()



@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name

    builder = InlineKeyboardBuilder()
    builder.button(
        text="📊 Відкрити Store Check",
        web_app=WebAppInfo(url=settings.MINI_APP_URL),
    )

    await message.answer(
        f"Привіт, <b>{full_name}</b>!\n\n"
        f"Натисни кнопку нижче, щоб розпочати моніторинг цін.",
        reply_markup=builder.as_markup(),
    )
