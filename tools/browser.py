"""Browser navigation and tab management tools."""

import logging
from typing import Dict, Any

try:
    import pyautogui
except ImportError:
    pyautogui = None

logger = logging.getLogger("desktop_agent.tools.browser")

BROWSER_ACTIONS = {
    "new_tab": lambda: pyautogui.hotkey("ctrl", "t"),
    "close_tab": lambda: pyautogui.hotkey("ctrl", "w"),
    "next_tab": lambda: pyautogui.hotkey("ctrl", "tab"),
    "prev_tab": lambda: pyautogui.hotkey("ctrl", "shift", "tab"),
    "reopen_tab": lambda: pyautogui.hotkey("ctrl", "shift", "t"),
    "refresh": lambda: pyautogui.press("f5"),
    "zoom_in": lambda: pyautogui.hotkey("ctrl", "+"),
    "zoom_out": lambda: pyautogui.hotkey("ctrl", "-"),
    "zoom_reset": lambda: pyautogui.hotkey("ctrl", "0"),
    "find": lambda: pyautogui.hotkey("ctrl", "f"),
    "history": lambda: pyautogui.hotkey("ctrl", "h"),
    "bookmarks": lambda: pyautogui.hotkey("ctrl", "shift", "o"),
    "address_bar": lambda: pyautogui.hotkey("ctrl", "l"),
    "go_back": lambda: pyautogui.hotkey("alt", "left"),
    "go_forward": lambda: pyautogui.hotkey("alt", "right"),
}


def browser_action(action: str) -> Dict[str, Any]:
    """Execute standard browser navigation and tab controls.
    
    Supported: 'new_tab', 'close_tab', 'next_tab', 'prev_tab', 'reopen_tab',
               'refresh', 'zoom_in', 'zoom_out', 'zoom_reset', 'find',
               'history', 'bookmarks', 'address_bar', 'go_back', 'go_forward'
    """
    act = (action or "").strip().lower().replace(" ", "_").replace("-", "_")

    if not pyautogui:
        return {"success": False, "error": "pyautogui unavailable."}

    handler = BROWSER_ACTIONS.get(act)
    if not handler:
        return {
            "success": False,
            "error": f"Unknown browser action '{action}'. Supported: {list(BROWSER_ACTIONS.keys())}",
        }

    try:
        handler()
        return {"success": True, "action": act, "message": f"Browser action '{act}' executed."}
    except Exception as e:
        return {"success": False, "error": str(e)}
