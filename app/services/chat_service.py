from __future__ import annotations

import base64
from dataclasses import dataclass

from openai import AsyncOpenAI


@dataclass(slots=True)
class ChatAttachment:
    """一次请求中临时传给模型的媒体附件。"""

    kind: str
    filename: str
    mime_type: str
    data: bytes


@dataclass(slots=True)
class ChatCompletionResult:
    """模型回复结果。"""

    text: str
    request_id: str | None = None


class ChatService:
    """封装 OpenAI Responses API 调用。"""

    def __init__(self, client: AsyncOpenAI, model: str, image_detail: str = "auto") -> None:
        self.client = client
        self.model = model
        self.image_detail = image_detail

    def build_user_content(self, text: str, attachments: list[ChatAttachment] | None = None) -> list[dict[str, str]]:
        """把用户文字和媒体附件转换为 Responses API 的多模态 content。"""
        content: list[dict[str, str]] = [{"type": "input_text", "text": text}]
        for attachment in attachments or []:
            encoded = base64.b64encode(attachment.data).decode("ascii")
            if attachment.kind == "image":
                content.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:{attachment.mime_type};base64,{encoded}",
                        "detail": self.image_detail,
                    }
                )
            else:
                content.append(
                    {
                        "type": "input_file",
                        "filename": attachment.filename,
                        "file_data": encoded,
                    }
                )
        return content

    async def complete(self, messages: list[dict[str, object]]) -> ChatCompletionResult:
        """向模型发送上下文消息，并返回整理后的文本回复。"""
        response = await self.client.responses.create(model=self.model, input=messages)
        text = getattr(response, "output_text", "") or ""
        return ChatCompletionResult(text=text.strip(), request_id=getattr(response, "id", None))
