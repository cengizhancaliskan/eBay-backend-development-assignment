from src.core.config import Settings


def test_settings():
    """Test settings configuration."""
    settings = Settings()
    assert settings.DB_TABLE_PREFIX == "test_"
    assert isinstance(settings.async_database_url, str)
    assert "postgresql+asyncpg" in settings.async_database_url
