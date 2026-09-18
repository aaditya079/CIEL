"""Game launcher and updater integrations for Steam and Epic Games."""

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
import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("desktop_agent.tools.games")

# Common Steam App IDs for quick launching
STEAM_GAMES = {
    "csgo": "730",
    "cs2": "730",
    "counter strike": "730",
    "dota": "570",
    "dota 2": "570",
    "tf2": "440",
    "team fortress": "440",
    "apex": "1172470",
    "apex legends": "1172470",
    "pubg": "578080",
    "destiny 2": "1085660",
    "cyberpunk": "1091500",
    "gta": "271590",
    "gta v": "271590",
    "rust": "252490",
    "helldivers": "553850",
    "helldivers 2": "553850",
}


def open_steam_action(action: str = "downloads") -> Dict[str, Any]:
    """Execute a Steam client protocol command."""
    act = action.lower().strip()
    protocol_urls = {
        "downloads": "steam://open/downloads",
        "update": "steam://open/downloads",
        "updates": "steam://open/downloads",
        "library": "steam://open/games",
        "games": "steam://open/games",
        "friends": "steam://open/friends",
        "news": "steam://open/news",
        "settings": "steam://open/settings",
        "main": "steam://open/main",
    }
    url = protocol_urls.get(act, "steam://open/downloads")
    try:
        os.startfile(url)
        msg = f"Opened Steam {act} page."
        return {
            "success": True,
            "url": url,
            "message": msg,
            "spoken": f"Opening Steam {act}.",
        }
    except Exception as e:
        logger.error(f"Failed to open Steam protocol {url}: {e}")
        return {"success": False, "error": str(e), "message": f"Could not launch Steam: {e}"}


def launch_game(game_name_or_id: str) -> Dict[str, Any]:
    """Launch a game by name or Steam App ID."""
    clean = str(game_name_or_id).lower().strip()
    app_id = STEAM_GAMES.get(clean, clean)

    if app_id.isdigit():
        url = f"steam://run/{app_id}"
        try:
            os.startfile(url)
            msg = f"Launching Steam game (ID: {app_id})."
            return {"success": True, "app_id": app_id, "message": msg, "spoken": f"Launching game."}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"Failed to launch game: {e}"}
    else:
        # Try generic protocol launch
        try:
            os.startfile(f"steam://open/games")
            return {
                "success": True,
                "message": f"Game '{clean}' not in shortcut catalog. Opened Steam Library.",
                "spoken": "Opened Steam library.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def game_control(action: str, target: Optional[str] = None) -> Dict[str, Any]:
    """Unified game control tool."""
    act = str(action).lower().strip()
    if act in ("update", "updates", "downloads"):
        return open_steam_action("downloads")
    elif act in ("library", "games"):
        return open_steam_action("games")
    elif act in ("launch", "run", "play") and target:
        return launch_game(target)
    elif act == "epic":
        try:
            os.startfile("com.epicgames.launcher://apps")
            return {"success": True, "message": "Opened Epic Games Launcher.", "spoken": "Opening Epic Games."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return open_steam_action(act)
