from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import get_settings
from app.infra.redis_client import get_redis
from app.services.job_queue import JobQueue

router = Router()


@router.message(Command("job_result"))
async def job_result_handler(message: Message) -> None:
    if not message.text:
        await message.answer("Usage: /job_result <job_id>")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Usage: /job_result <job_id>")
        return

    job_id = parts[1].strip()
    settings = get_settings()
    redis = await get_redis(settings)
    queue = JobQueue(redis=redis, result_ttl_seconds=settings.job_result_ttl_seconds)
    result = await queue.get_result(job_id)

    if not result:
        await message.answer("No result found yet. The job may still be processing.")
        return

    lines = [
        f"job_id: {result.get('job_id', job_id)}",
        f"status: {result.get('status', 'unknown')}",
        f"chat_id: {result.get('chat_id', '-')}",
        f"user_id: {result.get('user_id', '-')}",
        f"score: {result.get('score', '-')}",
        f"processed_at: {result.get('processed_at', '-')}",
    ]
    if "error" in result:
        lines.append(f"error: {result['error']}")

    await message.answer("\n".join(lines))
