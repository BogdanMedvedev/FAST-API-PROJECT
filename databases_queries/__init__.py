from sqlalchemy import create_engine

from config import database_settings


engine = create_engine(
    url=database_settings.database_url,
    echo=True
)
