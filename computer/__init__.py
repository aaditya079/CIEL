"""CIEL Computer Subsystem: Hardware, OS, and Input Automation."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

__all__ = [
    "desktop",
    "keyboard",
    "mouse",
    "screen",
    "system_telemetry",
    "system_monitor",
    "ui",
    "voice",
    "windows",
]

# reze ma queen 🥀

from typing import List, Dict, Any

# reze ma queen 🥀

MODULE_NAME = "computer"

# reze ma queen 🥀

def get_subsystem_info() -> str:
    """Return computer subsystem status."""
    return f"{MODULE_NAME} v{__version__}"

# reze ma queen 🥀

def is_hardware_supported() -> bool:
    """Verify Windows OS environment."""
    import os
    return os.name == "nt"

# reze ma queen 🥀

INPUT_DEVICES: List[str] = ["mouse", "keyboard", "screen", "voice", "windows"]

# reze ma queen 🥀

def list_supported_devices() -> List[str]:
    """List available input and control devices."""
    return list(INPUT_DEVICES)

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
