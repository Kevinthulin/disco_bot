"""
Per-guild state management for the Music cog.

Handles queue, playback state, and settings for each Discord server.
"""

import asyncio
import time
import discord
from collections import deque
from typing import Optional, Dict, Any, Set

from .config import DEFAULT_ALLOWED_CHANNEL


class GuildMusicState:
    """
    Holds music-related state for a single guild.

    Each guild (server) gets its own instance to prevent state conflicts.

    Attributes:
        guild_id: Discord guild ID
        queue: Song queue (deque)
        current_song: Currently playing song info
        is_playing: Whether audio is playing
        is_paused: Whether playback is paused
        voice_client: Voice channel connection
        skip_votes: Set of user IDs who voted to skip
        last_activity: Timestamp of last command usage
        allowed_channel_name: Channel where commands are allowed
        play_retry_count: Counter for play_next retries
    """

    def __init__(self, guild_id: int):
        """
        Initialize guild state.

        Args:
            guild_id: Discord guild ID
        """
        self.guild_id = guild_id
        self.queue: deque = deque()
        self.current_song: Optional[Dict[str, Any]] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.voice_client: Optional[discord.VoiceClient] = None
        self.skip_votes: Set[int] = set()
        self.alone_check_task: Optional[asyncio.Task] = None
        self.inactivity_timer: Optional[asyncio.Task] = None
        self.last_activity: Optional[float] = None
        self.allowed_channel_name: str = DEFAULT_ALLOWED_CHANNEL
        self.play_retry_count: int = 0

    def update_activity(self) -> None:
        """Update the last activity timestamp to current time."""
        self.last_activity = time.monotonic()

    def cleanup(self) -> None:
        """Reset all voice-related state variables."""
        self.queue.clear()
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.skip_votes.clear()
        self.last_activity = None
        self.play_retry_count = 0

    def cancel_tasks(self) -> None:
        """Cancel all background tasks."""
        if self.alone_check_task:
            self.alone_check_task.cancel()
            self.alone_check_task = None
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
            self.inactivity_timer = None


class GuildStateManager:
    """
    Manages GuildMusicState instances for all guilds.

    Provides thread-safe access to per-guild state.
    """

    def __init__(self):
        """Initialize the state manager."""
        self._states: Dict[int, GuildMusicState] = {}

    def get(self, guild_id: int) -> GuildMusicState:
        """
        Get or create state for a guild.

        Args:
            guild_id: Discord guild ID

        Returns:
            GuildMusicState for the guild
        """
        if guild_id not in self._states:
            self._states[guild_id] = GuildMusicState(guild_id)
        return self._states[guild_id]

    def remove(self, guild_id: int) -> None:
        """
        Remove state for a guild.

        Cleans up resources before removal.

        Args:
            guild_id: Discord guild ID
        """
        if guild_id in self._states:
            state = self._states[guild_id]
            state.cancel_tasks()
            state.cleanup()
            del self._states[guild_id]

    def cleanup_all(self) -> None:
        """Clean up all guild states."""
        for state in self._states.values():
            state.cancel_tasks()
            state.cleanup()
        self._states.clear()
