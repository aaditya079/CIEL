"""Application launching, process inspection, and window resolution for Windows 11."""

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


import os
import time
import subprocess
import logging
from typing import List, Dict, Any, Optional

from safety.kill_switch import kill_switch
from computer.windows import find_window, focus_window, list_open_windows

logger = logging.getLogger("desktop_agent.tools.apps")

# Registry of known Windows apps and their launch schemes or executable aliases
KNOWN_APPS = {
    "spotify": {
        "protocols": ["spotify:"],
        "executables": ["spotify.exe"],
        "paths": [
            os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe"),
        ],
        "uwp": "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
    },
    "discord": {
        "protocols": ["discord:"],
        "executables": ["discord.exe"],
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Discord\Discord.exe"),
        ],
    },
    "steam": {
        "protocols": ["steam:"],
        "executables": ["steam.exe"],
        "paths": [
            r"C:\Program Files (x86)\Steam\Steam.exe",
            r"C:\Program Files\Steam\Steam.exe",
        ],
    },
    "notepad": {
        "executables": ["notepad.exe"],
    },
    "calculator": {
        "protocols": ["calculator:"],
        "executables": ["calc.exe"],
    },
    "calc": {
        "protocols": ["calculator:"],
        "executables": ["calc.exe"],
    },
    "settings": {
        "protocols": ["ms-settings:"],
    },
    "chrome": {
        "executables": ["chrome.exe"],
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
    },
    "brave": {
        "executables": ["brave.exe"],
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
    },
    "brave-browser": {
        "executables": ["brave.exe"],
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
    },
    "brave browser": {
        "executables": ["brave.exe"],
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
    },
    "firefox": {
        "executables": ["firefox.exe"],
        "paths": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
    },
    "vscode": {
        "executables": ["code.cmd", "code.exe"],
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ],
    },
    "code": {
        "executables": ["code.cmd", "code.exe"],
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ],
    },
    "edge": {
        "protocols": ["microsoft-edge:"],
        "executables": ["msedge.exe"],
    },
    "explorer": {
        "executables": ["explorer.exe"],
    },
}


def get_running_processes() -> List[Dict[str, Any]]:
    """Retrieve list of currently running processes on Windows."""
    kill_switch.check()
    processes = []
    try:
        cmd = 'Get-Process | Select-Object Id, ProcessName, MainWindowTitle | ConvertTo-Json -Compress'
        output = subprocess.check_output(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            text=True,
            timeout=5
        )
        import json
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
        for p in data:
            processes.append({
                "pid": p.get("Id"),
                "name": p.get("ProcessName", ""),
                "title": p.get("MainWindowTitle", ""),
            })
    except Exception as e:
        logger.error(f"Error fetching running processes: {e}")
    return processes


def is_app_running(app_name: str) -> bool:
    """Check if an application is currently running by process or window title."""
    app_lower = app_name.lower().strip()
    
    # Check open windows first
    for win in list_open_windows(only_visible=True):
        if app_lower in win["title"].lower():
            return True

    # Check processes
    for proc in get_running_processes():
        if app_lower in proc["name"].lower() or (proc["title"] and app_lower in proc["title"].lower()):
            return True

    return False


def open_application(
    app_name: str = "",
    application_name: str = "",
    name: str = "",
    wait_timeout: float = 8.0,
    **kwargs
) -> bool:
    """Open an application by friendly name, executable, or protocol URI.
    
    If the application is already running, brings its window to foreground.
    Accepts app_name, application_name, or name aliases.
    """
    kill_switch.check()
    target_raw = app_name or application_name or name or kwargs.get("app") or kwargs.get("program") or ""
    target_str = str(target_raw).strip()
    if not target_str:
        logger.error("open_application called without target application name.")
        return False

    norm_name = target_str.lower()
    logger.info(f"Opening application '{target_str}'...")

    # If already running, focus the window
    existing_win = find_window(norm_name)
    if existing_win:
        logger.info(f"App '{target_str}' already open; focusing existing window.")
        focus_window(existing_win["hwnd"])
        return True

    info = KNOWN_APPS.get(norm_name)

    # Strategy 1: Protocol URI (e.g. spotify:, ms-settings:, etc.)
    if info and "protocols" in info:
        for proto in info["protocols"]:
            try:
                os.startfile(proto)
                logger.info(f"Launched via protocol '{proto}'")
                _wait_for_window_or_process(norm_name, wait_timeout)
                return True
            except Exception as e:
                logger.debug(f"Protocol '{proto}' launch failed: {e}")

    # Strategy 2: Known explicit paths
    if info and "paths" in info:
        for p in info["paths"]:
            if os.path.exists(p.split()[0]):
                try:
                    subprocess.Popen(p, shell=True)
                    logger.info(f"Launched via explicit path '{p}'")
                    _wait_for_window_or_process(norm_name, wait_timeout)
                    return True
                except Exception as e:
                    logger.debug(f"Explicit path launch failed: {e}")

    # Strategy 3: Standard executables
    executables = (info.get("executables") if info else []) or [f"{norm_name}.exe", norm_name]
    for exe in executables:
        try:
            # Try launching with Start-Process via powershell or subprocess
            subprocess.Popen([exe], shell=True)
            logger.info(f"Launched via executable '{exe}'")
            _wait_for_window_or_process(norm_name, wait_timeout)
            return True
        except Exception as e:
            logger.debug(f"Executable '{exe}' launch failed: {e}")

    # Strategy 4: Windows start command
    try:
        os.system(f"start {norm_name}")
        _wait_for_window_or_process(norm_name, wait_timeout)
        return True
    except Exception as e:
        logger.error(f"Failed to open '{target_str}': {e}")
        return False


def _wait_for_window_or_process(app_name: str, timeout: float = 8.0) -> bool:
    """Wait for the application window or process to appear."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        kill_switch.check()
        if is_app_running(app_name):
            time.sleep(0.5)
            # Try to bring to foreground
            win = find_window(app_name)
            if win:
                focus_window(win["hwnd"])
            return True
        time.sleep(0.4)
    return False


def close_application(
    app_name: str = "",
    application_name: str = "",
    name: str = "",
    **kwargs
) -> bool:
    """Close an application gracefully or terminate its process."""
    kill_switch.check()
    target_raw = app_name or application_name or name or kwargs.get("app") or kwargs.get("program") or ""
    target_str = str(target_raw).strip()
    if not target_str:
        logger.error("close_application called without target application name.")
        return False

    norm_name = target_str.lower()
    logger.info(f"Closing application '{target_str}'...")

    # First attempt graceful window close
    win = find_window(norm_name)
    if win:
        from computer.windows import close_window
        close_window(win["hwnd"])
        time.sleep(0.5)

    # Terminate process if still running
    exe_name = norm_name if norm_name.endswith(".exe") else f"{norm_name}.exe"
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", exe_name],
            capture_output=True,
            timeout=5
        )
        return True
    except Exception as e:
        logger.error(f"Failed to kill process {exe_name}: {e}")
        return False
