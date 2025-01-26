from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import database_settings


engine = create_async_engine(
    url=database_settings.database_url,
    echo=True
)

session_factory = async_sessionmaker(engine, expire_on_commit=True)

async def get_session():
    """Сессия для взаимодействия с БД"""
    async with session_factory() as session:
        yield session


depends_session = Annotated[AsyncSession, Depends(get_session)]
