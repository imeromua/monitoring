import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.handlers import start, menu
from bot.middlewares.auth import AuthMiddleware
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Middleware
    dp.message.middleware(AuthMiddleware())

    # Роутери
    dp.include_router(start.router)
    dp.include_router(menu.router)

    logger.info("Bot started")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
