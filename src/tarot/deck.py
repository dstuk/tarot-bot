"""Tarot Deck management and card operations."""
import json
import random
from pathlib import Path
from typing import List, Optional, Dict
from src.models.card import Card


class TarotDeck:
    """Manages the 78-card Tarot deck with multilingual support."""

    def __init__(self, data_file: str = "data/tarot_cards.json"):
        """Initialize the Tarot deck by loading card data from JSON."""
        self.data_file = Path(data_file)
        self.cards: List[Card] = []
        self.cards_by_id: Dict[int, Card] = {}
        self.cards_by_name: Dict[str, Dict[str, Card]] = {
            "en": {},
            "ru": {},
            "uk": {},
        }
        self._load_cards()

    def _load_cards(self) -> None:
        """Load all cards from the JSON data file."""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Tarot card data file not found: {self.data_file}")

        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load Major Arcana
        for card_data in data.get("major_arcana", []):
            card = Card.from_dict(card_data)
            if card.validate():
                self._add_card(card)

        # Load Minor Arcana
        minor_arcana = data.get("minor_arcana", {})
        for suit in ["wands", "cups", "swords", "pentacles"]:
            for card_data in minor_arcana.get(suit, []):
                card = Card.from_dict(card_data)
                if card.validate():
                    self._add_card(card)

    def _add_card(self, card: Card) -> None:
        """Add a card to all internal indexes."""
        self.cards.append(card)
        self.cards_by_id[card.id] = card

        # Index by name in all languages
        for lang in ["en", "ru", "uk"]:
            name = card.get_name(lang).lower()
            self.cards_by_name[lang][name] = card

    def get_card_by_id(self, card_id: int) -> Optional[Card]:
        """Get a card by its ID."""
        return self.cards_by_id.get(card_id)

    def get_card_by_name(self, name: str, language: str = "en") -> Optional[Card]:
        """Get a card by its name in the specified language."""
        normalized_name = name.lower().strip()
        # Remove common prefixes
        normalized_name = normalized_name.replace("the ", "").replace("карта ", "")
        return self.cards_by_name.get(language, {}).get(normalized_name)

    def draw_random_cards(self, count: int = 3) -> List[Card]:
        """Draw random cards from the deck without replacement."""
        if count > len(self.cards):
            count = len(self.cards)
        return random.sample(self.cards, count)

    def find_similar_cards(self, name: str, language: str = "en", threshold: float = 0.8) -> List[Card]:
        """Find cards with names similar to the search term (fuzzy matching)."""
        # Simple fuzzy matching based on substring matching
        # For production, consider using libraries like rapidfuzz or fuzzywuzzy
        normalized_search = name.lower().strip()
        matches = []

        for card in self.cards:
            card_name = card.get_name(language).lower()
            # Check if search term is a substantial substring
            if normalized_search in card_name or card_name in normalized_search:
                matches.append(card)
            # Check keywords
            elif any(normalized_search in keyword.lower() for keyword in card.get_keywords(language)):
                matches.append(card)

        return matches

    def get_all_cards(self) -> List[Card]:
        """Get all cards in the deck."""
        return self.cards.copy()

    def get_major_arcana(self) -> List[Card]:
        """Get all Major Arcana cards."""
        return [card for card in self.cards if card.arcana == "major"]

    def get_minor_arcana(self) -> List[Card]:
        """Get all Minor Arcana cards."""
        return [card for card in self.cards if card.arcana == "minor"]

    def get_suit(self, suit: str) -> List[Card]:
        """Get all cards of a specific suit."""
        return [card for card in self.cards if card.suit == suit]

    def __len__(self) -> int:
        """Return the number of cards in the deck."""
        return len(self.cards)

    def __repr__(self) -> str:
        """String representation of the deck."""
        return f"TarotDeck({len(self.cards)} cards)"
