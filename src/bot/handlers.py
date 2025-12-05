"""Telegram bot command and message handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.i18n.translations import translation_manager
from src.bot.keyboards import get_main_menu_keyboard
from src.services.session_service import SessionService
from src.services.ai_service import AIService
from src.models.user_session import UserSession, SessionState, Reading
from src.tarot.deck import TarotDeck
from src.tarot.spreads import create_spread
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize services
session_service = SessionService()
ai_service = AIService()
tarot_deck = TarotDeck()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - show welcome message with action buttons.

    T030: Implement /start command handler with welcome message and action buttons.
    """
    user_id = update.effective_user.id

    # Reset or create new session
    session = UserSession(
        user_id=user_id,
        language="en",  # Default, will be detected from first message
        state=SessionState.IDLE
    )
    session_service.save_session(session)

    welcome_message = translation_manager.get_message_text("welcome", "en")
    keyboard = get_main_menu_keyboard("en")

    await update.message.reply_text(welcome_message, reply_markup=keyboard)
    logger.info(f"User {user_id} started bot session")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /help command - show usage instructions.

    T031: Implement /help command handler with usage instructions.
    """
    user_id = update.effective_user.id
    session = session_service.get_session(user_id)

    # Use session language if available, otherwise default to English
    language = session.language if session else "en"

    help_message = translation_manager.get_message_text("help", language)
    keyboard = get_main_menu_keyboard(language)

    await update.message.reply_text(help_message, reply_markup=keyboard)
    logger.info(f"User {user_id} requested help")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle inline keyboard button callbacks.

    T032: Implement "Ask a question" button callback handler (state transition).
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = session_service.get_session(user_id)

    if not session:
        session = UserSession(
            user_id=user_id,
            language="en",
            state=SessionState.IDLE
        )

    callback_data = query.data

    if callback_data == "action:ask_question":
        # Transition to AWAITING_QUESTION state
        session.state = SessionState.AWAITING_QUESTION
        session_service.save_session(session)

        prompt_message = translation_manager.get_message_text("prompt_question", session.language)
        await query.edit_message_text(prompt_message)
        logger.info(f"User {user_id} initiated question reading")

    elif callback_data == "action:explain_combination":
        # Transition to AWAITING_CUSTOM_QUESTION state (first ask the question)
        session.state = SessionState.AWAITING_CUSTOM_QUESTION
        session_service.save_session(session)

        # Ask for their question first
        prompt_message = translation_manager.get_message_text("prompt_question", session.language)
        await query.edit_message_text(prompt_message)
        logger.info(f"User {user_id} initiated custom combination reading")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle user text messages based on current session state.

    T036: Implement question text message handler.
    T037: Integrate card drawing, AI interpretation, and response formatting.
    T038: Add multilingual response formatting.
    T039: Add validation and error handling (5-500 char limit).
    T040: Add AI service failure error handling.
    T041: Add logging for reading completions.
    """
    user_id = update.effective_user.id
    message_text = update.message.text

    session = session_service.get_session(user_id)

    if not session or session.state == SessionState.IDLE:
        # User sent message without proper context
        error_message = translation_manager.get_error_text("invalid_state", "en")
        keyboard = get_main_menu_keyboard("en")
        await update.message.reply_text(error_message, reply_markup=keyboard)
        return

    # Detect language from message if not already detected
    from src.bot.middleware import detect_language
    detected_language = detect_language(message_text)
    if detected_language != session.language:
        session.language = detected_language
        session_service.save_session(session)

    if session.state == SessionState.AWAITING_QUESTION:
        await handle_question_input(update, session, message_text)
    elif session.state == SessionState.AWAITING_CUSTOM_QUESTION:
        await handle_custom_question_input(update, session, message_text)
    elif session.state == SessionState.AWAITING_CARDS:
        await handle_cards_input(update, session, message_text)


