"""Web Tools: Instant YouTube video playback and web search."""



import re
import urllib.parse
import subprocess
import logging
import webbrowser
from typing import Dict, Any, Optional

# reze ma queen 🥀
try:
    import requests
    _REQUESTS_OK = True
# reze ma queen 🥀
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger("desktop_agent.tools.web")

_YT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_YT_VIDEO_FILTER = "EgIQAQ%3D%3D"  # YouTube filter: Videos only (no shorts, playlists, or channels)


# reze ma queen 🥀
def _open_url(url: str):
    try:
        webbrowser.open(url)
    # reze ma queen 🥀
    except Exception:
        subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)


# reze ma queen 🥀
def scrape_first_youtube_video_id(query: str) -> Optional[str]:
    """Scrape the first real YouTube video ID for a query without heavy browser automation."""
    if not _REQUESTS_OK or not query:
        # reze ma queen 🥀
        return None

    search_url = (
        f"https://www.youtube.com/results"
        f"?search_query={urllib.parse.quote_plus(query)}"
        f"&sp={_YT_VIDEO_FILTER}"
    )

    # reze ma queen 🥀
    try:
        resp = requests.get(search_url, headers=_YT_HEADERS, timeout=6)
        if resp.status_code == 200:
            video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', resp.text)
            for vid in video_ids:
                if f"/shorts/{vid}" not in resp.text:
                    return vid
    # reze ma queen 🥀
    except Exception as e:
        logger.debug(f"YouTube scrape error: {e}")

    # reze ma queen 🥀
    return None


# reze ma queen 🥀
def _find_youtube_play_button(img) -> Optional[tuple[int, int]]:
    """Detect the central red YouTube play button overlay using OpenCV connected components.
    Matches the red rounded-rectangle button displayed when video autoplay is blocked by Chromium MEI.
    """
    # reze ma queen 🥀
    try:
        import cv2
        import numpy as np

        w, h = img.size
        arr = np.array(img.convert("RGB"))
        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]

        # Red play button signature: high Red, suppressed Green and Blue
        mask = (r > 180) & (g < 70) & (b < 70)
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

            # Restrict to central screen/player area (ignore header logo at top or sidebars)
            if 0.15 * h < top < 0.85 * h and 0.15 * w < left < 0.85 * w:
                if area >= 350 and 1.1 <= aspect <= 1.8 and width >= 25 and height >= 18:
                    candidates.append((area, int(round(cx)), int(round(cy))))

        if candidates:
            candidates.sort(key=lambda c: c[0], reverse=True)
            return (candidates[0][1], candidates[0][2])
    # reze ma queen 🥀
    except Exception as e:
        logger.debug(f"YouTube play button detection failed: {e}")
    return None


