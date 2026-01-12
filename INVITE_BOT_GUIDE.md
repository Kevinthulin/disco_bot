# How to Share Your Bot with Others

This guide explains how to let other people add your Discord bot to their servers.

## Quick Method: Share Invite Link

### Step 1: Generate Bot Invite Link

1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Select Your Bot Application**
   - Click on your bot application

3. **Go to OAuth2 → URL Generator**
   - Click "OAuth2" in the left sidebar
   - Click "URL Generator" submenu

4. **Select Scopes**
   - Check `bot`
   - Check `applications.commands` (optional, for slash commands)

5. **Select Bot Permissions**
   Check the following permissions:
   - **Connect** (join voice channels)
   - **Speak** (play audio)
   - **Use Voice Activity** (optional)
   - **Send Messages** (respond to commands)
   - **Read Message History** (read commands)
   - **Embed Links** (for queue embeds)
   - **Attach Files** (optional)

6. **Copy the Generated URL**
   - Scroll down to see the generated URL
   - Copy it (looks like: `https://discord.com/api/oauth2/authorize?client_id=...`)

### Step 2: Share the Link

**Option A: Direct Share**
- Send the invite link to the person via Discord, email, or any messaging app
- They click the link and select their server

**Option B: Create a Simple Website**
- Create a free GitHub Pages site with just the invite link
- Or use a simple HTML page

**Option C: Add to README**
- Add the invite link to your bot's README.md
- People can click it directly from GitHub

---

## What the Other Person Needs to Do

1. **Click the Invite Link**
   - They'll be redirected to Discord

2. **Select Their Server**
   - Choose which server to add the bot to
   - They must have "Manage Server" permission

3. **Authorize Permissions**
   - Review the permissions
   - Click "Authorize"

4. **Bot Joins Server**
   - Bot will appear in their server's member list
   - Bot will be offline until it's running

---

## Two Scenarios

### Scenario 1: You Host the Bot (Recommended)

**You:**
- Host the bot on Railway/Render/etc.
- Bot runs 24/7 on your account
- You pay for hosting (or use free tier)

**Other Person:**
- Just adds bot via invite link
- Uses bot in their server
- No setup needed

**Pros:**
- Easy for them
- You control updates
- One bot instance serves all servers

**Cons:**
- You pay hosting costs
- You maintain it

---

### Scenario 2: They Host the Bot Themselves

**You:**
- Share the code (GitHub repo)
- Share hosting instructions
- They get their own bot token

**Other Person:**
- Gets bot token from Discord Developer Portal
- Sets up hosting
- Runs their own instance

**Pros:**
- They control their instance
- No cost to you
- They can customize it

**Cons:**
- More complex for them
- They need to maintain it
- Each server needs separate hosting

---

## Creating a Permanent Invite Link

### Method 1: Using OAuth2 URL Generator (Easiest)

1. Follow steps above to generate URL
2. The URL is permanent (as long as your bot exists)
3. Share this URL with anyone

**Example URL:**
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=36703232&scope=bot
```

### Method 2: Create a Simple HTML Page

Create `invite.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Add Music Bot to Your Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #2C2F33;
            color: white;
        }
        .button {
            display: inline-block;
            padding: 15px 30px;
            background: #5865F2;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 18px;
            margin-top: 20px;
        }
        .button:hover {
            background: #4752C4;
        }
    </style>
</head>
<body>
    <h1>Discord Music Bot</h1>
    <p>Add the bot to your server and enjoy music!</p>
    <a href="YOUR_INVITE_URL_HERE" class="button">Add Bot to Server</a>
</body>
</html>
```

---

## What Permissions Mean

| Permission | Why Needed |
|------------|------------|
| **Connect** | Bot needs to join voice channels |
| **Speak** | Bot needs to play audio |
| **Send Messages** | Bot needs to respond to commands |
| **Read Message History** | Bot needs to read commands |
| **Embed Links** | Bot uses embeds for queue display |
| **Use Voice Activity** | Optional, for better voice quality |

---

## Security Considerations

### If You Host the Bot:

1. **Keep Token Secret**
   - Never share your bot token
   - Only share the invite link

2. **Monitor Usage**
   - Check logs regularly
   - Watch for abuse

3. **Set Rate Limits**
   - Already implemented in the bot
   - Prevents spam

### If They Host the Bot:

1. **Share Code, Not Token**
   - They need to create their own bot
   - They get their own token

2. **Provide Clear Instructions**
   - Share `HOSTING_GUIDE.md`
   - Help them set up

---

## Quick Share Template

Copy this and fill in your invite URL:

```
Discord Music Bot Invite

Add the bot to your server:
[INVITE_LINK_HERE]

Features:
• Play YouTube videos
• Queue system
• Vote to skip
• Volume control
• Auto-disconnect when alone

Required Permissions:
• Connect to voice channels
• Speak in voice channels
• Send messages
• Read message history

Enjoy!
```

---

## Troubleshooting

### "Bot doesn't appear in server"
- Make sure bot is online (hosting is running)
- Check bot has correct permissions
- Verify invite link is correct

### "Bot can't join voice channel"
- Check bot has "Connect" and "Speak" permissions
- Verify voice channel permissions
- Make sure bot is online

### "Commands don't work"
- Bot must be in a channel with "music" in the name
- Check bot has "Send Messages" permission
- Verify intents are enabled in Developer Portal

---

## Additional Resources

- Discord Developer Portal: https://discord.com/developers/applications
- Discord Permissions Calculator: https://discordapi.com/permissions.html
- Bot Invite Generator: https://discord.com/developers/docs/topics/oauth2

