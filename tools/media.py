"""Media & Volume Tools: Control system audio and media playback on Windows."""

import time
import logging
from typing import Dict, Any

try:
    import pyautogui
    pyautogui.PAUSE = 0.01
except ImportError:
    pyautogui = None

logger = logging.getLogger("desktop_agent.tools.media")

ACTION_KEY_MAP = {
    "play_pause": "playpause",
    "play": "playpause",
    "pause": "playpause",
    "resume": "playpause",
    "next": "nexttrack",
    "next_track": "nexttrack",
    "skip": "nexttrack",
    "prev": "prevtrack",
    "prev_track": "prevtrack",
    "previous": "prevtrack",
    "stop": "stop",
    "mute": "volumemute",
    "unmute": "volumemute",
    "toggle_mute": "volumemute",
    "volume_up": "volumeup",
    "volume_down": "volumedown",
    "louder": "volumeup",
    "quieter": "volumedown",
}


def media_control(action: str) -> Dict[str, Any]:
    """Execute a media playback or volume command on Windows.
    
    Supported actions:
      'play_pause', 'next', 'prev', 'stop', 'volume_up', 'volume_down', 'mute'
    """
    act = (action or "").strip().lower().replace(" ", "_").replace("-", "_")
    key_name = ACTION_KEY_MAP.get(act)

    if not key_name:
        return {
            "success": False,
            "error": f"Unknown media action: '{action}'. Supported: {list(set(ACTION_KEY_MAP.keys()))}",
        }

    if not pyautogui:
        return {"success": False, "error": "pyautogui is required for media key control."}

    try:
        if act in ("volume_up", "louder"):
            pyautogui.press("volumeup", presses=5)
            msg = "Volume increased."
        elif act in ("volume_down", "quieter"):
            pyautogui.press("volumedown", presses=5)
            msg = "Volume decreased."
        else:
            pyautogui.press(key_name)
            msg = f"Media command '{act}' sent."

        return {"success": True, "action": act, "message": msg}
    except Exception as e:
        logger.error(f"Failed to execute media action '{act}': {e}")
        return {"success": False, "error": str(e)}


def set_volume(level: int) -> Dict[str, Any]:
    """Set master system volume to a percentage (0 to 100)."""
    target = max(0, min(100, int(level)))

    if not pyautogui:
        return {"success": False, "error": "pyautogui is required to adjust volume."}

    try:
        # Fast calibration: press volumedown 50 times (each step is 2%) to reach 0%, then press volumeup target//2 times
        old_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0.005
        pyautogui.press("volumedown", presses=52)
        if target > 0:
            up_presses = max(1, round(target / 2))
            pyautogui.press("volumeup", presses=up_presses)
        pyautogui.PAUSE = old_pause

        return {
            "success": True,
            "target_volume": target,
            "message": f"Volume set to {target}%.",
        }
    except Exception as e:
        logger.error(f"Error setting volume to {target}: {e}")
        return {"success": False, "error": str(e)}
