"""Internationalization utilities for multilingual bot interface."""
import json
from pathlib import Path
from typing import Dict, Optional


class TranslationManager:
    """Manages translations for bot UI text in multiple languages."""

    def __init__(self, locales_dir: str = "src/i18n/locales"):
        """Initialize translation manager and load all locale files."""
        self.locales_dir = Path(locales_dir)
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all translation files from locales directory."""
        for lang_code in ["en", "ru", "uk"]:
            locale_file = self.locales_dir / f"{lang_code}.json"
            if locale_file.exists():
                with open(locale_file, "r", encoding="utf-8") as f:
                    self.translations[lang_code] = json.load(f)

    def get_text(self, key: str, language: str = "en", **kwargs) -> str:
        """
        Get translated text for a given key.

        Args:
            key: Translation key
            language: Target language code
            **kwargs: Format arguments for string interpolation

        Returns:
            Translated text (falls back to English if language not found)
        """
        # Get translation dict for language (fallback to English)
        lang_dict = self.translations.get(language, self.translations.get("en", {}))

        # Get translated text
        text = lang_dict.get(key, key)

        # Apply string formatting if kwargs provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass  # Return unformatted if keys don't match

        return text

    def get_button_text(self, button_key: str, language: str = "en") -> str:
        """Get button text translation."""
        return self.get_text(f"btn_{button_key}", language)

    def get_message_text(self, message_key: str, language: str = "en", **kwargs) -> str:
        """Get message text translation with optional formatting."""
        return self.get_text(f"msg_{message_key}", language, **kwargs)

    def get_error_text(self, error_key: str, language: str = "en") -> str:
        """Get error message translation."""
        return self.get_text(f"err_{error_key}", language)


# Global translation manager instance
translation_manager = TranslationManager()
