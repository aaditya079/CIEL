"""Windows Desktop and WindowStation attachment helper.

Ensures that desktop capture, window enumeration, and UI Automation function
cleanly by executing on threads attached to the interactive input desktop (WinSta0\\Default).
"""

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


import ctypes
import threading
import logging
from typing import Callable, Any, TypeVar

logger = logging.getLogger("desktop_agent.computer.desktop")

DESKTOP_ACCESS = 0x01FF  # DESKTOP_ALL_ACCESS

T = TypeVar("T")


def attach_current_thread_to_input_desktop() -> bool:
    """Attempt to attach the calling thread to the active user input desktop."""
    user32 = ctypes.windll.user32
    try:
        hdesk = user32.OpenInputDesktop(0, False, DESKTOP_ACCESS)
        if not hdesk:
            return False
        return bool(user32.SetThreadDesktop(hdesk))
    except Exception as e:
        logger.debug(f"Failed to attach thread to input desktop: {e}")
        return False


def run_on_input_desktop(func: Callable[..., T], *args, **kwargs) -> T:
    """Execute a callable inside a dedicated clean thread attached to the interactive user desktop.
    
    This guarantees that Windows restrictions on SetThreadDesktop (which fails if
    the thread has existing windows or COM objects) never interfere with screenshot
    capture or window enumeration.
    """
    result = [None]
    exception = [None]

    def _worker():
        try:
            attach_current_thread_to_input_desktop()
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join()

    if exception[0] is not None:
        raise exception[0]

    return result[0]
