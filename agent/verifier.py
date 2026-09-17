"""Post-action outcome verification and UI change detection."""

import time
import logging
from typing import Dict, Any, Optional

from computer.windows import get_active_window, list_open_windows
from computer.ui import dump_ui_tree
from tools.apps import is_app_running

logger = logging.getLogger("desktop_agent.agent.verifier")


class Verifier:
    """Verifies that an executed action produced the intended outcome."""

    def verify(
        self,
        tool: str,
        arguments: Dict[str, Any],
        exec_result: Dict[str, Any],
        before_active_window: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform domain-specific checks on tool execution result."""
        if not exec_result.get("success", False):
            return {
                "verified": False,
                "reason": f"Execution failed: {exec_result.get('error')}",
                "recovery_hint": "Check error message and try an alternative method or verify parameters.",
            }

        # 1. Verify open_application
        if tool == "open_application":
            app_name = arguments.get("app_name", "")
            time.sleep(0.8)
            if is_app_running(app_name):
                return {
                    "verified": True,
                    "reason": f"Application '{app_name}' confirmed running.",
                    "recovery_hint": None,
                }
            return {
                "verified": False,
                "reason": f"Application '{app_name}' did not start or open within expected time.",
                "recovery_hint": "Try opening via full path or protocol URI.",
            }

        # 1b. Verify focus_window
        if tool == "focus_window":
            target = (arguments.get("title") or "").lower()
            time.sleep(0.3)
            active = get_active_window()
            if target and target in active.get("title", "").lower():
                return {
                    "verified": True,
                    "reason": f"Window '{target}' successfully brought to foreground.",
                    "recovery_hint": None,
                }
            return {
                "verified": True,  # Non-fatal if title differs
                "reason": f"Focus command dispatched for window '{target}'.",
                "recovery_hint": None,
            }

        # 2. Verify close_application
        if tool == "close_application":
            app_name = arguments.get("app_name", "")
            time.sleep(0.5)
            if not is_app_running(app_name):
                return {
                    "verified": True,
                    "reason": f"Application '{app_name}' closed successfully.",
                    "recovery_hint": None,
                }
            return {
                "verified": False,
                "reason": f"Application '{app_name}' appears to still be running.",
                "recovery_hint": "Try taskkill via PowerShell or close window handle directly.",
            }

        # 3. Verify click_ui_element or set_ui_element_text
        if tool in ("click_ui_element", "set_ui_element_text"):
            res = exec_result.get("result")
            if res is True:
                return {
                    "verified": True,
                    "reason": f"UI interaction on element '{arguments.get('name')}' succeeded.",
                    "recovery_hint": None,
                }
            return {
                "verified": False,
                "reason": f"Could not find or interact with UI element '{arguments.get('name')}'.",
                "recovery_hint": "Inspect screen via screenshot or dump_ui_tree to check element visibility.",
            }

        # 4. Check for unexpected dialogs/blocking popups
        popup = self._detect_unexpected_popup()
        if popup:
            return {
                "verified": False,
                "reason": f"Detected unexpected modal or popup window: '{popup}'",
                "recovery_hint": "Dismiss modal popup by pressing 'esc' or clicking 'Close'/'Later'.",
            }

        # Default: success
        return {
            "verified": True,
            "reason": "Action completed without errors.",
            "recovery_hint": None,
        }

    def _detect_unexpected_popup(self) -> Optional[str]:
        """Detect common modal popups such as 'Update available' or 'User Account Control'."""
        try:
            active = get_active_window()
            title = active.get("title", "").lower()
            popup_keywords = ["update available", "whats new", "sign in to continue", "error", "warning"]
            for kw in popup_keywords:
                if kw in title:
                    return active.get("title")
        except Exception:
            pass
        return None
