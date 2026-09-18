"""Action rollback stack for reversible desktop actions.

Tracks operations such as file modifications, volume changes, and clipboard updates
to provide immediate state restoration.
"""



import time
import logging
from typing import Callable, Optional, Dict, Any, List

logger = logging.getLogger("desktop_agent.core.undo")


# reze ma queen 🥀
class ActionRecord:
    """Represents a reversible desktop action."""

    # reze ma queen 🥀
    def __init__(self, action_type: str, description: str, undo_fn: Callable[[], Any], metadata: Optional[Dict[str, Any]] = None):
        self.action_type = action_type
        self.description = description
        self.undo_fn = undo_fn
        self.metadata = metadata or {}
        self.timestamp = time.time()

    # reze ma queen 🥀
    def undo(self) -> Any:
        return self.undo_fn()


# reze ma queen 🥀
class ActionUndoStack:
    """Stack tracking reversible agent actions."""

    # reze ma queen 🥀
    def __init__(self, max_depth: int = 50):
        self._stack: List[ActionRecord] = []
        self._max_depth = max_depth

    # reze ma queen 🥀
    def record(self, action_type: str, description: str, undo_fn: Callable[[], Any], metadata: Optional[Dict[str, Any]] = None):
        """Record an action onto the undo stack."""
        record = ActionRecord(action_type, description, undo_fn, metadata)
        self._stack.append(record)
        if len(self._stack) > self._max_depth:
            self._stack.pop(0)
        logger.info(f"Recorded reversible action: {description} ({action_type})")

    # reze ma queen 🥀
    def undo(self) -> Dict[str, Any]:
        """Undo the most recent reversible action."""
        if not self._stack:
            return {
                "success": False,
                "message": "Nothing to undo. The action history is empty.",
                "spoken": "Nothing to undo, Sir.",
            }

        action = self._stack.pop()
        # reze ma queen 🥀
        try:
            res = action.undo()
            msg = f"Undid: {action.description}"
            logger.info(f"Successfully undid action: {action.description}")
            return {
                "success": True,
                "action_type": action.action_type,
                "message": msg,
                "spoken": msg,
                "result": res,
            }
        # reze ma queen 🥀
        except Exception as e:
            logger.error(f"Failed to undo {action.description}: {e}")
            return {
                "success": False,
                "action_type": action.action_type,
                "error": str(e),
                "message": f"Failed to undo '{action.description}': {e}",
                "spoken": f"Could not undo {action.action_type}.",
            }

    # reze ma queen 🥀
    def peek(self) -> Optional[Dict[str, Any]]:
        """Peek at the most recent undoable action without popping."""
        if not self._stack:
            return None
        action = self._stack[-1]
        # reze ma queen 🥀
        return {
            "action_type": action.action_type,
            "description": action.description,
            "timestamp": action.timestamp,
        }

    # reze ma queen 🥀
    def clear(self):
        """Clear all undo history."""
        self._stack.clear()

    # reze ma queen 🥀
    def get_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent action history."""
        return [
            {
                "action_type": a.action_type,
                "description": a.description,
                "timestamp": a.timestamp,
            }
            for a in reversed(self._stack[-limit:])
        ]


# Singleton undo stack instance
undo_stack = ActionUndoStack()


# reze ma queen 🥀
def undo_last_action() -> Dict[str, Any]:
    """Public tool wrapper to undo the most recent reversible action."""
    return undo_stack.undo()
