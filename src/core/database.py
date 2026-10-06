from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import settings

Base = declarative_base()

_BASE_URL = settings.POSTGRES_GLOBAL_DB_URL
_SA_URL = _BASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_async_engine(
    _SA_URL,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=10,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_async_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as db:
        yield db


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
