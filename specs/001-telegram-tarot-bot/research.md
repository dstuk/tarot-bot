# Research: Telegram Tarot Reading Chatbot

**Feature**: 001-telegram-tarot-bot
**Date**: 2025-12-04
**Purpose**: Resolve technical unknowns and establish implementation decisions

## Research Items

### 1. AI Model Selection (Fine-Tuning Capability Required)

**Context**: User specified that fine-tuning capability is critical. Need to select an AI model/service that supports fine-tuning for Tarot interpretation personalization.

**Decision**: Use **Anthropic Claude API with prompt engineering** for MVP, with migration path to **OpenAI GPT-4 fine-tuning** or **open-source LLaMA 2 fine-tuning** for production.

**Rationale**:
- **Anthropic Claude API**:
  - Excellent at understanding context and generating nuanced interpretations
  - No fine-tuning in traditional sense, but supports sophisticated prompt engineering
  - Fast response times (<2s typical)
  - Good multilingual support (English, Russian, Ukrainian)
  - Cost-effective for MVP with pay-per-use pricing

- **OpenAI GPT-4 Fine-Tuning** (production migration option):
  - Official fine-tuning API available
  - Can be trained on Tarot-specific interpretation corpus
  - Maintains strong multilingual capabilities
  - Higher cost but production-ready

- **LLaMA 2 70B with LoRA Fine-Tuning** (self-hosted option):
  - Full control over fine-tuning process
  - Can be hosted on own infrastructure (cost control)
  - Requires more DevOps effort
  - Best for long-term customization

**Implementation Plan**:
1. **MVP**: Use Anthropic Claude API with carefully crafted system prompts containing Tarot interpretation guidelines
2. **Phase 2**: Collect user interactions and feedback to build fine-tuning dataset
3. **Phase 3**: Fine-tune GPT-4 or LLaMA 2 on collected Tarot interpretation data

**Alternatives Considered**:
- ~~HuggingFace Transformers (smaller models)~~: Too limited for nuanced Tarot interpretation quality
- ~~Google PaLM API~~: Less flexible prompt engineering, weaker multilingual support for Russian/Ukrainian
- ~~Azure OpenAI~~: Similar to OpenAI but adds deployment complexity

**Dependencies**:
- `anthropic` Python library (MVP)
- Future: `openai` library (fine-tuning) or `transformers` + `peft` (LLaMA fine-tuning)

---

### 2. Session Storage Solution

**Context**: Bot needs to maintain conversation state (language preference, reading history, conversation context) across interactions.

**Decision**: Use **Redis for session storage** with in-memory fallback for local development.

**Rationale**:
- **Redis**:
  - Fast key-value storage perfect for session data
  - Built-in TTL (time-to-live) for automatic session cleanup
  - Supports 100+ concurrent users easily
  - Industry standard for session management
  - Simple Python integration via `redis-py`
  - Can scale horizontally if needed

- **In-Memory Fallback** (development):
  - Python `dict` for local development
  - Zero external dependencies for quick setup
  - Automatically switches based on environment variable

**Data Structure**:
```python
session_key = f"tarot:session:{telegram_user_id}"
session_data = {
    "language": "en",  # detected language
    "last_reading": {
        "cards": ["The Fool", "The Tower", "Three of Cups"],
        "question": "Should I change my job?",
        "interpretation": "...",
        "timestamp": "2025-12-04T10:30:00Z"
    },
    "conversation_state": "awaiting_question",  # FSM state
    "reading_count": 3
}
```

**Session TTL**: 24 hours (conversation expires after 1 day of inactivity)

**Alternatives Considered**:
- ~~SQLite~~: Overkill for ephemeral session data, slower than Redis
- ~~PostgreSQL~~: Too heavy for session-only storage, adds deployment complexity
- ~~In-memory only~~: Loses session data on bot restart, not production-ready

**Dependencies**:
- `redis` Python library
- Redis server (Docker container for development, managed service for production)

---

### 3. Card Spread Configuration

**Context**: Spec assumption mentions 3-card spread, but user input didn't explicitly clarify. Need to resolve FR-004 clarification.

