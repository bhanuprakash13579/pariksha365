from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

import os as _os

# Safe pool sizing for Railway's hobby PostgreSQL (max 25 connections).
# Formula: (pool_size + max_overflow) × WEB_CONCURRENCY ≤ 25
# With defaults: (3 + 7) × 2 workers = 20 connections — leaves 5 spare for
# seed scripts, admin tools, or pgAdmin. Raise DB_POOL_SIZE via Railway env
# vars if you're on a plan with a higher connection cap.
_DB_POOL_SIZE = int(_os.getenv("DB_POOL_SIZE", "3"))
_DB_MAX_OVERFLOW = int(_os.getenv("DB_MAX_OVERFLOW", "7"))
_DB_POOL_TIMEOUT = int(_os.getenv("DB_POOL_TIMEOUT", "30"))

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True,
    # Railway Postgres drops idle connections after a few minutes. Without
    # pool_pre_ping the first request after an idle period hangs for the full
    # TCP timeout before SQLAlchemy notices and reconnects — users experience
    # this as the app being "frozen" or returning Network Error on login.
    pool_pre_ping=True,
    pool_recycle=1500,
    pool_size=_DB_POOL_SIZE,
    max_overflow=_DB_MAX_OVERFLOW,
    pool_timeout=_DB_POOL_TIMEOUT,
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Alias used by main.py lifespan seeder
SessionLocal = async_session_maker

Base = declarative_base()

async def get_db():
    async with async_session_maker() as session:
        yield session
