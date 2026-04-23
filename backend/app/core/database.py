from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

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
    # Keep pool sizing at SQLAlchemy defaults (pool_size=5, max_overflow=10)
    # to stay well under Railway's per-instance connection cap. Bumping these
    # previously made multi-worker deployments exhaust the DB connection limit
    # so every request queued indefinitely — manifesting as login hangs.
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
