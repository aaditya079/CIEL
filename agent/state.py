"""Agent runtime state and execution history."""

import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ActionRecord:
    step: int
    tool: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None
    thought: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "tool": self.tool,
            "arguments": self.arguments,
            "result": self.result,
            "success": self.success,
            "error": self.error,
            "thought": self.thought,
            "timestamp": self.timestamp,
        }


class AgentState:
    """Maintains live runtime context for an autonomous agent task."""

    def __init__(self, goal: str, max_actions: int = 50):
        self.task_id = str(uuid.uuid4())[:8]
        self.goal = goal
        self.status = "idle"  # idle, running, paused, completed, failed, stopped
        self.step = 0
        self.max_actions = max_actions
        self.history: List[ActionRecord] = []
        self.active_window: Dict[str, Any] = {}
        self.last_screenshot_b64: Optional[str] = None
        self.error_message: Optional[str] = None
        self.final_result: Optional[str] = None
        self.created_at = time.time()

    def start(self):
        self.status = "running"
        self.step = 0

    def is_finished(self) -> bool:
        return self.status in ("completed", "failed", "stopped") or self.step >= self.max_actions

    def record_action(
        self,
        tool: str,
        arguments: Dict[str, Any],
        result: Optional[Any],
        success: bool,
        error: Optional[str] = None,
        thought: Optional[str] = None,
    ) -> ActionRecord:
        self.step += 1
        record = ActionRecord(
            step=self.step,
            tool=tool,
            arguments=arguments,
            result=result,
            success=success,
            error=error,
            thought=thought,
        )
        self.history.append(record)
        return record

    def get_recent_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.history[-limit:]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "status": self.status,
            "step": self.step,
            "max_actions": self.max_actions,
            "history_count": len(self.history),
            "recent_actions": self.get_recent_history(limit=3),
            "active_window": self.active_window.get("title", ""),
            "error_message": self.error_message,
            "final_result": self.final_result,
        }
