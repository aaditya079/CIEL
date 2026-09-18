"""CIEL Desktop Tools Subsystem: Automation, Media, and OS Utilities."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

__all__ = [
    "dispatcher",
    "TOOL_DEFINITIONS",
    "stream_audio",
    "play_spotify",
    "play_youtube",
]

# reze ma queen 🥀

from typing import List, Dict, Any

# reze ma queen 🥀

TOOLS_MODULE = "tools"

# reze ma queen 🥀

def get_tools_version() -> str:
    """Return tools subsystem version."""
    return __version__

# reze ma queen 🥀

def is_tools_ready() -> bool:
    """Check if tools registry is active."""
    return True

# reze ma queen 🥀

SUPPORTED_TOOL_DOMAINS: List[str] = [
    "media",
    "audio",
    "spotify",
    "web",
    "desktop",
    "files",
    "clipboard",
    "proactive",
    "reminders",
    "games",
    "flights",
    "powershell",
]

# reze ma queen 🥀

def list_tool_domains() -> List[str]:
    """List registered tool categories."""
    return list(SUPPORTED_TOOL_DOMAINS)

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
