from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.storage.models import ChatErrorLog, ChatMessage, ChatRequest, ChatSession


class ChatRepository:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory

    async def get_active_session(self, chat_id: int, user_id: int) -> ChatSession | None:
        async with self.session_factory() as session:
            stmt = (
                select(ChatSession)
                .where(ChatSession.chat_id == chat_id, ChatSession.user_id == user_id, ChatSession.status == "active")
                .order_by(ChatSession.id.desc())
                .limit(1)
            )
            return await session.scalar(stmt)

    async def create_session(self, chat_id: int, user_id: int) -> ChatSession:
        async with self.session_factory() as session:
            record = ChatSession(chat_id=chat_id, user_id=user_id, status="active")
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def close_session(self, session_id: int) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(ChatSession)
                .where(ChatSession.id == session_id)
                .values(status="closed", ended_at=datetime.now(timezone.utc))
            )
            await session.commit()

    async def touch_session(self, session_id: int) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(ChatSession)
                .where(ChatSession.id == session_id)
                .values(last_message_at=datetime.now(timezone.utc))
            )
            await session.commit()

    async def create_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        async with self.session_factory() as session:
            record = ChatMessage(session_id=session_id, role=role, content=content)
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def get_recent_messages(self, session_id: int, limit: int) -> list[ChatMessage]:
        async with self.session_factory() as session:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.id.desc())
                .limit(limit)
            )
            result = await session.scalars(stmt)
            return list(reversed(result.all()))

    async def create_request(
        self,
        session_id: int,
        user_id: int,
        model: str,
        request_text: str,
    ) -> ChatRequest:
        async with self.session_factory() as session:
            record = ChatRequest(
                session_id=session_id,
                user_id=user_id,
                model=model,
                status="processing",
                request_text=request_text,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def complete_request(
        self,
        request_id: int,
        response_text: str,
        openai_request_id: str | None = None,
    ) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(ChatRequest)
                .where(ChatRequest.id == request_id)
                .values(
                    status="succeeded",
                    response_text=response_text,
                    openai_request_id=openai_request_id,
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()

    async def fail_request(self, request_id: int, error_type: str, error_message: str) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(ChatRequest)
                .where(ChatRequest.id == request_id)
                .values(
                    status="failed",
                    error_type=error_type,
                    error_message=error_message,
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()

    async def log_error(
        self,
        event_name: str,
        error_type: str,
        error_message: str,
        context: str | None = None,
        request_id: int | None = None,
        session_id: int | None = None,
        user_id: int | None = None,
    ) -> ChatErrorLog:
        async with self.session_factory() as session:
            record = ChatErrorLog(
                request_id=request_id,
                session_id=session_id,
                user_id=user_id,
                event_name=event_name,
                error_type=error_type,
                error_message=error_message,
                context=context,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record
