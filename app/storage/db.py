from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.config import Settings

# 全局数据库引擎和会话工厂单例
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None


def get_engine(settings: Settings) -> AsyncEngine:
    """
    获取数据库引擎单例。

    使用全局单例模式避免重复创建引擎。

    Args:
        settings: 应用配置对象

    Returns:
        SQLAlchemy 异步引擎实例
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.postgres_dsn,
            pool_pre_ping=True,
            connect_args={"ssl": False},
        )
    return _engine


def get_session_factory(settings: Settings) -> async_sessionmaker:
    """
    获取数据库会话工厂单例。

    Args:
        settings: 应用配置对象

    Returns:
        SQLAlchemy 异步会话工厂
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(settings), expire_on_commit=False)
    return _session_factory


async def ping_database(settings: Settings) -> bool:
    """
    检查数据库连接是否正常。

    Args:
        settings: 应用配置对象

    Returns:
        连接成功返回 True
    """
    engine = get_engine(settings)
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True
