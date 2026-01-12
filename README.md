# Discord Music Bot

A Discord bot that plays YouTube videos in voice channels with advanced features including per-guild state management, rate limiting, and security improvements.

## Features

- Play YouTube videos in Discord voice channels
- Queue system for multiple songs
- Play, pause, resume, skip, and stop controls
- Remove songs from queue by position
- Vote to skip system (requires majority vote when multiple users)
- Auto-disconnect when alone in voice channel
- Auto-disconnect after 15 minutes of inactivity
- Volume control (0-100%)
- Search YouTube directly from Discord
- Queue display with embeds
- Rate limiting to prevent spam
- Input sanitization for security
- Multi-server support (each server has its own queue)
- Proper logging for debugging
- SSL certificate verification enabled

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- A Discord bot token

### Installing FFmpeg

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract and add to your system PATH

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Setup

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Get a Discord Bot Token:**
   - See [DISCORD_TOKEN_SETUP.md](DISCORD_TOKEN_SETUP.md) for detailed instructions
   - Quick version: Go to https://discord.com/developers/applications
   - Create a new application → Bot section → Add Bot → Copy token
   - **IMPORTANT**: Enable "Message Content Intent" and "Server Members Intent" in the Bot section

4. **Set the Discord token as an environment variable:**

   **Windows (PowerShell):**
   ```powershell
   $env:DISCORD_TOKEN="your_token_here"
   ```

   **Windows (Command Prompt):**
   ```cmd
   set DISCORD_TOKEN=your_token_here
   ```

   **Linux/macOS:**
   ```bash
   export DISCORD_TOKEN=your_token_here
   ```

   **Note**: You need to set this every time you open a new terminal. For permanent setup, see DISCORD_TOKEN_SETUP.md

5. **Invite the bot to your server:**
   - In Discord Developer Portal, go to OAuth2 > URL Generator
   - Select scopes: `bot`
   - Select bot permissions:
     - `Connect` (join voice channels)
     - `Speak` (play audio)
     - `Send Messages` (respond to commands)
     - `Read Message History` (read commands)
     - `Embed Links` (for queue display)
     - `Use Voice Activity` (optional)
   - Copy the generated URL and open it in your browser
   
   **To share with others:** See [INVITE_BOT_GUIDE.md](INVITE_BOT_GUIDE.md) for instructions on creating and sharing invite links.

## Running the Bot

Navigate to the `disco_bot` directory and run:

```bash
cd disco_bot
python disc_bot.py
```

You should see:
```
BotName#1234 has connected to Discord!
Bot is in 1 guild(s)
Command prefix: !
Loaded cog: music
Loaded 1 cog(s), 0 failed
```

## Commands

**All commands must be used in a channel containing "music" in its name** (e.g., "music", "music-bot"). Admins can change this with `!setchannel`.

| Command | Aliases | Description | Rate Limit |
|---------|---------|-------------|------------|
| `!join` | `!connect` | Join your voice channel | 2 per 5s |
| `!switch` | `!move`, `!change` | Switch to your voice channel | 2 per 5s |
| `!leave` | `!disconnect`, `!dc` | Leave the voice channel | 2 per 5s |
| `!play <query>` | `!p` | Play a YouTube video or search | 2 per 5s |
| `!pause` | | Pause the current song | 2 per 5s |
| `!resume` | | Resume the paused song | 2 per 5s |
| `!stop` | | Stop and clear the queue | 2 per 5s |
| `!skip` | `!next`, `!s` | Skip to the next song (voting if multiple users) | 2 per 5s |
| `!queue` | `!q` | Show the current queue | 2 per 5s |
| `!remove <position>` | | Remove a song from queue by position | 2 per 5s |
| `!clear` | | Clear the queue | 2 per 5s |
| `!volume [0-100]` | `!vol` | Set or display volume | 2 per 5s |
| `!setchannel <name>` | `!channel` | Change allowed channel (Admin only) | 1 per 10s |

## Usage Examples

### Basic Playback

```
!join                    # Join voice channel
!play never gonna give you up  # Search and play
!play https://youtube.com/watch?v=dQw4w9WgXcQ  # Play from URL
!pause                   # Pause playback
!resume                  # Resume playback
!volume 75              # Set volume to 75%
!volume                 # Check current volume
```

