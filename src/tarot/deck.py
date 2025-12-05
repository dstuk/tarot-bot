"""Tarot Deck management and card operations."""
import json
import random
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from src.models.card import Card
from rapidfuzz import fuzz, process


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

    def _normalize_card_name(self, name: str, language: str = "en") -> str:
        """Normalize card name for better matching."""
        normalized = name.lower().strip()

        # Remove common prefixes/articles
        normalized = normalized.replace("the ", "").replace("карта ", "").replace("карт ", "")

        # Handle number variations for Slavic languages (Russian/Ukrainian)
        if language in ["ru", "uk"]:
            # Map common number words to standard forms
            number_variations = {
                # Russian/Ukrainian: short form → standard form
                "один": "туз",  # ace
                "одна": "туз",
                "два": "двойка",
                "две": "двойка",
                "три": "тройка",
                "четыре": "четверка",
                "пять": "пятерка",
                "шесть": "шестерка",
                "семь": "семерка",
                "восемь": "восьмерка",
                "девять": "девятка",
                "десять": "десятка",
            }

            for short_form, standard_form in number_variations.items():
                # Replace if it's at the beginning of the string
                if normalized.startswith(short_form + " "):
                    normalized = normalized.replace(short_form + " ", standard_form + " ", 1)
                    break

        return normalized

    def get_card_by_id(self, card_id: int) -> Optional[Card]:
        """Get a card by its ID."""
        return self.cards_by_id.get(card_id)

    def get_card_by_name(self, name: str, language: str = "en") -> Optional[Card]:
        """Get a card by its name in the specified language."""
        normalized_name = self._normalize_card_name(name, language)
        return self.cards_by_name.get(language, {}).get(normalized_name)

    def draw_random_cards(self, count: int = 3) -> List[Card]:
        """Draw random cards from the deck without replacement."""
        if count > len(self.cards):
            count = len(self.cards)
        return random.sample(self.cards, count)

    def find_similar_cards(self, name: str, language: str = "en", threshold: float = 70.0) -> List[Tuple[Card, float]]:
        """
        Find cards with names similar to the search term using fuzzy matching.

        Args:
            name: Card name to search for
            language: Language code (en/ru/uk)
            threshold: Minimum similarity score (0-100)

        Returns:
            List of tuples (card, score) sorted by similarity score (highest first)
        """
        normalized_search = self._normalize_card_name(name, language)

        # Create choices for fuzzy matching
        choices = {}
        for card in self.cards:
            card_name = card.get_name(language).lower()
            normalized_card_name = self._normalize_card_name(card_name, language)
            choices[normalized_card_name] = card

        # Use rapidfuzz to find best matches
        results = process.extract(
            normalized_search,
            choices.keys(),
            scorer=fuzz.WRatio,  # Weighted ratio works well for partial matches
            limit=5,  # Return top 5 matches
            score_cutoff=threshold  # Only return matches above threshold
        )

        # Convert results to (Card, score) tuples
        matches = [(choices[match[0]], match[1]) for match in results]

        return matches

    def get_card_by_name_fuzzy(self, name: str, language: str = "en", threshold: float = 80.0) -> Optional[Card]:
        """
        Get a card by name with fuzzy matching fallback.

        First tries exact match, then falls back to fuzzy matching.
        Returns the best match if similarity is above threshold.

        Args:
            name: Card name to search for
            language: Language code (en/ru/uk)
            threshold: Minimum similarity score for fuzzy match (0-100)

        Returns:
            Card object if found, None otherwise
        """
        # Try exact match first
        exact_match = self.get_card_by_name(name, language)
        if exact_match:
            return exact_match

        # Fall back to fuzzy matching
        fuzzy_matches = self.find_similar_cards(name, language, threshold)
        if fuzzy_matches:
            # Return the best match (highest score)
            return fuzzy_matches[0][0]

        return None

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
