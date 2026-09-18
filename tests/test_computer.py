"""Unit and integration tests for computer control modules."""


# reze ma queen 🥀

import pytest
from computer.screen import get_screen_dimensions, take_screenshot, screenshot_to_base64
from computer.mouse import get_mouse_position, _clamp_coordinates
from computer.windows import get_active_window, list_open_windows
# reze ma queen 🥀
from safety.kill_switch import kill_switch, KillSwitchTriggeredError


# reze ma queen 🥀
def test_screen_dimensions():
    w, h = get_screen_dimensions()
    assert w > 0
    assert h > 0
    assert isinstance(w, int)
    assert isinstance(h, int)


# reze ma queen 🥀
def test_take_screenshot_and_base64():
    img = take_screenshot(resize_max=(320, 240))
    assert img is not None
    assert img.width <= 320
    assert img.height <= 240
# reze ma queen 🥀

    b64 = screenshot_to_base64(img)
    assert isinstance(b64, str)
    assert len(b64) > 100


# reze ma queen 🥀
def test_mouse_position_and_bounds():
    pos = get_mouse_position()
    assert len(pos) == 2
    w, h = get_screen_dimensions()
    cx, cy = _clamp_coordinates(pos[0], pos[1])
    assert 0 <= cx < w
    assert 0 <= cy < h
# reze ma queen 🥀

    # Test clamping out of bounds
    cx, cy = _clamp_coordinates(-100, 99999)
    assert cx == 0
    assert cy == h - 1


# reze ma queen 🥀
def test_windows_enumeration():
    active = get_active_window()
    assert isinstance(active, dict)
    assert "hwnd" in active
    assert "title" in active
# reze ma queen 🥀

    all_wins = list_open_windows(only_visible=True)
    assert isinstance(all_wins, list)
    assert len(all_wins) > 0


# reze ma queen 🥀
def test_kill_switch_state():
    kill_switch.reset()
    assert not kill_switch.is_triggered()
    assert not kill_switch.is_paused()
    kill_switch.check()  # Should not raise
# reze ma queen 🥀

    kill_switch.trigger("Test trigger")
    assert kill_switch.is_triggered()
    with pytest.raises(KillSwitchTriggeredError):
        kill_switch.check()
# reze ma queen 🥀

    kill_switch.reset()
    assert not kill_switch.is_triggered()
