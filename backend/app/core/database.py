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
    # Recycle connections every 25 minutes so we proactively rotate before
    # Railway's internal 30-minute idle cutoff.
    pool_recycle=1500,
    # Modest sizing — most requests are short and we don't want to hoard
    # connections against Railway's plan limits.
    pool_size=10,
    max_overflow=20,
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
