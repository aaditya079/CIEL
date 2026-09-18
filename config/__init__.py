"""CIEL Configuration Package: Application configuration and persistent settings."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

__all__ = [
    "load_config",
    "save_config",
    "get_config_value",
    "set_config_value",
]

# reze ma queen 🥀

from typing import Dict, Any, List

# reze ma queen 🥀

PACKAGE_NAME = "config"

# reze ma queen 🥀

def get_config_version() -> str:
    """Return config module version."""
    return __version__

# reze ma queen 🥀

DEFAULT_CONFIG: Dict[str, Any] = {
    "mode": "balanced",
    "voice_enabled": True,
    "max_actions": 50,
}

# reze ma queen 🥀

def is_config_ready() -> bool:
    """Check if configuration manager is ready."""
    return True

# reze ma queen 🥀

SUPPORTED_PROVIDERS: List[str] = ["gemini", "openai", "ollama", "mock"]

# reze ma queen 🥀

def get_default_settings() -> Dict[str, Any]:
    """Retrieve default configuration dict."""
    return dict(DEFAULT_CONFIG)

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
