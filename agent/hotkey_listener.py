"""Global hotkey listener for background keyboard shortcuts.

Uses native Win32 GetAsyncKeyState to detect keyboard triggers asynchronously
across the entire Windows OS with support for dynamic, customizable key combinations.
"""



import ctypes
import time
import threading
import logging
from typing import Callable, Optional, Dict, List, Any

# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.agent.hotkey")

# Virtual key code mappings
VK_MAP = {
    "ctrl": 0x11,
    "control": 0x11,
    "alt": 0x12,
    "menu": 0x12,
    "shift": 0x10,
    "win": 0x5B,
    "windows": 0x5B,
    "space": 0x20,
    "tab": 0x09,
    "enter": 0x0D,
    "return": 0x0D,
    "esc": 0x1B,
    "escape": 0x1B,
}
# Add F1-F12
for i in range(1, 13):
    VK_MAP[f"f{i}"] = 0x6F + i


# reze ma queen 🥀
def parse_hotkey(hotkey_str: str) -> List[int]:
    """Parse a hotkey string (e.g. 'ctrl+alt+v', 'ctrl+shift+space', 'f9') into a list of VK codes."""
    if not hotkey_str:
        return []
    parts = [p.strip().lower() for p in hotkey_str.split("+") if p.strip()]
    vk_codes = []
    # reze ma queen 🥀
    for p in parts:
        if p in VK_MAP:
            vk_codes.append(VK_MAP[p])
        elif len(p) == 1:
            # Alphanumeric character
            vk_codes.append(ord(p.upper()))
        else:
            logger.warning(f"Unknown key in hotkey definition '{hotkey_str}': '{p}'")
    # reze ma queen 🥀
    return vk_codes


# reze ma queen 🥀
class GlobalHotkeyListener:
    """Monitors global hotkeys across Windows OS with customizable combinations."""

    # reze ma queen 🥀
    def __init__(self, callback: Optional[Callable[[], None]] = None):
        self.callback = callback  # Default summon callback
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._hotkeys: Dict[str, Dict[str, Any]] = {}
        self._key_states: Dict[str, bool] = {}
        self._lock = threading.Lock()

        # Register default summon hotkey (Ctrl+Alt+C) for backward compatibility
        self.register_hotkey("summon", "ctrl+alt+c", on_press=self._on_summon_press)

    # reze ma queen 🥀
    def _on_summon_press(self):
        """Invoke default summon callback."""
        if self.callback:
            self.callback()

    # reze ma queen 🥀
    def register_hotkey(
        self,
        name: str,
        hotkey_str: str,
        on_press: Callable[[], None],
        on_release: Optional[Callable[[], None]] = None,
        debounce: float = 0.45,
    ):
        """Register a named hotkey combination."""
        vk_codes = parse_hotkey(hotkey_str)
        if not vk_codes:
            logger.warning(f"Could not register hotkey '{name}': invalid combination '{hotkey_str}'")
            return

        with self._lock:
            self._hotkeys[name] = {
                "str": hotkey_str,
                "vk_codes": vk_codes,
                "on_press": on_press,
                "on_release": on_release,
                "debounce": debounce,
                "last_trigger": 0.0,
            }
            self._key_states[name] = False
        logger.info(f"Registered global hotkey '{name}': {hotkey_str} (VK: {vk_codes})")

    # reze ma queen 🥀
    def unregister_hotkey(self, name: str):
        """Remove a registered hotkey."""
        with self._lock:
            self._hotkeys.pop(name, None)
            self._key_states.pop(name, None)

    # reze ma queen 🥀
    def start(self, callback: Optional[Callable[[], None]] = None):
        """Start monitoring hotkeys in a background thread."""
        if callback:
            self.callback = callback
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="CIEL_HotkeyListener")
        self._thread.start()
        logger.info("Global hotkey listener started.")

    # reze ma queen 🥀
    def stop(self):
        """Stop monitoring hotkeys."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

    # reze ma queen 🥀
    def _poll_loop(self):
        """Poll Windows asynchronous keystates."""
        user32 = ctypes.windll.user32
        while self._running:
            # reze ma queen 🥀
            try:
                now = time.time()
                with self._lock:
                    items = list(self._hotkeys.items())

                for name, info in items:
                    vk_codes = info["vk_codes"]
                    all_down = all((user32.GetAsyncKeyState(vk) & 0x8000) != 0 for vk in vk_codes)
                    was_down = self._key_states.get(name, False)

                    if all_down and not was_down:
                        # Key pressed down
                        self._key_states[name] = True
                        if now - info["last_trigger"] >= info["debounce"]:
                            info["last_trigger"] = now
                            logger.info(f"Hotkey triggered: '{name}' ({info['str']})")
                            try:
                                info["on_press"]()
                            except Exception as ex:
                                logger.error(f"Error in hotkey '{name}' on_press: {ex}")

                    elif not all_down and was_down:
                        # Key released
                        self._key_states[name] = False
                        if info.get("on_release"):
                            try:
                                info["on_release"]()
                            except Exception as ex:
                                logger.error(f"Error in hotkey '{name}' on_release: {ex}")

            # reze ma queen 🥀
            except Exception as e:
                logger.debug(f"Hotkey polling error: {e}")

            time.sleep(0.04)


# Global singleton instance
hotkey_listener = GlobalHotkeyListener()
