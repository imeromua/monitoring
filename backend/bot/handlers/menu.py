from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Store Check — Команди:</b>\n\n"
        "/start — Відкрити Mini App\n"
        "/help — Ця довідка\n\n"
        "Для роботи з системою використовуй кнопку Mini App."
    )
