"""Spotify Tool: Direct protocol launch and playback controller for Spotify on Windows."""

import time
import urllib.parse
import subprocess
import logging
from typing import Dict, Any

import computer.windows as windows
import computer.keyboard as keyboard
import tools.apps as apps

logger = logging.getLogger("desktop_agent.tools.spotify")


def _find_and_click_spotify_play_button() -> bool:
    """Visually locate the bright green Spotify circular Play button in the top result card."""
    try:
        import numpy as np
        import computer.screen as screen
        import computer.mouse as mouse

        img = screen.take_screenshot()
        w, h = img.size
        arr = np.array(img.convert("RGB"))

        # Spotify signature green: #1ed760 / #1db954 (G dominant, low R and B)
        mask = (arr[:, :, 1] > 170) & (arr[:, :, 0] < 85) & (arr[:, :, 2] < 125) & (arr[:, :, 1] > 1.2 * (arr[:, :, 0].astype(int) + arr[:, :, 2].astype(int)))

        # Search in the top-result region
        y1, y2 = int(0.10 * h), int(0.48 * h)
        x1, x2 = int(0.28 * w), int(0.82 * w)
        sub = mask[y1:y2, x1:x2]
        pts = np.argwhere(sub)

        if len(pts) > 25:
            cy = int(pts[:, 0].mean()) + y1
            cx = int(pts[:, 1].mean()) + x1
            logger.info(f"Detected Spotify green play button at ({cx}, {cy}). Clicking to play...")
            mouse.click(cx, cy)
            return True
    except Exception as e:
        logger.debug(f"Visual play button detection failed: {e}")
    return False


def play_spotify(query: str = "") -> Dict[str, Any]:
    """Launch Spotify and play requested track, artist, or resume playback.
    
    Uses Windows spotify: URI scheme to jump straight to search results,
    then locates the green Play button or top result card to start playback.
    """
    clean_q = (query or "").strip()

    try:
        if clean_q:
            # Use Windows Spotify URI protocol to immediately open search in Spotify
            spotify_uri = f"spotify:search:{urllib.parse.quote(clean_q)}"
            subprocess.Popen(["cmd", "/c", "start", "", spotify_uri], shell=False)

            # Allow Spotify window to focus and render search results
            time.sleep(1.5)
            windows.focus_window("Spotify")
            time.sleep(0.5)

            # 1. Try to click the green circular Play button on the Top Result card
            clicked = _find_and_click_spotify_play_button()

            # 2. Fallback: Double click top result card area or send keyboard play sequence
            if not clicked:
                open_wins = windows.list_open_windows()
                spot_win = next((w for w in open_wins if "spotify" in w.get("title", "").lower()), None)
                if spot_win and spot_win.get("width", 0) > 200:
                    card_x = spot_win["left"] + int(spot_win["width"] * 0.45)
                    card_y = spot_win["top"] + int(spot_win["height"] * 0.23)
                    import computer.mouse as mouse
                    mouse.double_click(card_x, card_y)
                else:
                    keyboard.press_key("tab")
                    keyboard.press_key("enter")

            # Brief pause and ensure playback state
            time.sleep(0.5)

            return {
                "success": True,
                "query": clean_q,
                "message": f"Playing '{clean_q}' on Spotify.",
            }
        else:
            # No song specified: launch or focus Spotify and press play/pause
            apps.open_application("Spotify")
            time.sleep(1.0)
            keyboard.press_key("playpause")
            return {
                "success": True,
                "query": "",
                "message": "Spotify playback toggled.",
            }
    except Exception as e:
        logger.error(f"Error in play_spotify: {e}")
        return {"success": False, "error": str(e)}
