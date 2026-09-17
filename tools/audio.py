"""Windows audio device and sound settings management tools."""

import os
import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("desktop_agent.tools.audio")


def open_sound_settings(panel: str = "sound") -> Dict[str, Any]:
    """Launch native Windows Sound Settings or legacy mixer."""
    p = str(panel).lower().strip()
    if p in ("mixer", "volume_mixer", "apps"):
        target = "ms-settings:apps-volume"
        desc = "Volume Mixer"
    elif p in ("devices", "sound", "output", "input"):
        target = "ms-settings:sound"
        desc = "Sound Settings"
    else:
        target = "ms-settings:sound"
        desc = "Sound Settings"

    try:
        os.startfile(target)
        return {
            "success": True,
            "target": target,
            "message": f"Opened Windows {desc}.",
            "spoken": f"Opening {desc}.",
        }
    except Exception as e:
        logger.error(f"Failed to open {target}: {e}")
        return {"success": False, "error": str(e), "message": f"Could not launch sound settings: {e}"}


def audio_control(action: str = "settings") -> Dict[str, Any]:
    """Unified audio control dispatcher."""
    act = str(action).lower().strip()
    if act in ("mixer", "volume mixer"):
        return open_sound_settings("mixer")
    return open_sound_settings("sound")
