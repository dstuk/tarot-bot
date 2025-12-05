# Tasks: Telegram Tarot Reading Chatbot

**Input**: Design documents from `specs/001-telegram-tarot-bot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Per constitution requirement, TDD approach with tests written BEFORE implementation. Tests ARE included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (src/, tests/, data/)
- [x] T002 Initialize Python project with pyproject.toml or setup.py
- [x] T003 Create requirements.txt with dependencies: python-telegram-bot, anthropic, langdetect, redis, pytest, pytest-asyncio, pytest-mock, black, flake8, mypy
- [x] T004 [P] Create .env.example template with TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, REDIS_URL, ENVIRONMENT
- [x] T005 [P] Create .gitignore for Python (.env, __pycache__/, venv/, *.pyc)
- [x] T006 [P] Create README.md with project overview and quickstart link
- [x] T007 [P] Set up pytest configuration in pytest.ini or pyproject.toml
- [x] T008 [P] Configure black formatter in pyproject.toml
- [x] T009 [P] Configure flake8 linter in .flake8 or pyproject.toml
- [x] T010 [P] Configure mypy type checker in mypy.ini or pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 Create Tarot card data file at data/tarot_cards.json with 78 cards (22 Major Arcana + 56 Minor Arcana) in 3 languages (en, ru, uk)
- [x] T012 [P] Create configuration module in src/config.py to load environment variables (bot token, API keys, Redis URL)
- [x] T013 [P] Create Card entity model in src/models/card.py with validation per data-model.md
- [x] T014 [P] Create UserSession entity model in src/models/user_session.py with FSM states per data-model.md
- [x] T015 [P] Create Reading entity model in src/models/user_session.py (automated and custom types) - Note: Embedded in user_session.py as Reading is not independently managed
- [x] T016 [P] Implement TarotDeck class in src/tarot/deck.py to load and manage 78 cards from JSON
- [x] T017 Implement SessionService in src/services/session_service.py with Redis + in-memory fallback for user session management
- [x] T018 [P] Implement language detection utility in src/bot/middleware.py using langdetect with Ukrainian/Russian disambiguation
- [x] T019 [P] Create translation utility module in src/i18n/translations.py for multilingual text loading
- [x] T020 [P] Create translation files: src/i18n/locales/en.json, src/i18n/locales/ru.json, src/i18n/locales/uk.json with bot UI text
- [x] T021 [P] Create inline keyboard builder in src/bot/keyboards.py for two main action buttons
- [x] T022 Implement bot entry point in src/main.py with async application setup, command/message handlers registration
- [x] T023 [P] Add logging configuration in src/main.py with structured logging (user_id, command, timestamp)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automated Tarot Reading (Priority: P1) 🎯 MVP

**Goal**: Users can ask a question and receive a 3-card Tarot reading with AI-powered interpretation in their language

**Independent Test**: Send a question in English/Russian/Ukrainian via Telegram bot, receive 3-card reading with interpretation

### Tests for User Story 1 (TDD - Write These FIRST) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T024 [P] [US1] Write contract test for /start command in tests/contract/test_bot_commands.py - verify welcome message and two buttons appear
- [ ] T025 [P] [US1] Write contract test for "Ask a question" button callback in tests/contract/test_bot_commands.py - verify state transitions to awaiting_question
- [ ] T026 [P] [US1] Write integration test for automated reading flow in tests/integration/test_telegram_flow.py - end-to-end question → 3 cards → interpretation
- [ ] T027 [P] [US1] Write unit test for 3-card spread logic in tests/unit/test_spreads.py - verify Past-Present-Future card drawing
- [ ] T028 [P] [US1] Write unit test for AI interpretation service in tests/unit/test_interpreter.py - verify prompt construction and response formatting
- [ ] T029 [P] [US1] Write unit test for language detection in tests/unit/test_language_detection.py - verify English/Russian/Ukrainian detection

### Implementation for User Story 1

- [x] T030 [US1] Implement /start command handler in src/bot/handlers.py to send welcome message with action buttons (per contracts/bot-commands.md)
- [x] T031 [US1] Implement /help command handler in src/bot/handlers.py to send usage instructions in user's language
- [x] T032 [US1] Implement "Ask a question" button callback handler in src/bot/handlers.py to transition state to awaiting_question
- [x] T033 [US1] Implement 3-card spread logic in src/tarot/spreads.py to draw 3 random cards (Past-Present-Future positions)
- [x] T034 [US1] Implement AI service in src/services/ai_service.py using Anthropic Claude API with prompt engineering for Tarot interpretation
- [x] T035 [US1] Implement TarotInterpreter in src/tarot/interpreter.py to format prompts, call AI service, and format responses (Note: Integrated directly into AI service and handlers)
- [x] T036 [US1] Implement question text message handler in src/bot/handlers.py to process user question when in awaiting_question state
- [x] T037 [US1] Integrate card drawing, AI interpretation, and response formatting in question handler
- [x] T038 [US1] Add multilingual response formatting in question handler (card names + interpretation in detected language)
- [x] T039 [US1] Add validation and error handling for empty/too-long questions per contracts/bot-commands.md (5-500 chars)
- [x] T040 [US1] Add error handling for AI service failures with user-friendly localized error messages
- [x] T041 [US1] Add logging for reading completions (user_id, question, cards drawn, language, timestamp)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Custom Tarot Combination Interpretation (Priority: P2)

**Goal**: Users can input their own card names and receive an interpretation of that specific combination

**Independent Test**: Submit card names like "The Fool, The Tower, Three of Cups" and receive coherent interpretation

### Tests for User Story 2 (TDD - Write These FIRST) ⚠️

- [ ] T042 [P] [US2] Write contract test for "Explain my own tarot combination" button callback in tests/contract/test_bot_commands.py
- [ ] T043 [P] [US2] Write integration test for custom card interpretation flow in tests/integration/test_telegram_flow.py
- [ ] T044 [P] [US2] Write unit test for card name parsing logic in tests/unit/test_card_parser.py - verify fuzzy matching, delimiter handling
- [ ] T045 [P] [US2] Write unit test for unrecognized card handling in tests/unit/test_card_parser.py

### Implementation for User Story 2

- [ ] T046 [P] [US2] Create CardCombination entity model in src/models/card_combination.py per data-model.md
- [ ] T047 [US2] Implement CardParser service in src/services/card_parser.py with fuzzy matching (threshold 0.8) for card names in 3 languages
- [ ] T048 [US2] Add delimiter handling in CardParser (comma, newline, "and", "и", "та")
- [ ] T049 [US2] Add card name normalization in CardParser (lowercase, trim, remove "the"/"карта")
- [ ] T050 [US2] Implement "Explain my own tarot combination" button callback handler in src/bot/handlers.py
- [ ] T051 [US2] Implement card names text message handler in src/bot/handlers.py for awaiting_cards state
- [ ] T052 [US2] Integrate CardParser with handler to parse user input and identify cards
- [ ] T053 [US2] Add custom interpretation generation in TarotInterpreter (src/tarot/interpreter.py) for user-submitted cards
- [ ] T054 [US2] Add validation for 1-10 unique cards per data-model.md
- [ ] T055 [US2] Implement partial recognition error handling (suggest "continue" or "try again") per contracts/bot-commands.md
- [ ] T056 [US2] Add logging for custom interpretations (user_id, submitted cards, parsed cards, language)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Multi-Turn Conversation and Follow-up Questions (Priority: P3)

**Goal**: Users can ask follow-up questions about their reading with context awareness

**Independent Test**: After receiving a reading, ask "Tell me more about The Tower" and get contextual response

### Tests for User Story 3 (TDD - Write These FIRST) ⚠️

- [ ] T057 [P] [US3] Write integration test for follow-up question flow in tests/integration/test_telegram_flow.py
- [ ] T058 [P] [US3] Write unit test for context extraction from last_reading in tests/unit/test_interpreter.py

### Implementation for User Story 3

- [ ] T059 [P] [US3] Extend UserSession model to store conversation_history (list of messages) in src/models/user_session.py
- [ ] T060 [US3] Implement context-aware message handler in src/bot/handlers.py to detect follow-up questions vs new reading requests
- [ ] T061 [US3] Add context extraction logic in TarotInterpreter to include last_reading cards and question in follow-up prompts
- [ ] T062 [US3] Implement card-specific follow-up logic (detect card mentions like "The Tower" in follow-up questions)
- [ ] T063 [US3] Add conversation state management to distinguish between follow-up and fresh reading
- [ ] T064 [US3] Add "start fresh reading" detection when user clicks buttons after follow-up conversation
- [ ] T065 [US3] Add logging for follow-up interactions (user_id, follow-up question, context used)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T066 [P] Add rate limiting middleware in src/bot/middleware.py (5 requests per user per minute)
- [ ] T067 [P] Add content moderation filter in src/bot/middleware.py for inappropriate questions
- [ ] T068 [P] Add performance monitoring for AI API calls (track response times)
- [ ] T069 [P] Add Telegram message size validation (4096 char limit) with truncation strategy
- [ ] T070 [P] Implement graceful shutdown handler in src/main.py (SIGTERM/SIGINT)
- [ ] T071 [P] Add health check endpoint (optional) for production monitoring
- [ ] T072 [P] Create Dockerfile for containerized deployment
- [ ] T073 [P] Create docker-compose.yml with bot service and Redis
- [ ] T074 [P] Add comprehensive error handling documentation in README.md
- [ ] T075 [P] Add deployment guide in README.md (Docker, environment variables, Redis setup)
- [ ] T076 [P] Run full integration test suite and verify all user stories pass
- [ ] T077 [P] Run performance tests with pytest-benchmark or locust (200 concurrent users target)
- [ ] T078 [P] Verify code coverage ≥80% with pytest --cov
- [ ] T079 [P] Run code formatters (black) and linters (flake8, mypy) on entire codebase
- [ ] T080 Validate quickstart.md by following setup steps from scratch

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1 (independently testable)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 for last_reading context, but should be independently testable

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Models before services
- Services before handlers
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models and utilities within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
pytest tests/contract/test_bot_commands.py::test_start_command &
pytest tests/contract/test_bot_commands.py::test_ask_question_button &
pytest tests/unit/test_spreads.py &
pytest tests/unit/test_interpreter.py &
pytest tests/unit/test_language_detection.py &
wait

# Launch all models and utilities for User Story 1 together:
# (These tasks can be assigned to different developers)
# T030: Implement /start handler
# T031: Implement /help handler
# T033: Implement 3-card spread
# T034: Implement AI service
# (All work on different files, no conflicts)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T024-T041)
   - Developer B: User Story 2 (T042-T056)
   - Developer C: User Story 3 (T057-T065)
3. Stories complete and integrate independently

---

## Implementation Notes

### TDD Workflow (Per Constitution)

For each user story:

1. **Write tests first** (contract, integration, unit)
2. **Run tests** - verify they FAIL (red)
3. **Implement minimal code** to pass tests (green)
4. **Refactor** for quality while keeping tests green
5. **Verify coverage** ≥80% before moving to next task

### File Path Reference

All tasks include specific file paths. Reference project structure from plan.md:

```
src/
├── bot/handlers.py, keyboards.py, middleware.py
├── tarot/deck.py, spreads.py, interpreter.py
├── i18n/translations.py, locales/
├── services/ai_service.py, session_service.py, card_parser.py
├── models/user_session.py, reading.py, card.py, card_combination.py
├── config.py
└── main.py

