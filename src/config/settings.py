from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Bank Churn API"
    app_version: str = "1.0.0"
    app_environment: Literal["development", "test", "production"] = "development"
    debug: bool = False

    # Database: sqlite by default, switch to postgres via .env.
    database_backend: Literal["sqlite", "postgres"] = "sqlite"
    sqlite_database_path: str = str(PROJECT_ROOT / "data" / "bank_churn.db")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "bank_churn_db"

    model_artifact_path: str = str(PROJECT_ROOT / "artifacts" / "bank_churn_model.joblib")
    model_metadata_path: str = str(PROJECT_ROOT / "artifacts" / "model_metadata.json")
    feature_schema_path: str = str(PROJECT_ROOT / "artifacts" / "feature_schema.json")

    # Stored as a plain string (not list[str]) because pydantic-settings tries
    # to JSON-decode list-typed env values before field validators run, which
    # breaks on a simple comma-separated string. Parsed via the property below.
    cors_origins_raw: str = Field(default="http://localhost:8501", alias="cors_origins")

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]

    @property
    def database_url(self) -> str:
        if self.database_backend == "postgres":
            user = quote_plus(self.postgres_user)
            password = quote_plus(self.postgres_password)
            return (
                f"postgresql+asyncpg://{user}:{password}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

        database_path = Path(self.sqlite_database_path)
        database_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+aiosqlite:///{database_path}"

    @property
    def database_engine_kwargs(self) -> dict:
        if self.database_backend == "postgres":
            return {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
                "pool_recycle": 300,
                "pool_pre_ping": True,
                "pool_reset_on_return": "rollback",
            }
        return {"connect_args": {"check_same_thread": False}}


@lru_cache
def get_settings() -> Settings:
    return Settings()
