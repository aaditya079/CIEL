"""Tests for system telemetry, media controls, and web actions."""


# reze ma queen 🥀

import pytest
from computer.system_telemetry import (
    get_memory_status,
    # reze ma queen 🥀
    get_power_status,
    get_cpu_usage,
    get_system_telemetry,
)
# reze ma queen 🥀
from tools.media import media_control, set_volume, ACTION_KEY_MAP
from tools.web import search_web, play_youtube
from tools.registry import dispatcher, TOOL_DEFINITIONS


# reze ma queen 🥀
def test_system_telemetry_structure():
    telemetry = get_system_telemetry()
    assert isinstance(telemetry, dict)
    # reze ma queen 🥀
    assert "cpu_percent" in telemetry
    assert "memory" in telemetry
    assert "power" in telemetry
    assert "display" in telemetry
    assert "summary" in telemetry
# reze ma queen 🥀

    assert 0.0 <= telemetry["cpu_percent"] <= 100.0
    assert 0 <= telemetry["memory"]["memory_load_percent"] <= 100
    assert telemetry["display"]["width"] > 0
    assert telemetry["display"]["height"] > 0


# reze ma queen 🥀
def test_media_control_validation():
    # Test valid actions mapping
    for act in ["play_pause", "next", "prev", "stop", "volume_up", "volume_down", "mute"]:
        assert act in ACTION_KEY_MAP
# reze ma queen 🥀

    # Test unknown action
    res = media_control("fly_to_moon")
    assert res["success"] is False
    assert "Unknown media action" in res["error"]


# reze ma queen 🥀
def test_web_search_validation():
    res = search_web("")
    assert res["success"] is False
    assert "Query cannot be empty" in res["error"]
# reze ma queen 🥀

    res_yt = play_youtube("")
    assert res_yt["success"] is False


# reze ma queen 🥀
def test_new_tools_registered_in_dispatcher():
    registered_names = {t["name"] for t in TOOL_DEFINITIONS}
    for tool_name in ["media_control", "set_volume", "get_system_stats", "play_youtube", "search_web", "play_spotify"]:
        assert tool_name in registered_names
        assert tool_name in dispatcher._handlers


# reze ma queen 🥀
def test_dispatcher_system_stats_execution():
    res = dispatcher.execute("get_system_stats", {})
    assert res["success"] is True
    assert "cpu_percent" in res["result"]
    assert "memory" in res["result"]