async def handle_question_input(update: Update, session: UserSession, question: str) -> None:
    """
    Process user question and generate automated Tarot reading.

    Implements validation, card drawing, AI interpretation, and response formatting.
    """
    user_id = update.effective_user.id

    # T039: Validate question length
    if len(question.strip()) < 5:
        error_message = translation_manager.get_error_text("empty_question", session.language)
        await update.message.reply_text(error_message)
        logger.warning(f"User {user_id} provided too short question: {len(question)} chars")
        return

    if len(question) > 500:
        error_message = translation_manager.get_error_text("long_question", session.language)
        await update.message.reply_text(error_message)
        logger.warning(f"User {user_id} provided too long question: {len(question)} chars")
        return

    # Show processing message
    processing_message = translation_manager.get_message_text("processing", session.language)
    processing_msg = await update.message.reply_text(processing_message)

    try:
        # T037: Draw 3 cards for Past-Present-Future spread
        spread = create_spread("three_card", tarot_deck, session.language)
        cards, positions = spread.draw_cards()

        logger.info(f"User {user_id} drew cards: {[card.id for card in cards]}")

        # T037: Generate AI interpretation
        interpretation = await ai_service.generate_reading_interpretation(
            question=question,
            cards=cards,
            positions=positions,
            language=session.language
        )

        # T038: Format multilingual response
        response = format_reading_response(
            question=question,
            cards=cards,
            positions=positions,
            interpretation=interpretation,
            language=session.language
        )

        # Save reading to session
        reading = Reading(
            type="automated",
            cards=[card.id for card in cards],
            question=question,
            card_positions=positions,
            interpretation=interpretation,
            language=session.language,
            timestamp=datetime.utcnow()
        )
        session.save_reading(reading)
        session.state = SessionState.IDLE
        session_service.save_session(session)

        # Delete processing message and send reading
        await processing_msg.delete()
        keyboard = get_main_menu_keyboard(session.language)
        await update.message.reply_text(response, reply_markup=keyboard, parse_mode="Markdown")

        # T041: Log reading completion
        logger.info(f"User {user_id} completed automated reading. Question: '{question[:50]}...', Cards: {[card.id for card in cards]}")

    except Exception as e:
        # T040: Handle AI service failures
        logger.error(f"Error generating reading for user {user_id}: {str(e)}", exc_info=True)

        await processing_msg.delete()
        error_message = translation_manager.get_error_text("ai_service", session.language)
        keyboard = get_main_menu_keyboard(session.language)
        await update.message.reply_text(error_message, reply_markup=keyboard)

        # Reset session state
        session.state = SessionState.IDLE
        session_service.save_session(session)


async def handle_custom_question_input(update: Update, session: UserSession, question: str) -> None:
    """
    Process user's question for custom reading, then prompt for card names.

    This is the first step of a two-step custom reading flow.
    """
    user_id = update.effective_user.id

    # Validate question length
    if len(question.strip()) < 5:
        error_message = translation_manager.get_error_text("empty_question", session.language)
        await update.message.reply_text(error_message)
        logger.warning(f"User {user_id} provided too short question: {len(question)} chars")
        return

    if len(question) > 500:
        error_message = translation_manager.get_error_text("long_question", session.language)
        await update.message.reply_text(error_message)
        logger.warning(f"User {user_id} provided too long question: {len(question)} chars")
        return

    # Store the question in conversation context
    session.conversation_context["custom_question"] = question
    session.state = SessionState.AWAITING_CARDS
    session_service.save_session(session)

    # Now ask for the card names
    prompt_message = translation_manager.get_message_text("prompt_cards", session.language)
    await update.message.reply_text(prompt_message)
    logger.info(f"User {user_id} provided question for custom reading, now awaiting cards")


