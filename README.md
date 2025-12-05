# Telegram Tarot Reading Chatbot 🔮

A multilingual Telegram bot that provides personalized Tarot card readings using AI-powered interpretations.

## Features

- **Free Trial**: First reading is completely FREE for every new user
- **Automated Tarot Readings**: Ask a question and receive a 3-card reading (Past-Present-Future)
- **Custom Card Interpretation**: Input your own card combination for interpretation
- **Smart Card Recognition**: Fuzzy matching handles typos and name variations (e.g., "семь кубков" → "семерка кубков")
- **Multilingual Support**: Works in English, Russian, and Ukrainian with automatic language detection
- **AI-Powered**: Uses Anthropic Claude for nuanced, context-aware interpretations
- **Conversational**: Follow-up questions and contextual responses
- **Telegram Stars Payment**: Subsequent readings cost 20 Telegram Stars (~$0.20-0.40)

## Quick Start

For detailed setup instructions, see [Quickstart Guide](specs/001-telegram-tarot-bot/quickstart.md).

### Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from @BotFather)
- Anthropic API Key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Tarot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY
```

### Running the Bot

```bash
python src/main.py
```

## Project Structure

```
Tarot/
├── src/
│   ├── bot/              # Telegram bot handlers and middleware
│   ├── tarot/            # Tarot card logic and interpretation
│   ├── i18n/             # Internationalization support
│   ├── services/         # Business services (AI, session, parser)
│   ├── models/           # Data models
│   ├── config.py         # Configuration management
│   └── main.py           # Application entry point
├── tests/                # Test suite (contract, integration, unit)
├── data/                 # Tarot card data
└── specs/                # Feature specifications and documentation
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_deck.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

## Documentation

- [Implementation Plan](specs/001-telegram-tarot-bot/plan.md) - Technical architecture and decisions
- [Data Model](specs/001-telegram-tarot-bot/data-model.md) - Entity schemas and relationships
- [Bot Commands Contract](specs/001-telegram-tarot-bot/contracts/bot-commands.md) - API specifications
- [Research Document](specs/001-telegram-tarot-bot/research.md) - Technical decisions and rationale
- [Quickstart Guide](specs/001-telegram-tarot-bot/quickstart.md) - Detailed setup and usage

## Constitution Compliance

This project follows the [Tarot Project Constitution](.specify/memory/constitution.md):

- ✅ Code Quality: SRP, <10 cyclomatic complexity, clear naming
- ✅ Testing: TDD approach, ≥80% coverage, <5min test suite
- ✅ UX: Consistent interface, <5s response time, localized errors
- ✅ Performance: Async architecture, 100+ concurrent users
- ✅ Documentation: Complete specs, quickstart, API contracts

## License

MIT License

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to Railway.app.

**Quick Deploy to Railway:**
1. Push code to GitHub
2. Connect repository to Railway
3. Add environment variables (TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY)
4. Deploy automatically!

## Support

For issues or questions, please open an issue on GitHub.
