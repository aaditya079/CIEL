"""Keyboard simulation and text entry for Desktop Agent."""

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


import time
import logging
from typing import List
import pyautogui
import pyperclip

from safety.kill_switch import kill_switch
from computer.mouse import ensure_cursor_away_from_corner
from computer.desktop import run_on_input_desktop

logger = logging.getLogger("desktop_agent.computer.keyboard")

# Common key mappings and aliases
KEY_ALIASES = {
    "return": "enter",
    "control": "ctrl",
    "alternate": "alt",
    "windows": "win",
    "super": "win",
    "escape": "esc",
}


def _normalize_key(key: str) -> str:
    """Normalize key name to PyAutoGUI standard."""
    lower_key = key.strip().lower()
    return KEY_ALIASES.get(lower_key, lower_key)


def type_text(text: str, interval: float = 0.01, use_clipboard_fallback: bool = True, **kwargs) -> None:
    """Type text safely on the interactive input desktop."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    if not text:
        return

    # Check if text contains non-ASCII characters or multiline
    is_complex = any(ord(c) > 127 for c in text) or "\n" in text

    def _do_type():
        if is_complex and use_clipboard_fallback:
            logger.debug(f"Pasting complex text via clipboard (len={len(text)})")
            old_clipboard = pyperclip.paste()
            try:
                pyperclip.copy(text)
                time.sleep(0.05)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.05)
            finally:
                try:
                    pyperclip.copy(old_clipboard)
                except Exception:
                    pass
        else:
            logger.debug(f"Typing text (len={len(text)}): {text[:30]}...")
            pyautogui.write(text, interval=interval)

    run_on_input_desktop(_do_type)
    kill_switch.check()


def press_key(key: str, **kwargs) -> None:
    """Press and release a single key on the input desktop."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    norm_key = _normalize_key(key)
    logger.debug(f"Pressing key: {norm_key}")

    def _do_press():
        pyautogui.press(norm_key)

    run_on_input_desktop(_do_press)
    kill_switch.check()


def hotkey(*keys: str, **kwargs) -> None:
    """Press a key combination (e.g., 'ctrl', 'c' or 'alt', 'tab') on the input desktop."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    norm_keys = [_normalize_key(k) for k in keys]
    logger.debug(f"Executing hotkey: {' + '.join(norm_keys)}")

    def _do_hotkey():
        pyautogui.hotkey(*norm_keys)

    run_on_input_desktop(_do_hotkey)
    kill_switch.check()


def key_down(key: str, **kwargs) -> None:
    """Hold a key down."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    norm_key = _normalize_key(key)
    run_on_input_desktop(lambda: pyautogui.keyDown(norm_key))


def key_up(key: str, **kwargs) -> None:
    """Release a key."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    norm_key = _normalize_key(key)
    run_on_input_desktop(lambda: pyautogui.keyUp(norm_key))

