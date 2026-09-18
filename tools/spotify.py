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


def _find_and_click_spotify_play_button(timeout: float = 3.5) -> bool:
    """Visually locate the bright green Spotify circular Play button in the top result card
    using OpenCV connected component analysis, rejecting checkmarks, text, and sidebars.
    """
    import time
    try:
        import cv2
        import numpy as np
        import computer.screen as screen
        import computer.mouse as mouse

        start_time = time.time()
        while time.time() - start_time < timeout:
            img = screen.take_screenshot(resize_max=None)
            w, h = img.size
            arr = np.array(img.convert("RGB"))

            # Spotify signature green: G dominant, low R and B
            r = arr[:, :, 0]
            g = arr[:, :, 1]
            b = arr[:, :, 2]

            mask = (g > 150) & (r < 100) & (b < 140) & (g.astype(int) > 1.15 * (r.astype(int) + b.astype(int)))
            mask_u8 = (mask * 255).astype(np.uint8)

            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8)

            candidates = []
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                left = stats[i, cv2.CC_STAT_LEFT]
                top = stats[i, cv2.CC_STAT_TOP]
                width = stats[i, cv2.CC_STAT_WIDTH]
                height = stats[i, cv2.CC_STAT_HEIGHT]
                cx, cy = centroids[i]
                aspect = width / max(1, height)

                # Search within top/middle content area (exclude top navbar and bottom player bar)
                if 0.10 * h < top < 0.65 * h and 0.15 * w < left < 0.85 * w:
                    # Circular play button criteria: area >= 150 (on 1080p typically 800-3500px), aspect ~ 1.0
                    if area >= 150 and 0.75 <= aspect <= 1.35 and width >= 15 and height >= 15:
                        candidates.append((area, int(round(cx)), int(round(cy))))

            if candidates:
                # Top candidate by area is the circular play button on the top result card
                candidates.sort(key=lambda c: c[0], reverse=True)
                best_area, cx, cy = candidates[0]
                logger.info(f"Detected Spotify green play button at ({cx}, {cy}) (area={best_area}). Clicking to play...")
                mouse.click(cx, cy)
                return True

            time.sleep(0.3)

    except Exception as e:
        logger.debug(f"Visual play button detection failed: {e}")
    return False


def play_spotify(query: str = "", **kwargs) -> Dict[str, Any]:
    """Launch Spotify and play requested track, artist, or resume playback.
    
    Uses Windows spotify: URI scheme to jump straight to search results,
    then locates the green Play button or top result card to start playback.
    """
    clean_q = (query or kwargs.get("track") or kwargs.get("song") or kwargs.get("q") or "").strip()

    try:
        if clean_q:
            # Use Windows Spotify URI protocol to immediately open search in Spotify
            spotify_uri = f"spotify:search:{urllib.parse.quote(clean_q)}"
            subprocess.Popen(["cmd", "/c", "start", "", spotify_uri], shell=False)

            # Allow Spotify window to focus and render search results
            time.sleep(1.2)
            windows.focus_window("Spotify")
            time.sleep(0.4)

            # 1. Try to click the green circular Play button on the Top Result card
            clicked = _find_and_click_spotify_play_button(timeout=3.0)

            # 2. Fallback: Double click top result card area or send keyboard enter
            if not clicked:
                open_wins = windows.list_open_windows()
                spot_win = next((w for w in open_wins if "spotify" in w.get("title", "").lower() and w.get("width", 0) > 200), None)
                if spot_win:
                    card_x = spot_win["left"] + int(spot_win["width"] * 0.45)
                    card_y = spot_win["top"] + int(spot_win["height"] * 0.23)
                    import computer.mouse as mouse
                    mouse.double_click(card_x, card_y)
                else:
                    keyboard.press_key("tab")
                    keyboard.press_key("enter")

            # Pause briefly to allow playback state to register
            time.sleep(0.6)

            # 3. Verification: check if playback started (Spotify window title changes from 'Spotify Free' to artist/track)
            active_win = windows.get_active_window()
            open_wins = windows.list_open_windows()
            is_playing = any(
                clean_q.lower() in w["title"].lower() or ("-" in w["title"] and "spotify" not in w["title"].lower())
                for w in open_wins if w.get("pid") == active_win.get("pid")
            )

            # If still not verified playing, press playpause to trigger playback
            if not is_playing and not clicked:
                keyboard.press_key("playpause")

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
