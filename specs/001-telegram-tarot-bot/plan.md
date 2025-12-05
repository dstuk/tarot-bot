# Implementation Plan: Telegram Tarot Reading Chatbot

**Branch**: `001-telegram-tarot-bot` | **Date**: 2025-12-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-telegram-tarot-bot/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Telegram bot that provides Tarot card readings in three languages (English, Russian, Ukrainian). The bot uses AI to generate personalized interpretations based on traditional Tarot meanings. Users can either ask a question to receive an automated reading or input their own card combination for interpretation. The system must support language detection, maintain conversation state, and deliver responses within 5 seconds to maintain conversational flow.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: python-telegram-bot (Telegram Bot API), anthropic (Claude API - MVP) or openai (GPT-4 fine-tuning - production), langdetect (language detection)
**Storage**: Redis (production session storage) with in-memory fallback (development)
**Testing**: pytest (unit/integration tests), pytest-asyncio (async test support), pytest-mock (mocking)
**Target Platform**: Linux server (cloud deployment: AWS/GCP/Azure) or local development environment
**Project Type**: single (backend-only bot service)
**Performance Goals**: <5 second response time per interaction, support 100+ concurrent user sessions
**Constraints**: <5s response time (per spec SC-005), must handle 100 concurrent users (per spec SC-006), Telegram message size limit 4096 characters, <4s AI response time target
**Scale/Scope**: 100+ concurrent users initially, 3 languages, 78-card Tarot deck, 3-card Past-Present-Future spread (resolved from research)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality & Maintainability
- [x] Functions designed with single responsibility principle
- [x] Cyclomatic complexity target <10 per function
- [x] Clear separation: telegram handlers, tarot logic, AI integration, language detection
- [x] No anticipated code duplication (card drawing, interpretation formatting will be abstracted)

### Testing Standards (NON-NEGOTIABLE)
- [x] TDD approach confirmed: tests before implementation
- [x] Target: ≥80% unit test coverage for business logic
- [x] Integration tests planned for Telegram API and AI model interactions
- [x] Contract tests planned for bot command handlers
- [x] Test execution time goal: unit suite <5 min

### User Experience Consistency
- [x] Consistent button interface (two primary actions)
- [x] Error messages will be user-friendly and localized
- [x] Language detection automatic and transparent
- [x] Response time <5s maintained across all interactions
- [x] Localization via i18n-ready design (not machine translation)

### Performance Requirements
- [x] <5s response time target (spec SC-005)
- [x] 100 concurrent user target (spec SC-006)
- [x] Async architecture planned for non-blocking operations
- [x] AI API calls will be monitored and optimized
- [x] Load testing strategy: Use locust or pytest-benchmark to simulate 200 concurrent users

### Documentation & Knowledge Sharing
- [x] OpenAPI/internal documentation for bot commands planned
- [x] README with setup, usage, Telegram bot token configuration
- [x] Tarot card data structure and interpretation logic will be documented
- [x] AI model selection and fine-tuning process will be documented in research.md

### Status: ✅ PASS (all requirements met after Phase 1 design)

## Project Structure

### Documentation (this feature)

```text
specs/001-telegram-tarot-bot/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── bot-commands.md  # Telegram bot command contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── bot/
│   ├── handlers.py          # Telegram message/command handlers
│   ├── keyboards.py         # Button/keyboard definitions
│   └── middleware.py        # Language detection, rate limiting
├── tarot/
│   ├── deck.py              # Tarot deck data (78 cards, multilingual)
│   ├── spreads.py           # Card spread logic (3-card, etc.)
│   └── interpreter.py       # AI integration for card interpretation
├── i18n/
│   ├── translations.py      # Translation utilities
│   └── locales/             # Language files (en, ru, uk)
│       ├── en.json
│       ├── ru.json
│       └── uk.json
├── services/
│   ├── ai_service.py        # AI model integration (OpenAI/Anthropic/etc.)
│   ├── session_service.py   # User session management
│   └── card_parser.py       # Parse user-submitted card names
├── models/
│   ├── user_session.py      # User session data model
│   ├── reading.py           # Tarot reading data model
│   └── card.py              # Card entity model
├── config.py                # Configuration (API keys, bot token)
└── main.py                  # Bot entry point

tests/
├── contract/
│   └── test_bot_commands.py     # Contract tests for bot commands
├── integration/
│   ├── test_telegram_flow.py    # End-to-end user flow tests
│   └── test_ai_integration.py   # AI service integration tests
└── unit/
    ├── test_deck.py             # Tarot deck logic tests
    ├── test_spreads.py          # Card spread tests
    ├── test_interpreter.py      # Interpretation logic tests
    ├── test_card_parser.py      # Card name parsing tests
    └── test_language_detection.py  # Language detection tests

data/
└── tarot_cards.json         # Tarot card data (names, meanings in 3 languages)

requirements.txt             # Python dependencies
.env.example                 # Environment variable template
README.md                    # Setup and usage documentation
```

**Structure Decision**: Single project (backend-only) structure selected. This is a Python-based Telegram bot with no frontend UI. The structure separates concerns into logical modules: bot interface layer, tarot domain logic, i18n support, AI service integration, and data models. Tests are organized by type (contract/integration/unit) to support TDD and constitution compliance.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. The design is straightforward with clear separation of concerns and no unnecessary abstraction layers.
