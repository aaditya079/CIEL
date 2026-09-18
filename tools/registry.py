"""Central Tool Registry: definitions, JSON schema, validation, and dispatch."""

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
import logging
from typing import Dict, Any, List, Callable

from safety.kill_switch import kill_switch
from safety.permissions import permissions

import computer.mouse as mouse
import computer.keyboard as keyboard
import computer.screen as screen
import computer.windows as windows
import computer.ui as ui
import tools.apps as apps
import tools.powershell as powershell
import tools.files as files
import tools.media as media
import tools.web as web
import tools.spotify as spotify
import tools.streamer as streamer
import tools.desktop_control as desktop
import tools.browser as browser
import tools.reminders as reminders
import tools.proactive as proactive
import tools.clipboard as clipboard
import tools.flights as flights
import tools.games as games
import tools.audio as audio
import tools.code_helper as code_helper
import core.undo as undo
import memory.long_term as memory
from computer.system_telemetry import get_system_telemetry

logger = logging.getLogger("desktop_agent.tools.registry")

# Standard tool definitions for LLM function calling
TOOL_DEFINITIONS = [
    {
        "name": "screenshot",
        "description": "Capture the current Windows desktop screen. Returns screen dimensions and screenshot confirmation.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "find_ui_element",
        "description": "Locate an accessible UI control (button, textbox, checkbox, etc.) on screen using Windows UI Automation without coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Element name or partial text label (e.g. 'Search', 'Play', 'OK')"},
                "role": {"type": "string", "description": "Control type: 'Button', 'TextBox', 'CheckBox', 'MenuItem', 'TabItem', 'Window'"},
                "window_title": {"type": "string", "description": "Optional specific window title to search within"},
            },
            "required": [],
        },
    },
    {
        "name": "click_ui_element",
        "description": "Find and click an accessible Windows UI element directly using UI Automation.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Element name or label to click"},
                "role": {"type": "string", "description": "Role of the element (e.g. 'Button', 'TextBox')"},
                "window_title": {"type": "string", "description": "Optional window title"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "set_ui_element_text",
        "description": "Focus an accessible TextBox or Edit control and enter text into it.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name or placeholder of the input field"},
                "text": {"type": "string", "description": "The exact text to type"},
                "window_title": {"type": "string", "description": "Optional window title"},
            },
            "required": ["name", "text"],
        },
    },
    {
        "name": "open_application",
        "description": "Launch or focus a Windows application by name, protocol, or executable (e.g. 'Spotify', 'Discord', 'Chrome', 'Brave', 'Notepad', 'Settings').",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Application name or protocol (e.g. 'Spotify', 'Discord', 'Brave', 'calc')"},
                "application_name": {"type": "string", "description": "Alias for app_name"},
                "name": {"type": "string", "description": "Alias for app_name"},
            },
            "required": [],
        },
    },
    {
        "name": "close_application",
        "description": "Close an open application gracefully.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Application name or process name to close"},
                "application_name": {"type": "string", "description": "Alias for app_name"},
            },
            "required": [],
        },
    },
    {
        "name": "get_active_window",
        "description": "Get information about the currently focused foreground window.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "list_open_windows",
        "description": "List all currently open application windows on the desktop.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "focus_window",
        "description": "Bring an application window to the foreground and focus it by title, partial title, or application name (e.g. 'Spotify', 'Discord', 'Chrome', 'Notepad').",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Application name or window title to focus"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "click",
        "description": "Click the mouse at specified coordinates, or at the current mouse position if x and y are omitted. Note: Prefer click_ui_element whenever possible.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate in pixels"},
                "y": {"type": "integer", "description": "Y coordinate in pixels"},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Mouse button (default: left)"},
                "clicks": {"type": "integer", "description": "Number of clicks (default: 1)"},
            },
            "required": [],
        },
    },
    {
        "name": "double_click",
        "description": "Double click the left mouse button at specified coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate"},
                "y": {"type": "integer", "description": "Y coordinate"},
            },
            "required": [],
        },
    },
    {
        "name": "right_click",
        "description": "Right click the mouse at specified coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate"},
                "y": {"type": "integer", "description": "Y coordinate"},
            },
            "required": [],
        },
    },
    {
        "name": "type_text",
        "description": "Type text into the currently focused window or field.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to type"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "press_key",
        "description": "Press a single key (e.g. 'enter', 'tab', 'esc', 'space', 'backspace', 'up', 'down').",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key name to press"},
            },
            "required": ["key"],
        },
    },
    {
        "name": "hotkey",
        "description": "Execute a key combination (e.g. ['ctrl', 'c'], ['ctrl', 'v'], ['alt', 'f4'], ['enter']).",
        "parameters": {
            "type": "object",
            "properties": {
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of key names to press together in order",
                },
            },
            "required": ["keys"],
        },
    },
    {
        "name": "scroll",
        "description": "Scroll the mouse wheel (positive = up, negative = down).",
        "parameters": {
            "type": "object",
            "properties": {
                "clicks": {"type": "integer", "description": "Number of scroll clicks (e.g. -5 to scroll down, 5 to scroll up)"},
                "x": {"type": "integer", "description": "Optional X coordinate to hover while scrolling"},
                "y": {"type": "integer", "description": "Optional Y coordinate to hover while scrolling"},
            },
            "required": ["clicks"],
        },
    },
    {
        "name": "drag",
        "description": "Click and drag mouse cursor from start to end coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_x": {"type": "integer", "description": "Start X"},
                "from_y": {"type": "integer", "description": "Start Y"},
                "to_x": {"type": "integer", "description": "Target X"},
                "to_y": {"type": "integer", "description": "Target Y"},
            },
            "required": ["from_x", "from_y", "to_x", "to_y"],
        },
    },
    {
        "name": "run_powershell",
        "description": "Execute a controlled PowerShell command and return its output.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "PowerShell command to execute"},
            },
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read contents of a local text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to file"},
            },
            "required": ["filepath"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and folders in a local directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (default: current dir)"},
            },
            "required": [],
        },
    },
    {
        "name": "wait",
        "description": "Pause execution for a brief duration (in seconds) to allow UI animation or loading.",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {"type": "number", "description": "Time to wait in seconds (default: 1.0)"},
            },
            "required": [],
        },
    },
    {
        "name": "media_control",
        "description": "Control Windows system media playback and sound: 'play_pause', 'next', 'prev', 'stop', 'volume_up', 'volume_down', 'mute'.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["play_pause", "next", "prev", "stop", "volume_up", "volume_down", "mute"],
                    "description": "Media action to execute",
                }
            },
            "required": ["action"],
        },
    },
    {
        "name": "set_volume",
        "description": "Set Windows master system volume level (0 to 100 percent).",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "Target volume percentage from 0 to 100"},
            },
            "required": ["level"],
        },
    },
    {
        "name": "get_system_stats",
        "description": "Inspect real-time Windows hardware telemetry (CPU percentage, RAM total/used/load, Battery state, and display resolution).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "stream_audio",
        "description": "Stream audio directly in the background (Gemini / Bixby mode) using yt-dlp & ffplay without opening browser windows or showing ads.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Track, artist, or music title to stream in background"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "stop_audio_stream",
        "description": "Stop any active background audio stream immediately.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "play_youtube",
        "description": "Search for and immediately play a YouTube video in the browser with autoplay blocker bypass.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search title, artist, or video name to play"},
                "browser_name": {"type": "string", "description": "Optional browser: 'brave', 'chrome', 'firefox'"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_web",
        "description": "Search the web directly in the default browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "play_spotify",
        "description": "Launch Spotify and play a song, artist, album, or playlist directly via Spicetify API or instant hotkeys.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Track, artist, or playlist to play on Spotify"},
            },
            "required": [],
        },
    },
    {
        "name": "lock_screen",
        "description": "Lock the Windows desktop workstation immediately.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "show_desktop",
        "description": "Minimize all windows and display the desktop.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "open_task_manager",
        "description": "Open Windows Task Manager.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "open_file_explorer",
        "description": "Open Windows File Explorer.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "open_system_settings",
        "description": "Open Windows Settings app.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "sleep_display",
        "description": "Turn off or sleep the display monitors.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "window_action",
        "description": "Control the foreground window: 'maximize', 'minimize', 'snap_left', 'snap_right', 'fullscreen', 'switch_window'.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["maximize", "minimize", "snap_left", "snap_right", "fullscreen", "switch_window"],
                    "description": "Window management action",
                }
            },
            "required": ["action"],
        },
    },
    {
        "name": "get_weather",
        "description": "Get real-time weather report for a city or local area.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name (e.g. 'London', 'New York', 'Tokyo')"},
            },
            "required": [],
        },
    },
    {
        "name": "set_wallpaper",
        "description": "Set desktop wallpaper image.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "Absolute path to the image file"},
            },
            "required": ["image_path"],
        },
    },
    {
        "name": "browser_action",
        "description": "Perform browser navigation or tab management: 'new_tab', 'close_tab', 'next_tab', 'prev_tab', 'reopen_tab', 'refresh', 'zoom_in', 'zoom_out', 'zoom_reset', 'find', 'history', 'bookmarks', 'address_bar', 'go_back', 'go_forward'.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Browser action to execute",
                }
            },
            "required": ["action"],
        },
    },
    {
        "name": "set_reminder",
        "description": "Schedule a timed voice alarm and notification.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Reminder task description"},
                "minutes": {"type": "number", "description": "Minutes from now to trigger"},
            },
            "required": ["message", "minutes"],
        },
    },
    {
        "name": "list_reminders",
        "description": "List all active scheduled reminders.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "undo_last_action",
        "description": "Undo the most recent reversible action (e.g. file changes, volume adjustments).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "remember_fact",
        "description": "Store a user preference, note, or fact into persistent long-term memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key or topic (e.g. 'favorite_song', 'user_name')"},
                "value": {"type": "string", "description": "The fact or value to remember"},
                "category": {"type": "string", "description": "Category ('facts' or 'preferences')"},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "recall_fact",
        "description": "Retrieve a remembered fact or preference from persistent memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "The key or topic to recall"},
            },
            "required": ["key"],
        },
    },
    {
        "name": "list_memories",
        "description": "List all stored long-term memories, preferences, and notes.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "morning_briefing",
        "description": "Synthesize and announce a daily morning / status briefing (weather, time, hardware stats, reminders).",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Optional city for weather"},
                "speak": {"type": "boolean", "description": "Whether to speak aloud via SAPI voice"},
            },
            "required": [],
        },
    },
    {
        "name": "find_flights",
        "description": "Search flights between cities on Google Flights or Skyscanner.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Destination city or airport"},
                "origin": {"type": "string", "description": "Optional departure city"},
                "date": {"type": "string", "description": "Departure date or time frame"},
                "return_date": {"type": "string", "description": "Optional return date"},
            },
            "required": ["destination"],
        },
    },
    {
        "name": "game_control",
        "description": "Steam & Epic Games control: open downloads/updates, library, or launch a game.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "'update', 'downloads', 'library', 'launch', or 'epic'"},
                "target": {"type": "string", "description": "Game name or Steam App ID if action is 'launch'"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "clipboard_action",
        "description": "Read, copy to, or clear the system clipboard.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "'read', 'copy', or 'clear'"},
                "text": {"type": "string", "description": "Text to copy if action is 'copy'"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "audio_control",
        "description": "Open Windows sound settings or application volume mixer.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "'settings' or 'mixer'"},
            },
            "required": [],
        },
    },
    {
        "name": "write_file",
        "description": "Write text content to a file with automatic undo history.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Text content to write"},
            },
            "required": ["filepath", "content"],
        },
    },
    {
        "name": "delete_file",
        "description": "Safely move a file to the Windows Recycle Bin.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "File path to delete"},
            },
            "required": ["filepath"],
        },
    },
    {
        "name": "move_file",
        "description": "Move or rename a file with undo support.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source file path"},
                "destination": {"type": "string", "description": "Destination file path"},
            },
            "required": ["source", "destination"],
        },
    },
    {
        "name": "check_python_syntax",
        "description": "Verify the syntax of a Python file or code snippet.",
        "parameters": {
            "type": "object",
            "properties": {
                "code_or_file": {"type": "string", "description": "File path or raw Python code"},
            },
            "required": ["code_or_file"],
        },
    },
]


