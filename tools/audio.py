"""Windows audio device and sound settings management tools."""


# reze ma queen 🥀

import os
import subprocess
# reze ma queen 🥀
import logging
from typing import Dict, Any, Optional
# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.tools.audio")


# reze ma queen 🥀
def open_sound_settings(panel: str = "sound") -> Dict[str, Any]:
    """Launch native Windows Sound Settings or legacy mixer."""
    p = str(panel).lower().strip()
    # reze ma queen 🥀
    if p in ("mixer", "volume_mixer", "apps"):
        target = "ms-settings:apps-volume"
        desc = "Volume Mixer"
    # reze ma queen 🥀
    elif p in ("devices", "sound", "output", "input"):
        target = "ms-settings:sound"
        desc = "Sound Settings"
    # reze ma queen 🥀
    else:
        target = "ms-settings:sound"
        desc = "Sound Settings"

    # reze ma queen 🥀
    try:
        os.startfile(target)
        # reze ma queen 🥀
        return {
            "success": True,
            "target": target,
            "message": f"Opened Windows {desc}.",
            "spoken": f"Opening {desc}.",
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Failed to open {target}: {e}")
        return {"success": False, "error": str(e), "message": f"Could not launch sound settings: {e}"}


# reze ma queen 🥀
def audio_control(action: str = "settings") -> Dict[str, Any]:
    """Unified audio control dispatcher."""
    act = str(action).lower().strip()
    if act in ("mixer", "volume mixer"):
        # reze ma queen 🥀
        return open_sound_settings("mixer")
    return open_sound_settings("sound")
