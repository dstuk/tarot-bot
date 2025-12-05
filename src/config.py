"""Configuration management for Telegram Tarot Bot."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    # Telegram Bot Configuration
    telegram_bot_token: str

    # AI Service Configuration
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Session Storage Configuration
    redis_url: Optional[str] = None

    # Application Environment
    environment: str = "development"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        return cls(
            telegram_bot_token=telegram_bot_token,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            redis_url=os.getenv("REDIS_URL"),
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    @property
    def use_redis(self) -> bool:
        """Check if Redis should be used for session storage."""
        return self.redis_url is not None

    @property
    def has_ai_service(self) -> bool:
        """Check if any AI service is configured."""
        return self.anthropic_api_key is not None or self.openai_api_key is not None


# Global configuration instance
config = Config.from_env()
