from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Bot scaffold is running.\n"
        "Use /native <text> to queue a C++ scoring job.\n"
        "Use /job_result <job_id> to fetch the worker result."
    )
