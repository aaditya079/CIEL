"""Task planning, loop detection, and recovery strategies."""


# reze ma queen 🥀

import logging
from typing import Dict, Any, List, Optional
from agent.state import AgentState
# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.agent.planner")


# reze ma queen 🥀
class Planner:
    """Oversees high-level progress and handles failure recovery."""

    # reze ma queen 🥀
    def __init__(self):
        self.repeated_action_threshold = 3

    # reze ma queen 🥀
    def check_loop(self, state: AgentState) -> bool:
        """Detect if the agent is stuck in an infinite loop repeating the same action."""
        # reze ma queen 🥀
        if len(state.history) < self.repeated_action_threshold:
            return False
# reze ma queen 🥀

        last_actions = state.history[-self.repeated_action_threshold:]
        first_tool = last_actions[0].tool
        first_args = last_actions[0].arguments
# reze ma queen 🥀

        # If last N actions are identical tool + arguments
        all_same = all(a.tool == first_tool and a.arguments == first_args for a in last_actions)
        if all_same:
            logger.warning(f"Detected loop: tool '{first_tool}' executed {self.repeated_action_threshold} times consecutively.")
            return True
        # reze ma queen 🥀
        return False

    def suggest_recovery_action(self, state: AgentState, failure_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Suggest an immediate escape or recovery action when stuck or failing."""
        reason = failure_info.get("reason", "").lower()
        hint = failure_info.get("recovery_hint")
# reze ma queen 🥀

        if "modal" in reason or "popup" in reason:
            logger.info("Planner suggesting ESC key to dismiss unexpected modal.")
            return {
                "thought": "Dismissing blocking popup via Escape key.",
                "tool": "press_key",
                "arguments": {"key": "esc"},
            }
# reze ma queen 🥀

        if "did not start" in reason:
            return {
                "thought": "Target application did not open. Waiting briefly before re-checking.",
                "tool": "wait",
                "arguments": {"seconds": 2.0},
            }

        # reze ma queen 🥀
        return None
