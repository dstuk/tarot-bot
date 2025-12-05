# Data Model: Telegram Tarot Reading Chatbot

**Feature**: 001-telegram-tarot-bot
**Date**: 2025-12-04
**Purpose**: Define data entities, relationships, and validation rules

## Core Entities

### 1. TarotCard

Represents a single card from the 78-card Tarot deck.

**Attributes**:
- `id` (int): Unique card identifier (0-77)
- `names` (dict): Multilingual card names
  - `en` (str): English name
  - `ru` (str): Russian name
  - `uk` (str): Ukrainian name
- `meanings` (dict): Multilingual interpretations
  - `[lang]` (dict): Per-language meanings
    - `upright` (str): Upright position meaning
    - `reversed` (str): Reversed position meaning (optional for MVP)
- `keywords` (dict): Multilingual keyword lists
  - `[lang]` (list[str]): Keywords for quick reference
- `suit` (str|null): Card suit ("wands"|"cups"|"swords"|"pentacles"|null for Major Arcana)
- `number` (int|null): Card number within suit (1-14) or Major Arcana (0-21)
- `arcana` (str): "major" or "minor"

**Validation Rules**:
- `id` must be unique (0-77)
- `names` must contain keys: "en", "ru", "uk"
- `arcana` must be one of: "major", "minor"
- If `arcana == "major"`, then `suit == null` and `number` in [0-21]
- If `arcana == "minor"`, then `suit` in ["wands", "cups", "swords", "pentacles"] and `number` in [1-14]

**Example**:
```python
{
    "id": 0,
    "names": {
        "en": "The Fool",
        "ru": "Дурак",
        "uk": "Дурень"
    },
    "meanings": {
        "en": {
            "upright": "New beginnings, innocence, spontaneity, free spirit"
        },
        "ru": {
            "upright": "Новые начинания, невинность, спонтанность, свободный дух"
        },
        "uk": {
            "upright": "Нові починання, невинність, спонтанність, вільний дух"
        }
    },
    "keywords": {
        "en": ["beginnings", "innocence", "journey"],
        "ru": ["начало", "невинность", "путешествие"],
        "uk": ["початок", "невинність", "подорож"]
    },
    "suit": null,
    "number": 0,
    "arcana": "major"
}
```

---

### 2. UserSession

Represents an active conversation session with a Telegram user.

**Attributes**:
- `user_id` (int): Telegram user ID (primary key)
- `language` (str): Detected language code ("en"|"ru"|"uk")
- `state` (str): Current conversation state (FSM state)
  - `"idle"`: No active interaction
  - `"awaiting_question"`: Waiting for user question
  - `"awaiting_cards"`: Waiting for card names input
  - `"processing"`: Bot is generating response
- `last_reading` (Reading|null): Most recent reading data
- `conversation_context` (dict): Additional context data
  - `card_input_attempts` (int): Number of card parsing attempts (for error handling)
  - `last_interaction` (datetime): Timestamp of last message
- `created_at` (datetime): Session creation timestamp
- `updated_at` (datetime): Last update timestamp

**Validation Rules**:
- `user_id` must be positive integer
- `language` must be one of: "en", "ru", "uk"
- `state` must be one of valid FSM states
- Session expires after 24 hours of inactivity (TTL)

**State Transitions**:
```
idle → awaiting_question (user clicks "Ask a question")
idle → awaiting_cards (user clicks "Explain my own tarot combination")
awaiting_question → processing (user sends question text)
awaiting_cards → processing (user sends card names)
processing → idle (interpretation sent)
```

**Storage**: Redis with TTL = 24 hours

**Example**:
```python
{
    "user_id": 123456789,
    "language": "en",
    "state": "idle",
    "last_reading": {
        "type": "automated",
        "cards": [0, 16, 32],  # card IDs
        "question": "Should I change my job?",
        "interpretation": "The Fool suggests...",
        "timestamp": "2025-12-04T10:30:00Z"
    },
    "conversation_context": {
        "card_input_attempts": 0,
        "last_interaction": "2025-12-04T10:30:00Z"
    },
    "created_at": "2025-12-04T10:00:00Z",
    "updated_at": "2025-12-04T10:30:00Z"
}
```

