# Telegram Stars Payment Integration

This bot uses **Telegram Stars** to charge 20 stars per Tarot reading.

## How It Works

### User Flow:
1. User clicks "Ask a question" or "Explain my own combination"
2. Bot sends payment invoice for 20 ⭐ Telegram Stars
3. User pays using Telegram Stars in-app
4. Payment is confirmed
5. Bot proceeds with the reading

### Payment States:
- `AWAITING_PAYMENT` - Waiting for user to complete payment
- `AWAITING_QUESTION` - Payment successful, waiting for question (automated reading)
- `AWAITING_CUSTOM_QUESTION` - Payment successful, waiting for question (custom reading)

## Implementation Details

### Files Modified:
- **`src/services/payment_service.py`** - New payment service
- **`src/models/user_session.py`** - Added `AWAITING_PAYMENT` state
- **`src/bot/handlers.py`** - Updated to request payment before reading
- **`src/main.py`** - Registered payment handlers

### Payment Configuration:
```python
STARS_PER_READING = 20  # in src/services/payment_service.py
```

## Telegram Stars Pricing

| Stars | Approximate USD | Use Case |
|-------|----------------|----------|
| 20 ⭐ | ~$0.20-0.40 | Single reading |
| 100 ⭐ | ~$1-2 | Reading package |
| 500 ⭐ | ~$5-10 | Premium features |

**Note**: Exact pricing varies by region.

## Testing Payments

### Test Mode (Development):
Telegram doesn't have a separate test payment mode for Stars. To test:

1. **Use a Test Bot**:
   - Create a separate test bot with @BotFather
   - Deploy test version
   - Make small real payments (20 stars = ~$0.20)

2. **Test Payment Flow**:
   - Send /start
   - Click action button
   - Payment invoice appears
   - Complete payment with test Telegram account
   - Verify bot proceeds to question input

### Production:
- Use your main bot token
- Payments are real and processed by Telegram
- You receive 95% of payment (Telegram takes 5% fee)

## Withdrawing Earnings

1. Go to **@BotFather**
2. Send `/mybots`
3. Select your bot
4. Go to **Bot Settings** → **Payments**
5. Link payment provider (Stripe, etc.)
6. Withdraw earnings

## Customizing Prices

To change the price per reading:

### Option 1: Change STARS_PER_READING constant
```python
# In src/services/payment_service.py
STARS_PER_READING = 50  # Change from 20 to 50
```

### Option 2: Implement Tiered Pricing
```python
PRICING = {
    "automated": 20,  # 3-card reading
    "custom": 15,      # Custom interpretation
    "premium": 50,     # Premium features
}
```

### Option 3: Dynamic Pricing by Language/Region
```python
PRICING_BY_REGION = {
    "en": 20,
    "ru": 15,
    "uk": 15,
}
```

## Payment Security

### Built-in Security:
- ✅ Telegram handles all payment processing
- ✅ No credit card data touches your server
- ✅ PCI DSS compliant (handled by Telegram)
- ✅ Fraud detection by Telegram
- ✅ Automatic refunds for failed services

### Additional Measures:
```python
# In payment_service.py
async def handle_precheckout(update, context):
    # Validate user eligibility
    # Check for abuse patterns
    # Verify session exists
    await query.answer(ok=True)
```

## Handling Refunds

If you need to refund a payment:

1. **Via @BotFather**:
   - Go to Bot Settings → Payments
   - View transactions
   - Issue refunds

2. **Programmatic Refunds** (coming soon):
   ```python
   # Telegram Bot API will support refund API
   await context.bot.refund_star_payment(
       user_id=user_id,
       telegram_payment_charge_id=charge_id
   )
   ```

## Payment Analytics

Track payment metrics:

```python
# Log all payments
logger.info(f"Payment: user={user_id}, amount={amount}, type={reading_type}")

# Store in database for analytics:
# - Total revenue
# - Conversion rate (views → payments)
# - Popular reading types
# - Peak usage times
```

## Troubleshooting

### Invoice doesn't appear
**Solutions:**
- Check bot has payment provider configured in @BotFather
- Verify `PAYMENT_PROVIDER_TOKEN` is empty (for Stars)
- Check `currency="XTR"` for Telegram Stars
- Ensure user's Telegram version supports Stars

### Payment succeeds but bot doesn't respond
**Check:**
- `PreCheckoutQueryHandler` is registered
- `SUCCESSFUL_PAYMENT` filter is active
- `pre_checkout_query` in `allowed_updates`
- Session state transitions correctly

### Users can't pay
**Possible causes:**
- User's region doesn't support Stars yet
- Insufficient Stars balance
- Telegram app version too old
- Bot not properly configured in @BotFather

## Legal Considerations

### Terms of Service:
You must provide:
- Clear pricing information
- Refund policy
- Terms of service
- Privacy policy

### Example Terms:
> **Pricing**: Each Tarot reading costs 20 Telegram Stars (~$0.20-0.40).
>
> **Refund Policy**: Refunds available within 24 hours if AI service fails.
>
> **No Guarantees**: Tarot readings are for entertainment purposes only.

### Add to bot's /help:
```python
help_text = """
🔮 Tarot Bot Help

💫 Pricing: 20 ⭐ per reading
🔄 Refunds: Within 24h if service fails
⚠️ Entertainment only - not financial/medical advice
📜 Full terms: /terms
"""
```

## Future Enhancements

### 1. Subscription Model:
```python
SUBSCRIPTIONS = {
    "daily": {"stars": 100, "readings": 10},
    "monthly": {"stars": 500, "readings": unlimited"},
}
```

### 2. Free Trial:
```python
# Give first reading free
if user.reading_count == 0:
    proceed_without_payment()
else:
    request_payment()
```

### 3. Discounts/Promotions:
```python
if promo_code == "TAROT50":
    stars_required = STARS_PER_READING * 0.5
```

### 4. Gift Readings:
```python
# User can buy reading for another user
await send_invoice(
    recipient_id=friend_id,
    payer_id=user_id,
    ...
)
```

## Support

For payment-related issues:
- **Users**: Contact @BotFather support
- **Developers**: Check [Telegram Bot API Payments](https://core.telegram.org/bots/payments)
- **This Bot**: Open GitHub issue with "[Payment]" tag

---

**Ready to monetize your bot! 💰✨**
