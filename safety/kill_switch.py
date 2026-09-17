"""Emergency stop and kill switch mechanism for Desktop Agent."""

import threading
import time
import logging
from typing import Callable, List, Optional
import pyautogui

logger = logging.getLogger("desktop_agent.safety.kill_switch")

# Disable PyAutoGUI's default FAILSAFE to prevent false positives in background sessions at (0,0)
# Instead, our KillSwitch manages Ctrl+Alt+X hotkey and intentional corner slam detection.
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


class KillSwitchTriggeredError(Exception):
    """Raised when the emergency kill switch is activated."""
    pass


class KillSwitch:
    """Manages the global emergency kill switch.
    
    Provides thread-safe abort signals via Ctrl+Alt+X or programmatic triggers.
    """
    _instance: Optional["KillSwitch"] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused by default
        self._callbacks: List[Callable[[], None]] = []
        self._listener_thread: Optional[threading.Thread] = None
        self._running = False
        self._has_moved_from_zero = False
        self._initialized = True

    def is_triggered(self) -> bool:
        """Check whether emergency stop has been requested."""
        return self._stop_event.is_set()

    def is_paused(self) -> bool:
        """Check whether execution is currently paused."""
        return not self._pause_event.is_set()

    def check(self) -> None:
        """Raise KillSwitchTriggeredError if emergency stop was triggered, or block while paused."""
        if self._stop_event.is_set():
            raise KillSwitchTriggeredError("Emergency kill switch activated! Halting all operations immediately.")
        
        # Check if user intentionally slammed mouse into corner (0,0) after having moved it
        try:
            pos = pyautogui.position()
            if pos.x == 0 and pos.y == 0 and self._has_moved_from_zero:
                time.sleep(0.05)
                pos2 = pyautogui.position()
                if pos2.x == 0 and pos2.y == 0:
                    self.trigger("Mouse slammed into corner (0,0)")
                    raise KillSwitchTriggeredError("Mouse fail-safe corner triggered!")
            elif pos.x > 50 or pos.y > 50:
                self._has_moved_from_zero = True
        except KillSwitchTriggeredError:
            raise
        except Exception:
            pass

        # If paused, wait until resumed or killed
        while not self._pause_event.is_set():
            if self._stop_event.is_set():
                raise KillSwitchTriggeredError("Emergency kill switch activated while paused!")
            time.sleep(0.1)

    def trigger(self, reason: str = "Manual emergency stop") -> None:
        """Trigger emergency stop immediately."""
        logger.critical(f"KILL SWITCH TRIGGERED: {reason}")
        self._stop_event.set()
        # Resume pause so waiting threads wake up and abort
        self._pause_event.set()
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error executing kill switch callback: {e}")

    def pause(self) -> None:
        """Pause agent execution."""
        logger.info("Kill switch: Pause requested.")
        self._pause_event.clear()

    def resume(self) -> None:
        """Resume agent execution."""
        logger.info("Kill switch: Resume requested.")
        self._pause_event.set()

    def reset(self) -> None:
        """Reset the kill switch state for a new run."""
        self._stop_event.clear()
        self._pause_event.set()
        self._has_moved_from_zero = False
        logger.info("Kill switch reset.")

    def add_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to run upon kill switch trigger."""
        self._callbacks.append(callback)

    def start_listener(self) -> None:
        """Start hotkey listener in a background daemon thread."""
        if self._running:
            return
        self._running = True
        self._listener_thread = threading.Thread(target=self._hotkey_poll_loop, daemon=True)
        self._listener_thread.start()
        logger.info("Kill switch hotkey listener started (monitoring Ctrl+Alt+X).")

    def stop_listener(self) -> None:
        """Stop background listener."""
        self._running = False
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=1.0)
        logger.info("Kill switch hotkey listener stopped.")

    def _hotkey_poll_loop(self) -> None:
        """Poll for Ctrl+Alt+X using Win32 API GetAsyncKeyState (reliable, zero extra dependencies)."""
        import ctypes
        user32 = ctypes.windll.user32
        VK_CONTROL = 0x11
        VK_MENU = 0x12  # Alt
        VK_X = 0x58

        while self._running:
            try:
                # Check if Ctrl, Alt, and X are all down
                ctrl_down = (user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0
                alt_down = (user32.GetAsyncKeyState(VK_MENU) & 0x8000) != 0
                x_down = (user32.GetAsyncKeyState(VK_X) & 0x8000) != 0

                if ctrl_down and alt_down and x_down:
                    logger.warning("Ctrl+Alt+X detected via Win32 GetAsyncKeyState!")
                    self.trigger("Ctrl+Alt+X hotkey pressed")
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error in hotkey poll loop: {e}")
            time.sleep(0.05)


# Global singleton instance
kill_switch = KillSwitch()
