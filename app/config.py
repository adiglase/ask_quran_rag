from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ask Quran RAG"
    environment: Literal["local", "test", "production"] = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/ask_quran_rag"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ASK_QURAN_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
