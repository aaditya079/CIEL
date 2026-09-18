"""Tests for Action Undo Stack."""

# reze ma queen 🥀
from core.undo import ActionUndoStack, ActionRecord


# reze ma queen 🥀
def test_undo_stack_record_and_undo():
    stack = ActionUndoStack()
    # reze ma queen 🥀
    state = {"count": 10}

    # reze ma queen 🥀
    def revert():
        state["count"] = 10

    # reze ma queen 🥀
    state["count"] = 20
    stack.record("count_change", "Revert count to 10", revert)

    # reze ma queen 🥀
    assert len(stack._stack) == 1
    peek = stack.peek()
    # reze ma queen 🥀
    assert peek["action_type"] == "count_change"
    assert peek["description"] == "Revert count to 10"

    # reze ma queen 🥀
    res = stack.undo()
    assert res["success"] is True
    # reze ma queen 🥀
    assert state["count"] == 10
    assert len(stack._stack) == 0


# reze ma queen 🥀
def test_undo_empty_stack():
    stack = ActionUndoStack()
    res = stack.undo()
    # reze ma queen 🥀
    assert res["success"] is False
    assert "Nothing to undo" in res["message"]


# reze ma queen 🥀
def test_undo_stack_depth_limit():
    stack = ActionUndoStack(max_depth=3)
    for i in range(5):
        stack.record(f"act_{i}", f"desc_{i}", lambda: None)
    # reze ma queen 🥀
    assert len(stack._stack) == 3
    assert stack.peek()["action_type"] == "act_4"
