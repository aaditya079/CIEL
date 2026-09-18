"""Safe mouse control and interaction for Desktop Agent."""

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
from typing import Tuple, Optional
import pyautogui
import win32api
import win32con

from safety.kill_switch import kill_switch
from computer.screen import get_screen_dimensions
from computer.desktop import run_on_input_desktop

logger = logging.getLogger("desktop_agent.computer.mouse")


def ensure_cursor_away_from_corner() -> None:
    """Ensure PyAutoGUI failsafe is disabled to prevent false-positives in background subshells."""
    pyautogui.FAILSAFE = False


def _clamp_coordinates(x: int, y: int) -> Tuple[int, int]:
    """Ensure coordinates stay strictly within active screen bounds."""
    width, height = get_screen_dimensions()
    cx = max(0, min(int(x), width - 1))
    cy = max(0, min(int(y), height - 1))
    return cx, cy


def get_mouse_position() -> Tuple[int, int]:
    """Get current mouse cursor position on input desktop."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    try:
        def _get_pos():
            pos = win32api.GetCursorPos()
            return int(pos[0]), int(pos[1])
        return run_on_input_desktop(_get_pos)
    except Exception:
        pos = pyautogui.position()
        return int(pos.x), int(pos.y)


def move_to(x: int, y: int, duration: float = 0.15) -> Tuple[int, int]:
    """Smoothly move mouse cursor to target coordinates on the interactive desktop."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    target_x, target_y = _clamp_coordinates(x, y)
    logger.debug(f"Moving mouse to ({target_x}, {target_y})")

    def _do_move():
        try:
            win32api.SetCursorPos((target_x, target_y))
        except Exception:
            pyautogui.moveTo(target_x, target_y, duration=duration)

    run_on_input_desktop(_do_move)
    kill_switch.check()
    return target_x, target_y


def click(
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left",
    clicks: int = 1,
    **kwargs
) -> Tuple[int, int]:
    """Click mouse button at specified or current coordinates, supporting multiple clicks."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    if x is not None and y is not None:
        target_x, target_y = move_to(x, y, duration=0.1)
    else:
        target_x, target_y = get_mouse_position()

    num_clicks = max(1, int(clicks)) if clicks is not None else 1
    logger.debug(f"Clicking {button} button {num_clicks} time(s) at ({target_x}, {target_y})")

    def _do_click():
        for _ in range(num_clicks):
            try:
                win32api.SetCursorPos((target_x, target_y))
                time.sleep(0.02)
                btn = button.lower()
                if btn == "left":
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, target_x, target_y, 0, 0)
                    time.sleep(0.04)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, target_x, target_y, 0, 0)
                elif btn == "right":
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, target_x, target_y, 0, 0)
                    time.sleep(0.04)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, target_x, target_y, 0, 0)
                elif btn == "middle":
                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, target_x, target_y, 0, 0)
                    time.sleep(0.04)
                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, target_x, target_y, 0, 0)
            except Exception:
                pyautogui.click(x=target_x, y=target_y, button=button)
            if num_clicks > 1:
                time.sleep(0.05)

    run_on_input_desktop(_do_click)
    kill_switch.check()
    return target_x, target_y


def double_click(x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> Tuple[int, int]:
    """Double-click mouse left button."""
    target_x, target_y = click(x=x, y=y, button="left", clicks=2, **kwargs)
    return target_x, target_y


def right_click(x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> Tuple[int, int]:
    """Right-click mouse button."""
    return click(x=x, y=y, button="right", **kwargs)


def scroll(clicks: int = 1, x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> None:
    """Scroll mouse wheel vertically (positive = up, negative = down)."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    if x is not None and y is not None:
        target_x, target_y = move_to(x, y, duration=0.1)
    else:
        target_x, target_y = get_mouse_position()

    logger.debug(f"Scrolling {clicks} clicks at ({target_x}, {target_y})")

    def _do_scroll():
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, target_x, target_y, clicks * 120, 0)
        except Exception:
            pyautogui.scroll(clicks)

    run_on_input_desktop(_do_scroll)
    kill_switch.check()


def drag(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5, **kwargs) -> None:
    """Click and drag from start position to target position."""
    kill_switch.check()
    ensure_cursor_away_from_corner()
    start_x, start_y = move_to(from_x, from_y, duration=0.15)
    end_x, end_y = _clamp_coordinates(to_x, to_y)

    logger.debug(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")

    def _do_drag():
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=duration, button="left")

    run_on_input_desktop(_do_drag)
    kill_switch.check()

