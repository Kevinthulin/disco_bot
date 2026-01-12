# Free Hosting Guide for Discord Music Bot

This guide covers free hosting options for your Discord bot to run 24/7.

## Recommended Options

### 1. **Railway** (Recommended)
- **Free tier**: $5 credit/month (usually enough for a bot)
- **Pros**: Easy setup, good performance, automatic deployments
- **Cons**: Requires credit card (won't charge if under limit)

### 2. **Render**
- **Free tier**: 750 hours/month (enough for 24/7)
- **Pros**: No credit card needed, easy setup
- **Cons**: Spins down after 15 min inactivity (free tier)

### 3. **Fly.io**
- **Free tier**: 3 shared VMs, 3GB storage
- **Pros**: Good performance, no credit card needed
- **Cons**: More complex setup

---

## Option 1: Railway (Recommended)

### Setup Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your `disco_bot` repository

3. **Configure Environment Variables**
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add: `DISCORD_TOKEN` = `your_bot_token_here`

4. **FFmpeg Installation**
   - The project includes `nixpacks.toml` which automatically installs FFmpeg
   - Railway will install FFmpeg during the build process
   - No manual configuration needed

5. **Set Start Command** (if needed)
   - Go to "Settings" → "Deploy"
   - Start command should be: `python disc_bot.py`
   - Root directory: `disco_bot` (if deploying from repo root)
   - **Note**: `nixpacks.toml` already specifies this, so Railway should auto-detect it

6. **Deploy**
   - Railway will automatically detect Python, install FFmpeg, and install dependencies from `requirements.txt`
   - Check logs to see if bot connects successfully
   - **Note**: Railway uses `requirements.txt` for dependencies (not Pipfile)

**Note**: Railway may require a credit card but won't charge if you stay under the free tier limit.

---

## Option 2: Render

### Setup Steps:

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select your repository

3. **Configure Service**
   - **Name**: `discord-music-bot` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r disco_bot/requirements.txt`
   - **Start Command**: `python disco_bot/disc_bot.py`
   - **Root Directory**: `disco_bot` (if needed)
   - **Note**: Render uses `requirements.txt` for dependencies (not Pipfile)

4. **Add Environment Variable**
   - Scroll to "Environment Variables"
   - Add: `DISCORD_TOKEN` = `your_bot_token_here`

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your bot
   - Check logs to verify it's running

**Note**: Free tier spins down after 15 minutes of inactivity. For 24/7, consider upgrading or use Railway.

---

## Option 3: Fly.io

### Setup Steps:

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create Account**
   ```bash
   fly auth signup
   ```

3. **Initialize Fly App**
   ```bash
   cd disco_bot
   fly launch
   ```
   - Follow prompts
   - Don't deploy yet (we need to configure first)

4. **Create `fly.toml`** (see below)

5. **Set Secrets**
   ```bash
   fly secrets set DISCORD_TOKEN=your_bot_token_here
   ```

6. **Deploy**
   ```bash
   fly deploy
   ```

---

## Required Files for Hosting

### `Procfile` (for Heroku/Railway compatibility)
```
worker: python disc_bot.py
```

**Note**: Hosting platforms typically use `requirements.txt` for dependencies. The `Pipfile` is for local development with pipenv.

### `runtime.txt` (optional, specify Python version)
```
python-3.11.0
```

### `fly.toml` (for Fly.io)
```toml
app = "your-app-name"
primary_region = "iad"

[build]

[env]
  DISCORD_TOKEN = ""

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

  [[services.tcp_checks]]
    interval = "15s"
    timeout = "2s"
    grace_period = "1s"
```

---

## Quick Setup Checklist

Before deploying, make sure:

- Bot token is ready (from Discord Developer Portal)
- `requirements.txt` is up to date
- Bot has proper permissions in your Discord server
- Intents are enabled (Message Content, Voice States)
- FFmpeg is available (most hosts have it pre-installed)

---

## Troubleshooting

### Bot doesn't start
- Check logs in hosting dashboard
- Verify `DISCORD_TOKEN` environment variable is set
- Ensure start command is correct

### Bot disconnects frequently
- Free tiers may have resource limits
- Check if host spins down after inactivity
- Consider upgrading to paid tier for 24/7

### Audio doesn't work
- Verify FFmpeg is installed on host
- Some hosts require installing FFmpeg manually
- Check host documentation for FFmpeg setup

### Import errors
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility
- Review host logs for specific errors

---

## Tips

1. **Keep bot token secret** - Never commit it to GitHub
2. **Monitor logs** - Check hosting dashboard regularly
3. **Set up alerts** - Some hosts offer email notifications
4. **Backup your code** - Keep your code in GitHub
5. **Test locally first** - Make sure everything works before deploying

---

## Additional Resources

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Fly.io Docs: https://fly.io/docs
- Discord.py Docs: https://discordpy.readthedocs.io

---

## After Deployment

Once deployed:
1. Check logs to confirm bot connected
2. Test commands in your Discord server
3. Monitor for any errors
4. Enjoy your 24/7 music bot!

