"""Headless Background Audio Streamer (Gemini / Bixby Mode) for Desktop Agent.

Streams audio directly from YouTube / YouTube Music in the background using pre-installed
yt-dlp and ffplay. Eliminates heavy browser window overhead, bypasses video ads,
and delivers instant voice-assistant-style music playback.
"""

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
import shutil
import logging
import subprocess
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger("desktop_agent.tools.streamer")

_ACTIVE_PROC_DLP: Optional[subprocess.Popen] = None
_ACTIVE_PROC_PLAY: Optional[subprocess.Popen] = None
_CURRENT_TRACK: Optional[str] = None
_STREAM_LOCK = threading.Lock()

# Detect pre-installed system binaries
_YTDLP_PATH = shutil.which("yt-dlp") or os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python312\Scripts\yt-dlp.EXE")
_FFPLAY_PATH = shutil.which("ffplay")


def _resolve_binaries() -> bool:
    global _YTDLP_PATH, _FFPLAY_PATH
    if not _YTDLP_PATH or not os.path.exists(_YTDLP_PATH):
        _YTDLP_PATH = shutil.which("yt-dlp")
    if not _FFPLAY_PATH or not os.path.exists(_FFPLAY_PATH):
        _FFPLAY_PATH = shutil.which("ffplay")
        if not _FFPLAY_PATH:
            # Check winget standard path
            winget_base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
            if os.path.exists(winget_base):
                for root, _, files in os.walk(winget_base):
                    if "ffplay.exe" in [f.lower() for f in files]:
                        _FFPLAY_PATH = os.path.join(root, "ffplay.exe")
                        break
    return bool(_YTDLP_PATH and _FFPLAY_PATH and os.path.exists(_YTDLP_PATH) and os.path.exists(_FFPLAY_PATH))


def is_audio_streaming() -> bool:
    """Check if background audio stream is currently playing."""
    with _STREAM_LOCK:
        if _ACTIVE_PROC_PLAY is not None:
            poll = _ACTIVE_PROC_PLAY.poll()
            return poll is None
        return False


def get_current_stream_track() -> Optional[str]:
    """Get the name/query of the currently streaming track."""
    return _CURRENT_TRACK if is_audio_streaming() else None


def stop_audio_stream() -> Dict[str, Any]:
    """Stop any active background audio stream immediately."""
    global _ACTIVE_PROC_DLP, _ACTIVE_PROC_PLAY, _CURRENT_TRACK
    with _STREAM_LOCK:
        stopped = False
        if _ACTIVE_PROC_PLAY is not None:
            try:
                _ACTIVE_PROC_PLAY.terminate()
                stopped = True
            except Exception:
                pass
            _ACTIVE_PROC_PLAY = None

        if _ACTIVE_PROC_DLP is not None:
            try:
                _ACTIVE_PROC_DLP.terminate()
                stopped = True
            except Exception:
                pass
            _ACTIVE_PROC_DLP = None

        _CURRENT_TRACK = None
        logger.info("Background audio stream terminated.")
        return {
            "success": True,
            "stopped": stopped,
            "message": "Background audio stream stopped.",
        }


def stream_audio(query: str, **kwargs) -> Dict[str, Any]:
    """Stream audio directly in the background without opening a browser or showing ads.
    
    Acts like Google Assistant, Gemini, or Bixby: audio begins playing
    instantly out of the system speakers in the background.
    """
    global _ACTIVE_PROC_DLP, _ACTIVE_PROC_PLAY, _CURRENT_TRACK

    clean_q = (query or kwargs.get("q") or kwargs.get("song") or kwargs.get("track") or "").strip()
    if not clean_q:
        return {"success": False, "error": "Query cannot be empty."}

    if not _resolve_binaries():
        return {
            "success": False,
            "error": "yt-dlp or ffplay binaries not found on system. Please verify installation.",
        }

    # Stop any existing stream first
    stop_audio_stream()

    try:
        logger.info(f"Starting background audio stream for: '{clean_q}'")

        # Pipe yt-dlp stdout directly into ffplay stdin for progressive streaming
        # ytsearch1: searches YouTube and picks the top audio match directly
        dlp_cmd = [
            _YTDLP_PATH,
            "-f", "bestaudio/ba",
            "--no-playlist",
            "-o", "-",
            f"ytsearch1:{clean_q}",
        ]

        ffplay_cmd = [
            _FFPLAY_PATH,
            "-nodisp",
            "-autoexit",
            "-loglevel", "quiet",
            "-i", "-",
        ]

        with _STREAM_LOCK:
            _ACTIVE_PROC_DLP = subprocess.Popen(
                dlp_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            _ACTIVE_PROC_PLAY = subprocess.Popen(
                ffplay_cmd,
                stdin=_ACTIVE_PROC_DLP.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            _CURRENT_TRACK = clean_q

        return {
            "success": True,
            "query": clean_q,
            "mode": "headless_stream",
            "message": f"Streaming '{clean_q}' in the background (Gemini/Bixby mode).",
        }

    except Exception as e:
        logger.error(f"Failed to start audio stream for '{clean_q}': {e}")
        stop_audio_stream()
        return {"success": False, "error": str(e)}
