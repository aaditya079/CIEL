"""Window management, enumeration, and foreground focus for Desktop Agent."""

import time
import logging
from typing import List, Dict, Any, Optional
import win32gui
import win32process
import win32con
import win32api

from safety.kill_switch import kill_switch
from computer.desktop import run_on_input_desktop

logger = logging.getLogger("desktop_agent.computer.windows")


def _get_active_window_internal() -> Dict[str, Any]:
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return {"hwnd": 0, "title": "", "rect": None, "pid": 0}

    title = win32gui.GetWindowText(hwnd)
    rect = win32gui.GetWindowRect(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    return {
        "hwnd": hwnd,
        "title": title,
        "rect": {
            "left": rect[0],
            "top": rect[1],
            "right": rect[2],
            "bottom": rect[3],
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1],
        },
        "pid": pid,
    }


def get_active_window(check_kill_switch: bool = True) -> Dict[str, Any]:
    """Get the currently focused foreground window details."""
    if check_kill_switch:
        kill_switch.check()
    return run_on_input_desktop(_get_active_window_internal)


def _list_open_windows_internal(only_visible: bool = True) -> List[Dict[str, Any]]:
    windows = []

    def enum_cb(hwnd, extra):
        if only_visible and not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd).strip()
        if not title:
            return True

        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        if width <= 0 or height <= 0:
            return True

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        windows.append({
            "hwnd": hwnd,
            "title": title,
            "rect": {
                "left": rect[0],
                "top": rect[1],
                "right": rect[2],
                "bottom": rect[3],
                "width": width,
                "height": height,
            },
            "pid": pid,
        })
        return True

    win32gui.EnumWindows(enum_cb, None)
    return windows


def list_open_windows(only_visible: bool = True) -> List[Dict[str, Any]]:
    """List all open top-level application windows."""
    kill_switch.check()
    return run_on_input_desktop(_list_open_windows_internal, only_visible)


def find_window(query: str) -> Optional[Dict[str, Any]]:
    """Find a window whose title matches query (case-insensitive substring)."""
    q = query.lower()
    windows = list_open_windows(only_visible=True)
    for win in windows:
        if q in win["title"].lower():
            return win
    return None


def focus_window(title_or_hwnd: Any = None, title: Optional[str] = None) -> bool:
    """Bring target window to the foreground and focus it."""
    kill_switch.check()
    target = title if title is not None else title_or_hwnd
    if isinstance(target, int):
        hwnd = target
    else:
        target_str = str(target or "")
        win = find_window(target_str)
        if not win:
            # Fall back to process name match if window title changed (e.g. Spotify playing track)
            try:
                from tools.apps import get_running_processes
                procs = get_running_processes()
                target_lower = target_str.lower()
                matching_pids = {p["pid"] for p in procs if target_lower in p["name"].lower() and p.get("pid")}
                if matching_pids:
                    for w in list_open_windows(only_visible=True):
                        if w.get("pid") in matching_pids:
                            win = w
                            break
            except Exception:
                pass

        if not win:
            logger.warning(f"Window matching '{target_str}' not found.")
            return False
        hwnd = win["hwnd"]

    def _focus_internal():
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32gui.SetForegroundWindow(hwnd)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to focus window hwnd={hwnd}: {e}")
            return False

    res = run_on_input_desktop(_focus_internal)
    time.sleep(0.1)
    return res


def close_window(title_or_hwnd: Any) -> bool:
    """Send WM_CLOSE to gracefully close a window."""
    kill_switch.check()
    if isinstance(title_or_hwnd, int):
        hwnd = title_or_hwnd
    else:
        win = find_window(str(title_or_hwnd))
        if not win:
            return False
        hwnd = win["hwnd"]

    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        logger.info(f"Sent WM_CLOSE to hwnd={hwnd}")
        return True
    except Exception as e:
        logger.error(f"Failed to close window: {e}")
        return False
