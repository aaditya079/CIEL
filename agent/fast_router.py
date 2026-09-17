"""Deterministic intent router for low-latency desktop commands.

Matches common patterns for audio, media playback, system monitoring,
desktop controls, and application shortcuts to execute via native APIs without inference latency.
"""

import re
import logging
from typing import Dict, Any, Optional

from tools.media import media_control, set_volume
from tools.web import play_youtube, search_web
from tools.spotify import play_spotify
from tools.desktop_control import (
    lock_screen,
    show_desktop,
    open_task_manager,
    open_file_explorer,
    open_system_settings,
    sleep_display,
    window_action,
    get_weather,
)
from tools.browser import browser_action
from tools.reminders import set_reminder, list_reminders
from tools.proactive import generate_morning_briefing
from tools.clipboard import get_clipboard, set_clipboard, clear_clipboard
from tools.flights import find_flights
from tools.games import open_steam_action, launch_game, STEAM_GAMES
from tools.audio import open_sound_settings
from core.undo import undo_last_action
from memory.long_term import remember_fact, recall_fact, list_memories
from computer.system_telemetry import get_system_telemetry

logger = logging.getLogger("desktop_agent.agent.fast_router")


class FastPathRouter:
    """Detects and immediately dispatches deterministic desktop intents."""

    def route(self, goal: str) -> Optional[Dict[str, Any]]:
        """Evaluate goal against fast patterns. Returns result dict if handled, else None."""
        raw = (goal or "").strip()
        if not raw:
            return None

        clean = raw.lower().strip()
        # Remove polite prefixes or assistant name invocations ("ciel", "ceil", "please", "hey ciel")
        clean = re.sub(r"^(?:hey\s+|hi\s+)?(?:ciel|ceil)[,\s:]*", "", clean).strip()
        clean = re.sub(r"^(?:please|could you|can you)\s+", "", clean).strip()

        # 1. Volume Set: "set volume to 50", "volume 70", "volume 30%"
        vol_match = re.search(r"^(?:set\s+)?volume\s+(?:to\s+)?(\d{1,3})\s*%?$", clean) or \
                    re.search(r"^(\d{1,3})\s*%\s*volume$", clean)
        if vol_match:
            lvl = int(vol_match.group(1))
            res = set_volume(lvl)
            msg = f"Volume set to {lvl}%."
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "set_volume",
                "arguments": {"level": lvl},
                "message": msg,
                "spoken": msg,
            }

        # 2. Volume Mute / Unmute
        if clean in ("mute", "unmute", "toggle mute", "sound off", "sound on", "silence"):
            res = media_control("mute")
            msg = "Sound muted or unmuted."
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "media_control",
                "arguments": {"action": "mute"},
                "message": msg,
                "spoken": "Audio muted.",
            }

        # 3. Volume Up / Down
        if clean in ("volume up", "turn it up", "louder", "increase volume", "raise volume"):
            res = media_control("volume_up")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "media_control",
                "arguments": {"action": "volume_up"},
                "message": "Volume increased.",
                "spoken": "Volume up.",
            }

        if clean in ("volume down", "turn it down", "quieter", "lower volume", "decrease volume"):
            res = media_control("volume_down")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "media_control",
                "arguments": {"action": "volume_down"},
                "message": "Volume decreased.",
                "spoken": "Volume down.",
            }

        # 4. Media Playback: Pause / Resume / Play / Stop / Next / Previous
        if clean in ("pause", "pause music", "pause song", "pause video", "stop music"):
            res = media_control("play_pause")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "media_control",
                "arguments": {"action": "play_pause"},
                "message": "Playback paused.",
                "spoken": "Paused.",
            }

        if clean in ("resume", "resume music", "unpause", "play music", "play song"):
            res = media_control("play_pause")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "media_control",
                "arguments": {"action": "play_pause"},
                "message": "Playback resumed.",
                "spoken": "Playing.",
            }

        if clean in ("next track", "next song", "skip", "skip track", "skip song"):
            res = media_control("next")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "media_control",
                "arguments": {"action": "next"},
                "message": "Skipped to next track.",
                "spoken": "Next track.",
            }

        if clean in ("previous track", "prev track", "previous song", "prev song"):
            res = media_control("prev")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "media_control",
                "arguments": {"action": "prev"},
                "message": "Previous track.",
                "spoken": "Previous track.",
            }

        # 5. System Telemetry & Health
        if clean in ("system stats", "system status", "cpu", "cpu usage", "ram", "ram usage",
                    "memory", "battery", "battery status", "pc stats", "pc health", "system info"):
            telemetry = get_system_telemetry()
            summary = telemetry["summary"]
            spoken = f"CPU is at {telemetry['cpu_percent']} percent, and memory load is {telemetry['memory']['memory_load_percent']} percent."
            if telemetry["power"]["has_battery"]:
                spoken += f" Battery is at {telemetry['power']['battery_percent']} percent."
            return {
                "handled": True,
                "success": True,
                "tool": "get_system_stats",
                "arguments": {},
                "message": summary,
                "spoken": spoken,
                "data": telemetry,
            }

        # 6. YouTube Playback: "play harvey on youtube", "watch queen on youtube"
        yt_match = re.search(r"^(?:play|watch)\s+(.+?)\s+on\s+youtube$", clean) or \
                   re.search(r"^youtube\s+(?:play\s+)?(.+)$", clean)
        if yt_match:
            query = yt_match.group(1).strip()
            res = play_youtube(query)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "play_youtube",
                "arguments": {"query": query},
                "message": res.get("message", f"Playing {query} on YouTube."),
                "spoken": f"Playing {query} on YouTube.",
            }

        # 7. Spotify Search & Play: "open spotify and play harvey", "play harvey on spotify"
        sp_match = re.search(r"^(?:open\s+spotify\s+and\s+)?play\s+(.+?)\s+on\s+spotify$", clean) or \
                   re.search(r"^open\s+spotify\s+and\s+play\s+(.+)$", clean) or \
                   re.search(r"^spotify\s+(?:play\s+)?(.+)$", clean)
        if sp_match:
            query = sp_match.group(1).strip()
            res = play_spotify(query)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "play_spotify",
                "arguments": {"query": query},
                "message": res.get("message", f"Playing {query} on Spotify."),
                "spoken": f"Playing {query} on Spotify.",
            }

        # 8. Weather: "weather", "weather in london", "what's the weather"
        weather_match = re.search(r"^(?:what(?:'s| is) the\s+)?weather(?:\s+(?:like\s+)?in\s+(.+))?$", clean)
        if weather_match:
            city = (weather_match.group(1) or "").strip()
            res = get_weather(city)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "get_weather",
                "arguments": {"city": city},
                "message": res.get("message", "Weather retrieved."),
                "spoken": res.get("spoken", res.get("message")),
            }

        # 9. Desktop & Window Management
        if clean in ("lock", "lock pc", "lock screen", "lock computer", "lock workstation"):
            res = lock_screen()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "lock_screen",
                "arguments": {},
                "message": "Workstation locked.",
                "spoken": "Locking PC.",
            }

        if clean in ("show desktop", "desktop", "minimize all", "minimise everything", "go to desktop"):
            res = show_desktop()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "show_desktop",
                "arguments": {},
                "message": "Showing desktop.",
                "spoken": "Desktop.",
            }

        if clean in ("task manager", "open task manager", "processes"):
            res = open_task_manager()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "open_task_manager",
                "arguments": {},
                "message": "Task Manager opened.",
                "spoken": "Opening Task Manager.",
            }

        if clean in ("file explorer", "open file explorer", "explorer", "my computer"):
            res = open_file_explorer()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "open_file_explorer",
                "arguments": {},
                "message": "File Explorer opened.",
                "spoken": "Opening File Explorer.",
            }

        if clean in ("settings", "open settings", "system settings", "windows settings"):
            res = open_system_settings()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "open_system_settings",
                "arguments": {},
                "message": "Settings opened.",
                "spoken": "Opening Settings.",
            }

        if clean in ("sleep display", "screen off", "display off", "turn off screen", "turn off display"):
            res = sleep_display()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "sleep_display",
                "arguments": {},
                "message": "Display turned off.",
                "spoken": "Turning off display.",
            }

        if clean in ("maximize", "maximize window", "maximize screen"):
            res = window_action("maximize")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "window_action",
                "arguments": {"action": "maximize"},
                "message": "Window maximized.",
                "spoken": "Maximized.",
            }

        if clean in ("minimize", "minimize window"):
            res = window_action("minimize")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "window_action",
                "arguments": {"action": "minimize"},
                "message": "Window minimized.",
                "spoken": "Minimized.",
            }

        if clean in ("fullscreen", "full screen"):
            res = window_action("fullscreen")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "window_action",
                "arguments": {"action": "fullscreen"},
                "message": "Fullscreen toggled.",
                "spoken": "Fullscreen.",
            }

        # 10. Reminders: "remind me in 5 minutes to check oven"
        remind_match = re.search(r"^remind(?:\s+me)?\s+(?:in\s+)?(\d+(?:\.\d+)?)\s*(?:m|min|mins|minutes?)?\s+(?:to\s+)?(.+)$", clean)
        if remind_match:
            mins = float(remind_match.group(1))
            task_msg = remind_match.group(2).strip()
            res = set_reminder(task_msg, mins)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "set_reminder",
                "arguments": {"message": task_msg, "minutes": mins},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        # 11. Browser Navigation & Tabs
        browser_alias_map = {
            "new tab": "new_tab",
            "open new tab": "new_tab",
            "open a tab": "new_tab",
            "close tab": "close_tab",
            "close this tab": "close_tab",
            "next tab": "next_tab",
            "previous tab": "prev_tab",
            "prev tab": "prev_tab",
            "reopen tab": "reopen_tab",
            "refresh": "refresh",
            "refresh page": "refresh",
            "reload": "refresh",
            "reload page": "refresh",
            "zoom in": "zoom_in",
            "zoom out": "zoom_out",
            "reset zoom": "zoom_reset",
            "find on page": "find",
            "history": "history",
            "bookmarks": "bookmarks",
            "go back": "go_back",
            "go forward": "go_forward",
        }
        if clean in browser_alias_map:
            b_act = browser_alias_map[clean]
            res = browser_action(b_act)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "browser_action",
                "arguments": {"action": b_act},
                "message": f"Browser {clean} executed.",
                "spoken": f"{clean}.",
            }

        # 12. Web Search: "search for quantum computing", "google weather today"
        search_match = re.search(r"^(?:search(?:\s+the\s+web)?\s+(?:for\s+)?|google\s+)(.+)$", clean)
        if search_match:
            query = search_match.group(1).strip()
            res = search_web(query)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "search_web",
                "arguments": {"query": query},
                "message": res.get("message", f"Searching for {query}."),
                "spoken": f"Searching for {query}.",
            }

        # 13. Undo: "undo", "undo that", "revert", "undo last action"
        if clean in ("undo", "undo that", "revert", "undo last action", "undo action", "cancel that"):
            res = undo_last_action()
            return {
                "handled": True,
                "success": res.get("success", False),
                "tool": "undo_last_action",
                "arguments": {},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        # 14. Proactive Morning Briefing: "morning briefing", "daily briefing", "status report", "good morning"
        if clean in ("morning briefing", "daily briefing", "status report", "daily status",
                     "good morning", "briefing", "morning report", "sitrep"):
            res = generate_morning_briefing(speak=True)
            return {
                "handled": True,
                "success": True,
                "tool": "morning_briefing",
                "arguments": {},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        # 15. Clipboard Intelligence
        if clean in ("what's on my clipboard", "whats on my clipboard", "read clipboard",
                     "show clipboard", "clipboard", "inspect clipboard"):
            res = get_clipboard()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "clipboard_action",
                "arguments": {"action": "read"},
                "message": f"Clipboard content:\n{res.get('text', '')}",
                "spoken": res.get("spoken"),
            }

        if clean in ("clear clipboard", "empty clipboard"):
            res = clear_clipboard()
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "clipboard_action",
                "arguments": {"action": "clear"},
                "message": "Clipboard cleared.",
                "spoken": "Clipboard cleared.",
            }

        copy_match = re.search(r"^copy\s+(.+?)(?:\s+to\s+clipboard)?$", clean)
        if copy_match and not clean.startswith("copy file"):
            text_to_copy = copy_match.group(1).strip()
            res = set_clipboard(text_to_copy)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "clipboard_action",
                "arguments": {"action": "copy", "text": text_to_copy},
                "message": f"Copied '{text_to_copy}' to clipboard.",
                "spoken": "Copied to clipboard.",
            }

        # 16. Flight Search: "flights from NYC to London", "find flights to Tokyo"
        flight_from_to = re.search(r"^(?:find\s+)?flights?(?:\s+search)?\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+(?:on|for)\s+(.+))?$", clean)
        if flight_from_to:
            orig = flight_from_to.group(1).strip()
            dest = flight_from_to.group(2).strip()
            dt = (flight_from_to.group(3) or "").strip()
            res = find_flights(destination=dest, origin=orig, date=dt)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "find_flights",
                "arguments": {"destination": dest, "origin": orig, "date": dt},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        flight_to = re.search(r"^(?:find\s+)?flights?(?:\s+search)?\s+to\s+(.+?)(?:\s+(?:on|for)\s+(.+))?$", clean)
        if flight_to:
            dest = flight_to.group(1).strip()
            dt = (flight_to.group(2) or "").strip()
            res = find_flights(destination=dest, date=dt)
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "find_flights",
                "arguments": {"destination": dest, "date": dt},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        # 17. Steam & Games Control
        if clean in ("update steam games", "update steam", "update games",
                     "open steam downloads", "steam downloads", "check game updates"):
            res = open_steam_action("downloads")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "game_control",
                "arguments": {"action": "downloads"},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        if clean in ("open steam", "steam", "steam library", "open steam library", "open game library", "game library"):
            res = open_steam_action("games")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "game_control",
                "arguments": {"action": "games"},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        game_launch_match = re.search(r"^(?:launch|play)\s+([a-zA-Z0-9\s]+)$", clean)
        if game_launch_match:
            g_name = game_launch_match.group(1).strip()
            if g_name in STEAM_GAMES or g_name.replace(" ", "") in STEAM_GAMES:
                res = launch_game(g_name)
                return {
                    "handled": True,
                    "success": res.get("success", True),
                    "tool": "game_control",
                    "arguments": {"action": "launch", "target": g_name},
                    "message": res.get("message"),
                    "spoken": res.get("spoken"),
                }

        # 18. Sound & Audio Settings
        if clean in ("sound settings", "audio settings", "sound devices", "audio output"):
            res = open_sound_settings("sound")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "audio_control",
                "arguments": {"action": "settings"},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        if clean in ("volume mixer", "audio mixer", "sound mixer"):
            res = open_sound_settings("mixer")
            return {
                "handled": True,
                "success": res.get("success", True),
                "tool": "audio_control",
                "arguments": {"action": "mixer"},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        # 19. Persistent Long-Term Memory
        remember_match = re.search(r"^remember\s+(?:that\s+)?(.+?)\s+is\s+(.+)$", clean)
        if remember_match:
            k = remember_match.group(1).strip()
            v = remember_match.group(2).strip()
            res = remember_fact(k, v)
            return {
                "handled": True,
                "success": True,
                "tool": "remember_fact",
                "arguments": {"key": k, "value": v},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        recall_match = re.search(r"^(?:recall|what is my|what's my|what was my)\s+(.+)$", clean)
        if recall_match:
            k = recall_match.group(1).strip().rstrip("?")
            res = recall_fact(k)
            return {
                "handled": True,
                "success": res.get("found", False),
                "tool": "recall_fact",
                "arguments": {"key": k},
                "message": res.get("message"),
                "spoken": res.get("spoken"),
            }

        if clean in ("what do you remember", "list memories", "show memories"):
            memories = list_memories()
            facts_count = len(memories.get("facts", {}))
            prefs_count = len(memories.get("preferences", {}))
            msg = f"Stored memories:\nFacts: {memories.get('facts', {})}\nPreferences: {memories.get('preferences', {})}"
            spoken = f"I remember {facts_count} facts and {prefs_count} preferences."
            return {
                "handled": True,
                "success": True,
                "tool": "list_memories",
                "arguments": {},
                "message": msg,
                "spoken": spoken,
                "data": memories,
            }

        return None


# Global fast router singleton instance
fast_router = FastPathRouter()
