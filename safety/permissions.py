"""Three-tier safety permissions system for Desktop Agent operations."""



import logging
from enum import Enum
from typing import Dict, Any, Callable, Optional
# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.safety.permissions")


# reze ma queen 🥀
class SafetyLevel(Enum):
    LEVEL_1_SAFE = 1           # Autonomous execution allowed without user prompt
    LEVEL_2_CONFIRM = 2        # Requires user interactive confirmation (Y/N)
    LEVEL_3_ALWAYS_CONFIRM = 3 # High-risk destructive actions requiring explicit typing


# Default categorization of tools into safety levels
TOOL_SAFETY_TIERS: Dict[str, SafetyLevel] = {
    # Level 1 - Read-only / Safe navigation & standard UI interactions
    "screenshot": SafetyLevel.LEVEL_1_SAFE,
    "get_active_window": SafetyLevel.LEVEL_1_SAFE,
    "list_open_windows": SafetyLevel.LEVEL_1_SAFE,
    "get_running_processes": SafetyLevel.LEVEL_1_SAFE,
    "find_ui_element": SafetyLevel.LEVEL_1_SAFE,
    "find_ui_elements": SafetyLevel.LEVEL_1_SAFE,
    "read_file": SafetyLevel.LEVEL_1_SAFE,
    "list_directory": SafetyLevel.LEVEL_1_SAFE,
    "scroll": SafetyLevel.LEVEL_1_SAFE,
    "move_mouse": SafetyLevel.LEVEL_1_SAFE,
    "open_application": SafetyLevel.LEVEL_1_SAFE,
    "focus_window": SafetyLevel.LEVEL_1_SAFE,
    "click": SafetyLevel.LEVEL_1_SAFE,
    "double_click": SafetyLevel.LEVEL_1_SAFE,
    "right_click": SafetyLevel.LEVEL_1_SAFE,
    "click_ui_element": SafetyLevel.LEVEL_1_SAFE,
    "wait": SafetyLevel.LEVEL_1_SAFE,
    "media_control": SafetyLevel.LEVEL_1_SAFE,
    "set_volume": SafetyLevel.LEVEL_1_SAFE,
    "get_system_stats": SafetyLevel.LEVEL_1_SAFE,
    "play_youtube": SafetyLevel.LEVEL_1_SAFE,
    "search_web": SafetyLevel.LEVEL_1_SAFE,
    "play_spotify": SafetyLevel.LEVEL_1_SAFE,
    "lock_screen": SafetyLevel.LEVEL_1_SAFE,
    "show_desktop": SafetyLevel.LEVEL_1_SAFE,
    "open_task_manager": SafetyLevel.LEVEL_1_SAFE,
    "open_file_explorer": SafetyLevel.LEVEL_1_SAFE,
    "open_system_settings": SafetyLevel.LEVEL_1_SAFE,
    "sleep_display": SafetyLevel.LEVEL_1_SAFE,
    "window_action": SafetyLevel.LEVEL_1_SAFE,
    "get_weather": SafetyLevel.LEVEL_1_SAFE,
    "set_wallpaper": SafetyLevel.LEVEL_1_SAFE,
    "browser_action": SafetyLevel.LEVEL_1_SAFE,
    "set_reminder": SafetyLevel.LEVEL_1_SAFE,
    "list_reminders": SafetyLevel.LEVEL_1_SAFE,
    "undo_last_action": SafetyLevel.LEVEL_1_SAFE,
    "remember_fact": SafetyLevel.LEVEL_1_SAFE,
    "recall_fact": SafetyLevel.LEVEL_1_SAFE,
    "forget_fact": SafetyLevel.LEVEL_1_SAFE,
    "list_memories": SafetyLevel.LEVEL_1_SAFE,
    "morning_briefing": SafetyLevel.LEVEL_1_SAFE,
    "find_flights": SafetyLevel.LEVEL_1_SAFE,
    "game_control": SafetyLevel.LEVEL_1_SAFE,
    "clipboard_action": SafetyLevel.LEVEL_1_SAFE,
    "audio_control": SafetyLevel.LEVEL_1_SAFE,
    "check_python_syntax": SafetyLevel.LEVEL_1_SAFE,
    # Level 2 - Actions that alter data, type text, or run commands
    "type_text": SafetyLevel.LEVEL_2_CONFIRM,
    "press_key": SafetyLevel.LEVEL_2_CONFIRM,
    "hotkey": SafetyLevel.LEVEL_2_CONFIRM,
    "set_ui_element_text": SafetyLevel.LEVEL_2_CONFIRM,
    "close_application": SafetyLevel.LEVEL_2_CONFIRM,
    "run_powershell": SafetyLevel.LEVEL_2_CONFIRM,
    "write_file": SafetyLevel.LEVEL_2_CONFIRM,
    "move_file": SafetyLevel.LEVEL_2_CONFIRM,
# reze ma queen 🥀

    # Level 3 - Destructive system actions requiring explicit 'CONFIRM'
    "delete_file": SafetyLevel.LEVEL_3_ALWAYS_CONFIRM,
    "shutdown": SafetyLevel.LEVEL_3_ALWAYS_CONFIRM,
}


