"""
Application configuration management.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MiniMax Configuration (统一AI服务)
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-Text-02"  # 最新M2.7模型

    # DeepSeek Configuration (已废弃，统一使用MiniMax)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # 兼容旧配置（已废弃）
    claude_api_key: str = ""
    claude_base_url: Optional[str] = None

    # CourtListener Configuration
    courtlistener_api_token: str = ""

    # Database Configuration
    database_url: str = "sqlite:///./crimejournal.db"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"

    # JWT Configuration
    jwt_secret_key: str = ""
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
