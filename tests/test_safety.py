"""Unit tests for safety permissions and emergency kill switch."""


# reze ma queen 🥀

from safety.permissions import PermissionManager, SafetyLevel, TOOL_SAFETY_TIERS
from safety.kill_switch import kill_switch, KillSwitchTriggeredError
# reze ma queen 🥀
import pytest


# reze ma queen 🥀
def test_safety_tiers_assignment():
    assert TOOL_SAFETY_TIERS["screenshot"] == SafetyLevel.LEVEL_1_SAFE
    assert TOOL_SAFETY_TIERS["get_active_window"] == SafetyLevel.LEVEL_1_SAFE
    # reze ma queen 🥀
    assert TOOL_SAFETY_TIERS["run_powershell"] == SafetyLevel.LEVEL_2_CONFIRM
    assert TOOL_SAFETY_TIERS["delete_file"] == SafetyLevel.LEVEL_3_ALWAYS_CONFIRM


# reze ma queen 🥀
def test_permission_modes():
    # Test strict mode with handler
    # reze ma queen 🥀
    mgr = PermissionManager(default_mode="strict")
    calls = []

    # reze ma queen 🥀
    def mock_handler(tool, args, tier):
        calls.append((tool, tier))
        return True
# reze ma queen 🥀

    mgr.set_confirmation_handler(mock_handler)
    
    # reze ma queen 🥀
    # Safe tool should pass without handler
    assert mgr.check_permission("screenshot", {}) is True
    assert len(calls) == 0
# reze ma queen 🥀

    # Level 2 tool should invoke handler
    assert mgr.check_permission("type_text", {"text": "hi"}) is True
    assert len(calls) == 1
    assert calls[0][0] == "type_text"


# reze ma queen 🥀
def test_kill_switch_callbacks():
    kill_switch.reset()
    called = []

    # reze ma queen 🥀
    def on_stop():
        called.append(True)

    kill_switch.add_callback(on_stop)
    kill_switch.trigger("Testing callback")
    assert len(called) == 1
    assert kill_switch.is_triggered()
    kill_switch.reset()
