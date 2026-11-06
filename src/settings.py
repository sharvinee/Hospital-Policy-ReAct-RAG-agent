"""Load and validate environment-based settings for the policy RAG application."""

from functools import cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Validated application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(min_length=1)

    embedding_model: str = "openai:text-embedding-3-small"
    chat_model: str = "openai:gpt-5.6-luna"

    retrieval_top_k: int = Field(default=4, ge=1)
    retrieval_score_threshold: float = Field(default=0.405, ge=0.0, le=1.0)

    langsmith_api_key: str = Field(min_length=1)



@cache
def get_settings() -> Settings:
    """Return one cached, validated Settings instance per process."""
    return Settings()
