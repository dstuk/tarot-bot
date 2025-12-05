"""Tarot card spread logic for different reading types."""
from typing import List, Tuple
from src.models.card import Card
from src.tarot.deck import TarotDeck


class CardSpread:
    """Base class for Tarot card spreads."""

    def __init__(self, deck: TarotDeck):
        """Initialize spread with a Tarot deck."""
        self.deck = deck

    def draw_cards(self) -> Tuple[List[Card], List[str]]:
        """
        Draw cards for this spread.

        Returns:
            Tuple of (cards, positions) where positions are position names/meanings
        """
        raise NotImplementedError


class ThreeCardSpread(CardSpread):
    """Three-card Past-Present-Future spread."""

    def __init__(self, deck: TarotDeck, language: str = "en"):
        """
        Initialize three-card spread.

        Args:
            deck: Tarot deck to draw from
            language: Language for position names
        """
        super().__init__(deck)
        self.language = language
        self.position_names = self._get_position_names()

    def _get_position_names(self) -> List[str]:
        """Get position names in the selected language."""
        positions = {
            "en": ["Past", "Present", "Future"],
            "ru": ["Прошлое", "Настоящее", "Будущее"],
            "uk": ["Минуле", "Теперішнє", "Майбутнє"],
        }
        return positions.get(self.language, positions["en"])

    def draw_cards(self) -> Tuple[List[Card], List[str]]:
        """
        Draw three cards for Past-Present-Future reading.

        Returns:
            Tuple of (cards, positions)
        """
        cards = self.deck.draw_random_cards(count=3)
        return cards, self.position_names

    def get_description(self) -> str:
        """Get description of this spread in the selected language."""
        descriptions = {
            "en": "Three-card spread representing Past, Present, and Future",
            "ru": "Расклад из трёх карт: Прошлое, Настоящее, Будущее",
            "uk": "Розклад з трьох карт: Минуле, Теперішнє, Майбутнє",
        }
        return descriptions.get(self.language, descriptions["en"])


class SingleCardSpread(CardSpread):
    """Single card spread for quick guidance."""

    def __init__(self, deck: TarotDeck, language: str = "en"):
        """Initialize single-card spread."""
        super().__init__(deck)
        self.language = language

    def draw_cards(self) -> Tuple[List[Card], List[str]]:
        """Draw single card for guidance."""
        cards = self.deck.draw_random_cards(count=1)
        positions = {
            "en": ["Guidance"],
            "ru": ["Совет"],
            "uk": ["Порада"],
        }
        return cards, positions.get(self.language, positions["en"])


def create_spread(spread_type: str, deck: TarotDeck, language: str = "en") -> CardSpread:
    """
    Factory function to create appropriate spread.

    Args:
        spread_type: Type of spread ("three_card", "single", etc.)
        deck: Tarot deck to use
        language: Language for position names

    Returns:
        CardSpread instance
    """
    spreads = {
        "three_card": ThreeCardSpread,
        "single": SingleCardSpread,
    }

    spread_class = spreads.get(spread_type, ThreeCardSpread)
    return spread_class(deck, language)
