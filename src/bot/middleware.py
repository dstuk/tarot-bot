"""Bot middleware for language detection and rate limiting."""
import re
from typing import Optional
from langdetect import detect, LangDetectException


class LanguageDetector:
    """Detect user language with Ukrainian/Russian disambiguation."""

    # Ukrainian-specific characters and words
    UKRAINIAN_MARKERS = {
        "chars": ["і", "ї", "є", "ґ"],
        "words": ["чи", "який", "мені", "тобі", "цей", "той", "ця", "та", "ті", "тих"],
    }

    # Russian-specific characters and words
    RUSSIAN_MARKERS = {
        "chars": ["ы", "э", "ъ"],
        "words": ["или", "который", "мне", "тебе", "этот", "тот", "эта", "эти", "тех"],
    }

    @classmethod
    def detect_language(cls, text: str, default: str = "en") -> str:
        """
        Detect language from text with Ukrainian/Russian disambiguation.

        Args:
            text: Input text to analyze
            default: Default language if detection fails

        Returns:
            Language code: "en", "ru", or "uk"
        """
        if not text or len(text.strip()) < 3:
            return default

        try:
            # First pass: use langdetect
            detected = detect(text)

            # If detected as English, return immediately
            if detected == "en":
                return "en"

            # If detected as Russian, check for Ukrainian markers
            if detected == "ru":
                return cls._disambiguate_cyrillic(text)

            # If detected as Ukrainian, verify it's not Russian
            if detected == "uk":
                if cls._has_russian_markers(text):
                    return "ru"
                return "uk"

            # For other detections, fall back to Cyrillic disambiguation
            if cls._is_cyrillic(text):
                return cls._disambiguate_cyrillic(text)

            return default

        except LangDetectException:
            # Fallback: check if text contains Cyrillic
            if cls._is_cyrillic(text):
                return cls._disambiguate_cyrillic(text)
            return default

    @classmethod
    def _is_cyrillic(cls, text: str) -> bool:
        """Check if text contains Cyrillic characters."""
        cyrillic_pattern = re.compile("[а-яА-ЯёЁіїєґІЇЄҐ]")
        return bool(cyrillic_pattern.search(text))

    @classmethod
    def _has_ukrainian_markers(cls, text: str) -> bool:
        """Check for Ukrainian-specific markers in text."""
        text_lower = text.lower()

        # Check for Ukrainian-specific characters
        if any(char in text_lower for char in cls.UKRAINIAN_MARKERS["chars"]):
            return True

        # Check for Ukrainian-specific words
        words = text_lower.split()
        if any(word in words for word in cls.UKRAINIAN_MARKERS["words"]):
            return True

        return False

    @classmethod
    def _has_russian_markers(cls, text: str) -> bool:
        """Check for Russian-specific markers in text."""
        text_lower = text.lower()

        # Check for Russian-specific characters
        if any(char in text_lower for char in cls.RUSSIAN_MARKERS["chars"]):
            return True

        # Check for Russian-specific words
        words = text_lower.split()
        if any(word in words for word in cls.RUSSIAN_MARKERS["words"]):
            return True

        return False

    @classmethod
    def _disambiguate_cyrillic(cls, text: str) -> str:
        """Disambiguate between Ukrainian and Russian for Cyrillic text."""
        # Check Ukrainian markers first (more specific)
        if cls._has_ukrainian_markers(text):
            return "uk"

        # Check Russian markers
        if cls._has_russian_markers(text):
            return "ru"

        # Calculate character frequency ratio for 'і' vs 'и'
        i_count = text.lower().count("і")
        y_count = text.lower().count("и")

        # Ukrainian uses 'і' more frequently
        if i_count > 0 and (y_count == 0 or i_count / (i_count + y_count) > 0.3):
            return "uk"

        # Default to Russian if no clear indicators
        return "ru"


class RateLimiter:
    """Simple rate limiter to prevent spam (5 requests per user per minute)."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: dict = {}  # {user_id: [timestamps]}

    def is_allowed(self, user_id: int) -> tuple[bool, int]:
        """
        Check if user request is allowed.

        Args:
            user_id: Telegram user ID

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        from datetime import datetime, timedelta

        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Get user request history
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []

        # Filter out old requests outside the time window
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] if ts > window_start
        ]

        # Check if under limit
        current_count = len(self.user_requests[user_id])
        if current_count < self.max_requests:
            self.user_requests[user_id].append(now)
            return True, self.max_requests - current_count - 1
        else:
            return False, 0


# Global instances
language_detector = LanguageDetector()
rate_limiter = RateLimiter()


# Convenience functions for use in handlers
def detect_language(text: str, default: str = "en") -> str:
    """Detect language from text."""
    return language_detector.detect_language(text, default)


def rate_limit_middleware(handler):
    """
    Middleware wrapper for rate limiting handlers.

    Args:
        handler: The async handler function to wrap

    Returns:
        Wrapped handler with rate limiting
    """
    async def wrapper(update, context):
        from telegram import Update
        from src.i18n.translations import translation_manager

        user_id = update.effective_user.id
        is_allowed, remaining = rate_limiter.is_allowed(user_id)

        if not is_allowed:
            # Get user language from session if available
            from src.services.session_service import SessionService
            session_service = SessionService()
            session = session_service.get_session(user_id)
            language = session.language if session else "en"

            error_message = translation_manager.get_error_text("rate_limit", language)
            error_message = error_message.format(remaining=remaining)

            if update.message:
                await update.message.reply_text(error_message)
            elif update.callback_query:
                await update.callback_query.answer(error_message, show_alert=True)

            return

        # Call the original handler
        return await handler(update, context)

    return wrapper
