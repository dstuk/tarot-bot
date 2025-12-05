"""Tarot Card entity model."""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Card:
    """Represents a single Tarot card from the 78-card deck."""

    id: int
    names: Dict[str, str]  # {"en": "The Fool", "ru": "Дурак", "uk": "Дурень"}
    meanings: Dict[str, Dict[str, str]]  # {"en": {"upright": "..."}, ...}
    keywords: Dict[str, List[str]]  # {"en": ["beginnings", ...], ...}
    suit: Optional[str]  # "wands"|"cups"|"swords"|"pentacles"|None for Major Arcana
    number: Optional[int]  # Card number or None
    arcana: str  # "major" or "minor"

    def get_name(self, language: str = "en") -> str:
        """Get card name in specified language."""
        return self.names.get(language, self.names["en"])

    def get_meaning(self, language: str = "en", position: str = "upright") -> str:
        """Get card meaning in specified language and position."""
        lang_meanings = self.meanings.get(language, self.meanings["en"])
        return lang_meanings.get(position, "")

    def get_keywords(self, language: str = "en") -> List[str]:
        """Get card keywords in specified language."""
        return self.keywords.get(language, self.keywords["en"])

    def validate(self) -> bool:
        """Validate card data structure."""
        # ID must be 0-77
        if not 0 <= self.id <= 77:
            return False

        # Must have names in all languages
        required_langs = {"en", "ru", "uk"}
        if not required_langs.issubset(self.names.keys()):
            return False

        # Arcana must be major or minor
        if self.arcana not in ["major", "minor"]:
            return False

        # Major Arcana validation
        if self.arcana == "major":
            if self.suit is not None:
                return False
            if self.number is None or not 0 <= self.number <= 21:
                return False

        # Minor Arcana validation
        if self.arcana == "minor":
            if self.suit not in ["wands", "cups", "swords", "pentacles"]:
                return False
            if self.number is None or not 1 <= self.number <= 14:
                return False

        return True

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        """Create Card instance from dictionary."""
        return cls(
            id=data["id"],
            names=data["names"],
            meanings=data["meanings"],
            keywords=data["keywords"],
            suit=data.get("suit"),
            number=data.get("number"),
            arcana=data["arcana"],
        )