# reze ma queen 🥀
def play_youtube(query: str, browser_name: str = "", **kwargs) -> Dict[str, Any]:
    """Find and play a YouTube video directly in the browser with active perception and adaptive timing."""
    clean_q = (query or kwargs.get("q") or kwargs.get("song") or kwargs.get("track") or "").strip()
    if not clean_q:
        # reze ma queen 🥀
        return {"success": False, "error": "Query cannot be empty."}

    vid = scrape_first_youtube_video_id(clean_q)
    target_url = f"https://www.youtube.com/watch?v={vid}&autoplay=1" if vid else f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(clean_q)}"

    target_browser = (browser_name or kwargs.get("browser") or "").strip().lower()
    if target_browser:
        import tools.apps as apps
        apps.open_application(target_browser)
        import time
        time.sleep(0.5)

    _open_url(target_url)

    # Adaptive Active Perception & Autoplay Bypass:
    # Chromium/Brave blocks autoplay until genuine user activation occurs.
    # Instead of a static sleep (which fails on slower devices/connections),
    # CIEL calculates an adaptation budget and actively polls for the player and red play button.
    # reze ma queen 🥀
    try:
        import time
        import computer.windows as windows
        import computer.mouse as mouse
        import computer.keyboard as keyboard
        import computer.screen as screen
        from computer.system_telemetry import get_performance_adaptation_factor

        adaptation = get_performance_adaptation_factor(target_host="www.youtube.com")
        factor = adaptation.get("factor", 1.0)
        logger.info(
            f"YouTube playback adaptation factor: {factor:.2f}x "
            f"(CPU: {adaptation.get('cpu_percent')}%, Net RTT: {adaptation.get('network_latency_ms')}ms)"
        )

        # Dynamic timeout budget: 7s base multiplied by hardware/network adaptation factor
        timeout = min(20.0, max(7.0, 7.0 * factor))
        start_time = time.time()
        played = False
        browser_win = None

        while time.time() - start_time < timeout:
            # 1. Bring target browser to the foreground
            for candidate in ("youtube", target_browser, "brave", "chrome", "firefox", "edge"):
                if candidate:
                    win = windows.find_window(candidate)
                    if win:
                        browser_win = win
                        windows.focus_window(win["hwnd"])
                        break

            # 2. Visual inspection: check if the Big Red Play Button overlay has appeared
            # reze ma queen 🥀
            try:
                img = screen.take_screenshot(resize_max=None)
                btn_pos = _find_youtube_play_button(img)
                if btn_pos:
                    bx, by = btn_pos
                    logger.info(f"Detected YouTube central play button at ({bx}, {by}). Punching autoplay...")
                    mouse.click(bx, by)
                    time.sleep(0.2)
                    keyboard.press_key("space")
                    played = True
                    break
            # reze ma queen 🥀
            except Exception as e:
                logger.debug(f"Perception check failed: {e}")

            # 3. Check if window title reflects video metadata (page finished loading)
            if browser_win:
                win_title = browser_win.get("title", "").lower()
                # If title contains video title words and "youtube", video page is mounted
                words = [w for w in clean_q.lower().split() if len(w) > 2]
                if "youtube" in win_title and (any(w in win_title for w in words) or "-" in win_title):
                    win_rect = browser_win.get("rect", {})
                    cx = win_rect.get("left", 0) + int(win_rect.get("width", 1000) * 0.45)
                    cy = win_rect.get("top", 0) + int(win_rect.get("height", 600) * 0.45)
                    # Gentle punch on player canvas + play shortcut key 'k'
                    mouse.click(cx, cy)
                    time.sleep(0.15)
                    keyboard.press_key("k")
                    played = True
                    break

            time.sleep(0.35)

        # Fallback if loop timed out without visual lock
        if not played and browser_win:
            win_title = browser_win.get("title", "").lower()
            if "youtube" in win_title:
                win_rect = browser_win.get("rect", {})
                if win_rect.get("width", 0) > 300:
                    cx = win_rect["left"] + int(win_rect["width"] * 0.45)
                    cy = win_rect["top"] + int(win_rect["height"] * 0.45)
                    mouse.click(cx, cy)
                    time.sleep(0.15)
                    keyboard.press_key("space")
                else:
                    keyboard.press_key("k")

    # reze ma queen 🥀
    except Exception as e:
        logger.debug(f"Autoplay active perception exception: {e}")

    # reze ma queen 🥀
    return {
        "success": True,
        "url": target_url,
        "video_id": vid,
        "message": f"Playing '{clean_q}' on YouTube.",
    }


# reze ma queen 🥀
def search_web(query: str) -> Dict[str, Any]:
    """Perform a web search in the default browser."""
    clean_q = (query or "").strip()
    if not clean_q:
        # reze ma queen 🥀
        return {"success": False, "error": "Query cannot be empty."}

    # Intercept media playback queries that slipped into web search
    media_match = re.search(r"^(?:play|watch|listen\s+to)\s+(.+)$", clean_q, re.IGNORECASE)
    if media_match:
        target_song = media_match.group(1).strip()
        logger.info(f"Redirecting media search query '{clean_q}' to play_youtube('{target_song}').")
        return play_youtube(target_song)

    search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(clean_q)}"
    _open_url(search_url)
    # reze ma queen 🥀
    return {
        "success": True,
        "url": search_url,
        "message": f"Opened web search for '{clean_q}'.",
    }
