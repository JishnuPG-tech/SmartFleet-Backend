import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models.base import Base

connect_args = {}
if "sqlite" in settings.async_database_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DB_ECHO,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    import app.models  # Ensure all models are loaded
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
