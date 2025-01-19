from pydantic_settings import BaseSettings


class DatabasesSettings(BaseSettings):
    """Настройки подключения к БД"""

    HOSTNAME: str
    NAME: str
    PORT: int
    USER: str
    PASSWORD: str

    class Config:
        env_prefix = 'DB_'
        case_sensitive = False
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOSTNAME}:{self.PORT}/{self.NAME}'


database_settings = DatabasesSettings()
