"""
Application configuration management.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MiniMax Configuration (用于总结、实体提取等任务)
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-M2.7-highspeed"  # 最新M2.7高速模型

    # DeepSeek Configuration
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

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

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_key_must_be_set(cls, v: str) -> str:
        """Ensure JWT secret key is set and meets minimum length requirement."""
        if not v or len(v) < 32:
            raise ValueError(
                "JWT secret key must be set in environment variables (JWT_SECRET_KEY) "
                "and must be at least 32 characters long"
            )
        return v

    # Embedding Model Configuration
    embedding_model: str = "all-MiniLM-L6-v2"

    # Application Settings
    app_name: str = "CrimeJournal"
    app_version: str = "1.0.0"
    debug: bool = True

    # CORS Configuration
    allowed_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