### Queue Management

```
!play song 1            # Add first song
!play song 2            # Add second song to queue
!queue                  # Show queue
!remove 2               # Remove song at position 2
!skip                   # Skip current song
!clear                  # Clear entire queue
```

### Voice Channel Management

```
!join                   # Join user's voice channel
!switch                 # Move bot to your voice channel
!leave                  # Disconnect from voice channel
```

### Admin Commands

```
!setchannel general     # Change allowed channel to "general" (Admin only)
```

## Important Notes

### Channel Restrictions
- **All music commands only work in channels containing "music" in the name**
- Examples: "music", "music-bot", "general-music"
- Admins can change this with `!setchannel <channel_name>`
- The `!setchannel` command can be used from any channel

### Rate Limiting
- Commands are rate-limited to **2 uses per 5 seconds per user**
- This prevents spam and abuse
- You'll see a cooldown message if you use commands too quickly

### Multi-Server Support
- **Each Discord server has its own queue and settings**
- The bot can be in multiple servers simultaneously
- Each server's queue is independent

### Auto-Disconnect
- Bot disconnects if **alone in voice channel** for 1 minute (when not playing)
- Bot disconnects after **15 minutes of inactivity** (no commands used)
- Bot stays connected while playing music

### Vote-to-Skip
- If only 1 person in channel: Skip immediately
- If multiple people: Requires majority vote
- Admins can always skip immediately
- Votes reset when a new song starts

## Project Structure

```
disco_bot/
├── disc_bot.py              # Main bot file
├── cogs/
│   ├── __init__.py
│   ├── config.py            # Configuration and constants
│   ├── audio_source.py      # Audio source handling
│   ├── music_helpers.py     # Helper functions and decorators
│   ├── background_tasks.py  # Auto-disconnect tasks
│   ├── song_extractor.py    # YouTube extraction
│   ├── guild_state.py       # Per-guild state management
│   └── music.py             # Main music cog
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── DISCORD_TOKEN_SETUP.md    # Token setup guide
```

## Troubleshooting

### Bot doesn't join voice channel
- Make sure you're in a voice channel
- Check bot has "Connect" and "Speak" permissions
- Verify you're using commands in the correct channel (must contain "music")

### Audio doesn't play
- Verify FFmpeg is installed and in PATH: `ffmpeg -version`
- Check bot has "Connect" and "Speak" permissions
- Try a different voice channel
- Check Windows Firewall settings

### "Command not found" errors
- Make sure the cogs loaded successfully (check console output)
- Verify command prefix is `!`
- Check you're in a channel with "music" in the name

### Rate limit errors
- Wait a few seconds between commands
- Rate limit is 2 commands per 5 seconds per user

### Bot disconnects unexpectedly
- Bot auto-disconnects when alone (if not playing)
- Bot auto-disconnects after 15 minutes of inactivity
- This is normal behavior to save resources

### Token setup issues
- See [DISCORD_TOKEN_SETUP.md](DISCORD_TOKEN_SETUP.md) for detailed token setup guide
- Make sure you copied the **BOT token**, not a user token
- Verify intents are enabled in Developer Portal

### SSL Certificate Errors
- If you get SSL errors, you can temporarily disable verification in `config.py`
- Change `'nocheckcertificate': False` to `True` (not recommended for security)

## Security Features

- SSL certificate verification enabled
- Input sanitization (prevents Discord markdown injection)
- Rate limiting on all commands
- Per-guild state isolation
- Proper error handling and logging

## Security

**IMPORTANT**: This is a public repository. Never commit your Discord bot token or any secrets.

- **Never commit** your `DISCORD_TOKEN` to Git
- **Always use** environment variables for sensitive data
- **Reset your token** immediately if accidentally exposed
- See [SECURITY.md](SECURITY.md) for detailed security guidelines and best practices

### Quick Security Checklist

Before pushing to GitHub:
- [ ] No `.env` files committed (they're in `.gitignore`)
- [ ] No hardcoded tokens in code
- [ ] No secrets in configuration files
- [ ] All sensitive data uses environment variables

## License

See LICENSE file for details.
