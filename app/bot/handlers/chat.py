from __future__ import annotations

from io import BytesIO

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import Settings, get_settings
from app.managers.chat_manager import ChatManager
from app.services.chat_service import ChatAttachment, ChatService
from app.storage.db import get_session_factory
from app.storage.repositories.chat_repository import ChatRepository
from app.utils.message_chunks import split_telegram_message

router = Router()


def build_chat_service(settings: Settings) -> ChatService:
    """根据配置创建聊天模型服务。"""
    from openai import AsyncOpenAI

    client_kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        client_kwargs["base_url"] = settings.openai_base_url
    return ChatService(
        client=AsyncOpenAI(**client_kwargs),
        model=settings.openai_model,
        image_detail=settings.openai_image_detail,
    )


async def download_telegram_file(bot: Bot, file_id: str) -> bytes:
    """从 Telegram 下载文件内容到内存。"""
    telegram_file = await bot.get_file(file_id)
    buffer = BytesIO()
    await bot.download_file(telegram_file.file_path, destination=buffer)
    return buffer.getvalue()


async def collect_attachments(message: Message, settings: Settings) -> list[ChatAttachment]:
    """从 Telegram 消息中提取当前支持的媒体附件。"""
    bot = message.bot
    attachments: list[ChatAttachment] = []

    if message.photo:
        photo = message.photo[-1]
        if photo.file_size and photo.file_size > settings.telegram_media_max_bytes:
            raise ValueError("图片文件过大。")
        attachments.append(
            ChatAttachment(
                kind="image",
                filename=f"telegram-photo-{photo.file_unique_id}.jpg",
                mime_type="image/jpeg",
                data=await download_telegram_file(bot, photo.file_id),
            )
        )

    if message.video:
        if message.video.file_size and message.video.file_size > settings.telegram_media_max_bytes:
            raise ValueError("视频文件过大。")
        attachments.append(
            ChatAttachment(
                kind="video",
                filename=message.video.file_name or f"telegram-video-{message.video.file_unique_id}.mp4",
                mime_type=message.video.mime_type or "video/mp4",
                data=await download_telegram_file(bot, message.video.file_id),
            )
        )

    if message.audio:
        if message.audio.file_size and message.audio.file_size > settings.telegram_media_max_bytes:
            raise ValueError("音频文件过大。")
        attachments.append(
            ChatAttachment(
                kind="audio",
                filename=message.audio.file_name or f"telegram-audio-{message.audio.file_unique_id}.mp3",
                mime_type=message.audio.mime_type or "audio/mpeg",
                data=await download_telegram_file(bot, message.audio.file_id),
            )
        )

    if message.voice:
        if message.voice.file_size and message.voice.file_size > settings.telegram_media_max_bytes:
            raise ValueError("语音文件过大。")
        attachments.append(
            ChatAttachment(
                kind="audio",
                filename=f"telegram-voice-{message.voice.file_unique_id}.ogg",
                mime_type=message.voice.mime_type or "audio/ogg",
                data=await download_telegram_file(bot, message.voice.file_id),
            )
        )

    return attachments


async def answer_model_reply(message: Message, reply: str) -> None:
    """把模型回复按 Telegram 长度限制分段发送。"""
    for chunk in split_telegram_message(reply):
        await message.answer(chunk)


@router.message(Command("chat"))
async def chat_handler(message: Message) -> None:
    if message.chat.type != "private":
        await message.answer("请在私聊中使用 /chat。")
        return

    if not message.from_user:
        await message.answer("无法识别当前用户。")
        return

    settings = get_settings()
    repository = ChatRepository(get_session_factory(settings))
    service = build_chat_service(settings)
    manager = ChatManager(repository=repository, service=service, settings=settings)
    session_id = await manager.enable_chat(message.chat.id, message.from_user.id)
    await message.answer(f"聊天模式已开启。session_id: {session_id}")


@router.message()
async def chat_text_handler(message: Message) -> None:
    if message.chat.type != "private":
        return
    if not message.from_user:
        return
    if message.text and message.text.startswith("/"):
        return

    settings = get_settings()
    repository = ChatRepository(get_session_factory(settings))
    service = build_chat_service(settings)
    manager = ChatManager(repository=repository, service=service, settings=settings)

    try:
        attachments = await collect_attachments(message, settings)
        if not message.text and not message.caption and not attachments:
            return
        text = message.text or message.caption or "请分析这条媒体消息。"
        _, reply = await manager.handle_user_message(message.chat.id, message.from_user.id, text, attachments)
    except ValueError as exc:
        await message.answer(str(exc))
        return
    except Exception:
        await message.answer("抱歉，当前无法回复。")
        return

    await answer_model_reply(message, reply)
