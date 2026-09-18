"""Desktop control tools for Windows display, workstation lock, and window state."""

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
import os
import re
import urllib.parse
import subprocess
import logging
from typing import Dict, Any, Optional

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger("desktop_agent.tools.desktop_control")


def lock_screen() -> Dict[str, Any]:
    """Lock the Windows workstation immediately."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return {"success": True, "message": "Workstation locked."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_desktop() -> Dict[str, Any]:
    """Minimize all windows and show desktop (Win+D)."""
    if pyautogui:
        pyautogui.hotkey("win", "d")
        return {"success": True, "message": "Showing desktop."}
    return {"success": False, "error": "pyautogui unavailable."}


def open_task_manager() -> Dict[str, Any]:
    """Launch Windows Task Manager."""
    if pyautogui:
        pyautogui.hotkey("ctrl", "shift", "esc")
        return {"success": True, "message": "Task Manager opened."}
    return {"success": False, "error": "pyautogui unavailable."}


def open_file_explorer() -> Dict[str, Any]:
    """Open Windows File Explorer (Win+E)."""
    if pyautogui:
        pyautogui.hotkey("win", "e")
        return {"success": True, "message": "File Explorer opened."}
    return {"success": False, "error": "pyautogui unavailable."}


def open_system_settings() -> Dict[str, Any]:
    """Open Windows Settings app (Win+I)."""
    if pyautogui:
        pyautogui.hotkey("win", "i")
        return {"success": True, "message": "Settings opened."}
    return {"success": False, "error": "pyautogui unavailable."}


def sleep_display() -> Dict[str, Any]:
    """Turn off / sleep the monitors via Windows Win32 API."""
    try:
        # HWND_BROADCAST = 0xFFFF, WM_SYSCOMMAND = 0x0112, SC_MONITORPOWER = 0xF170, 2 = Power Off
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
        return {"success": True, "message": "Display put to sleep."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def window_action(action: str) -> Dict[str, Any]:
    """Control window state on Windows.
    
    Supported: 'maximize', 'minimize', 'snap_left', 'snap_right', 'fullscreen', 'switch_window'
    """
    act = (action or "").strip().lower().replace(" ", "_")
    if not pyautogui:
        return {"success": False, "error": "pyautogui unavailable."}

    try:
        if act == "maximize":
            pyautogui.hotkey("win", "up")
        elif act == "minimize":
            pyautogui.hotkey("win", "down")
        elif act == "snap_left":
            pyautogui.hotkey("win", "left")
        elif act == "snap_right":
            pyautogui.hotkey("win", "right")
        elif act == "fullscreen":
            pyautogui.press("f11")
        elif act in ("switch_window", "switch"):
            pyautogui.hotkey("alt", "tab")
        else:
            return {"success": False, "error": f"Unknown window action: {action}"}

        return {"success": True, "action": act, "message": f"Window action '{act}' executed."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_weather(city: str = "") -> Dict[str, Any]:
    """Fetch current weather report for a specified city (or auto-detect location)."""
    target = (city or "").strip()
    query_city = urllib.parse.quote_plus(target) if target else ""

    if _REQUESTS_OK:
        try:
            url = f"https://wttr.in/{query_city}?format=%l:+%t,+%C"
            r = requests.get(url, headers={"User-Agent": "curl/7.68.0"}, timeout=5)
            if r.status_code == 200 and r.text.strip():
                clean_text = r.text.strip()
                # e.g. "Delhi: +32°C, Sunny"
                clean_text = re.sub(r"[^\x00-\x7F]+", "°", clean_text)
                spoken = clean_text.replace(":", " is").replace("°C", " degrees Celsius")
                return {
                    "success": True,
                    "city": target or "Local",
                    "report": clean_text,
                    "spoken": f"The weather in {spoken}.",
                    "message": clean_text,
                }
        except Exception as e:
            logger.debug(f"wttr.in error: {e}")

    # Fallback to browser search
    search_q = f"weather in {target}" if target else "weather"
    subprocess.Popen(["cmd", "/c", "start", "", f"https://www.google.com/search?q={urllib.parse.quote_plus(search_q)}"], shell=False)
    return {
        "success": True,
        "city": target,
        "message": f"Opened weather search for '{target}'.",
        "spoken": f"Here is the weather for {target}." if target else "Here is your weather.",
    }


def set_wallpaper(image_path: str) -> Dict[str, Any]:
    """Set the Windows desktop background wallpaper."""
    path = os.path.abspath(os.path.expanduser(image_path))
    if not os.path.exists(path):
        return {"success": False, "error": f"Image file not found: {path}"}

    try:
        # SPI_SETDESKWALLPAPER = 20, SPIF_UPDATEINIFILE = 1, SPIF_SENDCHANGE = 2 (1|2 = 3)
        res = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(path), 3)
        if res:
            return {"success": True, "message": f"Desktop wallpaper set to {os.path.basename(path)}."}
        else:
            return {"success": False, "error": "SystemParametersInfoW returned 0."}
    except Exception as e:
        return {"success": False, "error": str(e)}
