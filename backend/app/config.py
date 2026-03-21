"""
Application configuration management.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Claude Configuration
    claude_api_key: str
    claude_base_url: Optional[str] = None

    # DeepSeek Configuration
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # CourtListener Configuration
    courtlistener_api_token: str

    # Database Configuration
    database_url: str = "sqlite:///./crimejournal.db"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"

    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Embedding Model Configuration
    embedding_model: str = "all-MiniLM-L6-v2"

    # Application Settings
    app_name: str = "CrimeJournal"
    app_version: str = "1.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
