from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    bot_admin_ids: str = Field(default="", validation_alias="BOT_ADMIN_IDS")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    postgres_dsn: str = Field(
        default="postgresql+asyncpg://tg_user:tg_password@localhost:5432/tg_bot",
        validation_alias="POSTGRES_DSN",
    )
    job_result_ttl_seconds: int = Field(default=3600, validation_alias="JOB_RESULT_TTL_SECONDS")

    @property
    def admin_ids(self) -> set[int]:
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
    return Settings()
