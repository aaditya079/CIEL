"""Tests for FastPathRouter intent matching and routing."""

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


import pytest
from agent.fast_router import fast_router


def test_fast_router_volume():
    # Volume set
    res = fast_router.route("volume 50")
    assert res is not None
    assert res["handled"] is True
    assert res["tool"] == "set_volume"
    assert res["arguments"] == {"level": 50}

    # Volume set with prefix
    res2 = fast_router.route("ciel set volume to 80%")
    assert res2 is not None
    assert res2["tool"] == "set_volume"
    assert res2["arguments"] == {"level": 80}


def test_fast_router_mute():
    res = fast_router.route("ciel mute")
    assert res is not None
    assert res["tool"] == "media_control"
    assert res["arguments"] == {"action": "mute"}


def test_fast_router_media_keys():
    res_pause = fast_router.route("pause music")
    assert res_pause is not None
    assert res_pause["tool"] == "media_control"
    assert res_pause["arguments"] == {"action": "play_pause"}

    res_next = fast_router.route("next track")
    assert res_next is not None
    assert res_next["tool"] == "media_control"
    assert res_next["arguments"] == {"action": "next"}


def test_fast_router_system_stats():
    res = fast_router.route("ciel system stats")
    assert res is not None
    assert res["handled"] is True
    assert res["tool"] == "get_system_stats"
    assert "data" in res


def test_fast_router_youtube():
    res = fast_router.route("play bohemian rhapsody on youtube")
    assert res is not None
    assert res["handled"] is True
    assert res["tool"] == "play_youtube"
    assert res["arguments"]["query"] == "bohemian rhapsody"


def test_fast_router_spotify():
    res = fast_router.route("open spotify and play harvey")
    assert res is not None
    assert res["handled"] is True
    assert res["tool"] == "play_spotify"
    assert res["arguments"]["query"] == "harvey"


def test_fast_router_weather():
    res = fast_router.route("ciel weather in Tokyo")
    assert res is not None
    assert res["handled"] is True
    assert res["tool"] == "get_weather"
    assert res["arguments"]["city"].lower() == "tokyo"


def test_fast_router_desktop_actions():
    res_desk = fast_router.route("ciel show desktop")
    assert res_desk is not None
    assert res_desk["tool"] == "show_desktop"

    res_tm = fast_router.route("ciel task manager")
    assert res_tm is not None
    assert res_tm["tool"] == "open_task_manager"

    res_max = fast_router.route("ciel maximize")
    assert res_max is not None
    assert res_max["tool"] == "window_action"
    assert res_max["arguments"] == {"action": "maximize"}


def test_fast_router_unhandled_complex_goals():
    # Arbitrary complex UI tasks must return None so the vision LLM agent handles them
    assert fast_router.route("organize all pdf files on my desktop into a folder") is None
    assert fast_router.route("open discord and send message to alex") is None
    assert fast_router.route("log into my email and check inbox") is None
