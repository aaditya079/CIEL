"""Tests for Action Undo Stack."""

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


from core.undo import ActionUndoStack, ActionRecord


def test_undo_stack_record_and_undo():
    stack = ActionUndoStack()
    state = {"count": 10}

    def revert():
        state["count"] = 10

    state["count"] = 20
    stack.record("count_change", "Revert count to 10", revert)

    assert len(stack._stack) == 1
    peek = stack.peek()
    assert peek["action_type"] == "count_change"
    assert peek["description"] == "Revert count to 10"

    res = stack.undo()
    assert res["success"] is True
    assert state["count"] == 10
    assert len(stack._stack) == 0


def test_undo_empty_stack():
    stack = ActionUndoStack()
    res = stack.undo()
    assert res["success"] is False
    assert "Nothing to undo" in res["message"]


def test_undo_stack_depth_limit():
    stack = ActionUndoStack(max_depth=3)
    for i in range(5):
        stack.record(f"act_{i}", f"desc_{i}", lambda: None)
    assert len(stack._stack) == 3
    assert stack.peek()["action_type"] == "act_4"
