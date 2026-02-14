from functools import lru_cache

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment / .env file.

    We allow extra keys so older env vars (like ALEMBIC_DB_URL, APP_SECRET)
    don't cause validation errors.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ScholarValley Operating System API"

    database_url: str

    @field_validator("database_url", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Use psycopg2 driver if URL is postgresql:// so connection works."""
        if v.startswith("postgresql://") and "+" not in v.split("://")[0]:
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    aws_region: str = "us-east-1"
    aws_s3_bucket: str

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    ses_from_email: str | None = None

    frontend_origin: AnyUrl | None = None

    # Optional legacy/extra values – do not break if present
    alembic_db_url: str | None = None
    app_secret: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
