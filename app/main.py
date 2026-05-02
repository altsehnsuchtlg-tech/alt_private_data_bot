from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.router import main_router
from app.config import get_settings
from app.infra.redis_client import close_redis
from app.logging_setup import configure_logging
from app.storage.db import ping_database


async def run() -> None:
    configure_logging()
    settings = get_settings()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.include_router(main_router)

    try:
        await ping_database(settings)
        logging.getLogger(__name__).info("PostgreSQL ping successful")
    except Exception:
        logging.getLogger(__name__).warning("PostgreSQL ping failed at startup", exc_info=True)

    try:
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        await close_redis()
        await bot.session.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
