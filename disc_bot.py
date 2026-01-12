"""
Discord Music Bot - Main Entry Point

Initializes the Discord bot, loads cogs/extensions, and handles global events.
Manages bot lifecycle and error handling.

Requirements:
    - DISCORD_TOKEN environment variable must be set
    - Bot must have Message Content Intent and Voice States Intent enabled
    - Required permissions: Connect, Speak, Send Messages, Read Message History
"""

import discord
from discord.ext import commands
import os
import sys
import logging
from pathlib import Path
from typing import Optional


# ============================================================================
# LOGGING SETUP
# ============================================================================

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('disco_bot')


# ============================================================================
# CONFIGURATION
# ============================================================================

# Command prefix for bot commands
COMMAND_PREFIX = '!'

# Bot intents configuration
# Required: message_content (for reading commands), voice_states (for voice)
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Initialize bot
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


# ============================================================================
# BOT EVENTS
# ============================================================================

@bot.event
async def on_ready() -> None:
    """
    Called when the bot successfully connects to Discord.

    Loads all cogs from the cogs directory and prints connection status.
    """
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')
    logger.info(f'Command prefix: {COMMAND_PREFIX}')

    # Load only the main music cog (not helper modules)
    cogs_dir = Path(__file__).parent / 'cogs'
    # Only load music.py as a cog, not the helper modules
    main_cogs = ['music']

    if cogs_dir.exists():
        loaded_count = 0
        failed_count = 0

        for cog_name in main_cogs:
            cog_file = cogs_dir / f'{cog_name}.py'
            if cog_file.exists():
                try:
                    await bot.load_extension(f'cogs.{cog_name}')
                    logger.info(f'Loaded cog: {cog_name}')
                    loaded_count += 1
                except Exception as e:
                    logger.error(f'Failed to load cog {cog_name}: {e}')
                    failed_count += 1

        logger.info(f'Loaded {loaded_count} cog(s), {failed_count} failed')
    else:
        logger.warning(f'Cogs directory not found: {cogs_dir}')


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    """
    Global error handler for all commands.

    Handles common command errors and provides user-friendly messages.
    Ignores command not found errors (user typos).

    Args:
        ctx: Command context
        error: Exception that occurred
    """
    # Ignore command not found errors (user typos)
    if isinstance(error, commands.CommandNotFound):
        return

    # Handle missing required arguments
    if isinstance(error, commands.MissingRequiredArgument):
        param_name = error.param.name
        await ctx.send(
            f'❌ Missing required argument: `{param_name}`\n'
            f'Use `{COMMAND_PREFIX}help {ctx.command}` for usage information.'
        )
        return

    # Handle command cooldowns
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = error.retry_after
        await ctx.send(
            f'⏳ Command is on cooldown. Try again in {retry_after:.1f}s'
        )
        return

    # Handle permission errors
    if isinstance(error, commands.MissingPermissions):
        missing_perms = ', '.join(error.missing_permissions)
        await ctx.send(
            f'❌ You don\'t have permission to use this command.\n'
            f'Missing permissions: {missing_perms}'
        )
        return

    # Handle check failures (e.g., channel restrictions)
    if isinstance(error, commands.CheckFailure):
        # Let cog handle its own check failures
        return

    # Log and notify about other errors
    error_type = type(error).__name__
    logger.error(f'Error in command {ctx.command}: {error_type}: {error}')
    await ctx.send(
        f'❌ An error occurred: {error_type}\n'
        'Please try again or contact an administrator.'
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def get_token() -> Optional[str]:
    """
    Get Discord bot token from environment variable.

    Returns:
        Bot token string or None if not set
    """
    return os.getenv('DISCORD_TOKEN')


def print_setup_instructions() -> None:
    """Print instructions for setting up the Discord token."""
    print('=' * 60)
    print('❌ DISCORD_TOKEN environment variable not set!')
    print('=' * 60)
    print('\n📝 To set your Discord bot token:')
    print('\n  Windows PowerShell:')
    print('    $env:DISCORD_TOKEN="your_token_here"')
    print('\n  Windows Command Prompt:')
    print('    set DISCORD_TOKEN=your_token_here')
    print('\n  Linux/Mac:')
    print('    export DISCORD_TOKEN=your_token_here')
    print('\n📖 For detailed instructions, see DISCORD_TOKEN_SETUP.md')
    print('=' * 60)


def main() -> None:
    """
    Main entry point for the bot.

    Gets token from environment, validates it, and starts the bot.
    Handles common startup errors gracefully.
    """
    # Get token from environment
    token = get_token()

    if not token:
        print_setup_instructions()
        sys.exit(1)

    # Validate token format (basic check)
    if len(token) < 50:  # Discord tokens are typically 59+ characters
        logger.warning(
            'Token seems too short. Discord bot tokens are typically 59+ '
            'characters. Please verify it\'s correct.'
        )

    try:
        logger.info('Starting bot...')
        bot.run(token, log_handler=None)  # We handle logging ourselves
    except discord.LoginFailure:
        print('=' * 60)
        print('❌ Error: Invalid Discord token!')
        print('=' * 60)
        print('\n📝 Make sure:')
        print('  • You copied the BOT token (not user token)')
        print('  • Token is from Discord Developer Portal > Bot section')
        print('  • Token hasn\'t been regenerated')
        print('\n📖 See DISCORD_TOKEN_SETUP.md for help')
        print('=' * 60)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info('Bot stopped by user')
        sys.exit(0)
    except Exception as e:
        error_type = type(e).__name__
        print('=' * 60)
        print(f'❌ Error starting bot: {error_type}: {e}')
        print('=' * 60)
        print('\n📝 Common issues:')
        print('  • Check internet connection')
        print('  • Verify bot token is correct')
        print('  • Ensure intents are enabled in Developer Portal')
        print('  • Check firewall/antivirus settings')
        sys.exit(1)


if __name__ == '__main__':
    main()