---

### 3. Reading

Represents a completed Tarot reading (automated or custom).

**Attributes**:
- `type` (str): Reading type ("automated"|"custom")
- `cards` (list[int]): List of card IDs (3 cards for 3-card spread)
- `question` (str): User's question (for automated readings)
- `card_positions` (list[str]): Position meanings (e.g., ["Past", "Present", "Future"])
- `interpretation` (str): AI-generated interpretation text
- `language` (str): Language of interpretation ("en"|"ru"|"uk")
- `timestamp` (datetime): When reading was performed

**Validation Rules**:
- `type` must be "automated" or "custom"
- `cards` must contain exactly 3 card IDs (for 3-card spread)
- Each card ID in `cards` must be valid (0-77)
- `interpretation` must not exceed 4000 chars (Telegram limit with buffer)
- If `type == "automated"`, `question` must not be empty
- `language` must be one of: "en", "ru", "uk"

**Relationships**:
- Embedded in `UserSession.last_reading`
- Not persisted independently in MVP (part of session only)

**Example** (Automated Reading):
```python
{
    "type": "automated",
    "cards": [0, 16, 15],  # The Fool, The Tower, The Devil
    "question": "Should I change my job?",
    "card_positions": ["Past", "Present", "Future"],
    "interpretation": "The Fool in the Past position indicates that your journey began with...",
    "language": "en",
    "timestamp": "2025-12-04T10:30:00Z"
}
```

**Example** (Custom Reading):
```python
{
    "type": "custom",
    "cards": [1, 10, 21],  # The Magician, Wheel of Fortune, The World
    "question": "",  # No question for custom readings
    "card_positions": ["Card 1", "Card 2", "Card 3"],
    "interpretation": "The Magician combined with the Wheel of Fortune suggests...",
    "language": "en",
    "timestamp": "2025-12-04T10:35:00Z"
}
```

---

### 4. CardCombination

Represents a user-submitted set of card names (for custom interpretation).

**Attributes**:
- `raw_input` (str): Original user input
- `parsed_cards` (list[int]): Resolved card IDs
- `unrecognized_cards` (list[str]): Card names that couldn't be parsed
- `language` (str): Detected language of input

**Validation Rules**:
- `raw_input` must not be empty
- `parsed_cards` must contain 1-10 card IDs (min 1, max 10 for sanity)
- Each card ID must be unique (no duplicates in single reading)
- If `len(unrecognized_cards) > 0`, prompt user for clarification

**Parsing Logic**:
1. Detect language from input text
2. Split input by common delimiters: comma, newline, "and", "и", "та"
3. Normalize each card name (lowercase, trim, remove "the"/"карта")
4. Match against card names in detected language (fuzzy match threshold: 0.8)
5. If no match, add to `unrecognized_cards`

**Example**:
```python
{
    "raw_input": "The Fool, Tower, three of cups",
    "parsed_cards": [0, 16, 32],
    "unrecognized_cards": [],
    "language": "en"
}
```

**Example** (Partial Match):
```python
{
    "raw_input": "Маг, Колесо удачи, Непонятная карта",
    "parsed_cards": [1, 10],
    "unrecognized_cards": ["Непонятная карта"],
    "language": "ru"
}
```

---

## Data Relationships

```
UserSession (1) ──> (0..1) Reading
    └─> last_reading

Reading (1) ──> (3) TarotCard
    └─> cards[] (list of card IDs)

CardCombination (1) ──> (1..10) TarotCard
    └─> parsed_cards[] (list of card IDs)
```

