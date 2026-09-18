"""Clipboard inspection and manipulation tools."""

# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀


import logging
from typing import Dict, Any, Optional
import pyperclip

logger = logging.getLogger("desktop_agent.tools.clipboard")


def get_clipboard() -> Dict[str, Any]:
    """Retrieve the current clipboard text and metadata."""
    try:
        text = pyperclip.paste() or ""
        lines = text.splitlines()
        words = text.split()
        return {
            "success": True,
            "text": text,
            "length": len(text),
            "word_count": len(words),
            "line_count": len(lines),
            "preview": text[:200] + ("..." if len(text) > 200 else ""),
            "message": f"Clipboard contains {len(words)} words ({len(text)} characters).",
            "spoken": f"Clipboard contains {len(words)} words.",
        }
    except Exception as e:
        logger.error(f"Failed to read clipboard: {e}")
        return {"success": False, "error": str(e), "message": f"Could not read clipboard: {e}"}


def set_clipboard(text: str) -> Dict[str, Any]:
    """Write text to the system clipboard."""
    try:
        pyperclip.copy(text)
        return {
            "success": True,
            "length": len(text),
            "message": f"Copied {len(text)} characters to clipboard.",
            "spoken": "Copied to clipboard.",
        }
    except Exception as e:
        logger.error(f"Failed to copy to clipboard: {e}")
        return {"success": False, "error": str(e), "message": f"Could not copy to clipboard: {e}"}


def clear_clipboard() -> Dict[str, Any]:
    """Clear the system clipboard."""
    try:
        pyperclip.copy("")
        return {
            "success": True,
            "message": "Clipboard cleared.",
            "spoken": "Clipboard cleared.",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Could not clear clipboard: {e}"}


def clipboard_action(action: str, text: Optional[str] = None) -> Dict[str, Any]:
    """Unified clipboard dispatcher for tool registry."""
    act = str(action).strip().lower()
    if act in ("read", "get", "inspect"):
        return get_clipboard()
    elif act in ("write", "set", "copy"):
        return set_clipboard(text or "")
    elif act in ("clear", "empty"):
        return clear_clipboard()
    else:
        return {"success": False, "error": f"Unknown clipboard action: '{action}'"}
