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

    # Payment Whitelist (users who get free unlimited readings)
    payment_whitelist: list[int] = None  # List of Telegram user IDs

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        # Parse payment whitelist from comma-separated user IDs
        whitelist_str = os.getenv("PAYMENT_WHITELIST", "")
        payment_whitelist = []
        if whitelist_str:
            try:
                payment_whitelist = [int(uid.strip()) for uid in whitelist_str.split(",") if uid.strip()]
            except ValueError:
                print(f"Warning: Invalid PAYMENT_WHITELIST format: {whitelist_str}")

        return cls(
            telegram_bot_token=telegram_bot_token,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            redis_url=os.getenv("REDIS_URL"),
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            payment_whitelist=payment_whitelist,
        )

    @property
    def use_redis(self) -> bool:
        """Check if Redis should be used for session storage."""
        return self.redis_url is not None

    @property
    def has_ai_service(self) -> bool:
        """Check if any AI service is configured."""
        return self.anthropic_api_key is not None or self.openai_api_key is not None

    def is_whitelisted(self, user_id: int) -> bool:
        """Check if user is whitelisted for free unlimited readings."""
        if not self.payment_whitelist:
            return False
        return user_id in self.payment_whitelist


# Global configuration instance
config = Config.from_env()