**Decision**: **3-card spread (Past-Present-Future)** as default and only spread for MVP.

**Rationale**:
- Balances depth vs. complexity (not too simple, not too complex)
- Traditional and widely recognized spread pattern
- Manageable interpretation length (fits within Telegram's 4096 char limit)
- AI can generate coherent narrative across 3 cards
- User expectation alignment (spec assumption validated)

**Spread Structure**:
```
Card 1 (Past): Influences and events that led to current situation
Card 2 (Present): Current state and immediate circumstances
Card 3 (Future): Potential outcome and guidance moving forward
```

**Future Expansion** (P3 - out of MVP scope):
- Single card reading (quick guidance)
- 5-card spread (more detailed)
- Celtic Cross (10 cards - advanced users)

**Alternatives Considered**:
- ~~Single card~~: Too simplistic, may not feel valuable enough
- ~~Celtic Cross (10 cards)~~: Too complex for MVP, interpretation too long
- ~~User choice~~: Adds UI complexity, delays MVP

---

### 4. Language Detection Strategy

**Context**: Bot must detect English, Russian, and Ukrainian automatically from user input.

**Decision**: Use **langdetect** library with custom Russian/Ukrainian disambiguation logic.

**Rationale**:
- **langdetect** is lightweight and accurate for major languages
- Russian and Ukrainian detection requires special handling (both use Cyrillic, share vocabulary)
- Fallback strategy: default to English if detection confidence <80%

**Detection Algorithm**:
```python
1. Use langdetect to identify language
2. If detected as Russian:
   - Check for Ukrainian-specific words (і, є, ї, український, тощо)
   - Check character frequency (і vs и ratio)
   - If Ukrainian markers found, switch to Ukrainian
3. If confidence <80%, default to English
4. Cache detected language in user session
```

**Ukrainian-Specific Markers**:
- Unique characters: і, є, ї, ґ
- Common words: чи (vs Russian или), який (vs Russian который)
- Verb endings: -ться (Ukrainian) vs -тся (Russian)

**Alternatives Considered**:
- ~~fasttext language-identification~~: Too heavy (large model file), overkill for 3 languages
- ~~Manual regex rules~~: Too brittle, poor accuracy
- ~~User language selection~~: Adds friction, defeats "automatic detection" requirement

**Dependencies**:
- `langdetect` Python library

---

### 5. Tarot Card Data Structure and Multilingual Support

**Context**: Need to store 78 Tarot cards with names and meanings in 3 languages.

**Decision**: Use **JSON data file** (`data/tarot_cards.json`) with structured multilingual data.

**Data Structure**:
```json
{
  "major_arcana": [
    {
      "id": 0,
      "names": {
        "en": "The Fool",
        "ru": "Дурак",
        "uk": "Дурень"
      },
      "meanings": {
        "en": {
          "upright": "New beginnings, innocence, spontaneity, free spirit",
          "reversed": "Recklessness, taken advantage of, inconsideration"
        },
        "ru": {
          "upright": "Новые начинания, невинность, спонтанность, свободный дух",
          "reversed": "Безрассудство, наивность, необдуманность"
        },
        "uk": {
          "upright": "Нові починання, невинність, спонтанність, вільний дух",
          "reversed": "Безрозсудність, наївність, необачність"
        }
      },
      "keywords": {
        "en": ["beginnings", "innocence", "journey", "potential"],
        "ru": ["начало", "невинность", "путешествие", "потенциал"],
        "uk": ["початок", "невинність", "подорож", "потенціал"]
      },
      "suit": null,
      "number": 0,
      "arcana": "major"
    }
  ],
  "minor_arcana": {
    "wands": [...],
    "cups": [...],
    "swords": [...],
    "pentacles": [...]
  }
}
```

**Rationale**:
- JSON is human-readable and easy to edit/extend
- No database overhead for static reference data
- Fast loading at bot startup (single file read)
- Version control friendly (can track card data changes)

**Card Lookup**:
- Load JSON into memory at bot startup (one-time cost)
- Index by card name in all languages for fast parser lookups
- O(1) access by card ID for spread drawing

**Alternatives Considered**:
- ~~Database storage~~: Overkill for static reference data
- ~~Hardcoded Python dicts~~: Not maintainable, hard to translate/update
- ~~YAML format~~: Unnecessary complexity vs JSON

---

### 6. Bot Command Architecture

**Context**: Telegram bot needs clear command structure for user interactions.

**Decision**: Use **button-driven interface** with minimal text commands.

**Command Structure**:
- `/start` - Initialize bot, show welcome + buttons
- `/help` - Show usage instructions
- Button: "Ask a question" → triggers question input mode
- Button: "Explain my own tarot combination" → triggers card input mode
- Text input: Handled based on conversation state (FSM)

**State Machine**:
```
IDLE → /start → WELCOME (show buttons)
WELCOME → "Ask a question" → AWAITING_QUESTION
AWAITING_QUESTION → user types question → PROCESSING → READING_COMPLETE → WELCOME
WELCOME → "Explain combination" → AWAITING_CARDS
AWAITING_CARDS → user types cards → PROCESSING → INTERPRETATION_COMPLETE → WELCOME
```

**Rationale**:
- Buttons provide clear affordances (no "how do I use this?" confusion)
- FSM prevents state confusion and errors
- Aligns with spec requirement for two primary buttons

**Dependencies**:
- `python-telegram-bot` library with `InlineKeyboardButton` and `InlineKeyboardMarkup`

---

### 7. Best Practices for Python Telegram Bots

**Research**: Reviewed `python-telegram-bot` documentation and production bot patterns.

**Key Findings**:
1. **Use `async`/`await`**: Modern python-telegram-bot (v20+) is async-first
2. **Handler organization**: Separate handlers by command type (command, message, callback query)
3. **Error handling**: Global error handler for uncaught exceptions
4. **Graceful shutdown**: Handle SIGTERM/SIGINT for clean bot shutdown
5. **Rate limiting**: Use middleware to prevent spam (per-user rate limits)
6. **Logging**: Structured logging with context (user_id, command, timestamp)

**Performance Patterns**:
- Use `asyncio.gather()` for parallel AI calls (if multiple cards need individual lookups)
- Connection pooling for Redis
- Lazy-load heavy resources (AI client initialization on first use)

**Security Patterns**:
- Validate Telegram webhook signatures (if using webhooks instead of polling)
- Sanitize user input before passing to AI (prevent prompt injection)
- Environment variable for bot token (never hardcode)
- Rate limiting: 5 requests per user per minute

---

### 8. Testing Strategy for Async Telegram Bots

**Research**: Pytest patterns for async code and Telegram bot testing.

**Decision**: Use `pytest-asyncio` + mocking for Telegram API calls.

**Test Approach**:
1. **Unit Tests**: Mock Telegram objects, test handler logic in isolation
2. **Integration Tests**: Use `pytest-telegram-bot` fixtures or custom test client
3. **Contract Tests**: Verify bot command schemas and response formats

**Example Test Structure**:
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_start_command_shows_buttons():
    update = create_mock_update(text="/start")
    context = create_mock_context()

    await start_handler(update, context)

    assert context.bot.send_message.called
    assert "Ask a question" in sent_message_buttons
```

**Dependencies**:
- `pytest`
- `pytest-asyncio`
- `pytest-mock`

---

## Summary of Decisions

| Research Item | Decision | Status |
|---------------|----------|--------|
| AI Model | Anthropic Claude API (MVP) → OpenAI fine-tuning (Prod) | ✅ Resolved |
| Session Storage | Redis (prod) + in-memory (dev) | ✅ Resolved |
| Card Spread | 3-card Past-Present-Future spread | ✅ Resolved |
| Language Detection | langdetect + Ukrainian disambiguation | ✅ Resolved |
| Card Data | JSON file with multilingual structure | ✅ Resolved |
| Bot Architecture | Button-driven FSM with async handlers | ✅ Resolved |
| Testing | pytest-asyncio + mocking | ✅ Resolved |

**All NEEDS CLARIFICATION items resolved. Ready for Phase 1: Design & Contracts.**
