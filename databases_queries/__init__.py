from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import database_settings


engine = create_async_engine(
    url=database_settings.database_url,
    echo=True
)