**Notes**:
- `TarotCard` is static reference data (loaded once at startup)
- `UserSession` is ephemeral (Redis, 24h TTL)
- `Reading` is embedded in session (not a separate entity in MVP)
- `CardCombination` is transient (parsed during request, not persisted)

---

## Validation Rules Summary

### TarotCard
- ✓ Unique `id` (0-77)
- ✓ All language keys present in `names` and `meanings`
- ✓ Valid `arcana` type
- ✓ Suit/number consistency

### UserSession
- ✓ Valid Telegram `user_id`
- ✓ Valid language code
- ✓ Valid FSM state
- ✓ TTL enforced (24 hours)

### Reading
- ✓ Exactly 3 cards for 3-card spread
- ✓ Valid card IDs
- ✓ Interpretation ≤ 4000 characters
- ✓ Question required for automated readings

### CardCombination
- ✓ 1-10 unique card IDs
- ✓ Non-empty raw input
- ✓ Fuzzy match threshold ≥ 0.8

---

## State Machine Diagram

```
┌──────────────────────────────────────────────────────────┐
│                      UserSession FSM                      │
└──────────────────────────────────────────────────────────┘

    /start
      │
      ▼
   ┌──────┐
   │ IDLE │◄────────────────────────────────┐
   └──────┘                                  │
      │                                      │
      │  [Click "Ask a question"]            │
      ▼                                      │
┌───────────────────┐                        │
│ AWAITING_QUESTION │                        │
└───────────────────┘                        │
      │                                      │
      │  [User sends question text]          │
      ▼                                      │
┌────────────┐                               │
│ PROCESSING │───────────────────────────────┤
└────────────┘                               │
      │                                      │
      │  [Interpretation sent]               │
      └──────────────────────────────────────┘

    IDLE
      │
      │  [Click "Explain my own tarot combination"]
      ▼
┌──────────────────┐
│ AWAITING_CARDS   │
└──────────────────┘
      │
      │  [User sends card names]
      ▼
┌────────────┐
│ PROCESSING │───────────────────────────────┐
└────────────┘                               │
      │                                      │
      │  [Interpretation sent]               │
      └──────────────────────────────────────┘
```

---

## Data Storage Strategy

### Static Reference Data (Tarot Cards)
- **Format**: JSON file (`data/tarot_cards.json`)
- **Loading**: Once at bot startup, kept in memory
- **Size**: ~500KB (78 cards × 3 languages × meanings/keywords)
- **Access Pattern**: Fast lookup by ID or name

### Session Data (User Sessions)
- **Format**: JSON serialized to Redis
- **Key Pattern**: `tarot:session:{user_id}`
- **TTL**: 24 hours
- **Size per session**: ~5KB
- **Estimated storage**: 100 concurrent users × 5KB = 500KB

### Temporary Data (Card Parsing)
- **Format**: In-memory Python objects
- **Lifecycle**: Created during request, discarded after response
- **Not persisted**

**Total Storage Footprint**: < 1MB for MVP (negligible)

---

## Future Enhancements (Out of MVP Scope)

### Persistent Reading History
- Store readings in PostgreSQL or SQLite
- Allow users to view past readings
- Analytics on popular cards/questions

### User Preferences
- Preferred spread type
- Notification settings
- Custom interpretation style

### Card Reversal Support
- Add `reversed` boolean to Reading.cards
- Interpret cards differently when reversed
- 50% chance of reversal when drawing

---

## Compliance Check

### Constitution Alignment

**Code Quality & Maintainability**:
- ✓ Clear entity separation (SRP)
- ✓ Validation rules explicit and testable
- ✓ Data models are simple and focused

**Testing Standards**:
- ✓ Validation rules are unit-testable
- ✓ State transitions are integration-testable
- ✓ Each entity has clear boundaries for mocking

**Performance Requirements**:
- ✓ In-memory card data = O(1) lookups
- ✓ Redis session storage = sub-millisecond access
- ✓ Minimal serialization overhead (JSON)

**Data Model Complete. Ready for contract generation.**