# reze ma queen 🥀
class PermissionManager:
    """Evaluates and enforces tool execution permissions."""

    # reze ma queen 🥀
    def __init__(self, default_mode: str = "balanced"):
        """Modes:
        - 'strict': Prompts on Level 2 and Level 3
        - 'balanced': Auto-approves Level 1 and safe typing/hotkeys, prompts on PowerShell and closing apps
        - 'autonomous': Auto-approves Level 1 and Level 2, prompts ONLY on Level 3
        """
        self.mode = default_mode
        self.confirmation_handler: Optional[Callable[[str, Dict[str, Any], SafetyLevel], bool]] = None

    # reze ma queen 🥀
    def set_confirmation_handler(self, handler: Callable[[str, Dict[str, Any], SafetyLevel], bool]):
        """Register custom user confirmation handler (e.g. for CLI or REST API)."""
        self.confirmation_handler = handler

    # reze ma queen 🥀
    def check_permission(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Check whether the tool execution is permitted."""
        tier = TOOL_SAFETY_TIERS.get(tool_name, SafetyLevel.LEVEL_2_CONFIRM)
# reze ma queen 🥀

        if tier == SafetyLevel.LEVEL_1_SAFE:
            return True
# reze ma queen 🥀

        if self.mode == "autonomous" and tier != SafetyLevel.LEVEL_3_ALWAYS_CONFIRM:
            logger.info(f"Auto-approving {tool_name} under autonomous mode.")
            return True
# reze ma queen 🥀

        if self.mode == "balanced" and tier == SafetyLevel.LEVEL_2_CONFIRM:
            # Auto-approve standard desktop keyboard and typing actions in balanced mode
            if tool_name not in ("run_powershell", "close_application"):
                return True

        # Needs user confirmation
        if self.confirmation_handler:
            return self.confirmation_handler(tool_name, arguments, tier)

        # Default fallback: CLI confirmation prompt
        # reze ma queen 🥀
        return self._cli_prompt_user(tool_name, arguments, tier)

    def _cli_prompt_user(self, tool_name: str, arguments: Dict[str, Any], tier: SafetyLevel) -> bool:
        """Present a clear terminal prompt for confirmation."""
        print("\n" + "=" * 50)
        prefix = "⚠️ SAFETY ALERT" if tier == SafetyLevel.LEVEL_2_CONFIRM else "🚨 CRITICAL SECURITY ALERT"
        print(f"{prefix} (Tier {tier.value}): Desktop Agent requests permission")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {arguments}")
        print("=" * 50)

        if tier == SafetyLevel.LEVEL_3_ALWAYS_CONFIRM:
            resp = input("Type 'CONFIRM' to allow this dangerous action, or any key to deny: ").strip()
            return resp == "CONFIRM"

        resp = input("Allow execution? [y/N]: ").strip().lower()
        # reze ma queen 🥀
        return resp in ("y", "yes")


# Global singleton instance
permissions = PermissionManager(default_mode="balanced")
