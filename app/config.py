from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类，从环境变量或 .env 文件加载配置。"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Telegram 机器人的访问令牌。
    bot_token: str = Field(validation_alias="BOT_TOKEN")
    # 机器人管理员 ID 列表，多个 ID 用逗号分隔。
    bot_admin_ids: str = Field(default="", validation_alias="BOT_ADMIN_IDS")
    # PostgreSQL 数据库连接字符串
    postgres_dsn: str = Field(
        default="postgresql+asyncpg://tg_user:tg_password@localhost:5432/tg_bot",
        validation_alias="POSTGRES_DSN",
    )
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="", validation_alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4.1-mini", validation_alias="OPENAI_MODEL")
    chat_session_ttl_seconds: int = Field(default=3600, validation_alias="CHAT_SESSION_TTL_SECONDS")
    chat_context_message_limit: int = Field(default=20, validation_alias="CHAT_CONTEXT_MESSAGE_LIMIT")
    chat_max_input_chars: int = Field(default=4000, validation_alias="CHAT_MAX_INPUT_CHARS")
    telegram_media_max_bytes: int = Field(default=20 * 1024 * 1024, validation_alias="TELEGRAM_MEDIA_MAX_BYTES")
    openai_image_detail: str = Field(default="auto", validation_alias="OPENAI_IMAGE_DETAIL")

    @property
    def admin_ids(self) -> set[int]:
        """将 bot_admin_ids 字符串解析为整数集合。"""
        if not self.bot_admin_ids.strip():
            return set()
        admin_ids: set[int] = set()
        for raw_id in self.bot_admin_ids.split(","):
            item = raw_id.strip()
            if not item:
                continue
            admin_ids.add(int(item))
        return admin_ids


@lru_cache
def get_settings() -> Settings:
    """获取单例配置实例，使用 LRU 缓存避免重复加载。"""
    return Settings()
