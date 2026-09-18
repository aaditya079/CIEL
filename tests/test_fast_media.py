"""Unit tests for Next-Gen Instant Media Architecture.

Tests Spicetify bridge queue, headless background audio streaming,
and fast-router dual-mode routing.
"""

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


import os
try:
    import comtypes
    comtypes.CoInitialize()
except Exception:
    pass

from unittest.mock import patch, MagicMock
from tools.streamer import stream_audio, stop_audio_stream, is_audio_streaming
import tools.spicetify_bridge as spicetify_bridge
from agent.fast_router import fast_router
from tools.registry import dispatcher


def test_spicetify_bridge_extension_path():
    assert "ciel_bridge.js" in spicetify_bridge.SPICETIFY_EXT_PATH
    # Ensure bridge extension file exists
    assert os.path.exists(spicetify_bridge.SPICETIFY_EXT_PATH)


def test_spicetify_command_queue():
    spicetify_bridge.send_command("play", query="test_track_123")
    cmd = spicetify_bridge._COMMAND_QUEUE.get_nowait()
    assert cmd["action"] == "play"
    assert cmd["query"] == "test_track_123"


def test_streamer_dispatch_registration():
    assert "stream_audio" in dispatcher._handlers
    assert "stop_audio_stream" in dispatcher._handlers


def test_streamer_stop_when_idle():
    res = stop_audio_stream()
    assert res["success"] is True
    assert is_audio_streaming() is False


def test_fast_router_stream_intent():
    # Mock stream_audio to verify routing without launching actual ffplay
    with patch("agent.fast_router.stream_audio") as mock_stream:
        mock_stream.return_value = {"success": True, "mode": "headless_stream", "message": "Streaming lofi beats."}
        route = fast_router.route("stream lofi beats")
        assert route is not None
        assert route["tool"] == "stream_audio"
        assert route["arguments"]["query"] == "lofi beats"
        mock_stream.assert_called_once_with("lofi beats")


def test_fast_router_youtube_brave_intent():
    with patch("agent.fast_router.play_youtube") as mock_yt:
        mock_yt.return_value = {"success": True, "message": "Playing harvey on YouTube."}
        route = fast_router.route("open youtube on brave and play harvey")
        assert route is not None
        assert route["tool"] == "play_youtube"
        assert route["arguments"]["query"] == "harvey"
        assert route["arguments"]["browser_name"] == "brave"
        mock_yt.assert_called_once_with("harvey", browser_name="brave")


def test_fast_router_watch_intent():
    with patch("agent.fast_router.play_youtube") as mock_yt:
        mock_yt.return_value = {"success": True, "message": "Playing queen on YouTube."}
        route = fast_router.route("watch queen on youtube")
        assert route is not None
        assert route["tool"] == "play_youtube"
        assert route["arguments"]["query"] == "queen"
