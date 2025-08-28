from __future__ import annotations

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Use .env for local development. Avoid hardcoding secrets.
    """

    # AWS
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    aws_default_region: str = Field(default="us-east-1", description="Default AWS region")

    # Database
    database_url: str = Field(..., alias="DATABASE_URL", description="SQLAlchemy database URL for PostgreSQL")

    # Shutdown policy
    idle_threshold_minutes: int = Field(default=120, description="Minutes of idleness before shutdown")
    scheduler_interval_seconds: int = Field(default=300, description="Background scheduler tick interval in seconds")

    # App info
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


def get_settings() -> Settings:
    """
    Resolve settings with environment variables.
    This is used as a FastAPI dependency.
    """
    return Settings()  # type: ignore
