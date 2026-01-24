"""
Audio source for YouTube playback.

Handles YouTube video extraction and audio source creation for Discord.
"""

import discord
import asyncio
from typing import Optional, Dict, Any

from .config import (
    create_ytdl_instance,
    logger
)


class YTDLSource(discord.PCMVolumeTransformer):
    """
    YouTube audio source for Discord voice channels.

    Wraps FFmpegPCMAudio with volume control and metadata handling.
    Inherits from PCMVolumeTransformer to provide volume adjustment.

    Attributes:
        data (dict): Video metadata from yt-dlp
        title (str): Video title
        url (str): Video URL
        duration (int): Video duration in seconds
        thumbnail (str): Thumbnail URL
    """

    def __init__(
        self,
        source: discord.AudioSource,
        *,
        data: Dict[str, Any],
        volume: float = 0.5
    ):
        """
        Initialize YTDLSource with audio source and metadata.

        Args:
            source: Discord audio source (FFmpegPCMAudio)
            data: Video metadata dictionary from yt-dlp
            volume: Initial volume (0.0 to 1.0)
        """
        super().__init__(source, volume)
        self.data = data
        self.title = sanitize_title(data.get('title', 'Unknown'))
        self.url = data.get('url', '')
        self.duration = data.get('duration', 0)
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_data(
        cls,
        data: Dict[str, Any],
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        """
        Create a YTDLSource from already-extracted video data.
        
        This avoids re-extracting and speeds up playback.

        Args:
            data: Already-extracted video data from yt-dlp
            loop: Event loop (not used but kept for compatibility)

        Returns:
            YTDLSource instance ready for playback

        Raises:
            Exception: If audio source creation fails
        """
        # Get direct audio stream URL
        filename = data.get('url')
        
        if not filename or not filename.startswith(('http://', 'https://')):
            raise ValueError(
                f"No valid audio stream URL found in data. "
                f"Available keys: {list(data.keys())}"
            )

        # #region agent log
        import json
        with open(r'c:\Users\Kevin\Desktop\Github\disco_bot\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'sessionId':'debug-session','runId':'initial','hypothesisId':'H1','location':'audio_source.py:86','message':'Stream metadata before FFmpeg','data':{'asr':data.get('asr'),'abr':data.get('abr'),'acodec':data.get('acodec'),'sample_rate':data.get('sample_rate'),'format_id':data.get('format_id'),'ext':data.get('ext')},'timestamp':__import__('time').time()*1000}) + '\n')
        # #endregion

        logger.info(f"Using audio source URL: {filename[:80]}...")

        # Create FFmpeg audio source
        # Error code -22 (EINVAL) means invalid argument
        # Use absolute minimal options - Discord.py handles most processing
        try:
            # Try with minimal reconnect options only
            reconnect_opts = (
                '-reconnect 1 -reconnect_streamed 1 '
                '-reconnect_delay_max 5'
            )
            
            # #region agent log
            import json
            with open(r'c:\Users\Kevin\Desktop\Github\disco_bot\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({'sessionId':'debug-session','runId':'initial','hypothesisId':'H2','location':'audio_source.py:98','message':'FFmpeg options used','data':{'before_options':reconnect_opts,'has_after_options':False},'timestamp':__import__('time').time()*1000}) + '\n')
            # #endregion
            
            audio_source = discord.FFmpegPCMAudio(
                filename,
                before_options=reconnect_opts
            )
            logger.debug("FFmpeg created with reconnect options")
        except Exception as e:
            logger.warning(f"FFmpeg with reconnect failed: {e}")
            # Try with absolutely no options
            try:
                # #region agent log
                import json
                with open(r'c:\Users\Kevin\Desktop\Github\disco_bot\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'sessionId':'debug-session','runId':'initial','hypothesisId':'H2','location':'audio_source.py:105','message':'FFmpeg fallback - no options','data':{'reconnect_failed':str(e)},'timestamp':__import__('time').time()*1000}) + '\n')
                # #endregion
                
                audio_source = discord.FFmpegPCMAudio(filename)
                logger.debug("FFmpeg created with no options")
            except Exception as e2:
                logger.error(f"FFmpeg creation failed: {e2}")
                raise ValueError(
                    f"Failed to create FFmpeg audio source: {e2}"
                )

        return cls(audio_source, data=data)

    @classmethod
    async def from_url(
        cls,
        url: str,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        stream: bool = False
    ):
        """
        Create a YTDLSource from a YouTube URL or search query.
        
        NOTE: Prefer using from_data() with already-extracted data to avoid
        double extraction.

        Args:
            url: YouTube URL or search query
            loop: Event loop (uses default if None)
            stream: Whether to stream audio (True) or download first (False)

        Returns:
            YTDLSource instance ready for playback

        Raises:
            Exception: If video extraction or audio source creation fails
        """
        # Get loop safely
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()

        # Create fresh ytdl instance for thread safety
        ytdl = create_ytdl_instance()

        def extract_func():
            """Extract video info using yt-dlp."""
            return ytdl.extract_info(url, download=not stream)

        # Run extraction in executor to avoid blocking
        data = await loop.run_in_executor(None, extract_func)

        # Handle playlists or search results (take first entry)
        if 'entries' in data:
            data = data['entries'][0]

        # Use from_data to create the source
        return await cls.from_data(data, loop=loop)


def sanitize_title(title: str) -> str:
    """
    Sanitize song title to prevent Discord markdown injection.

    Escapes special markdown characters that could be used maliciously.

    Args:
        title: Raw title from YouTube

    Returns:
        Sanitized title safe for Discord display
    """
    if not title:
        return 'Unknown'

    # Escape Discord markdown characters
    markdown_chars = ['*', '_', '~', '`', '|', '>', '<', '[', ']', '(', ')']
    for char in markdown_chars:
        title = title.replace(char, f'\\{char}')

    # Limit title length to prevent embed issues
    max_length = 200
    if len(title) > max_length:
        title = title[:max_length - 3] + '...'

    return title
