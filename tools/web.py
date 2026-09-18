"""Web Tools: Instant YouTube video playback and web search."""

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


import re
import urllib.parse
import subprocess
import logging
import webbrowser
from typing import Dict, Any, Optional

try:
    import requests
    _REQUESTS_OK = True
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


def _open_url(url: str):
    try:
        webbrowser.open(url)
    except Exception:
        subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)


def scrape_first_youtube_video_id(query: str) -> Optional[str]:
    """Scrape the first real YouTube video ID for a query without heavy browser automation."""
    if not _REQUESTS_OK or not query:
        return None

    search_url = (
        f"https://www.youtube.com/results"
        f"?search_query={urllib.parse.quote_plus(query)}"
        f"&sp={_YT_VIDEO_FILTER}"
    )

    try:
        resp = requests.get(search_url, headers=_YT_HEADERS, timeout=6)
        if resp.status_code == 200:
            video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', resp.text)
            for vid in video_ids:
                if f"/shorts/{vid}" not in resp.text:
                    return vid
    except Exception as e:
        logger.debug(f"YouTube scrape error: {e}")

    return None


def play_youtube(query: str, browser_name: str = "", **kwargs) -> Dict[str, Any]:
    """Find and play a YouTube video directly in the browser with autoplay blocker bypass."""
    clean_q = (query or kwargs.get("q") or kwargs.get("song") or kwargs.get("track") or "").strip()
    if not clean_q:
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

    # Autoplay Blocker Bypass:
    # Chromium (Chrome/Brave) requires document user interaction before allowing video autoplay.
    # We focus the browser window, then click directly on the video canvas center.
    try:
        import time
        import computer.windows as windows
        import computer.mouse as mouse
        import computer.keyboard as keyboard

        # Allow browser tab to mount
        time.sleep(1.2)

        # Locate and focus the browser window
        browser_win = None
        for candidate in ("youtube", target_browser, "brave", "chrome", "firefox", "edge"):
            if candidate:
                browser_win = windows.find_window(candidate)
                if browser_win:
                    windows.focus_window(browser_win["hwnd"])
                    break

        if browser_win and browser_win.get("width", 0) > 300:
            win_rect = browser_win["rect"]
            cx = win_rect["left"] + int(win_rect["width"] * 0.45)
            cy = win_rect["top"] + int(win_rect["height"] * 0.45)
            # Click video canvas center to punch through autoplay barrier
            mouse.click(cx, cy)
            time.sleep(0.15)
            keyboard.press_key("space")
        else:
            time.sleep(0.5)
            keyboard.press_key("k")

    except Exception as e:
        logger.debug(f"Autoplay bypass exception: {e}")

    return {
        "success": True,
        "url": target_url,
        "video_id": vid,
        "message": f"Playing '{clean_q}' on YouTube.",
    }


def search_web(query: str) -> Dict[str, Any]:
    """Perform a web search in the default browser."""
    clean_q = (query or "").strip()
    if not clean_q:
        return {"success": False, "error": "Query cannot be empty."}

    search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(clean_q)}"
    _open_url(search_url)
    return {
        "success": True,
        "url": search_url,
        "message": f"Opened web search for '{clean_q}'.",
    }
