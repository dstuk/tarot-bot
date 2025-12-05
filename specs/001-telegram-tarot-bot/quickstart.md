# Quickstart Guide: Telegram Tarot Reading Chatbot

**Feature**: 001-telegram-tarot-bot
**Date**: 2025-12-04
**Purpose**: Get the Telegram Tarot bot running locally in <15 minutes

## Prerequisites

Before you start, ensure you have:

- **Python 3.11+** installed (`python --version`)
- **Git** installed
- **Telegram account** and the Telegram app
- **Internet connection** (for Telegram API and AI service)

**Optional** (for production-like environment):
- **Redis** (Docker recommended for local development)
- **Anthropic API key** or **OpenAI API key** (for AI-powered interpretations)

---

## Quick Setup (5 steps)

### Step 1: Clone and Enter Repository

```bash
git clone <repository-url>
cd Tarot
git checkout 001-telegram-tarot-bot
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to choose bot name and username
4. Copy the **bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your editor
```

Add your configuration to `.env`:
```ini
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# AI Service Configuration (choose one)
# Option 1: Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Option 2: OpenAI
# OPENAI_API_KEY=your_openai_api_key_here

# Session Storage (optional for MVP)
# REDIS_URL=redis://localhost:6379
# If not set, uses in-memory storage (dev only)

# Environment
ENVIRONMENT=development
```

### Step 5: Run the Bot

```bash
python src/main.py
```

Expected output:
```
[INFO] Loading Tarot card data...
[INFO] Loaded 78 cards in 3 languages
[INFO] Bot started: @YourBotUsername
[INFO] Press Ctrl+C to stop
```

---

## Verify It Works

### Test 1: Start Command

1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. ✅ You should see welcome message with two buttons

### Test 2: Ask a Question

1. Click "Ask a question" button
2. Type: "What should I focus on today?"
3. ✅ You should receive a 3-card reading with interpretation

### Test 3: Custom Card Interpretation

1. Click "Explain my own tarot combination"
2. Type: "The Fool, The Tower, Three of Cups"
3. ✅ You should receive an interpretation of those cards

### Test 4: Multilingual Support

1. Click "Ask a question"
2. Type in Russian: "Стоит ли мне менять работу?"
3. ✅ You should receive a reading in Russian

---

## Project Structure Overview

```
Tarot/
├── src/
│   ├── bot/                  # Telegram bot handlers
│   │   ├── handlers.py       # Command and message handlers
│   │   ├── keyboards.py      # Button definitions
│   │   └── middleware.py     # Language detection, rate limiting
│   ├── tarot/                # Tarot logic
│   │   ├── deck.py           # Card data management
│   │   ├── spreads.py        # Card spread logic
│   │   └── interpreter.py    # AI integration
│   ├── i18n/                 # Internationalization
│   │   ├── translations.py   # Translation utilities
│   │   └── locales/          # Language files (en, ru, uk)
│   ├── services/             # Business services
│   │   ├── ai_service.py     # AI model integration
│   │   ├── session_service.py # Session management
│   │   └── card_parser.py    # Card name parsing
│   ├── models/               # Data models
│   │   ├── user_session.py   # User session model
│   │   ├── reading.py        # Reading model
│   │   └── card.py           # Card entity model
│   ├── config.py             # Configuration management
│   └── main.py               # Entry point
├── tests/                    # Test suite (see testing guide)
├── data/
│   └── tarot_cards.json      # Tarot card database (78 cards)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # Full documentation
```

---

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_deck.py

# Run with verbosity
pytest -v
```

**Expected**: ≥80% code coverage (per constitution)

### Code Formatting

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint code
flake8 src/ tests/
```

### Type Checking

```bash
# Run type checker
mypy src/
```

---

## Common Issues

### Issue 1: "ModuleNotFoundError: No module named 'telegram'"

**Solution**: Activate virtual environment and reinstall dependencies
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue 2: Bot doesn't respond

**Possible causes**:
1. **Invalid bot token**: Check `.env` file, ensure token is correct
2. **Another instance running**: Stop other bot instances
3. **Network issues**: Check internet connection

**Debug**:
```bash
# Check bot token is valid
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
```

### Issue 3: AI service errors

**Solution**: Check API key configuration
```bash
# Test Anthropic API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-sonnet-20240229","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

### Issue 4: Redis connection failed

**Solution** (if using Redis):
```bash
# Start Redis with Docker
docker run -d -p 6379:6379 redis:alpine

# Or disable Redis (use in-memory storage)
# Comment out REDIS_URL in .env file
```

---

## Optional: Production Deployment

### Using Docker

```bash
# Build image
docker build -t tarot-bot .

# Run container
docker run -d \
  --name tarot-bot \
  --env-file .env \
  --restart unless-stopped \
  tarot-bot
```

### Environment Variables (Production)

```ini
# .env (production)
TELEGRAM_BOT_TOKEN=your_production_token
ANTHROPIC_API_KEY=your_production_key
REDIS_URL=redis://your-redis-host:6379
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Health Check Endpoint (Optional)

If you add a health check endpoint:
```bash
# Check bot status
curl http://localhost:8080/health
```

---

## Next Steps

### For Development

1. **Read the full documentation**:
   - [Implementation Plan](plan.md) - Technical architecture
   - [Data Model](data-model.md) - Entity schemas
   - [Bot Commands Contract](contracts/bot-commands.md) - API specifications

2. **Set up your IDE**:
   - Install Python extension
   - Configure linter (flake8)
   - Enable type checking (mypy)

3. **Review the codebase**:
   - Start with `src/main.py` (entry point)
   - Explore `src/bot/handlers.py` (bot logic)
   - Check `src/tarot/deck.py` (card data)

### For Testing

1. **Write tests first** (TDD per constitution):
   ```bash
   # Create test file
   touch tests/unit/test_new_feature.py

   # Write failing test
   # Implement feature
   # Verify test passes
   ```

2. **Run tests before committing**:
   ```bash
   pytest && black --check src/ && mypy src/
   ```

### For Contributing

1. **Follow constitution principles**:
   - ✅ Code coverage ≥80%
   - ✅ Cyclomatic complexity <10
   - ✅ All tests pass
   - ✅ Code formatted (black)

2. **Commit message format**:
   ```
   feat: add card reversal support
   fix: correct Ukrainian language detection
   test: add integration tests for /start command
   docs: update quickstart with Redis setup
   ```

---

## Support and Resources

### Documentation
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot library](https://docs.python-telegram-bot.org/)
- [Anthropic Claude API](https://docs.anthropic.com/)

### Troubleshooting
- Check logs: `tail -f logs/bot.log` (if logging configured)
- Enable debug mode: `LOG_LEVEL=DEBUG` in `.env`
- Test components individually: `pytest tests/unit/<component>.py`

### Getting Help
- Open an issue on GitHub
- Check `README.md` for detailed documentation
- Review `specs/001-telegram-tarot-bot/` for design docs

---

## Success Checklist

After completing quickstart, you should be able to:

- ✅ Run the bot locally
- ✅ Send `/start` and see welcome buttons
- ✅ Ask a question and receive a Tarot reading
- ✅ Enter custom card names and get interpretation
- ✅ Test in multiple languages (EN/RU/UK)
- ✅ Run tests with `pytest`
- ✅ Understand project structure

**Estimated time**: 10-15 minutes for first-time setup

**You're ready to start developing! 🎴**
