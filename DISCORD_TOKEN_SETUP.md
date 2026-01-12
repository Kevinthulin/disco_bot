# Discord Bot Token Setup Guide

## Where to Find Your Discord Bot Token

### Step 1: Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** in the top right
3. Give it a name (e.g., "My Music Bot")
4. Click **"Create"**

### Step 2: Create a Bot

1. In your application, go to the **"Bot"** section in the left sidebar
2. Click **"Add Bot"** or **"Reset Token"** if you already have one
3. Click **"Yes, do it!"** to confirm
4. **IMPORTANT**: Click **"Reset Token"** and then **"Copy"** to get your token
   - **Keep this token secret!** Never share it publicly or commit it to GitHub
   - If you lose it, you can reset it, but the old token will stop working

### Step 3: Enable Required Bot Permissions

1. Still in the **"Bot"** section, scroll down to **"Privileged Gateway Intents"**
2. Enable:
   - **Message Content Intent** (required for commands)
   - **Server Members Intent** (optional, but recommended)

3. Scroll down to **"Bot Permissions"** and enable:
   - **Connect** (join voice channels)
   - **Speak** (play audio)
   - **Use Voice Activity** (optional, for voice activity detection)

### Step 4: Invite Bot to Your Server

1. Go to the **"OAuth2"** section → **"URL Generator"**
2. Under **"Scopes"**, select:
   - **bot**
   - **applications.commands** (optional, for slash commands)
3. Under **"Bot Permissions"**, select:
   - **Connect**
   - **Speak**
   - **Use Voice Activity**
4. Copy the generated URL at the bottom
5. Open the URL in your browser
6. Select your Discord server and click **"Authorize"**
7. Complete any CAPTCHA if prompted

---

## How to Set Your Discord Token

### Option 1: Environment Variable (Recommended)

#### Windows PowerShell:
```powershell
$env:DISCORD_TOKEN="YOUR_TOKEN_HERE"
python disc_bot.py
```

#### Windows Command Prompt:
```cmdsw
set DISCORD_TOKEN=YOUR_TOKEN_HERE
python disc_bot.py
```

#### Linux/macOS:
```bash
export DISCORD_TOKEN="YOUR_TOKEN_HERE"
python disc_bot.py
```

**Note**: This only lasts for the current terminal session. Close the terminal and you'll need to set it again.

### Option 2: Permanent Environment Variable (Windows)

1. Press `Win + X` and select **"System"**
2. Click **"Advanced system settings"**
3. Click **"Environment Variables"**
4. Under **"User variables"**, click **"New"**
5. Variable name: `DISCORD_TOKEN`
6. Variable value: `YOUR_TOKEN_HERE`
7. Click **"OK"** on all windows
8. Restart your terminal/IDE

### Option 3: Using .env File (Alternative)

1. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

2. Create a `.env` file in the `disco_bot` directory:
   ```
   DISCORD_TOKEN=YOUR_TOKEN_HERE
   ```

3. Update `disc_bot.py` to load from .env:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

4. Add `.env` to `.gitignore` to keep your token safe:
   ```
   .env
   ```

---

## Security Best Practices

1. **Never commit your token to Git**
   - Add `.env` to `.gitignore` if using that method
   - Never paste your token in code files

2. **Reset your token if exposed**
   - Go to Discord Developer Portal → Bot → Reset Token
   - Update it everywhere you use it

3. **Use environment variables**
   - More secure than hardcoding
   - Easy to change without editing code

4. **Don't share your token**
   - Anyone with your token can control your bot
   - Treat it like a password

---

## Troubleshooting

### "Invalid Discord token!"
- Double-check you copied the entire token (it's long!)
- Make sure there are no extra spaces
- Try resetting the token and using the new one

### "Missing required argument: DISCORD_TOKEN"
- Make sure you set the environment variable before running
- Check spelling: `DISCORD_TOKEN` (all caps, underscore)
- Restart your terminal after setting environment variables

### Bot doesn't respond to commands
- Make sure the bot is online (green dot in Discord)
- Check that "Message Content Intent" is enabled in Developer Portal
- Verify the bot has permission to read messages in your server

### Bot can't join voice channel
- Make sure the bot has "Connect" and "Speak" permissions
- Check that you're in a voice channel when using `!join`
- Verify FFmpeg is installed correctly

---

## Quick Start Checklist

- [ ] Created Discord application
- [ ] Created bot and copied token
- [ ] Enabled Message Content Intent
- [ ] Enabled Connect and Speak permissions
- [ ] Invited bot to server
- [ ] Set DISCORD_TOKEN environment variable
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Installed FFmpeg
- [ ] Ran the bot (`python disc_bot.py`)

---

## Need Help?

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)
- [Discord.py Support Server](https://discord.gg/dpy)

