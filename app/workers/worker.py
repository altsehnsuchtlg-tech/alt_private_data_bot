from __future__ import annotations

import asyncio
import logging
import os
import socket
from datetime import UTC, datetime

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from app.config import get_settings
from app.services.job_queue import JOB_STREAM_NAME, JobQueue
from app.services.native_service import score_text

LOGGER = logging.getLogger(__name__)
GROUP_NAME = "native_workers"


async def ensure_consumer_group(redis: Redis) -> None:
    try:
        await redis.xgroup_create(name=JOB_STREAM_NAME, groupname=GROUP_NAME, id="$", mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


async def process_message(redis: Redis, queue: JobQueue, message_id: str, payload: dict[str, str]) -> None:
    chat_id = payload.get("chat_id", "0")
    user_id = payload.get("user_id", "0")
    text = payload.get("text", "")

    try:
        score = score_text(text)
        result = {
            "job_id": message_id,
            "status": "done",
            "chat_id": chat_id,
            "user_id": user_id,
            "score": str(score),
            "processed_at": datetime.now(UTC).isoformat(),
        }
    except Exception as exc:  # pragma: no cover - safety path
        LOGGER.exception("Failed to process job %s", message_id)
        result = {
            "job_id": message_id,
            "status": "failed",
            "chat_id": chat_id,
            "user_id": user_id,
            "score": "0",
            "error": str(exc),
            "processed_at": datetime.now(UTC).isoformat(),
        }

    await queue.store_result(message_id, result)
    await redis.xack(JOB_STREAM_NAME, GROUP_NAME, message_id)


async def worker_loop() -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    queue = JobQueue(redis=redis, result_ttl_seconds=settings.job_result_ttl_seconds)
    consumer_name = f"{socket.gethostname()}-{os.getpid()}"

    await ensure_consumer_group(redis)
    LOGGER.info("Worker started: group=%s consumer=%s", GROUP_NAME, consumer_name)

    try:
        while True:
            streams = await redis.xreadgroup(
                groupname=GROUP_NAME,
                consumername=consumer_name,
                streams={JOB_STREAM_NAME: ">"},
                count=10,
                block=5000,
            )
            if not streams:
                continue

            for _stream_name, messages in streams:
                for message_id, payload in messages:
                    await process_message(redis, queue, message_id, payload)
    finally:
        await redis.aclose()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
