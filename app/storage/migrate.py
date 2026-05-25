from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import text

from app.config import get_settings
from app.storage.db import get_engine


async def run_migrations() -> None:
    settings = get_settings()
    engine = get_engine(settings)
    migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
    sql_files = sorted(migrations_dir.resolve().glob("*.sql"))

    async with engine.begin() as conn:
        for path in sql_files:
            sql = path.read_text(encoding="utf-8")
            for statement in sql.split(";"):
                if statement.strip():
                    await conn.execute(text(statement))


def main() -> None:
    asyncio.run(run_migrations())


if __name__ == "__main__":
    main()
