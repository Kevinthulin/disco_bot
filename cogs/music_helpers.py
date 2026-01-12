"""
Helper functions for the Music cog.

Contains utility methods for channel checking, queue management,
and other helper functions.
"""

import discord
from discord.ext import commands
import re
from typing import Optional, Dict, Any
from collections import deque
from functools import wraps

from .config import MAX_QUEUE_DISPLAY


def check_channel(ctx: commands.Context, allowed_channel_name: str) -> bool:
    """
    Check if command is used in the allowed channel.

    Strips emojis and special characters from channel name for robust
    matching. Allows channels with emoji prefixes (e.g., "🎵 music"
    matches "music").

    Args:
        ctx: Command context
        allowed_channel_name: Name of the allowed channel

    Returns:
        True if channel name contains allowed channel name, False otherwise
    """
    channel_name = ctx.channel.name.lower().strip()
    # Remove emojis and special characters, keep alphanumeric and spaces
    channel_clean = re.sub(r'[^\w\s]', '', channel_name)
    allowed_name = allowed_channel_name.lower().strip()
    return allowed_name in channel_clean or channel_clean == allowed_name


def music_channel_only():
    """
    Decorator to restrict commands to the allowed music channel.

    Must be applied after @commands.command() decorator.
    Automatically sends error message if used in wrong channel.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            if not check_channel(ctx, self.allowed_channel_name):
                await ctx.send(
                    f"❌ Music commands can only be used in the "
                    f"**#{self.allowed_channel_name}** channel!"
                )
                return
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def get_queue_embed(
    current_song: Optional[Dict[str, Any]],
    queue: deque
) -> discord.Embed:
    """
    Create a Discord embed showing the current queue.

    Args:
        current_song: Currently playing song dictionary
        queue: Queue of songs

    Returns:
        Embed with current song and queue list
    """
    embed = discord.Embed(title="Music Queue", color=discord.Color.blue())

    # Show currently playing song
    if current_song:
        title = sanitize_for_embed(current_song.get('title', 'Unknown'))
        embed.add_field(
            name="Now Playing",
            value=f"🎵 {title}",
            inline=False
        )

    # Show queue (up to MAX_QUEUE_DISPLAY items)
    if queue:
        queue_list = []
        for i, song in enumerate(list(queue)[:MAX_QUEUE_DISPLAY], 1):
            title = sanitize_for_embed(song.get('title', 'Unknown'))
            queue_list.append(f"{i}. {title}")

        if len(queue) > MAX_QUEUE_DISPLAY:
            remaining = len(queue) - MAX_QUEUE_DISPLAY
            queue_list.append(f"... and {remaining} more")

        queue_value = "\n".join(queue_list) if queue_list else "Queue is empty"
        embed.add_field(name="Up Next", value=queue_value, inline=False)
    else:
        embed.add_field(name="Up Next", value="Queue is empty", inline=False)

    return embed


def sanitize_for_embed(text: str) -> str:
    """
    Sanitize text for safe display in Discord embeds.

    Args:
        text: Raw text

    Returns:
        Sanitized text safe for embed display
    """
    if not text:
        return 'Unknown'

    # Escape Discord markdown characters
    markdown_chars = ['*', '_', '~', '`', '|']
    for char in markdown_chars:
        text = text.replace(char, f'\\{char}')

    # Limit length
    max_length = 100
    if len(text) > max_length:
        text = text[:max_length - 3] + '...'

    return text


def calculate_required_votes(
    voice_client: Optional[discord.VoiceClient]
) -> int:
    """
    Calculate required votes to skip based on voice channel members.

    Args:
        voice_client: Discord voice client

    Returns:
        Number of votes required (majority + 1)
    """
    if not voice_client or not voice_client.channel:
        return 1

    members = [m for m in voice_client.channel.members if not m.bot]
    return max(1, (len(members) // 2) + 1)
