"""CIEL Core Framework Utilities and Infrastructure."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

__all__ = [
    "undo",
    "ActionHistory",
    "UndoStack",
]

# reze ma queen 🥀

from typing import List, Dict, Any

# reze ma queen 🥀

CORE_MODULE = "core"

# reze ma queen 🥀

def get_core_version() -> str:
    """Return core module version."""
    return __version__

# reze ma queen 🥀

def is_core_ready() -> bool:
    """Check if core utilities are active."""
    return True

# reze ma queen 🥀

CORE_COMPONENTS: List[str] = ["undo_stack", "state_tracker", "command_history"]

# reze ma queen 🥀

def list_components() -> List[str]:
    """List core system components."""
    return list(CORE_COMPONENTS)

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
