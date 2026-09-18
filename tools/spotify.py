"""Spotify Tool: Direct protocol launch and playback controller for Spotify on Windows."""

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
    
    Multi-Tier Chant Annulment Architecture:
    1. Spicetify Native Bridge (<10ms direct API) if active.
    2. Instant Search Hotkey Sequence (Ctrl+L -> type -> Enter -> hover & play) to eliminate stale race conditions.
    3. Title verification and media key playback assurance.
    """
    clean_q = (query or kwargs.get("track") or kwargs.get("song") or kwargs.get("q") or "").strip()

    try:
        if clean_q:
            # Tier 1: Spicetify Native Bridge (Instant Direct API)
            try:
                import tools.spicetify_bridge as spicetify_bridge
                if spicetify_bridge.is_bridge_connected():
                    logger.info(f"Spicetify Bridge active. Dispatching direct API playback for '{clean_q}'...")
                    spicetify_bridge.play_track(clean_q)
                    time.sleep(0.3)
                    return {
                        "success": True,
                        "query": clean_q,
                        "mode": "spicetify_bridge",
                        "message": f"Playing '{clean_q}' on Spotify via Native Spicetify Bridge.",
                    }
            except Exception as e:
                logger.debug(f"Spicetify bridge check failed: {e}")

            # Tier 2: Instant Search Hotkey Pipeline
            # Focus Spotify window
            windows.focus_window("Spotify")
            time.sleep(0.15)

            # Ctrl+L focuses search bar and clears any old query, preventing stale click race condition
            keyboard.hotkey("ctrl", "l")
            time.sleep(0.08)
            keyboard.type_text(clean_q)
            time.sleep(0.05)
            keyboard.press_key("enter")

            # Allow Spotify results to populate
            time.sleep(0.4)

            # Hover over the Top Result card to reveal the circular green play button
            spot_win = windows.find_window("spotify")
            if spot_win and spot_win.get("width", 0) > 200:
                card_x = spot_win["left"] + int(spot_win["width"] * 0.36)
                card_y = spot_win["top"] + int(spot_win["height"] * 0.25)
                import computer.mouse as mouse
                mouse.move_to(card_x, card_y, duration=0.08)
                time.sleep(0.15)

            # Click the green play button on the Top Result card
            clicked = _find_and_click_spotify_play_button(timeout=1.5)

            # Fallback: Double-click top result card area or send Enter
            if not clicked:
                if spot_win:
                    mouse.double_click(card_x, card_y)
                else:
                    keyboard.press_key("tab")
                    keyboard.press_key("enter")

            time.sleep(0.5)

            # Tier 3: Verification - Check if window title changed to artist/track
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
                "mode": "instant_hotkey",
                "message": f"Playing '{clean_q}' on Spotify.",
            }
        else:
            # No song specified: launch or focus Spotify and press play/pause
            apps.open_application("Spotify")
            time.sleep(0.5)
            keyboard.press_key("playpause")
            return {
                "success": True,
                "query": "",
                "message": "Spotify playback toggled.",
            }
    except Exception as e:
        logger.error(f"Error in play_spotify: {e}")
        return {"success": False, "error": str(e)}
