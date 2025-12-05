"""Telegram inline keyboard builders for bot interface."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.i18n.translations import translation_manager


def get_main_menu_keyboard(language: str = "en", show_history: bool = True) -> InlineKeyboardMarkup:
    """
    Get the main menu keyboard with action buttons.

    Args:
        language: Language code for button text
        show_history: Whether to show history button

    Returns:
        InlineKeyboardMarkup with action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton(
                translation_manager.get_button_text("ask_question", language),
                callback_data="action:ask_question",
            )
        ],
        [
            InlineKeyboardButton(
                translation_manager.get_button_text("explain_combination", language),
                callback_data="action:explain_combination",
            )
        ],
    ]

    # Add history button if user has readings
    if show_history:
        history_buttons = {
            "en": "📜 View History",
            "ru": "📜 История",
            "uk": "📜 Історія"
        }
        keyboard.append([
            InlineKeyboardButton(
                history_buttons.get(language, history_buttons["en"]),
                callback_data="action:view_history"
            )
        ])

    return InlineKeyboardMarkup(keyboard)


def get_continue_or_retry_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """
    Get keyboard for partial card recognition (continue or retry).

    Args:
        language: Language code for button text

    Returns:
        InlineKeyboardMarkup with continue/retry options
    """
    keyboard = [
        [InlineKeyboardButton("✅ Continue", callback_data="action:continue")],
        [InlineKeyboardButton("🔄 Try Again", callback_data="action:retry")],
    ]
    return InlineKeyboardMarkup(keyboard)
