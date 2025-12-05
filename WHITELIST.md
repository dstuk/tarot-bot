# Payment Whitelist Feature

## Overview

The **Payment Whitelist** allows you to grant **unlimited free readings** to specific users without requiring payment. This is useful for:

- **Testing**: Your own account for testing the bot
- **VIP users**: Special users who get lifetime free access
- **Admins/Mods**: Team members who help manage the bot
- **Beta testers**: Users who help test new features
- **Friends/Family**: People you want to give free access to

## How It Works

Whitelisted users **bypass all payment checks** and **never see payment prompts**. The priority order is:

1. **Whitelisted users** → Always free (highest priority)
2. **First-time users** → Free trial (1 reading)
3. **Regular users** → Payment required (20 Telegram Stars)

### User Experience:

**Whitelisted User:**
```
User clicks "Ask a question"
↓
Bot: "✨ VIP access - Free reading! Please ask your question:"
↓
User enters question
↓
Bot generates reading (no payment)
```

**Regular User (after free trial):**
```
User clicks "Ask a question"
↓
Bot: Sends payment invoice for 20 ⭐
↓
User pays
↓
User enters question
↓
Bot generates reading
```

## Configuration

### Method 1: Environment Variable (Recommended)

Add the `PAYMENT_WHITELIST` variable to your `.env` file with comma-separated Telegram user IDs:

```env
# .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
ANTHROPIC_API_KEY=your_api_key_here

# Payment whitelist: comma-separated user IDs
PAYMENT_WHITELIST=123456789,987654321,555555555
```

**Multiple users:**
```env
PAYMENT_WHITELIST=123456789,987654321,555555555,111222333
```

**Single user:**
```env
PAYMENT_WHITELIST=123456789
```

**No whitelist (everyone pays after free trial):**
```env
# Just omit PAYMENT_WHITELIST or leave it empty
PAYMENT_WHITELIST=
```

### Method 2: Railway/Deployment Platform

If deploying to Railway, Heroku, or similar:

1. Go to your project settings
2. Add environment variable:
   - **Key**: `PAYMENT_WHITELIST`
   - **Value**: `123456789,987654321` (your user IDs)
3. Redeploy the bot

## Finding Your Telegram User ID

### Method 1: Using @userinfobot

1. Open Telegram
2. Search for `@userinfobot`
3. Start the bot
4. It will reply with your user ID:
   ```
   Id: 123456789
   First: John
   Username: @john_doe
   ```

### Method 2: Using Bot Logs

1. Start your bot
2. Send `/start` to your bot
3. Check the bot logs - it will show:
   ```
   User 123456789 started bot session
   ```

### Method 3: Using @RawDataBot

1. Search for `@RawDataBot` in Telegram
2. Forward any message from the user to @RawDataBot
3. It shows complete user info including ID

## Examples

### Example 1: Whitelist Yourself for Testing

```env
# Your Telegram user ID
PAYMENT_WHITELIST=123456789
```

Now when you use the bot:
```
You: /start
Bot: [Welcome message with buttons]

You: [Click "Ask a question"]
Bot: ✨ VIP access - Free reading! Please ask your question:

You: Will I succeed in my project?
Bot: [Generates reading - no payment required]
```

### Example 2: Whitelist Team Members

```env
# You + 2 team members
PAYMENT_WHITELIST=123456789,987654321,555111222
```

All three users get unlimited free readings.

### Example 3: Production with Beta Testers

```env
# Production bot
ENVIRONMENT=production
PAYMENT_WHITELIST=123456789,987654321

# Regular users pay, but these 2 users are free
```

### Example 4: No Whitelist (Everyone Pays)

```env
# Don't set PAYMENT_WHITELIST at all
# Or set it to empty
PAYMENT_WHITELIST=
```

All users get:
- 1st reading: FREE (trial)
- 2nd+ readings: 20 Telegram Stars

## Managing the Whitelist

### Adding Users:

1. Get their Telegram user ID (using methods above)
2. Add to the comma-separated list:
   ```env
   # Before
   PAYMENT_WHITELIST=123456789

   # After adding user 999888777
   PAYMENT_WHITELIST=123456789,999888777
   ```
3. Restart the bot (or redeploy if on cloud)

### Removing Users:

1. Remove their ID from the list:
   ```env
   # Before
   PAYMENT_WHITELIST=123456789,999888777,555111222

   # After removing 999888777
   PAYMENT_WHITELIST=123456789,555111222
   ```
2. Restart the bot

**Note**: Removed users will need to pay starting from their **next reading**. Their current session is not affected.

### Checking Who's Whitelisted:

Add this to your admin commands (optional):

