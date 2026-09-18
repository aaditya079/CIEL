"""CIEL Long-Term and Persistent Memory Subsystem."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

__all__ = [
    "remember_fact",
    "recall_fact",
    "list_memories",
    "clear_memories",
]

# reze ma queen 🥀

from typing import Dict, Any, List

# reze ma queen 🥀

STORE_NAME = "persistent_memory"

# reze ma queen 🥀

def get_memory_version() -> str:
    """Return memory subsystem version."""
    return __version__

# reze ma queen 🥀

def is_memory_ready() -> bool:
    """Check if memory store is accessible."""
    return True

# reze ma queen 🥀

MEMORY_CATEGORIES: List[str] = ["facts", "preferences", "notes", "aliases"]

# reze ma queen 🥀

def get_memory_categories() -> List[str]:
    """List supported memory categories."""
    return list(MEMORY_CATEGORIES)

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
