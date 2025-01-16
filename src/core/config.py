from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # App Settings
    ENVIRONMENT: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKER_COUNT: int = 1
    APP_NAME: str = "Ebay Backend Assignment Listing API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Ebay Backend Assignment with SQLAlchemy and PostgreSQL"
    API_V1_STR: str = "/v1"

    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str | None = None
    DB_TABLE_PREFIX: str = "test_"

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Create cached settings instance to avoid reading env variables multiple times
    """
    return Settings()


settings = get_settings()
