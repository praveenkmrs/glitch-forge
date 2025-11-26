"""Application configuration using Pydantic Settings.

This module demonstrates production-ready configuration management:
1. Type-safe settings using Pydantic
2. Environment variable parsing
3. Validation on startup
4. Secrets management ready
"""

from typing import List

from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    These settings are loaded from environment variables and validated
    at application startup. This ensures configuration errors are caught
    immediately rather than at runtime.
    """

    # Application
    APP_NAME: str = "Glitch Forge HITL API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str  # REQUIRED - must be set in environment
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: PostgresDsn

    # Redis
    REDIS_URL: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
