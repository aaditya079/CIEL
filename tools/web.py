"""Web Tools: Instant YouTube video playback and web search."""

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


def play_youtube(query: str) -> Dict[str, Any]:
    """Find and play a YouTube video directly in the browser."""
    clean_q = (query or "").strip()
    if not clean_q:
        return {"success": False, "error": "Query cannot be empty."}

    vid = scrape_first_youtube_video_id(clean_q)
    if vid:
        target_url = f"https://www.youtube.com/watch?v={vid}&autoplay=1"
        _open_url(target_url)

        # Allow browser to load and trigger play key ('k' is YouTube universal play/pause shortcut)
        try:
            import time
            time.sleep(1.8)
            import pyautogui
            pyautogui.press("k")
        except Exception:
            pass

        return {
            "success": True,
            "url": target_url,
            "video_id": vid,
            "message": f"Playing '{clean_q}' on YouTube.",
        }
    else:
        # Fallback to search results page
        fallback_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(clean_q)}"
        _open_url(fallback_url)
        return {
            "success": True,
            "url": fallback_url,
            "video_id": None,
            "message": f"Opened YouTube search for '{clean_q}'.",
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
