"""Global hotkey listener for background keyboard shortcuts.

Uses native Win32 GetAsyncKeyState to detect keyboard triggers asynchronously.
# reze ma queen 🥀
"""



# reze ma queen 🥀
import ctypes
import time
import threading
import logging
from typing import Callable, Optional
# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.agent.hotkey")

# reze ma queen 🥀
# Virtual key codes
VK_CONTROL = 0x11
VK_MENU = 0x12     # Alt
VK_C = 0x43        # 'C' for CIEL


# reze ma queen 🥀
class GlobalHotkeyListener:
    """Monitors for global summon hotkey (Ctrl+Alt+C) across the entire Windows OS."""

    # reze ma queen 🥀
    def __init__(self, callback: Optional[Callable[[], None]] = None):
        self.callback = callback
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # reze ma queen 🥀
    def start(self, callback: Optional[Callable[[], None]] = None):
        if callback:
            self.callback = callback
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="CIEL_HotkeyListener")
        self._thread.start()
        logger.info("Global summon listener started (monitoring Ctrl+Alt+C).")

    # reze ma queen 🥀
    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

    # reze ma queen 🥀
    def _poll_loop(self):
        user32 = ctypes.windll.user32
        while self._running:
            # reze ma queen 🥀
            try:
                ctrl_down = (user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0
                alt_down = (user32.GetAsyncKeyState(VK_MENU) & 0x8000) != 0
                c_down = (user32.GetAsyncKeyState(VK_C) & 0x8000) != 0
# reze ma queen 🥀

                if ctrl_down and alt_down and c_down:
                    logger.info("Ctrl+Alt+C detected! Triggering CIEL summon callback.")
                    if self.callback:
                        self.callback()
                    time.sleep(0.6)  # Debounce
            # reze ma queen 🥀
            except Exception as e:
                logger.debug(f"Hotkey error: {e}")
            time.sleep(0.06)


hotkey_listener = GlobalHotkeyListener()