```python
# In handlers.py
async def list_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all whitelisted users (admin only)."""
    user_id = update.effective_user.id

    # Check if requester is admin
    if not config.is_whitelisted(user_id):
        await update.message.reply_text("❌ Admin access required")
        return

    if not config.payment_whitelist:
        await update.message.reply_text("📋 Whitelist is empty")
        return

    whitelist_str = "\n".join([f"• {uid}" for uid in config.payment_whitelist])
    await update.message.reply_text(f"📋 Whitelisted Users:\n\n{whitelist_str}")
```

## Security Considerations

### ✅ Best Practices:

1. **Keep IDs private**: Don't share your whitelist publicly
2. **Regular review**: Periodically review and remove inactive users
3. **Limit size**: Don't whitelist too many users (affects revenue)
4. **Use for testing**: Whitelist yourself and close team only

### ⚠️ Warnings:

- **Don't whitelist unknown users**: Only add trusted people
- **Monitor usage**: Check logs to ensure no abuse
- **Revenue impact**: Each whitelisted user = lost revenue

## Logs and Monitoring

Whitelisted users are logged differently:

```python
# Regular user (paying)
INFO: User 123456789 initiated automated reading - payment requested

# Whitelisted user (free)
INFO: User 987654321 initiated automated reading - WHITELISTED user (free)

# First-time user (free trial)
INFO: User 555111222 initiated automated reading - FREE first reading
```

Search logs for `WHITELISTED` to track VIP usage:

```bash
# View whitelisted user activity
grep "WHITELISTED" tarot_bot.log

# Count readings by whitelisted users
grep "WHITELISTED" tarot_bot.log | wc -l
```

## Troubleshooting

### Issue: Whitelisted user still sees payment prompt

**Causes:**
1. User ID is incorrect
2. Whitelist has typo or extra spaces
3. Bot wasn't restarted after adding to whitelist

**Solutions:**
1. Verify user ID using `@userinfobot`
2. Check `.env` format: `PAYMENT_WHITELIST=123456789,987654321` (no spaces)
3. Restart bot: `python src/main.py`

### Issue: Warning message about invalid whitelist format

```
Warning: Invalid PAYMENT_WHITELIST format: 123abc,456def
```

**Cause**: Non-numeric characters in user IDs

**Solution**: Use only numbers, separated by commas:
```env
# Wrong
PAYMENT_WHITELIST=@john_doe,@jane_doe

# Correct
PAYMENT_WHITELIST=123456789,987654321
```

### Issue: Removed user still gets free readings

**Cause**: Bot uses cached config, hasn't restarted

**Solution**: Restart the bot to reload config

## Implementation Details

### Files Modified:

**[src/config.py](src/config.py)**
- Added `payment_whitelist: list[int]` field
- Added `is_whitelisted(user_id)` method
- Parses `PAYMENT_WHITELIST` env var on startup

**[src/bot/handlers.py](src/bot/handlers.py)**
- Import `config`
- Check `config.is_whitelisted(user_id)` before payment
- Show VIP message for whitelisted users
- Log whitelisted user activity

### Code Flow:

```python
# In button_callback handler
if config.is_whitelisted(user_id):
    # VIP: Always free
    proceed_to_question()
elif session.is_first_reading():
    # Free trial: First reading free
    proceed_to_question()
else:
    # Regular: Require payment
    request_payment()
```

## Advanced Usage

### Dynamic Whitelist (Database)

For advanced use cases, store whitelist in database instead of env var:

```python
# Example: Store in Redis/PostgreSQL
class Config:
    def is_whitelisted(self, user_id: int) -> bool:
        # Check database instead of env var
        return db.check_vip_status(user_id)

# Allow users to purchase VIP status
async def purchase_vip(user_id: int):
    db.add_to_whitelist(user_id)
```

### Temporary Whitelist

Grant temporary VIP access:

```python
# Add expiry date
VIP_EXPIRY = {
    123456789: datetime(2025, 12, 31),  # Expires Dec 31, 2025
}

def is_whitelisted(user_id: int) -> bool:
    if user_id in VIP_EXPIRY:
        if datetime.now() < VIP_EXPIRY[user_id]:
            return True
    return user_id in config.payment_whitelist
```

### Referral-Based Whitelist

Reward users who refer friends:

```python
# User gets VIP after referring 5 friends
async def check_referrals(user_id: int):
    referral_count = db.get_referral_count(user_id)
    if referral_count >= 5:
        db.add_to_whitelist(user_id)
```

## Summary

The payment whitelist provides a simple way to:
- ✅ Give yourself unlimited free readings for testing
- ✅ Reward VIP users with free access
- ✅ Provide free access to team members
- ✅ Run beta testing without payment friction

**Just add user IDs to `PAYMENT_WHITELIST` environment variable!**

---

**Whitelist feature is ACTIVE and ready to use!** ✨
