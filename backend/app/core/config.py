"""
Application Configuration
Loads and validates settings from environment variables using Pydantic Settings.
All configuration must come from environment variables or .env file.
No hardcoded credentials or paths.
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings loaded from environment variables.
    See .env.example for documentation on each variable.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_name: str = "RAG Scholarship Intelligence System"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ------------------------------------------------------------------
    # API Server
    # ------------------------------------------------------------------
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ------------------------------------------------------------------
    # Database (PostgreSQL)
    # ------------------------------------------------------------------
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "rag_scholarship_db"

    @property
    def database_url(self) -> str:
        """Assemble the PostgreSQL connection URL from individual components."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def async_database_url(self) -> str:
        """Assemble async PostgreSQL connection URL (for async SQLAlchemy)."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ------------------------------------------------------------------
    # Vector Store
    # ------------------------------------------------------------------
    vector_store_type: Literal["chromadb", "pgvector"] = "chromadb"
    chroma_db_path: str = "./chroma_db"

    # ------------------------------------------------------------------
    # Embedding Model
    # ------------------------------------------------------------------
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_device: Literal["cpu", "cuda", "mps"] = "cpu"

    # ------------------------------------------------------------------
    # LLM Provider
    # ------------------------------------------------------------------
    llm_provider: Literal["mock", "openai", "google", "anthropic", "ollama"] = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    google_api_key: str = ""
    google_model: str = "gemini-1.5-flash"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-haiku-20240307"

    # ------------------------------------------------------------------
    # RAG Pipeline
    # ------------------------------------------------------------------
    chunk_size: int = 512
    chunk_overlap: int = 50
    retrieval_top_k: int = 5
    reranker_top_k: int = 3

    # ------------------------------------------------------------------
    # Hybrid Retrieval Weights
    # ------------------------------------------------------------------
    semantic_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.4, ge=0.0, le=1.0)

    # ------------------------------------------------------------------
    # Recommendation Scoring Weights
    # ------------------------------------------------------------------
    score_weight_semantic: float = Field(default=0.35, ge=0.0, le=1.0)
    score_weight_eligibility: float = Field(default=0.30, ge=0.0, le=1.0)
    score_weight_course: float = Field(default=0.15, ge=0.0, le=1.0)
    score_weight_academic: float = Field(default=0.10, ge=0.0, le=1.0)
    score_weight_deadline: float = Field(default=0.10, ge=0.0, le=1.0)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return upper


@lru_cache()
def get_settings() -> Settings:
    """
    Return cached Settings instance.
    Using lru_cache ensures settings are only parsed once per process.
    """
    return Settings()


# Convenience export — use this in other modules:
#   from app.core.config import settings
settings = get_settings()
