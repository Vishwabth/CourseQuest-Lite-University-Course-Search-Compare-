from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/coursequest"
    INGEST_TOKEN: str = "supersecrettoken"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    AUTO_INGEST: int = 0
    AUTO_INGEST_PATH: str = "/sample_data/courses.csv"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
if os.getenv("PYTEST_CURRENT_TEST"):
    Settings.model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")
settings = Settings()
def allowed_origins() -> List[str]:
    return [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