class ToolDispatcher:
    """Dispatches tool executions to their respective underlying computer or tools handler."""

    def __init__(self):
        self._handlers: Dict[str, Callable[..., Any]] = {
            "screenshot": self._handle_screenshot,
            "find_ui_element": ui.find_ui_element,
            "find_ui_elements": ui.find_ui_elements,
            "click_ui_element": ui.click_ui_element,
            "set_ui_element_text": ui.set_ui_element_text,
            "open_application": apps.open_application,
            "close_application": apps.close_application,
            "get_active_window": windows.get_active_window,
            "list_open_windows": windows.list_open_windows,
            "focus_window": self._handle_focus_window,
            "click": mouse.click,
            "double_click": mouse.double_click,
            "right_click": mouse.right_click,
            "type_text": keyboard.type_text,
            "press_key": keyboard.press_key,
            "hotkey": self._handle_hotkey,
            "scroll": mouse.scroll,
            "drag": mouse.drag,
            "run_powershell": powershell.run_powershell,
            "read_file": files.read_file,
            "list_directory": files.list_directory,
            "wait": self._handle_wait,
            "media_control": media.media_control,
            "set_volume": media.set_volume,
            "get_system_stats": get_system_telemetry,
            "stream_audio": streamer.stream_audio,
            "stop_audio_stream": streamer.stop_audio_stream,
            "play_youtube": web.play_youtube,
            "search_web": web.search_web,
            "play_spotify": spotify.play_spotify,
            "lock_screen": desktop.lock_screen,
            "show_desktop": desktop.show_desktop,
            "open_task_manager": desktop.open_task_manager,
            "open_file_explorer": desktop.open_file_explorer,
            "open_system_settings": desktop.open_system_settings,
            "sleep_display": desktop.sleep_display,
            "window_action": desktop.window_action,
            "get_weather": desktop.get_weather,
            "set_wallpaper": desktop.set_wallpaper,
            "browser_action": browser.browser_action,
            "set_reminder": reminders.set_reminder,
            "list_reminders": reminders.list_reminders,
            "undo_last_action": undo.undo_last_action,
            "remember_fact": memory.remember_fact,
            "recall_fact": memory.recall_fact,
            "forget_fact": memory.forget_fact,
            "list_memories": memory.list_memories,
            "morning_briefing": proactive.generate_morning_briefing,
            "find_flights": flights.find_flights,
            "game_control": games.game_control,
            "clipboard_action": clipboard.clipboard_action,
            "audio_control": audio.audio_control,
            "write_file": files.write_file,
            "delete_file": files.delete_file,
            "move_file": files.move_file,
            "check_python_syntax": code_helper.check_python_syntax,
        }

    def _handle_focus_window(self, title: str = "", **kwargs) -> bool:
        t = title or kwargs.get("title_or_hwnd") or kwargs.get("name") or ""
        return windows.focus_window(t)

    def _handle_screenshot(self, **kwargs) -> Dict[str, Any]:
        img = screen.take_screenshot()
        w, h = screen.get_screen_dimensions()
        return {
            "status": "success",
            "screen_width": w,
            "screen_height": h,
            "captured_size": [img.width, img.height],
        }

    def _handle_hotkey(self, keys: List[str]) -> bool:
        if isinstance(keys, str):
            keys = [keys]
        keyboard.hotkey(*keys)
        return True

    def _handle_wait(self, seconds: float = 1.0) -> bool:
        time.sleep(min(float(seconds), 10.0))
        return True

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate safety, check kill switch, and execute the requested tool."""
        kill_switch.check()

        if tool_name not in self._handlers:
            return {
                "success": False,
                "error": f"Unknown tool: '{tool_name}'",
                "result": None,
            }

        # Check safety permissions
        if not permissions.check_permission(tool_name, arguments):
            logger.warning(f"Tool {tool_name} rejected by user or safety policy.")
            return {
                "success": False,
                "error": f"Permission denied by user safety policy for {tool_name}",
                "result": None,
            }

        handler = self._handlers[tool_name]
        try:
            import inspect
            sig = inspect.signature(handler)
            has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            if has_var_kw:
                call_args = arguments
            else:
                call_args = {k: v for k, v in arguments.items() if k in sig.parameters}

            res = handler(**call_args)
            return {
                "success": True,
                "error": None,
                "result": res,
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name} with args {arguments}: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None,
            }


# Global tool dispatcher instance
dispatcher = ToolDispatcher()
