from __future__ import annotations


def split_telegram_message(text: str, limit: int = 4096) -> list[str]:
    """把文本拆成符合 Telegram 长度限制的消息片段。

    Telegram 不接受超过 4096 字符的单条消息。这里优先按行边界拆分，
    尽量保留段落可读性；如果单行本身过长，再退回到固定长度硬切。
    """
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        # 单行过长时无法保留完整行结构，先提交前面积累的内容，
        # 再把这一行按固定长度拆成多个片段。
        if len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            for start in range(0, len(line), limit):
                chunks.append(line[start : start + limit])
            continue
        if len(current) + len(line) > limit:
            chunks.append(current)
            current = line
        else:
            current += line
    if current:
        chunks.append(current)
    return chunks or [text[:limit]]
