"""AI Service for generating Tarot card interpretations."""
import logging
from typing import List, Optional
from src.config import config
from src.models.card import Card

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered Tarot interpretations using Anthropic Claude."""

    def __init__(self):
        """Initialize AI service with configured API."""
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate AI client based on configuration."""
        if config.anthropic_api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=config.anthropic_api_key)
                self.service_type = "anthropic"
                logger.info("Initialized Anthropic AI service")
            except ImportError:
                logger.error("anthropic package not installed")
        elif config.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=config.openai_api_key)
                self.service_type = "openai"
                logger.info("Initialized OpenAI AI service")
            except ImportError:
                logger.error("openai package not installed")
        else:
            logger.warning("No AI service configured")

    async def generate_reading_interpretation(
        self,
        cards: List[Card],
        question: str,
        language: str = "en",
        positions: List[str] = None,
    ) -> Optional[str]:
        """
        Generate interpretation for automated Tarot reading.

        Args:
            cards: List of drawn cards
            question: User's question
            language: Target language for interpretation
            positions: Card position meanings (e.g., ["Past", "Present", "Future"])

        Returns:
            AI-generated interpretation or None if failed
        """
        if not self.client:
            logger.error("No AI client available")
            return None

        if not positions:
            positions = ["Past", "Present", "Future"]

        # Build system prompt
        system_prompt = self._get_system_prompt(language)

        # Build user prompt
        user_prompt = self._build_reading_prompt(cards, question, language, positions)

        try:
            if self.service_type == "anthropic":
                return await self._call_anthropic(system_prompt, user_prompt)
            elif self.service_type == "openai":
                return await self._call_openai(system_prompt, user_prompt)
        except Exception as e:
            logger.exception(f"AI service error: {e}")
            return None

    async def generate_custom_interpretation(
        self, cards: List[Card], question: str = "", language: str = "en"
    ) -> Optional[str]:
        """
        Generate interpretation for user's custom card combination.

        Args:
            cards: List of user-submitted cards
            question: User's question (optional but recommended)
            language: Target language for interpretation

        Returns:
            AI-generated interpretation or None if failed
        """
        if not self.client:
            logger.error("No AI client available")
            return None

        system_prompt = self._get_system_prompt(language)
        user_prompt = self._build_custom_prompt(cards, question, language)

        try:
            if self.service_type == "anthropic":
                return await self._call_anthropic(system_prompt, user_prompt)
            elif self.service_type == "openai":
                return await self._call_openai(system_prompt, user_prompt)
        except Exception as e:
            logger.exception(f"AI service error: {e}")
            return None

    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt for AI based on language."""
        prompts = {
            "en": (
                "You are an expert Tarot card reader with deep knowledge of traditional Tarot meanings "
                "and symbolism. Provide insightful, supportive, and culturally appropriate interpretations. "
                "Connect the cards meaningfully to the user's question. Be empowering and avoid making "
                "definitive predictions. Keep interpretations under 3500 characters. "
                "Format: clear paragraphs, one per card, then overall interpretation."
            ),
            "ru": (
                "Вы эксперт по картам Таро с глубокими знаниями традиционных значений и символики Таро. "
                "Предоставляйте проницательные, поддерживающие и культурно уместные толкования. "
                "Значимо связывайте карты с вопросом пользователя. Будьте вдохновляющими и избегайте "
                "категоричных предсказаний. Держите толкования в пределах 3500 символов. "
                "Формат: понятные абзацы, один на карту, затем общее толкование."
            ),
            "uk": (
                "Ви експерт з карт Таро з глибоким знанням традиційних значень та символіки Таро. "
                "Надавайте проникливі, підтримуючі та культурно доречні тлумачення. "
                "Значуще пов'язуйте карти з питанням користувача. Будьте надихаючими та уникайте "
                "категоричних передбачень. Тримайте тлумачення в межах 3500 символів. "
                "Формат: зрозумілі абзаци, один на карту, потім загальне тлумачення."
            ),
        }
        return prompts.get(language, prompts["en"])

    def _build_reading_prompt(
        self, cards: List[Card], question: str, language: str, positions: List[str]
    ) -> str:
        """Build prompt for automated reading."""
        card_info = []
        for i, card in enumerate(cards):
            position = positions[i] if i < len(positions) else f"Card {i+1}"
            card_name = card.get_name(language)
            card_meaning = card.get_meaning(language, "upright")
            card_keywords = ", ".join(card.get_keywords(language))

            card_info.append(
                f"{position}: {card_name}\n"
                f"Traditional meaning: {card_meaning}\n"
                f"Keywords: {card_keywords}"
            )

        card_details = "\n\n".join(card_info)

        return f"""Question: {question}

Cards drawn:
{card_details}

Please provide a comprehensive Tarot reading interpretation in {language} that:
1. Explains each card in the context of its position and the question
2. Shows how the cards relate to each other
3. Offers guidance and insights addressing the user's question
4. Maintains a supportive and empowering tone"""

    def _build_custom_prompt(self, cards: List[Card], question: str, language: str) -> str:
        """Build prompt for custom card interpretation."""
        card_info = []
        for i, card in enumerate(cards, 1):
            card_name = card.get_name(language)
            card_meaning = card.get_meaning(language, "upright")
            card_keywords = ", ".join(card.get_keywords(language))

            card_info.append(
                f"Card {i}: {card_name}\n"
                f"Traditional meaning: {card_meaning}\n"
                f"Keywords: {card_keywords}"
            )

        card_details = "\n\n".join(card_info)

        # Include question if provided
        question_part = f"User's Question: {question}\n\n" if question else ""

        return f"""{question_part}User's card combination:
{card_details}

Please provide an interpretation in {language} that:
1. Explains what this specific combination of cards suggests in relation to {"the question" if question else "their situation"}
2. Shows how these cards interact and influence each other
3. Offers insights about the themes and energies present
4. Maintains a supportive and empowering tone"""

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic Claude API asynchronously."""
        import asyncio

        # Run synchronous API call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
        )
        return response.content[0].text

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API asynchronously."""
        import asyncio

        # Run synchronous API call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model="gpt-4",
                max_tokens=2000,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        )
        return response.choices[0].message.content


# Global AI service instance
ai_service = AIService()
