"""User Session entity model for conversation state management."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class SessionState(Enum):
    """Finite State Machine states for user conversation."""

    IDLE = "idle"
    AWAITING_PAYMENT = "awaiting_payment"
    AWAITING_QUESTION = "awaiting_question"
    AWAITING_CUSTOM_QUESTION = "awaiting_custom_question"
    AWAITING_CARDS = "awaiting_cards"
    PROCESSING = "processing"


@dataclass
class Reading:
    """Represents a completed Tarot reading."""

    type: str  # "automated" or "custom"
    cards: list[int]  # List of card IDs
    question: str  # User's question (empty for custom readings)
    card_positions: list[str]  # Position meanings ["Past", "Present", "Future"]
    interpretation: str  # AI-generated interpretation
    language: str  # Language of interpretation ("en"|"ru"|"uk")
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert Reading to dictionary for storage."""
        return {
            "type": self.type,
            "cards": self.cards,
            "question": self.question,
            "card_positions": self.card_positions,
            "interpretation": self.interpretation,
            "language": self.language,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reading":
        """Create Reading from dictionary."""
        return cls(
            type=data["type"],
            cards=data["cards"],
            question=data["question"],
            card_positions=data["card_positions"],
            interpretation=data["interpretation"],
            language=data["language"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class UserSession:
    """Represents an active conversation session with a Telegram user."""

    user_id: int
    language: str = "en"  # Detected language code
    state: SessionState = SessionState.IDLE
    last_reading: Optional[Reading] = None
    reading_count: int = 0  # Total number of completed readings
    reading_history: list[Reading] = field(default_factory=list)  # All past readings
    conversation_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update(self) -> None:
        """Update the session's last modified timestamp."""
        self.updated_at = datetime.now()

    def set_state(self, new_state: SessionState) -> None:
        """Change the conversation state."""
        self.state = new_state
        self.update()

    def set_language(self, language: str) -> None:
        """Set the detected language."""
        if language in ["en", "ru", "uk"]:
            self.language = language
            self.update()

    def save_reading(self, reading: Reading) -> None:
        """Save a completed reading to the session."""
        self.last_reading = reading
        self.reading_history.append(reading)
        self.reading_count += 1
        self.update()

    def get_reading_history(self, limit: int = 10) -> list[Reading]:
        """Get recent reading history (newest first)."""
        return list(reversed(self.reading_history[-limit:]))

    def is_first_reading(self) -> bool:
        """Check if this is the user's first reading."""
        return self.reading_count == 0

    def to_dict(self) -> dict:
        """Convert UserSession to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "language": self.language,
            "state": self.state.value,
            "last_reading": self.last_reading.to_dict() if self.last_reading else None,
            "reading_count": self.reading_count,
            "reading_history": [r.to_dict() for r in self.reading_history],
            "conversation_context": self.conversation_context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserSession":
        """Create UserSession from dictionary."""
        # Parse reading history
        reading_history = []
        for reading_data in data.get("reading_history", []):
            reading_history.append(Reading.from_dict(reading_data))

        return cls(
            user_id=data["user_id"],
            language=data["language"],
            state=SessionState(data["state"]),
            last_reading=(
                Reading.from_dict(data["last_reading"]) if data["last_reading"] else None
            ),
            reading_count=data.get("reading_count", 0),
            reading_history=reading_history,
            conversation_context=data.get("conversation_context", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
