"""Telegram bot command and message handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.i18n.translations import translation_manager
from src.bot.keyboards import get_main_menu_keyboard
from src.services.session_service import SessionService
from src.services.ai_service import AIService
from src.services.payment_service import payment_service, STARS_PER_READING
from src.models.user_session import UserSession, SessionState, Reading
from src.tarot.deck import TarotDeck
from src.tarot.spreads import create_spread
from src.config import config
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

    # Get existing session or create new one
    existing_session = session_service.get_session(user_id)
    has_history = existing_session and existing_session.reading_count > 0

    # Reset session state but preserve history
    session = UserSession(
        user_id=user_id,
        language=existing_session.language if existing_session else "en",
        state=SessionState.IDLE,
        reading_count=existing_session.reading_count if existing_session else 0,
        reading_history=existing_session.reading_history if existing_session else []
    )
    session_service.save_session(session)

    welcome_message = translation_manager.get_message_text("welcome", session.language)
    keyboard = get_main_menu_keyboard(session.language, show_history=has_history)

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
    has_history = session and session.reading_count > 0

    help_message = translation_manager.get_message_text("help", language)
    keyboard = get_main_menu_keyboard(language, show_history=has_history)

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
        # Store the reading type
        session.conversation_context["reading_type"] = "automated"

        # Check if user is whitelisted (VIP/admin/tester)
        if config.is_whitelisted(user_id):
            # Skip payment for whitelisted users
            session.state = SessionState.AWAITING_QUESTION
            session_service.save_session(session)

            vip_messages = {
                "en": "✨ VIP access - Free reading! Please ask your question:",
                "ru": "✨ VIP доступ - Бесплатное гадание! Задайте свой вопрос:",
                "uk": "✨ VIP доступ - Безкоштовне ворожіння! Поставте своє питання:"
            }

            prompt_message = vip_messages.get(session.language, vip_messages["en"])
            await query.edit_message_text(prompt_message)
            logger.info(f"User {user_id} initiated automated reading - WHITELISTED user (free)")
        # Check if this is user's first reading (free trial)
        elif session.is_first_reading():
            # Skip payment for first reading
            session.state = SessionState.AWAITING_QUESTION
            session_service.save_session(session)

            free_trial_messages = {
                "en": "🎁 Your first reading is FREE! Please ask your question:",
                "ru": "🎁 Ваше первое гадание БЕСПЛАТНО! Задайте свой вопрос:",
                "uk": "🎁 Ваше перше ворожіння БЕЗКОШТОВНО! Поставте своє питання:"
            }

            prompt_message = free_trial_messages.get(session.language, free_trial_messages["en"])
            await query.edit_message_text(prompt_message)
            logger.info(f"User {user_id} initiated automated reading - FREE first reading")
        else:
            # Request payment for subsequent readings
            session.state = SessionState.AWAITING_PAYMENT
            session_service.save_session(session)

            # Send payment invoice
            await query.edit_message_text("⏳ Preparing payment invoice...")

            payment_titles = {
                "en": "🔮 Tarot Reading",
                "ru": "🔮 Гадание на Таро",
                "uk": "🔮 Ворожіння на Таро"
            }
            payment_descriptions = {
                "en": f"Get a 3-card Tarot reading with AI-powered interpretation ({STARS_PER_READING} ⭐)",
                "ru": f"Получите расклад на 3 карты Таро с толкованием от ИИ ({STARS_PER_READING} ⭐)",
                "uk": f"Отримайте розклад на 3 карти Таро з тлумаченням від ШІ ({STARS_PER_READING} ⭐)"
            }

            await payment_service.send_invoice(
                update=update,
                context=context,
                title=payment_titles.get(session.language, payment_titles["en"]),
                description=payment_descriptions.get(session.language, payment_descriptions["en"]),
                payload=f"reading:automated:{user_id}",
                language=session.language
            )
            logger.info(f"User {user_id} initiated automated reading - payment requested")

    elif callback_data == "action:explain_combination":
        # Store the reading type
        session.conversation_context["reading_type"] = "custom"

        # Check if user is whitelisted (VIP/admin/tester)
        if config.is_whitelisted(user_id):
            # Skip payment for whitelisted users
            session.state = SessionState.AWAITING_CUSTOM_QUESTION
            session_service.save_session(session)

            vip_messages = {
                "en": "✨ VIP access - Free reading! Please tell me your question:",
                "ru": "✨ VIP доступ - Бесплатное гадание! Расскажите ваш вопрос:",
                "uk": "✨ VIP доступ - Безкоштовне ворожіння! Розкажіть ваше питання:"
            }

            prompt_message = vip_messages.get(session.language, vip_messages["en"])
            await query.edit_message_text(prompt_message)
            logger.info(f"User {user_id} initiated custom reading - WHITELISTED user (free)")
        # Check if this is user's first reading (free trial)
        elif session.is_first_reading():
            # Skip payment for first reading
            session.state = SessionState.AWAITING_CUSTOM_QUESTION
            session_service.save_session(session)

            free_trial_messages = {
                "en": "🎁 Your first reading is FREE! Please tell me your question:",
                "ru": "🎁 Ваше первое гадание БЕСПЛАТНО! Расскажите ваш вопрос:",
                "uk": "🎁 Ваше перше ворожіння БЕЗКОШТОВНО! Розкажіть ваше питання:"
            }

            prompt_message = free_trial_messages.get(session.language, free_trial_messages["en"])
            await query.edit_message_text(prompt_message)
            logger.info(f"User {user_id} initiated custom reading - FREE first reading")
        else:
            # Request payment for subsequent readings
            session.state = SessionState.AWAITING_PAYMENT
            session_service.save_session(session)

            # Send payment invoice
            await query.edit_message_text("⏳ Preparing payment invoice...")

            payment_titles = {
                "en": "🔮 Custom Tarot Interpretation",
                "ru": "🔮 Индивидуальное толкование Таро",
                "uk": "🔮 Індивідуальне тлумачення Таро"
            }
            payment_descriptions = {
                "en": f"Get interpretation for your own card combination ({STARS_PER_READING} ⭐)",
                "ru": f"Получите толкование вашей комбинации карт ({STARS_PER_READING} ⭐)",
                "uk": f"Отримайте тлумачення вашої комбінації карт ({STARS_PER_READING} ⭐)"
            }

            await payment_service.send_invoice(
                update=update,
                context=context,
                title=payment_titles.get(session.language, payment_titles["en"]),
                description=payment_descriptions.get(session.language, payment_descriptions["en"]),
                payload=f"reading:custom:{user_id}",
                language=session.language
            )
            logger.info(f"User {user_id} initiated custom reading - payment requested")

    elif callback_data == "action:view_history":
        # Show reading history
        await handle_view_history(update, session)


async def handle_view_history(update: Update, session: UserSession) -> None:
    """Display user's reading history."""
    query = update.callback_query
    user_id = update.effective_user.id

    if session.reading_count == 0:
        no_history_messages = {
            "en": "📜 You don't have any readings yet.\n\nClick 'Ask a question' to get your first reading!",
            "ru": "📜 У вас пока нет гаданий.\n\nНажмите 'Задать вопрос', чтобы получить первое гадание!",
            "uk": "📜 У вас поки немає ворожінь.\n\nНатисніть 'Поставити питання', щоб отримати перше ворожіння!"
        }
        await query.edit_message_text(no_history_messages.get(session.language, no_history_messages["en"]))
        return

    # Get recent history (last 5 readings)
    history = session.get_reading_history(limit=5)

    # Format history message
    history_headers = {
        "en": f"📜 **Your Reading History** (Last {len(history)} readings)\n\n",
        "ru": f"📜 **Ваша история гаданий** (Последние {len(history)})\n\n",
        "uk": f"📜 **Ваша історія ворожінь** (Останні {len(history)})\n\n"
    }

    message = history_headers.get(session.language, history_headers["en"])

    for i, reading in enumerate(history, 1):
        date_str = reading.timestamp.strftime("%Y-%m-%d %H:%M")
        reading_type_labels = {
            "automated": {"en": "Automated", "ru": "Автоматическое", "uk": "Автоматичне"},
            "custom": {"en": "Custom", "ru": "Индивидуальное", "uk": "Індивідуальне"}
        }
        type_label = reading_type_labels.get(reading.type, {}).get(session.language, reading.type)

        message += f"**{i}. {type_label}** ({date_str})\n"
        if reading.question:
            question_labels = {"en": "Question", "ru": "Вопрос", "uk": "Питання"}
            question_label = question_labels.get(session.language, "Question")
            message += f"❓ *{question_label}:* {reading.question[:80]}{'...' if len(reading.question) > 80 else ''}\n"
        message += "\n"

    # Add footer
    footer_messages = {
        "en": "_Tap a reading number to view full details (coming soon)_",
        "ru": "_Нажмите номер гадания для просмотра деталей (скоро)_",
        "uk": "_Натисніть номер ворожіння для перегляду деталей (незабаром)_"
    }
    message += footer_messages.get(session.language, footer_messages["en"])

    keyboard = get_main_menu_keyboard(session.language, show_history=True)
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode="Markdown")
    logger.info(f"User {user_id} viewed reading history ({len(history)} readings)")


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
        keyboard = get_main_menu_keyboard(session.language, show_history=True)  # Always show history after a reading
        await update.message.reply_text(response, reply_markup=keyboard, parse_mode="Markdown")

        # T041: Log reading completion
        logger.info(f"User {user_id} completed automated reading. Question: '{question[:50]}...', Cards: {[card.id for card in cards]}")

    except Exception as e:
        # T040: Handle AI service failures
        logger.error(f"Error generating reading for user {user_id}: {str(e)}", exc_info=True)

        await processing_msg.delete()
        error_message = translation_manager.get_error_text("ai_service", session.language)
        keyboard = get_main_menu_keyboard(session.language, show_history=(session.reading_count > 0))
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

    # Find cards by name with fuzzy matching
    cards = []
    unrecognized_names = []
    for card_name in card_names:
        # Use fuzzy matching with 75% threshold
        card = tarot_deck.get_card_by_name_fuzzy(card_name, session.language, threshold=75.0)
        if card:
            cards.append(card)
        else:
            unrecognized_names.append(card_name)

    # Validate at least one card was recognized
    if not cards:
        error_message = translation_manager.get_error_text("no_cards_recognized", session.language)
        await update.message.reply_text(error_message)
        logger.warning(f"User {user_id} provided unrecognizable card names: {cards_text}")
        return

    # If some cards were not recognized, inform the user but continue with recognized cards
    if unrecognized_names:
        warning_messages = {
            "en": f"⚠️ Note: Could not recognize these cards: {', '.join(unrecognized_names)}\n\nProceeding with recognized cards...",
            "ru": f"⚠️ Внимание: Не удалось распознать эти карты: {', '.join(unrecognized_names)}\n\nПродолжаем с распознанными картами...",
            "uk": f"⚠️ Увага: Не вдалося розпізнати ці карти: {', '.join(unrecognized_names)}\n\nПродовжуємо з розпізнаними картами..."
        }
        warning_msg = warning_messages.get(session.language, warning_messages["en"])
        await update.message.reply_text(warning_msg)
        logger.info(f"User {user_id} - {len(cards)} cards recognized, {len(unrecognized_names)} unrecognized: {unrecognized_names}")

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
        keyboard = get_main_menu_keyboard(session.language, show_history=True)  # Always show history after a reading
        await update.message.reply_text(response, reply_markup=keyboard, parse_mode="Markdown")

        # Log reading completion
        logger.info(f"User {user_id} completed custom reading. Question: '{custom_question[:50] if custom_question else 'none'}...', Cards: {[card.id for card in cards]}")

    except Exception as e:
        # Handle AI service failures
        logger.error(f"Error generating custom reading for user {user_id}: {str(e)}", exc_info=True)

        await processing_msg.delete()
        error_message = translation_manager.get_error_text("ai_service", session.language)
        keyboard = get_main_menu_keyboard(session.language, show_history=(session.reading_count > 0))
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


