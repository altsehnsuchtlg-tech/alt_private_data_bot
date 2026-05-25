from aiogram import Router

from app.bot.handlers.chat import router as chat_router
from app.bot.handlers.start import router as start_router

# 主路由，聚合所有子路由
main_router = Router()
# 按优先级顺序注册子路由
main_router.include_router(start_router)
main_router.include_router(chat_router)
