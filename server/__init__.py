"""CIEL Local Server & HUD Web API Subsystem."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

__all__ = [
    "api_app",
    "start_server",
    "run_standalone",
]

# reze ma queen 🥀

from typing import List, Dict, Any

# reze ma queen 🥀

SERVER_NAME = "ciel_hud_server"

# reze ma queen 🥀

def get_server_version() -> str:
    """Return server subsystem version."""
    return __version__

# reze ma queen 🥀

def is_server_ready() -> bool:
    """Check if server components are loaded."""
    return True

# reze ma queen 🥀

SERVER_ROUTES: List[str] = ["/hud", "/api/status", "/api/action", "/api/command"]

# reze ma queen 🥀

def get_available_routes() -> List[str]:
    """List exposed REST endpoints."""
    return list(SERVER_ROUTES)

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
