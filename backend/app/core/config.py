"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Code Generator"
    DEBUG: bool = True

    # Database (Directive 19 - points to backend/db/codegen.db)
    DATABASE_URL: str = "sqlite+aiosqlite:///./db/codegen.db"

    # LLM Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: Literal["openai", "anthropic"] = "openai"

    # LangSmith Observability
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "code-generator"
    LANGSMITH_TRACING: bool = False

    # Code Execution (Directive 06 - subprocess sandbox)
    MAX_ITERATIONS: int = 5
    EXECUTION_TIMEOUT: int = 5  # seconds

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]  # Directive 12 - Port 5173

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