tests/
├── contract/test_bot_commands.py
├── integration/test_telegram_flow.py, test_ai_integration.py
└── unit/test_deck.py, test_spreads.py, test_interpreter.py, test_card_parser.py, test_language_detection.py

data/tarot_cards.json
```

### Task ID Reference

- **T001-T010**: Setup tasks
- **T011-T023**: Foundational tasks
- **T024-T041**: User Story 1 (P1) - Automated Reading
- **T042-T056**: User Story 2 (P2) - Custom Interpretation
- **T057-T065**: User Story 3 (P3) - Follow-up Questions
- **T066-T080**: Polish & Production Readiness

### Validation Checkpoints

After each phase:
- ✅ All tests pass (pytest)
- ✅ Code formatted (black)
- ✅ Linting passes (flake8)
- ✅ Type checking passes (mypy)
- ✅ Coverage ≥80% (pytest --cov)

---

## Success Criteria Alignment

Tasks map to spec.md success criteria:

- **SC-001** (60s reading completion): Covered by T030-T041 (US1 implementation)
- **SC-002** (95% language detection): Covered by T018, T029 (language detection)
- **SC-003** (90% relevant interpretations): Covered by T034, T035 (AI service)
- **SC-004** (85% card input success): Covered by T047-T049 (card parser)
- **SC-005** (<5s response time): Covered by T068 (performance monitoring)
- **SC-006** (100 concurrent users): Covered by T077 (load testing)
- **SC-007** (80% completion rate): Tracked via T041 (reading logging)
- **SC-008** (70% helpful rating): Requires post-launch feedback mechanism (out of scope)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requires ≥80% coverage, <10 cyclomatic complexity, TDD approach
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

**Total Tasks**: 80
- Setup: 10 tasks
- Foundational: 13 tasks
- User Story 1: 18 tasks (6 tests + 12 implementation)
- User Story 2: 15 tasks (4 tests + 11 implementation)
- User Story 3: 9 tasks (2 tests + 7 implementation)
- Polish: 15 tasks

**Estimated MVP Scope (User Story 1 only)**: 10 + 13 + 18 = 41 tasks
