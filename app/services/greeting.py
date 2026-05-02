from datetime import datetime, timedelta, timezone

from aiogram.types import User

UTC_PLUS_8 = timezone(timedelta(hours=8), name="UTC+8")


def get_start_greeting() -> str:
    hour = datetime.now(UTC_PLUS_8).hour
    if 5 <= hour < 12:
        return "上午好"
    if 12 <= hour < 18:
        return "下午好"
    return "夜深了，注意休息"


def build_start_message(user: User | None) -> str:
    display_name = user.full_name if user else "你好"
    return (
        f"{get_start_greeting()},{display_name}\n\n"
        "当前可用命令：\n"
        "/start - 查看基础说明"
    )
