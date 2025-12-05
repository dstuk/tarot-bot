"""Telegram Tarot Bot - Main entry point."""
import logging
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, filters
from src.config import config
from src.bot.handlers import start_command, help_command, button_callback, handle_text_message, handle_successful_payment
from src.services.payment_service import payment_service
from src.bot.middleware import rate_limit_middleware

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("tarot_bot.log") if config.environment == "production" else logging.NullHandler(),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Initialize and run the Telegram bot."""
    logger.info("Starting Telegram Tarot Bot...")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Using Redis: {config.use_redis}")

    # Validate configuration
    if not config.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured!")
        sys.exit(1)

    if not config.has_ai_service:
        logger.warning("No AI service configured. AI features will not work.")

    # Create application
    application = Application.builder().token(config.telegram_bot_token).build()

    # Register command handlers with rate limiting
    application.add_handler(CommandHandler("start", rate_limit_middleware(start_command)))
    application.add_handler(CommandHandler("help", rate_limit_middleware(help_command)))

    # Register callback query handler for buttons with rate limiting
    application.add_handler(CallbackQueryHandler(rate_limit_middleware(button_callback)))

    # Register payment handlers (no rate limiting for payment callbacks)
    application.add_handler(PreCheckoutQueryHandler(payment_service.handle_precheckout))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))

    # Register message handler for text input with rate limiting
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rate_limit_middleware(handle_text_message)))

    # Start the bot
    logger.info("Bot is ready! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=["message", "callback_query", "pre_checkout_query"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Bot crashed with error: {e}")
        sys.exit(1)
