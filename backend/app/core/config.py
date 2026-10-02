"""Application Configuration & Environment Settings.

Loads and validates all system settings using Pydantic v2 BaseSettings.
Secrets and connection parameters are loaded from environment variables or .env.
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings model validated via Pydantic v2."""

    # Project Metadata
    APP_NAME: str = "CloudDesk"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]

    # Security & JWT Tokens
    JWT_SECRET_KEY: str = "clouddesk_dev_secret_key_32_characters_long_min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Relational Database (PostgreSQL)
    # Default asyncpg driver for asynchronous SQLAlchemy
    DATABASE_URL: str = (
        "postgresql+asyncpg://clouddesk_user:clouddesk_secure_password@localhost:5432/clouddesk_db"
    )
    DATABASE_URL_SYNC: str = (
        "postgresql://clouddesk_user:clouddesk_secure_password@localhost:5432/clouddesk_db"
    )

    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    # OpenAI & LLM Settings
    OPENAI_API_KEY: str = "mock-key-for-local-dev"
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # Triage Decision Engine Parameters
    CONFIDENCE_THRESHOLD: float = 0.85
    MAX_TRIAGE_RETRY_ATTEMPTS: int = 1
    LLM_TIMEOUT_SECONDS: float = 8.0

    # External Webhook Simulator
    MOCK_HELPDESK_CALLBACK_URL: str = (
        "http://localhost:8000/api/v1/webhooks/mock-helpdesk/status-update"
    )

    @field_validator("CONFIDENCE_THRESHOLD")
    @classmethod
    def validate_confidence_threshold(cls, v: float) -> float:
        """Ensure threshold is strictly between 0.0 and 1.0."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        return v

    @property
    def is_production(self) -> bool:
        """Convenience property to check if current environment is production."""
        return self.ENVIRONMENT.lower() == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Global singleton instance for injection across the application
settings = Settings()
