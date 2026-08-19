import enum
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseType(str, enum.Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    ENV_MODE: Literal["development", "staging", "production", "testing"] = "development"

    # Security
    JWT_SECRET_KEY: str = Field(
        default="DEV_SECRET_KEY_NEVER_USE_IN_PRODUCTION_32CHARS_MIN",
        description="JWT Secret key",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_TYPE: DatabaseType = DatabaseType.SQLITE
    SQLITE_DB_PATH: str = "./openhealthkit.db"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "openhealth"
    POSTGRES_PASSWORD: str = "openhealth_secret_pass"
    POSTGRES_DB: str = "openhealthkit_db"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Security & Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Initial Admin Setup
    INITIAL_ADMIN_EMAIL: str = "admin@openhealthkit.org"
    INITIAL_ADMIN_PASSWORD: str = "AdminPass123!ChangeMe"

    # i18n
    DEFAULT_LOCALE: str = "en"

    # Redis
    REDIS_URL: str | None = "redis://localhost:6379/0"
    ENABLE_REDIS: bool = False

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.ENV_MODE == "production":
            if "DEV_SECRET_KEY" in self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production mode, JWT_SECRET_KEY must be a secure "
                    "random secret of at least 32 characters. Do not use default development keys."
                )
            if self.INITIAL_ADMIN_PASSWORD == "AdminPass123!ChangeMe":
                raise ValueError(
                    "CRITICAL SECURITY ERROR: In production mode, INITIAL_ADMIN_PASSWORD must be changed from default."
                )
        return self

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_TYPE == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return f"sqlite:///{self.SQLITE_DB_PATH}"

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_TYPE == DatabaseType.POSTGRESQL:
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"


settings = Settings()
