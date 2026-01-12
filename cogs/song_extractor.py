"""
Song extraction from YouTube.

Handles YouTube URL and search query processing using yt-dlp.
"""

from typing import Optional, Dict, Any, List

from .config import (
    YTDL_FORMAT_OPTIONS,
    MAX_QUEUE_DISPLAY,
    create_ytdl_instance,
    logger
)
import yt_dlp as yt_dlp_module


async def extract_song_info(
    query: str,
    loop
) -> tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Extract song information from YouTube URL or search query.

    Handles both direct URLs and search queries. For search queries,
    uses ytsearch: prefix for better results.

    Args:
        query: YouTube URL or search query
        loop: Event loop for executor

    Returns:
        Tuple of (primary song info, list of additional songs for queue)
        Returns (None, []) if not found

    Raises:
        Exception: If extraction fails
    """
    additional_songs: List[Dict[str, Any]] = []

    def extract_func():
        """Extract video info using yt-dlp."""
        # Create fresh instance for thread safety
        ytdl = create_ytdl_instance()

        try:
            # Check if it's a URL
            is_url = any(
                query.startswith(prefix)
                for prefix in ['http://', 'https://', 'www.']
            )

            # Add ytsearch prefix for non-URL queries
            search_query = query if is_url else f"ytsearch:{query}"
            return ytdl.extract_info(search_query, download=False)
        except Exception as e:
            # Handle yt-dlp import errors with retry
            error_str = str(e)
            has_circular = 'circular import' in error_str
            has_ejs = '_EJS_WIKI_URL' in error_str

            if has_circular or has_ejs:
                logger.warning(
                    f"yt-dlp import error, retrying: {e}"
                )
                # Retry with fresh yt-dlp instance
                import importlib
                importlib.reload(yt_dlp_module)
                fresh_ytdl = yt_dlp_module.YoutubeDL(YTDL_FORMAT_OPTIONS)
                search_query = query if is_url else f"ytsearch:{query}"
                return fresh_ytdl.extract_info(search_query, download=False)
            raise

    data = await loop.run_in_executor(None, extract_func)

    if not data:
        return None, []

    # Handle playlists or search results
    if 'entries' in data:
        entries = data.get('entries', [])
        if not entries:
            return None, []

        if len(entries) > 1:
            # Multiple results - return first one, collect others
            song = entries[0]
            for entry in entries[1:MAX_QUEUE_DISPLAY]:
                if entry:
                    entry_url = entry.get('url', entry.get('webpage_url', ''))
                    additional_songs.append({
                        'title': entry.get('title', 'Unknown'),
                        'url': entry_url,
                        'thumbnail': entry.get('thumbnail')
                    })
            return song, additional_songs
        else:
            return entries[0] if entries else None, []
    else:
        return data, []
