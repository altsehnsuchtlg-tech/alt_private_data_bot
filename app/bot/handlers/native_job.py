from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import get_settings
from app.infra.redis_client import get_redis
from app.services.job_queue import JobQueue

router = Router()


@router.message(Command("native"))
async def native_job_handler(message: Message) -> None:
    if not message.text:
        await message.answer("Usage: /native <text>")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Usage: /native <text>")
        return

    settings = get_settings()
    redis = await get_redis(settings)
    queue = JobQueue(redis=redis, result_ttl_seconds=settings.job_result_ttl_seconds)
    job_id = await queue.enqueue_native_score(
        chat_id=message.chat.id,
        text=parts[1].strip(),
        user_id=message.from_user.id if message.from_user else 0,
    )

    await message.answer(
        "Job queued.\n"
        f"job_id: {job_id}\n"
        f"Check with: /job_result {job_id}"
    )
