"""Unit tests for application settings."""

from src.config.settings import Settings


class TestSettings:
    """Test Settings defaults and environment overrides."""

    def test_defaults(self):
        """Settings load sane defaults when no environment variables are set."""
        settings = Settings(_env_file=None)

        assert settings.app_title == "Enterprise Demo Cloud App"
        assert settings.environment == "development"
        assert settings.port == 8000
        assert settings.debug is False
        assert settings.redis_host == "localhost"
        assert settings.redis_port == 6379

    def test_env_override(self, monkeypatch):
        """Settings pick up values from environment variables."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("DEBUG", "true")

        settings = Settings(_env_file=None)

        assert settings.environment == "production"
        assert settings.port == 9000
        assert settings.debug is True
