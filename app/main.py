from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.router import main_router
from app.config import get_settings
from app.logging_setup import configure_logging
from app.storage.db import ping_database


async def run() -> None:
    """配置日志并启动 Telegram 机器人轮询。"""
    configure_logging()
    settings = get_settings()

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    # 将主路由注册到调度器
    dispatcher.include_router(main_router)

    # 启动时检查 PostgreSQL 连接
    try:
        await ping_database(settings)
        logging.getLogger(__name__).info("PostgreSQL ping successful")
    except Exception:
        logging.getLogger(__name__).warning("PostgreSQL ping failed at startup", exc_info=True)

    try:
        # 开始轮询更新，启动机器人。
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        await bot.session.close()


def main() -> None:
    """程序入口点，使用 asyncio 运行机器人。"""
    asyncio.run(run())


if __name__ == "__main__":
    main()
