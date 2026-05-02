from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

JOB_STREAM_NAME = "jobs:native_score"


class JobQueue:
    def __init__(self, redis: Redis, result_ttl_seconds: int = 3600) -> None:
        self.redis = redis
        self.result_ttl_seconds = result_ttl_seconds

    @staticmethod
    def result_key(job_id: str) -> str:
        return f"job:result:{job_id}"

    async def enqueue_native_score(self, chat_id: int, text: str, user_id: int) -> str:
        job_id = await self.redis.xadd(
            JOB_STREAM_NAME,
            {
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "text": text,
            },
        )
        return str(job_id)

    async def store_result(self, job_id: str, payload: dict[str, str]) -> None:
        key = self.result_key(job_id)
        await self.redis.hset(key, mapping=payload)
        await self.redis.expire(key, self.result_ttl_seconds)

    async def get_result(self, job_id: str) -> dict[str, Any]:
        result = await self.redis.hgetall(self.result_key(job_id))
        return result or {}
