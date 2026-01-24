"""
Configuration constants for the Music cog.

Contains all configuration values, timing constants, and yt-dlp settings.
"""

import logging
import yt_dlp


# ============================================================================
# LOGGING SETUP
# ============================================================================

# Configure logging for the music cog
logger = logging.getLogger('disco_bot.music')
logger.setLevel(logging.INFO)

# Create console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ============================================================================
# YT-DLP CONFIGURATION
# ============================================================================

# yt-dlp configuration for audio extraction
# Enhanced anti-bot detection settings for hosted environments
YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': False,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'extract_flat': False,
    # Anti-bot detection: Use browser-like user agent
    'user_agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    # Additional headers to mimic browser requests
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    },
    # Retry on errors (helps with temporary YouTube blocks)
    'retries': 3,
    'fragment_retries': 3,
    # Extractor args to bypass bot detection
    # Use iOS client which is more reliable and less likely to be blocked
    'extractor_args': {
        'youtube': {
            'player_client': ['ios', 'android', 'web'],
            'player_skip': ['webpage', 'configs'],
        }
    },
}

# Suppress yt-dlp warnings
# Accept any arguments to avoid breaking yt-dlp's internal calls
yt_dlp.utils.bug_reports_message = lambda *args, **kwargs: ''


def create_ytdl_instance():
    """
    Create a new yt-dlp instance.

    Returns a fresh instance to avoid state issues in multi-guild scenarios.
    """
    return yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS)


# Default instance for backwards compatibility
ytdl = create_ytdl_instance()


# ============================================================================
# FFMPEG CONFIGURATION
# ============================================================================

# FFmpeg options for smooth audio playback
# before_options: Connection and buffering settings
FFMPEG_BEFORE_OPTIONS = (
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
    '-bufsize 512k -fflags +genpts'
)

# options: Audio processing settings (PCM output for Discord)
# Simplified: removed audio filter that might cause issues
FFMPEG_OPTIONS = '-vn -f s16le -ar 48000 -ac 2'


# ============================================================================
# TIMING CONSTANTS
# ============================================================================

# Delay before playback to ensure buffer readiness (reduces stuttering)
BUFFER_DELAY_SECONDS = 0.2

# Delay after connecting to voice channel for stability
CONNECTION_STABILIZE_DELAY = 1.0

# Check interval for alone detection (seconds)
ALONE_CHECK_INTERVAL = 60

# Check interval for inactivity detection (seconds)
INACTIVITY_CHECK_INTERVAL = 60

# Timeout before disconnecting due to inactivity (seconds = 15 minutes)
INACTIVITY_TIMEOUT = 900


# ============================================================================
# RATE LIMITING
# ============================================================================

# Commands per seconds per user
COMMAND_RATE = 2
COMMAND_PER_SECONDS = 5


# ============================================================================
# DISPLAY CONSTANTS
# ============================================================================

# Maximum songs to show in queue embed
MAX_QUEUE_DISPLAY = 10

# Default channel name for command restriction
DEFAULT_ALLOWED_CHANNEL = 'music'

# Maximum retries for play_next before giving up
MAX_PLAY_RETRIES = 3
