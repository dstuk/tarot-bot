# Deployment Guide - Railway.app

This guide will help you deploy the Telegram Tarot Bot to Railway.app.

## Prerequisites

1. A [Railway.app](https://railway.app/) account (free tier available)
2. Your Telegram Bot Token from [@BotFather](https://t.me/botfather)
3. Your Anthropic API Key from [Anthropic Console](https://console.anthropic.com/)
4. Git repository with your code

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure these files exist in your repository:
- ✅ `Procfile` - Tells Railway how to start the bot
- ✅ `runtime.txt` - Specifies Python version
- ✅ `requirements.txt` - Lists all dependencies
- ✅ `.gitignore` - Excludes sensitive files

### 2. Push to GitHub (if not already done)

```bash
git init
git add .
git commit -m "Initial commit - Telegram Tarot Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3. Deploy to Railway

#### Option A: Via Railway Dashboard (Recommended)

1. Go to [Railway.app](https://railway.app/) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your Tarot bot repository
5. Railway will automatically detect it's a Python project

#### Option B: Via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 4. Configure Environment Variables

In your Railway project dashboard:

1. Go to your project
2. Click on the **"Variables"** tab
3. Add the following environment variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Optional Variables:**

```env
# Redis for persistent session storage
REDIS_URL=redis://your_redis_host:6379/0

# Payment whitelist for VIP/admin users (comma-separated user IDs)
PAYMENT_WHITELIST=123456789,987654321
```

**Note**: To find your Telegram user ID, message `@userinfobot` on Telegram. See [WHITELIST.md](WHITELIST.md) for details.

### 5. Add Redis (Optional but Recommended)

For persistent session storage:

1. In Railway dashboard, click **"New"** → **"Database"** → **"Add Redis"**
2. Railway will automatically create a `REDIS_URL` variable
3. Your bot will automatically use it (no code changes needed!)

### 6. Deploy and Monitor

#### Check Deployment Status
- Railway will automatically build and deploy
- Watch the build logs in the Railway dashboard
- Once deployed, check the **"Deployments"** tab

#### View Logs
```bash
# Via Railway CLI
railway logs

# Or view in dashboard under "Deployments" → Click on deployment → "View Logs"
```

#### Test Your Bot
1. Open Telegram
2. Find your bot (@your_bot_username)
3. Send `/start`
4. You should see the welcome message with buttons!

## Troubleshooting

### Bot doesn't respond
**Check:**
1. Logs in Railway dashboard - look for errors
2. Environment variables are set correctly
3. Bot token is valid (test with `https://api.telegram.org/bot<TOKEN>/getMe`)

### "No AI service configured" warning
**Fix:** Make sure `ANTHROPIC_API_KEY` is set in Railway variables

### Build fails
**Check:**
1. `requirements.txt` includes all dependencies
2. Python version in `runtime.txt` is supported (3.11.x)
3. No syntax errors in code

### Redis connection issues
**Solutions:**
- Use Railway's built-in Redis (recommended)
- Or set `REDIS_URL` to empty to use in-memory storage (sessions lost on restart)

## Cost Considerations

### Free Tier Limits (as of 2024)
- **$5 of usage per month** (includes compute + database)
- Bot runs 24/7
- Typically enough for:
  - ~500 active users
  - ~1000 readings per day
  - Redis storage

### Scaling Up
If you exceed free tier:
- Upgrade to **Hobby plan** ($5/month base + usage)
- Or optimize:
  - Use in-memory sessions (no Redis)
  - Implement reading limits per user

## Maintenance

### Update Bot Code
```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push

# Railway auto-deploys on push!
```

### Monitor Usage
- Check Railway dashboard for usage metrics
- Monitor logs for errors
- Track user activity in bot logs

### Restart Bot
```bash
# Via Railway CLI
railway run python -m src.main

# Or in dashboard: Deployments → Click deployment → "Restart"
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | - | Bot token from @BotFather |
| `ANTHROPIC_API_KEY` | ✅ Yes | - | Anthropic API key for AI |
| `REDIS_URL` | ⚠️ Optional | - | Redis connection URL |
| `PAYMENT_WHITELIST` | ⚠️ Optional | - | Comma-separated user IDs for free access |
| `ENVIRONMENT` | ⚠️ Optional | `development` | Set to `production` |
| `LOG_LEVEL` | ⚠️ Optional | `INFO` | Logging level |

## Security Best Practices

1. ✅ **Never commit** `.env` files to Git
2. ✅ **Always use** Railway's environment variables
3. ✅ **Rotate keys** if accidentally exposed
4. ✅ **Monitor logs** for suspicious activity
5. ✅ **Enable rate limiting** (already implemented)

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## Support

If you encounter issues:
1. Check Railway logs first
2. Review this guide
3. Check [Railway Community](https://discord.gg/railway)
4. Open an issue on GitHub

---

**Your bot should now be live and running 24/7 on Railway! 🎉**
