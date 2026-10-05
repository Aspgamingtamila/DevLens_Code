"""DevLens Configuration & Environment Settings.

Defines all configuration parameters with safe defaults for local development
and strict validations for production.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "DevLens"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API & Networking
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Database Configuration (Defaults to SQLite WAL mode for fast zero-config dev/testing)
    DATABASE_URL: str = "sqlite+aiosqlite:///./devlens.db"
    DB_ECHO: bool = False
    
    # JWT Authentication & Security
    # In production, JWT_SECRET_KEY must be provided via environment variable
    JWT_SECRET_KEY: str = "devlens-insecure-dev-secret-key-change-in-production-min-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Provider Configuration
    # Options: "mock" (default offline), "gemini", "openai"
    DEFAULT_AI_PROVIDER: str = "mock"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Rate Limiting & Safety Limits
    RATE_LIMIT_ANALYSES_PER_MINUTE: int = 20
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    MAX_CODE_LENGTH_CHARS: int = 10000
    MAX_CODE_LINES: int = 500
    MAX_PAYLOAD_SIZE_BYTES: int = 51200  # 50 KB
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
