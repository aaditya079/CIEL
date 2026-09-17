"""Tests for newly added fast-path intent router patterns."""

from unittest.mock import patch
from agent.fast_router import fast_router


def test_fast_router_undo():
    res = fast_router.route("ciel undo")
    assert res is not None
    assert res["tool"] == "undo_last_action"

    res2 = fast_router.route("undo that")
    assert res2 is not None
    assert res2["tool"] == "undo_last_action"


def test_fast_router_morning_briefing():
    with patch("tools.proactive.voice.speak"):
        res = fast_router.route("ciel morning briefing")
        assert res is not None
        assert res["tool"] == "morning_briefing"

        res2 = fast_router.route("good morning")
        assert res2 is not None
        assert res2["tool"] == "morning_briefing"


def test_fast_router_clipboard():
    res = fast_router.route("what's on my clipboard")
    assert res is not None
    assert res["tool"] == "clipboard_action"

    res_clear = fast_router.route("clear clipboard")
    assert res_clear is not None
    assert res_clear["arguments"]["action"] == "clear"

    res_copy = fast_router.route("copy hello world to clipboard")
    assert res_copy is not None
    assert res_copy["arguments"]["text"] == "hello world"


def test_fast_router_flights():
    with patch("webbrowser.open"):
        res = fast_router.route("flights from NYC to London on Friday")
        assert res is not None
        assert res["tool"] == "find_flights"
        assert res["arguments"]["origin"] == "nyc"
        assert res["arguments"]["destination"] == "london"

        res2 = fast_router.route("find flights to Paris")
        assert res2 is not None
        assert res2["tool"] == "find_flights"
        assert res2["arguments"]["destination"] == "paris"


def test_fast_router_games():
    with patch("os.startfile"):
        res = fast_router.route("update steam games")
        assert res is not None
        assert res["tool"] == "game_control"
        assert res["arguments"]["action"] == "downloads"

        res_lib = fast_router.route("open steam library")
        assert res_lib is not None
        assert res_lib["arguments"]["action"] == "games"


def test_fast_router_sound_settings():
    with patch("os.startfile"):
        res = fast_router.route("sound settings")
        assert res is not None
        assert res["tool"] == "audio_control"
        assert res["arguments"]["action"] == "settings"

        res_mix = fast_router.route("volume mixer")
        assert res_mix is not None
        assert res_mix["arguments"]["action"] == "mixer"


def test_fast_router_memory():
    res_rem = fast_router.route("remember that my project is ciel")
    assert res_rem is not None
    assert res_rem["tool"] == "remember_fact"
    assert res_rem["arguments"]["key"] == "my project"
    assert res_rem["arguments"]["value"] == "ciel"

    res_rec = fast_router.route("recall my project")
    assert res_rec is not None
    assert res_rec["tool"] == "recall_fact"
    assert res_rec["arguments"]["key"] == "my project"
