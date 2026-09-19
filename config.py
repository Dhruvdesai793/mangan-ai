"""Typed application settings loaded exclusively from environment variables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    mangan_env: str = "development"
    mangan_allowed_origins: str = "http://localhost:8501,http://127.0.0.1:8501"
    mangan_api_key: str = ""
    mangan_database_required: bool = False
    mangan_auto_seed: bool = True
    database_url: str = "postgresql+psycopg://moil:moil_dev_password@localhost:5432/moil_intelligence"

    gee_enabled: bool = False
    gee_project_id: str = ""
    gee_auth_method: str = "oauth"
    gee_allow_demo_features: bool = False
    gee_start_date: str = "2025-01-01"
    gee_end_date: str = "2025-12-31"
    gee_cloud_percent: int = Field(default=25, ge=0, le=100)

    frontend_api_url: str = "http://localhost:8000"

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.mangan_allowed_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
