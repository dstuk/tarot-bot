"""Payment service for handling Telegram Stars payments."""
import logging
from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Payment configuration
STARS_PER_READING = 20
PAYMENT_PROVIDER_TOKEN = ""  # Empty for Telegram Stars


class PaymentService:
    """Service for handling Telegram Stars payments."""

    @staticmethod
    async def send_invoice(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        title: str,
        description: str,
        payload: str,
        language: str = "en"
    ) -> None:
        """
        Send payment invoice to user.

        Args:
            update: Telegram update
            context: Bot context
            title: Payment title
            description: Payment description
            payload: Internal payload to identify payment
            language: User's language
        """
        # Price in Telegram Stars (smallest units)
        # 1 Star = 1 unit, so 20 Stars = 20 units
        prices = [LabeledPrice("Tarot Reading", STARS_PER_READING)]

        try:
            await context.bot.send_invoice(
                chat_id=update.effective_chat.id,
                title=title,
                description=description,
                payload=payload,
                provider_token=PAYMENT_PROVIDER_TOKEN,  # Empty for Stars
                currency="XTR",  # Telegram Stars currency code
                prices=prices,
                max_tip_amount=0,
                suggested_tip_amounts=[],
                start_parameter="tarot-reading",
                photo_url=None,  # Optional: Add bot/tarot image URL
                photo_size=None,
                photo_width=None,
                photo_height=None,
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False,
            )
            logger.info(f"Sent invoice to user {update.effective_user.id} for {STARS_PER_READING} stars")
        except Exception as e:
            logger.error(f"Failed to send invoice: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_precheckout(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle pre-checkout query (validate payment before processing).

        Args:
            update: Telegram update with pre_checkout_query
            context: Bot context
        """
        query = update.pre_checkout_query

        # Always approve (you can add validation logic here if needed)
        try:
            await query.answer(ok=True)
            logger.info(f"Approved pre-checkout for user {query.from_user.id}")
        except Exception as e:
            logger.error(f"Failed to answer pre-checkout: {e}", exc_info=True)
            await query.answer(ok=False, error_message="Payment processing error. Please try again.")

    @staticmethod
    def extract_payment_info(update: Update) -> dict:
        """
        Extract payment information from successful payment.

        Args:
            update: Telegram update with successful_payment

        Returns:
            Dict with payment details
        """
        payment = update.message.successful_payment

        return {
            "currency": payment.currency,
            "total_amount": payment.total_amount,
            "invoice_payload": payment.invoice_payload,
            "telegram_payment_charge_id": payment.telegram_payment_charge_id,
            "provider_payment_charge_id": payment.provider_payment_charge_id,
        }


# Global payment service instance
payment_service = PaymentService()
