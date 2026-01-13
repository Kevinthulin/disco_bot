"""
Music Cog for Discord Bot

Main cog file that orchestrates YouTube video playback in Discord.

Uses modular components for better maintainability.

Features:
    - YouTube video playback via yt-dlp
    - Queue management (add, remove, clear, view)
    - Vote-to-skip system
    - Auto-disconnect when alone or inactive
    - Channel restriction (commands only work in specified channel)
    - Volume control
    - Voice channel switching
    - Per-guild state for multi-server support
    - Rate limiting to prevent abuse
"""

import discord
from discord.ext import commands
import asyncio
from typing import Optional

# Import modular components
from .config import (
    BUFFER_DELAY_SECONDS,
    CONNECTION_STABILIZE_DELAY,
    COMMAND_RATE,
    COMMAND_PER_SECONDS,
    MAX_PLAY_RETRIES,
    logger
)
from .audio_source import YTDLSource, sanitize_title
from .music_helpers import (
    music_channel_only,
    get_queue_embed,
    calculate_required_votes
)
from .song_extractor import extract_song_info
from .guild_state import GuildStateManager
from .background_tasks import check_alone, check_inactivity


class Music(commands.Cog):
    """
    Music commands cog for Discord bot.

    Provides commands for playing YouTube videos, managing queues,
    controlling playback, and managing voice channel connections.

    Features:
        - YouTube video playback
        - Queue management
        - Vote-to-skip system
        - Auto-disconnect when alone or inactive
        - Channel restriction
        - Volume control
        - Per-guild state (multi-server support)
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize Music cog.

        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        self.states = GuildStateManager()

    def _get_state(self, ctx: commands.Context):
        """
        Get the guild state for the current context.

        Args:
            ctx: Command context

        Returns:
            GuildMusicState for the guild
        """
        return self.states.get(ctx.guild.id)

    @property
    def allowed_channel_name(self) -> str:
        """Default allowed channel name for decorator compatibility."""
        return 'music'

    def _start_background_tasks(self, ctx: commands.Context) -> None:
        """
        Start background tasks for auto-disconnect checks.

        Args:
            ctx: Command context
        """
        state = self._get_state(ctx)

        # Create getter functions for dynamic state access
        def get_voice_client():
            return state.voice_client

        def get_state_tuple():
            return (state.is_playing, state.is_paused)

        def get_last_activity():
            return state.last_activity

        def get_allowed_channel():
            return state.allowed_channel_name

        def cleanup():
            state.cleanup()
            state.voice_client = None

        if state.alone_check_task is None or state.alone_check_task.done():
            state.alone_check_task = self.bot.loop.create_task(
                check_alone(
                    get_voice_client,
                    get_state_tuple,
                    cleanup
                )
            )
        if state.inactivity_timer is None or state.inactivity_timer.done():
            state.inactivity_timer = self.bot.loop.create_task(
                check_inactivity(
                    get_voice_client,
                    get_last_activity,
                    get_state_tuple,
                    get_allowed_channel,
                    self.bot,
                    cleanup
                )
            )

    async def play_next(self, ctx: commands.Context) -> None:
        """
        Play the next song in the queue.

        Called automatically when current song ends. If queue is empty,
        stops playback and notifies user.

        Args:
            ctx: Command context for sending messages
        """
        state = self._get_state(ctx)

        if not state.queue:
            state.is_playing = False
            state.current_song = None
            state.play_retry_count = 0
            await ctx.send("Queue is empty! Use `!play` to add more songs.")
            return

        # Get next song from queue
        state.current_song = state.queue.popleft()

        try:
            # Create audio source from stored data
            # Check if we have full data, otherwise extract
            if '_full_data' in state.current_song:
                player = await YTDLSource.from_data(
                    state.current_song['_full_data'],
                    loop=self.bot.loop
                )
            else:
                # Fallback: extract from URL
                url = (
                    state.current_song.get('webpage_url') or
                    state.current_song.get('url') or
                    f"https://www.youtube.com/watch?v="
                    f"{state.current_song.get('id')}"
                )
                player = await YTDLSource.from_url(
                    url,
                    loop=self.bot.loop,
                    stream=True
                )

            # Small delay to ensure buffer is ready (reduces stuttering)
            await asyncio.sleep(BUFFER_DELAY_SECONDS)

            def after_callback(error: Optional[Exception]) -> None:
                """Callback after song finishes or errors."""
                if error is None:
                    state.play_retry_count = 0  # Reset on success
                    asyncio.run_coroutine_threadsafe(
                        self.play_next(ctx), self.bot.loop
                    )
                else:
                    logger.error(f'Player error: {error}')

            # Start playback
            if state.voice_client:
                state.voice_client.play(player, after=after_callback)
                state.is_playing = True
                state.is_paused = False
                state.skip_votes.clear()
                state.play_retry_count = 0
            else:
                logger.warning("Voice client not available for playback")
                state.is_playing = False

        except Exception as e:
            logger.error(f'Error playing song: {e}')
            await ctx.send(f'❌ Error playing song: {str(e)}')

            # Retry with limit to prevent infinite recursion
            state.play_retry_count += 1
            if state.play_retry_count < MAX_PLAY_RETRIES:
                logger.info(
                    f"Retrying play_next ({state.play_retry_count}/"
                    f"{MAX_PLAY_RETRIES})"
                )
                await self.play_next(ctx)
            else:
                logger.error(
                    f"Max retries ({MAX_PLAY_RETRIES}) reached, stopping"
                )
                state.play_retry_count = 0
                state.is_playing = False
                await ctx.send(
                    "❌ Failed to play songs after multiple attempts. "
                    "Queue cleared."
                )
                state.queue.clear()

    # ========================================================================
    # COMMANDS - VOICE CHANNEL MANAGEMENT
    # ========================================================================

    @commands.command(name='join', aliases=['connect'])
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def join(self, ctx: commands.Context) -> None:
        """
        Join the voice channel the user is currently in.

        If bot is already in a different channel, disconnects first.
        Starts background tasks for auto-disconnect checks.
        """
        state = self._get_state(ctx)

        if ctx.author.voice is None:
            await ctx.send("❌ You need to be in a voice channel!")
            return

        channel = ctx.author.voice.channel
        state.update_activity()

        try:
            # Disconnect from existing connection if in different channel
            if ctx.voice_client is not None:
                if ctx.voice_client.channel == channel:
                    await ctx.send(f"✅ Already in **{channel.name}**")
                    return
                await ctx.voice_client.disconnect()

            # Connect to voice channel
            state.voice_client = await channel.connect()
            self._start_background_tasks(ctx)
            await ctx.send(f"✅ Joined **{channel.name}**")

        except discord.errors.ClientException as e:
            error_msg = str(e)
            if "Already connected" in error_msg:
                await ctx.send(f"✅ Already connected to **{channel.name}**")
            else:
                await ctx.send(
                    f"❌ Failed to connect: {error_msg}\n"
                    "**Make sure:**\n"
                    "• Bot has 'Connect' and 'Speak' permissions\n"
                    "• You're in a valid voice channel\n"
                    "• Check firewall settings"
                )
            logger.warning(f'ClientException: {e}')
        except discord.errors.ConnectionClosed as e:
            await ctx.send(
                f"❌ Connection error (Code {e.code}): "
                f"{e.reason or 'Unknown'}\n"
                "**Try:**\n"
                "• Check Windows Firewall (allow Python)\n"
                "• Disable VPN if active\n"
                "• Try a different voice channel\n"
                "• Restart Discord and the bot"
            )
            logger.warning(f'ConnectionClosed error: {e.code} - {e.reason}')
        except Exception as e:
            error_type = type(e).__name__
            await ctx.send(
                f"❌ Error connecting: {error_type}: {str(e)}\n"
                "**Troubleshooting:**\n"
                "• Check bot permissions (Connect, Speak, View Channel)\n"
                "• Try a different voice channel\n"
                "• Check firewall/antivirus settings\n"
                "• Restart the bot"
            )
            logger.error(f'Voice connection error ({error_type}): {e}')

    @commands.command(name='switch', aliases=['move', 'change'])
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def switch(self, ctx: commands.Context) -> None:
        """
        Switch to the voice channel you're currently in.

        If bot is not connected, joins your channel.
        """
        state = self._get_state(ctx)
        state.update_activity()

        if ctx.author.voice is None:
            await ctx.send("❌ You need to be in a voice channel!")
            return

        user_voice_channel = ctx.author.voice.channel

        # If not connected, join user's channel
        if ctx.voice_client is None:
            try:
                state.voice_client = await user_voice_channel.connect()
                self._start_background_tasks(ctx)
                await ctx.send(f"✅ Joined **{user_voice_channel.name}**")
            except Exception as e:
                await ctx.send(
                    f"❌ Could not join voice channel: {str(e)}"
                )
                return

        # If in different channel, move to user's channel
        elif ctx.voice_client.channel != user_voice_channel:
            try:
                await ctx.voice_client.move_to(user_voice_channel)
                await ctx.send(
                    f"🔀 Switched to **{user_voice_channel.name}**"
                )
            except Exception as e:
                await ctx.send(
                    f"❌ Could not switch to voice channel: {str(e)}"
                )
                return
        else:
            await ctx.send(f"✅ Already in **{user_voice_channel.name}**")

    @commands.command(name='leave', aliases=['disconnect', 'dc'])
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def leave(self, ctx: commands.Context) -> None:
        """Leave the current voice channel."""
        state = self._get_state(ctx)
        state.update_activity()

        if ctx.voice_client is None:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        await ctx.voice_client.disconnect()
        state.voice_client = None
        state.cleanup()
        state.cancel_tasks()

        await ctx.send("✅ Left the voice channel")

    # ========================================================================
    # COMMANDS - PLAYBACK CONTROL
    # ========================================================================

    @commands.command(name='play', aliases=['p'])
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """
        Play a YouTube video or search for a video.

        Automatically joins user's voice channel if not connected.

        Args:
            query: YouTube URL or search query
        """
        state = self._get_state(ctx)
        state.update_activity()

        # Check if user is in a voice channel
        if ctx.author.voice is None:
            await ctx.send("❌ You need to be in a voice channel!")
            return

        # Ensure bot is connected to user's channel
        if ctx.voice_client is None:
            try:
                user_voice_channel = ctx.author.voice.channel
                state.voice_client = await user_voice_channel.connect()
                self._start_background_tasks(ctx)
                await asyncio.sleep(CONNECTION_STABILIZE_DELAY)
            except Exception as e:
                await ctx.send(
                    f"❌ Could not join voice channel: {str(e)}"
                )
                return
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            current_channel = ctx.voice_client.channel.name
            user_channel = ctx.author.voice.channel.name
            await ctx.send(
                f"❌ Bot is in **{current_channel}**, but you're in "
                f"**{user_channel}**.\n"
                f"Use `!switch` to move the bot to your channel."
            )
            return

        # Show typing indicator while processing
        async with ctx.typing():
            try:
                # Extract song information (no longer modifies queue directly)
                song, additional_songs = await extract_song_info(
                    query,
                    self.bot.loop
                )

                if not song:
                    await ctx.send(
                        f"❌ Could not find any results for: **{query}**\n"
                        "**Try:**\n"
                        "• A more specific search term\n"
                        "• A direct YouTube URL\n"
                        "• Check spelling"
                    )
                    return

                # Add additional songs to queue
                for additional in additional_songs:
                    state.queue.append(additional)

                # Create song info dictionary with full data
                song_info = {
                    'title': song.get('title', 'Unknown'),
                    'url': song.get('url'),
                    'webpage_url': song.get('webpage_url', ''),
                    'id': song.get('id'),
                    'thumbnail': song.get('thumbnail'),
                    '_full_data': song  # Keep full data to avoid re-extraction
                }

                # Add to queue if already playing, otherwise start playback
                if state.is_playing or state.is_paused:
                    state.queue.append(song_info)
                    title = sanitize_title(song_info['title'])
                    await ctx.send(f"✅ Added to queue: **{title}**")
                else:
                    state.current_song = song_info
                    title = song_info.get('title', 'Unknown')
                    logger.info(f"Creating audio source for: {title}")

                    # Use already-extracted data (much faster!)
                    try:
                        player = await YTDLSource.from_data(
                            song,  # Pass already-extracted data
                            loop=self.bot.loop
                        )
                        logger.info("Audio source created successfully")
                    except Exception as source_error:
                        logger.error(
                            f"Error creating audio source: {source_error}",
                            exc_info=True
                        )
                        await ctx.send(
                            f"❌ Error creating audio source: "
                            f"{str(source_error)}"
                        )
                        return

                    # Send "Now Playing" message immediately (before playback)
                    title = sanitize_title(song_info['title'])
                    await ctx.send(f"🎵 **Now Playing:** {title}")

                    # Small delay to ensure buffer is ready
                    await asyncio.sleep(BUFFER_DELAY_SECONDS)

                    def after_play_callback(
                        error: Optional[Exception]
                    ) -> None:
                        """Callback after song finishes."""
                        if error is None:
                            asyncio.run_coroutine_threadsafe(
                                self.play_next(ctx), self.bot.loop
                            )
                        else:
                            logger.error(f'Player error: {error}')

                    # Start playback - use ctx.voice_client to ensure sync
                    voice_client = ctx.voice_client or state.voice_client
                    if voice_client:
                        try:
                            voice_client.play(
                                player, after=after_play_callback
                            )
                            state.is_playing = True
                            state.is_paused = False
                            state.skip_votes.clear()
                            # Sync state.voice_client with ctx.voice_client
                            state.voice_client = voice_client
                        except Exception as play_error:
                            logger.error(
                                f'Error starting playback: {play_error}',
                                exc_info=True
                            )
                            await ctx.send(
                                f"❌ Error starting playback: {str(play_error)}"
                            )
                            state.is_playing = False
                    else:
                        await ctx.send(
                            "❌ Not connected to voice channel!"
                        )

            except Exception as e:
                logger.error(f'Error in play command: {e}', exc_info=True)
                await ctx.send(
                    f"❌ Error: {type(e).__name__}: {str(e)}\n"
                    "Check console for full error details."
                )

    @commands.command(name='pause')
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def pause(self, ctx: commands.Context) -> None:
        """Pause the currently playing song."""
        state = self._get_state(ctx)
        state.update_activity()

        if ctx.voice_client is None or not state.is_playing:
            await ctx.send("❌ Nothing is playing!")
            return

        if not state.is_paused:
            ctx.voice_client.pause()
            state.is_paused = True
            await ctx.send("⏸️ Paused")
        else:
            await ctx.send("❌ Already paused!")

    @commands.command(name='resume')
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def resume(self, ctx: commands.Context) -> None:
        """Resume the paused song."""
        state = self._get_state(ctx)
        state.update_activity()

        if ctx.voice_client is None:
            await ctx.send("❌ Nothing is playing!")
            return

        if state.is_paused:
            ctx.voice_client.resume()
            state.is_paused = False
            await ctx.send("▶️ Resumed")
        else:
            await ctx.send("❌ Not paused!")

    @commands.command(name='stop')
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def stop(self, ctx: commands.Context) -> None:
        """Stop the current song and clear the queue."""
        state = self._get_state(ctx)
        state.update_activity()

        if ctx.voice_client is None:
            await ctx.send("❌ Nothing is playing!")
            return

        ctx.voice_client.stop()
        state.queue.clear()
        state.is_playing = False
        state.is_paused = False
        state.current_song = None
        await ctx.send("⏹️ Stopped")

    @commands.command(name='skip', aliases=['next', 's'])
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def skip(self, ctx: commands.Context) -> None:
        """Skip the current song immediately."""
        state = self._get_state(ctx)
        state.update_activity()

        if ctx.voice_client is None or not state.is_playing:
            await ctx.send("❌ Nothing is playing!")
            return
        # Skip immediately (no voting required)
        ctx.voice_client.stop()
        state.skip_votes.clear()
        await ctx.send("⏭️ Skipped")


    # ========================================================================
    # COMMANDS - QUEUE MANAGEMENT
    # ========================================================================

    @commands.command(name='queue', aliases=['q'])
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def queue(self, ctx: commands.Context) -> None:
        """Display the current music queue."""
        state = self._get_state(ctx)
        state.update_activity()
        embed = get_queue_embed(state.current_song, state.queue)
        await ctx.send(embed=embed)

    @commands.command(name='clear')
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def clear(self, ctx: commands.Context) -> None:
        """Clear the music queue."""
        state = self._get_state(ctx)
        state.update_activity()
        state.queue.clear()
        await ctx.send("🗑️ Queue cleared!")

    @commands.command(name='remove')
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def remove(self, ctx: commands.Context, position: int) -> None:
        """Remove a song from the queue by position number."""
        state = self._get_state(ctx)
        state.update_activity()

        if not state.queue:
            await ctx.send("❌ Queue is empty!")
            return

        if position < 1 or position > len(state.queue):
            queue_len = len(state.queue)
            await ctx.send(
                f"❌ Invalid position! Queue has {queue_len} song(s). "
                f"Use `!queue` to see positions."
            )
            return

        # Convert deque to list, remove item, convert back
        from collections import deque
        queue_list = list(state.queue)
        removed_song = queue_list.pop(position - 1)
        state.queue = deque(queue_list)

        title = sanitize_title(removed_song.get('title', 'Unknown'))
        await ctx.send(
            f"🗑️ Removed **{title}** from position {position}"
        )

    # ========================================================================
    # COMMANDS - SETTINGS
    # ========================================================================

    @commands.command(name='volume', aliases=['vol'])
    @commands.cooldown(
        COMMAND_RATE, COMMAND_PER_SECONDS, commands.BucketType.user
    )
    @music_channel_only()
    async def volume(
        self,
        ctx: commands.Context,
        volume: Optional[int] = None
    ) -> None:
        """Set or display the playback volume (0-100)."""
        state = self._get_state(ctx)
        state.update_activity()

        if ctx.voice_client is None:
            await ctx.send("❌ Not connected to a voice channel!")
            return

        if volume is None:
            # Display current volume (with null check)
            if ctx.voice_client.source:
                vol_percent = int(ctx.voice_client.source.volume * 100)
                await ctx.send(f"🔊 Current volume: {vol_percent}%")
            else:
                await ctx.send("❌ No audio source active!")
            return

        # Set volume
        if 0 <= volume <= 100:
            if ctx.voice_client.source:
                ctx.voice_client.source.volume = volume / 100
                await ctx.send(f"🔊 Volume set to {volume}%")
            else:
                await ctx.send("❌ No audio source active!")
        else:
            await ctx.send("❌ Volume must be between 0 and 100!")

    @commands.command(name='setchannel', aliases=['channel'])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def setchannel(
        self,
        ctx: commands.Context,
        channel_name: str
    ) -> None:
        """Change the allowed channel for music commands (Admin only)."""
        state = self._get_state(ctx)
        state.allowed_channel_name = channel_name.lower().strip()
        await ctx.send(
            f"✅ Music commands are now restricted to "
            f"**#{state.allowed_channel_name}** channel!"
        )

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================

    @join.error
    @switch.error
    @leave.error
    @play.error
    @pause.error
    @resume.error
    @stop.error
    @skip.error
    @queue.error
    @clear.error
    @remove.error
    @volume.error
    async def command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ) -> None:
        """Handle command-specific errors."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ Command on cooldown. Try again in "
                f"{error.retry_after:.1f}s"
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        else:
            # Re-raise for global error handler
            raise error

    # ========================================================================
    # CLEANUP
    # ========================================================================

    def cog_unload(self) -> None:
        """Cleanup when cog is unloaded."""
        logger.info("Unloading Music cog, cleaning up...")
        self.states.cleanup_all()
        for vc in self.bot.voice_clients:
            asyncio.create_task(vc.disconnect())


async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(Music(bot))
    logger.info("Music cog loaded successfully")
