"""
Application configuration using pydantic-settings.
"""
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Active LLM Configuration
    llm_provider: Literal["ollama", "anthropic", "openai"] = Field(
        default="ollama",
        alias="LLM_PROVIDER"
    )
    llm_model: str = Field(
        default="qwen2.5:3b",
        alias="LLM_MODEL"
    )
    embedding_model: str = Field(
        default="nomic-embed-text",
        alias="EMBEDDING_MODEL"
    )

    # Ollama settings
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        alias="OLLAMA_BASE_URL"
    )
    ollama_models_path: Optional[str] = Field(
        default=r"D:\LLMs\ollama_store",
        alias="OLLAMA_MODELS"
    )

    # Cloud API keys (optional fallback)
    anthropic_api_key: Optional[str] = Field(
        default=None,
        alias="ANTHROPIC_API_KEY"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_KEY"
    )

    # Database (Supabase / Postgres / SQLite)
    database_url: str = Field(
        default="sqlite+aiosqlite:///./lenny_growth.db",
        alias="DATABASE_URL"
    )
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, alias="SUPABASE_KEY")

    # Supabase Storage Configuration
    supabase_storage_bucket: str = Field(
        default="lenny-growth-chats",
        alias="SUPABASE_STORAGE_BUCKET"
    )

    # Operational settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    request_timeout_s: int = Field(default=120, alias="REQUEST_TIMEOUT_S")
    similarity_threshold: float = Field(default=0.015, alias="SIMILARITY_THRESHOLD")
    top_k_retrieval: int = Field(default=6, alias="TOP_K_RETRIEVAL")


settings = Settings()
