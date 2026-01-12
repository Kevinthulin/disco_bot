"""
Background tasks for the Music cog.

Handles auto-disconnect functionality when bot is alone or inactive.
"""

import discord
import asyncio
import time

from .config import (
    ALONE_CHECK_INTERVAL,
    INACTIVITY_CHECK_INTERVAL,
    INACTIVITY_TIMEOUT,
    logger
)


async def check_alone(
    get_voice_client,
    get_state,
    cleanup_callback
) -> None:
    """
    Background task to check if bot is alone and auto-disconnect.

    Checks every ALONE_CHECK_INTERVAL seconds. If bot is alone and
    not playing/paused, disconnects after 1 minute.

    Args:
        get_voice_client: Function that returns current voice client
        get_state: Function that returns (is_playing, is_paused) tuple
        cleanup_callback: Function to call for cleanup
    """
    try:
        while True:
            await asyncio.sleep(ALONE_CHECK_INTERVAL)

            voice_client = get_voice_client()
            if voice_client and voice_client.channel:
                # Count non-bot members
                members = [
                    m for m in voice_client.channel.members
                    if not m.bot
                ]

                # If alone and not playing, disconnect
                if len(members) == 0:
                    is_playing, is_paused = get_state()
                    if not is_playing and not is_paused:
                        logger.info(
                            "Bot is alone in voice channel, disconnecting"
                        )
                        await voice_client.disconnect()
                        cleanup_callback()
                        break
    except asyncio.CancelledError:
        logger.debug("check_alone task cancelled")
    except Exception as e:
        logger.error(f"Error in check_alone task: {e}")


async def check_inactivity(
    get_voice_client,
    get_last_activity,
    get_state,
    get_allowed_channel_name,
    bot,
    cleanup_callback
) -> None:
    """
    Background task to disconnect after inactivity timeout.

    Checks every INACTIVITY_CHECK_INTERVAL seconds. If no commands
    have been used for INACTIVITY_TIMEOUT seconds and bot is not playing,
    disconnects and notifies in the music channel.

    Args:
        get_voice_client: Function that returns current voice client
        get_last_activity: Function that returns last activity timestamp
        get_state: Function that returns (is_playing, is_paused) tuple
        get_allowed_channel_name: Function that returns allowed channel name
        bot: Bot instance for sending messages
        cleanup_callback: Function to call for cleanup
    """
    try:
        while True:
            await asyncio.sleep(INACTIVITY_CHECK_INTERVAL)

            voice_client = get_voice_client()
            last_activity = get_last_activity()

            if voice_client and last_activity:
                # Use time.monotonic() instead of deprecated loop.time()
                time_since_activity = time.monotonic() - last_activity

                # If inactive and not playing, disconnect
                if time_since_activity > INACTIVITY_TIMEOUT:
                    is_playing, is_paused = get_state()
                    if not is_playing and not is_paused:
                        logger.info(
                            f"Bot inactive for {INACTIVITY_TIMEOUT}s, "
                            "disconnecting"
                        )
                        await voice_client.disconnect()
                        cleanup_callback()

                        # Try to notify in music channel
                        try:
                            # Get current channel name (may have changed)
                            channel_name = get_allowed_channel_name()
                            channel = discord.utils.get(
                                bot.get_all_channels(),
                                name=channel_name
                            )
                            if channel:
                                timeout_mins = INACTIVITY_TIMEOUT // 60
                                await channel.send(
                                    f"🔇 Disconnected due to inactivity "
                                    f"({timeout_mins} minutes "
                                    f"without commands)."
                                )
                        except Exception as e:
                            logger.warning(
                                f"Could not send inactivity message: {e}"
                            )
                        break
    except asyncio.CancelledError:
        logger.debug("check_inactivity task cancelled")
    except Exception as e:
        logger.error(f"Error in check_inactivity task: {e}")