async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle successful payment - transition user to appropriate state.

    After payment is confirmed, move user to the next step of their reading.
    """
    user_id = update.effective_user.id
    session = session_service.get_session(user_id)

    if not session:
        logger.error(f"No session found for user {user_id} after payment")
        return

    # Get payment info
    payment_info = payment_service.extract_payment_info(update)
    logger.info(f"User {user_id} completed payment: {payment_info}")

    # Get the reading type from session context
    reading_type = session.conversation_context.get("reading_type", "automated")

    # Thank user for payment
    thank_you_messages = {
        "en": "✅ Payment received! Thank you. Now let's proceed with your reading.",
        "ru": "✅ Платёж получен! Спасибо. Теперь приступим к вашему гаданию.",
        "uk": "✅ Платіж отримано! Дякуємо. Тепер перейдемо до вашого ворожіння."
    }
    await update.message.reply_text(
        thank_you_messages.get(session.language, thank_you_messages["en"])
    )

    # Transition to appropriate state based on reading type
    if reading_type == "automated":
        session.state = SessionState.AWAITING_QUESTION
        session_service.save_session(session)

        prompt_message = translation_manager.get_message_text("prompt_question", session.language)
        await update.message.reply_text(prompt_message)
        logger.info(f"User {user_id} paid - now awaiting question")

    elif reading_type == "custom":
        session.state = SessionState.AWAITING_CUSTOM_QUESTION
        session_service.save_session(session)

        prompt_message = translation_manager.get_message_text("prompt_question", session.language)
        await update.message.reply_text(prompt_message)
        logger.info(f"User {user_id} paid - now awaiting custom question")
