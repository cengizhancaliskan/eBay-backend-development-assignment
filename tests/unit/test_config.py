from src.core.config import Settings


def test_settings():
    """Test settings configuration."""
    settings = Settings()

    assert isinstance(settings.async_database_url, str)
    assert "postgresql+asyncpg" in settings.async_database_url
