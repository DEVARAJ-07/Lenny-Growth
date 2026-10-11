"""
Async database session management.
Supports PostgreSQL (with pgvector/asyncpg) and SQLite (with aiosqlite).
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.config import settings
from app.db.models import Base
from app.logging import logger

import os
from pathlib import Path

db_url = settings.database_url
if db_url.startswith("sqlite") and "lenny_growth.db" in db_url:
    # Anchor to project root if running from backend subfolder
    root_db = Path(__file__).resolve().parent.parent.parent.parent / "lenny_growth.db"
    if root_db.exists():
        db_url = f"sqlite+aiosqlite:///{root_db.as_posix()}"

is_sqlite = db_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized_successfully", url=settings.database_url.split("@")[-1])


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
