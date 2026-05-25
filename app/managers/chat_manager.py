from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.config import Settings
from app.services.chat_service import ChatAttachment, ChatService
from app.storage.repositories.chat_repository import ChatRepository

LOGGER = logging.getLogger(__name__)


class ChatManager:
    """编排聊天会话、上下文、模型调用和数据库记录。"""

    def __init__(self, repository: ChatRepository, service: ChatService, settings: Settings) -> None:
        self.repository = repository
        self.service = service
        self.settings = settings

    async def enable_chat(self, chat_id: int, user_id: int) -> int:
        session = await self.repository.get_active_session(chat_id, user_id)
        if session is not None:
            return session.id
        session = await self.repository.create_session(chat_id, user_id)
        return session.id

    async def handle_user_message(
        self,
        chat_id: int,
        user_id: int,
        text: str,
        attachments: list[ChatAttachment] | None = None,
    ) -> tuple[int, str]:
        """处理一条用户消息，并返回会话 ID 和模型回复。"""
        session = await self.repository.get_active_session(chat_id, user_id)
        now = datetime.now(timezone.utc)
        if session is None or session.last_message_at is None:
            session = await self.repository.create_session(chat_id, user_id)
        else:
            last_message_at = session.last_message_at
            if last_message_at.tzinfo is None:
                last_message_at = last_message_at.replace(tzinfo=timezone.utc)
            if (now - last_message_at).total_seconds() > self.settings.chat_session_ttl_seconds:
                await self.repository.close_session(session.id)
                session = await self.repository.create_session(chat_id, user_id)

        await self.repository.touch_session(session.id)
        user_message = text[: self.settings.chat_max_input_chars]
        if attachments:
            media_names = ", ".join(attachment.filename for attachment in attachments)
            user_message = f"{user_message}\n[本条消息包含媒体附件: {media_names}]".strip()
        await self.repository.create_message(session.id, "user", user_message)

        request = await self.repository.create_request(
            session_id=session.id,
            user_id=user_id,
            model=self.service.model,
            request_text=user_message,
        )

        history = await self.repository.get_recent_messages(session.id, self.settings.chat_context_message_limit)
        payload: list[dict[str, object]] = [{"role": msg.role, "content": msg.content} for msg in history]
        if attachments and payload:
            payload[-1] = {"role": "user", "content": self.service.build_user_content(user_message, attachments)}

        try:
            completion = await self.service.complete(payload)
            reply = completion.text or "抱歉，我暂时没有生成结果。"
            await self.repository.create_message(session.id, "assistant", reply)
            await self.repository.complete_request(request.id, reply, completion.request_id)
            return session.id, reply
        except Exception as exc:
            LOGGER.exception("Chat completion failed for session %s", session.id)
            await self.repository.fail_request(request.id, type(exc).__name__, str(exc))
            await self.repository.log_error(
                event_name="chat_completion_failed",
                error_type=type(exc).__name__,
                error_message=str(exc),
                context=user_message[:500],
                request_id=request.id,
                session_id=session.id,
                user_id=user_id,
            )
            raise
