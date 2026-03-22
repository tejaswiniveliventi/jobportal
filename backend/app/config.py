from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://jobportal:changeme_strong_pass@db:5432/jobportal_db"
    postgres_user: str = "jobportal"
    postgres_password: str = "changeme_strong_pass"
    postgres_db: str = "jobportal_db"

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    secret_key: str = "insecure-dev-key-replace-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    gemini_api_key: str = ""
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""
    jsearch_api_key: str = ""
    hunter_api_key: str = ""

    upload_dir: str = "/app/uploads"
    max_upload_size_mb: int = 10

    environment: str = "development"
    log_level: str = "INFO"
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
