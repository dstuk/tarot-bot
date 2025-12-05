# Free Trial Feature

## Overview

Every new user gets their **first Tarot reading completely FREE** - no payment required!

## How It Works

### For Users:
1. User opens bot and clicks `/start`
2. User clicks "Ask a question" or "Explain my own combination"
3. **First reading**: Bot displays "🎁 Your first reading is FREE!" and proceeds directly to question input
4. **Subsequent readings**: Bot requests payment of 20 Telegram Stars before proceeding

### Technical Implementation:
- Each `UserSession` tracks `reading_count` (incremented after each completed reading)
- `is_first_reading()` method checks if `reading_count == 0`
- Button handlers check `session.is_first_reading()` before requesting payment
- Free trial applies to BOTH automated and custom readings

## Benefits

### For Users:
- **Risk-free trial**: Experience the bot's quality before paying
- **No commitment**: Try once for free, pay only if satisfied
- **Fair value**: See AI-powered interpretation quality firsthand

### For Bot Owner:
- **Higher conversion**: Users try before buying → better conversion rates
- **User acquisition**: Free trial attracts more users
- **Trust building**: Demonstrates quality and builds confidence
- **Viral potential**: Happy free users recommend to friends

## Configuration

### Current Settings:
- **Free readings per user**: 1
- **Paid reading cost**: 20 Telegram Stars (~$0.20-0.40)

### Modifying Free Trial Count:

To offer more free readings (e.g., first 3 readings free):

```python
# In src/models/user_session.py
def is_first_reading(self) -> bool:
    """Check if this is within free trial period."""
    return self.reading_count < 3  # Changed from == 0 to < 3
```

### Disabling Free Trial:

To charge for all readings:

```python
# In src/bot/handlers.py, remove the is_first_reading() check:

# BEFORE (with free trial):
if session.is_first_reading():
    session.state = SessionState.AWAITING_QUESTION
    await query.edit_message_text("🎁 Your first reading is FREE!")
else:
    session.state = SessionState.AWAITING_PAYMENT
    await payment_service.send_invoice(...)

# AFTER (no free trial):
session.state = SessionState.AWAITING_PAYMENT
await payment_service.send_invoice(...)
```

## Implementation Details

### Files Modified:

**[src/models/user_session.py](src/models/user_session.py)**
- Added `reading_count: int = 0` field
- Added `is_first_reading() -> bool` method
- Updated `save_reading()` to increment counter
- Updated `to_dict()` and `from_dict()` serialization

**[src/bot/handlers.py](src/bot/handlers.py)**
- Modified `button_callback()` for "Ask a question" action
- Modified `button_callback()` for "Explain my own combination" action
- Added free trial check before payment request
- Added multilingual free trial messages

### State Flow:

**First Reading (Free):**
```
IDLE → Button Click → is_first_reading() == True → AWAITING_QUESTION
```

**Subsequent Readings (Paid):**
```
IDLE → Button Click → is_first_reading() == False → AWAITING_PAYMENT → Payment Success → AWAITING_QUESTION
```

## Analytics Tracking

Track free trial conversion rate:

```python
# Example analytics
total_users = count_users_with_reading_count_gte(0)
converted_users = count_users_with_reading_count_gte(2)
conversion_rate = converted_users / total_users * 100

# Log metrics
logger.info(f"Free trial conversion rate: {conversion_rate:.2f}%")
```

## A/B Testing Ideas

1. **Trial Length**: Test 1 vs 3 vs 5 free readings
2. **Trial Message**: Test different wording ("FREE" vs "On us" vs "No payment")
3. **Payment Timing**: Test immediate payment vs delayed payment prompt
4. **Trial Scope**: Test free automated only vs free both types

## User Messaging

### English:
- "🎁 Your first reading is FREE! Please ask your question:"
- "💫 Enjoying the readings? Subsequent readings cost 20 ⭐"

### Russian:
- "🎁 Ваше первое гадание БЕСПЛАТНО! Задайте свой вопрос:"
- "💫 Понравилось? Следующие гадания стоят 20 ⭐"

### Ukrainian:
- "🎁 Ваше перше ворожіння БЕЗКОШТОВНО! Поставте своє питання:"
- "💫 Сподобалось? Наступні ворожіння коштують 20 ⭐"

## Legal Considerations

Update terms of service to include:
- Free trial is limited to first reading per user
- No credit card required for trial
- Subsequent readings require payment
- Free trial cannot be transferred or combined

## Future Enhancements

1. **Referral Bonus**: Give free reading for each friend referred
2. **Win-back Free Reading**: Offer free reading to inactive users after 30 days
3. **Seasonal Promotions**: Extra free readings during holidays
4. **Achievement Rewards**: Free reading after 10 paid readings
5. **Birthday Bonus**: Free reading on user's birthday

---

**Free trial feature is ACTIVE and ready for deployment!** 🎁✨