async def handle_cards_input(update: Update, session: UserSession, cards_text: str) -> None:
    """
    Process user-provided card names and generate custom interpretation.

    Implements card name parsing, validation, AI interpretation, and response formatting.
    """
    user_id = update.effective_user.id

    # Get the stored question from conversation context
    custom_question = session.conversation_context.get("custom_question", "")

    # Parse card names from text (comma-separated)
    card_names = [name.strip() for name in cards_text.split(",")]

    # Find cards by name
    cards = []
    for card_name in card_names:
        card = tarot_deck.get_card_by_name(card_name, session.language)
        if card:
            cards.append(card)

    # Validate at least one card was recognized
    if not cards:
        error_message = translation_manager.get_error_text("no_cards_recognized", session.language)
        await update.message.reply_text(error_message)
        logger.warning(f"User {user_id} provided unrecognizable card names: {cards_text}")
        return

    # Show processing message
    processing_message = translation_manager.get_message_text("processing", session.language)
    processing_msg = await update.message.reply_text(processing_message)

    try:
        # Generate AI interpretation for custom cards with their question
        interpretation = await ai_service.generate_custom_interpretation(
            cards=cards,
            question=custom_question,
            language=session.language
        )

        # Format response
        response = format_custom_reading_response(
            question=custom_question,
            cards=cards,
            interpretation=interpretation,
            language=session.language
        )

        # Save reading to session
        reading = Reading(
            type="custom",
            cards=[card.id for card in cards],
            question=custom_question,
            card_positions=[],  # No specific positions for custom readings
            interpretation=interpretation,
            language=session.language,
            timestamp=datetime.utcnow()
        )
        session.save_reading(reading)
        session.state = SessionState.IDLE
        # Clear the stored question from context
        session.conversation_context.pop("custom_question", None)
        session_service.save_session(session)

        # Delete processing message and send reading
        await processing_msg.delete()
        keyboard = get_main_menu_keyboard(session.language)
        await update.message.reply_text(response, reply_markup=keyboard, parse_mode="Markdown")

        # Log reading completion
        logger.info(f"User {user_id} completed custom reading. Question: '{custom_question[:50] if custom_question else 'none'}...', Cards: {[card.id for card in cards]}")

    except Exception as e:
        # Handle AI service failures
        logger.error(f"Error generating custom reading for user {user_id}: {str(e)}", exc_info=True)

        await processing_msg.delete()
        error_message = translation_manager.get_error_text("ai_service", session.language)
        keyboard = get_main_menu_keyboard(session.language)
        await update.message.reply_text(error_message, reply_markup=keyboard)

        # Reset session state
        session.state = SessionState.IDLE
        session_service.save_session(session)


def format_reading_response(
    question: str,
    cards: list,
    positions: list[str],
    interpretation: str,
    language: str
) -> str:
    """
    Format automated reading response with card details and interpretation.

    T038: Multilingual response formatting.
    """
    title = translation_manager.get_message_text("reading_title", language)
    disclaimer = translation_manager.get_message_text("disclaimer", language)

    response_parts = [f"*{title}*\n"]

    # Add question
    question_label = {"en": "Question", "ru": "Вопрос", "uk": "Питання"}
    response_parts.append(f"*{question_label.get(language, 'Question')}:* {question}\n")

    # Add cards with positions
    cards_label = {"en": "Cards Drawn", "ru": "Выпавшие карты", "uk": "Витягнуті карти"}
    response_parts.append(f"*{cards_label.get(language, 'Cards')}:*")

    for i, (card, position) in enumerate(zip(cards, positions)):
        card_name = card.get_name(language)
        response_parts.append(f"{i+1}. *{position}*: {card_name}")

    response_parts.append("")

    # Add interpretation
    interpretation_label = {"en": "Interpretation", "ru": "Толкование", "uk": "Тлумачення"}
    response_parts.append(f"*{interpretation_label.get(language, 'Interpretation')}:*")
    response_parts.append(interpretation)

    # Add disclaimer
    response_parts.append(disclaimer)

    return "\n".join(response_parts)


def format_custom_reading_response(
    question: str,
    cards: list,
    interpretation: str,
    language: str
) -> str:
    """
    Format custom card combination response with interpretation.

    T038: Multilingual response formatting.
    """
    title = translation_manager.get_message_text("reading_title", language)
    disclaimer = translation_manager.get_message_text("disclaimer", language)

    response_parts = [f"*{title}*\n"]

    # Add question if provided
    if question:
        question_label = {"en": "Question", "ru": "Вопрос", "uk": "Питання"}
        response_parts.append(f"*{question_label.get(language, 'Question')}:* {question}\n")

    # Add cards
    cards_label = {"en": "Your Cards", "ru": "Ваши карты", "uk": "Ваші карти"}
    response_parts.append(f"*{cards_label.get(language, 'Your Cards')}:*")

    for i, card in enumerate(cards):
        card_name = card.get_name(language)
        response_parts.append(f"{i+1}. {card_name}")

    response_parts.append("")

    # Add interpretation
    interpretation_label = {"en": "Interpretation", "ru": "Толкование", "uk": "Тлумачення"}
    response_parts.append(f"*{interpretation_label.get(language, 'Interpretation')}:*")
    response_parts.append(interpretation)

    # Add disclaimer
    response_parts.append(disclaimer)

    return "\n".join(response_parts)
