"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_SECRET_KEY: str = "dev-secret-key-change-in-production"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://lexai:lexai_dev@localhost:5432/lexai"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = "your-gcp-project"
    GOOGLE_CLOUD_REGION: str = "us-central1"
    GCS_BUCKET_NAME: str = "lexai-documents-dev"
    VERTEX_AI_EMBEDDING_MODEL: str = "text-embedding-004"
    VERTEX_AI_LLM_MODEL: str = "gemini-1.5-pro-002"

    # Firebase
    FIREBASE_PROJECT_ID: str = "your-firebase-project"
    FIREBASE_SERVICE_ACCOUNT_JSON: str = "./firebase-service-account.json"

    # Ollama (Local Mode)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:7b"

    # Langfuse
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Processing
    MAX_UPLOAD_SIZE_MB: int = 50
    CHUNK_SIZE_TOKENS: int = 500
    CHUNK_OVERLAP_TOKENS: int = 50
    TOP_K_CHUNKS: int = 8
    DOCUMENT_TTL_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    # Feature Flags
    ENABLE_LOCAL_MODE: bool = True
    ENABLE_CLOUD_MODE: bool = True
    REQUIRE_AUTH_FOR_UPLOAD: bool = False

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        origins = [self.FRONTEND_URL]
        if self.APP_ENV == "development":
            origins += ["http://localhost:3000", "http://127.0.0.1:3000"]
        return origins

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
