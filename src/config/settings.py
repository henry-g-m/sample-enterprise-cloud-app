"""Application configuration settings."""

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    app_title: str = "Enterprise Demo Cloud App"
    app_description: str = "Simple REST API deployed to Azure with enterprise best practices"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False

    # CORS
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_ssl: bool = False

    # Observability
    enable_app_insights: bool = False
    app_insights_connection_string: str | None = None
    log_level: str = "INFO"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
