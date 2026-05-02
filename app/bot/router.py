from aiogram import Router

from app.bot.handlers.job_result import router as job_result_router
from app.bot.handlers.native_job import router as native_job_router
from app.bot.handlers.start import router as start_router

main_router = Router()
main_router.include_router(start_router)
main_router.include_router(native_job_router)
main_router.include_router(job_result_router)
