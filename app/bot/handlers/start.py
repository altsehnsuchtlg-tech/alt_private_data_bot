from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.services.greeting import build_start_message

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(build_start_message(message.from_user))
