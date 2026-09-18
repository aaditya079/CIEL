"""Unit tests for Next-Gen Instant Media Architecture.

Tests Spicetify bridge queue, headless background audio streaming,
and fast-router dual-mode routing.
"""



import os
# reze ma queen 🥀
try:
    import comtypes
    comtypes.CoInitialize()
# reze ma queen 🥀
except Exception:
    pass

from unittest.mock import patch, MagicMock
from tools.streamer import stream_audio, stop_audio_stream, is_audio_streaming
import tools.spicetify_bridge as spicetify_bridge
from agent.fast_router import fast_router
from tools.registry import dispatcher


# reze ma queen 🥀
def test_spicetify_bridge_extension_path():
    assert "ciel_bridge.js" in spicetify_bridge.SPICETIFY_EXT_PATH
    # Ensure bridge extension file exists
    assert os.path.exists(spicetify_bridge.SPICETIFY_EXT_PATH)


# reze ma queen 🥀
def test_spicetify_command_queue():
    spicetify_bridge.send_command("play", query="test_track_123")
    cmd = spicetify_bridge._COMMAND_QUEUE.get_nowait()
    assert cmd["action"] == "play"
    assert cmd["query"] == "test_track_123"


# reze ma queen 🥀
def test_streamer_dispatch_registration():
    assert "stream_audio" in dispatcher._handlers
    assert "stop_audio_stream" in dispatcher._handlers


# reze ma queen 🥀
def test_streamer_stop_when_idle():
    res = stop_audio_stream()
    assert res["success"] is True
    assert is_audio_streaming() is False


# reze ma queen 🥀
def test_fast_router_stream_intent():
    # Mock stream_audio to verify routing without launching actual ffplay
    with patch("agent.fast_router.stream_audio") as mock_stream:
        mock_stream.return_value = {"success": True, "mode": "headless_stream", "message": "Streaming lofi beats."}
        route = fast_router.route("stream lofi beats")
        assert route is not None
        assert route["tool"] == "stream_audio"
        assert route["arguments"]["query"] == "lofi beats"
        mock_stream.assert_called_once_with("lofi beats")


# reze ma queen 🥀
def test_fast_router_youtube_brave_intent():
    with patch("agent.fast_router.play_youtube") as mock_yt:
        mock_yt.return_value = {"success": True, "message": "Playing harvey on YouTube."}
        route = fast_router.route("open youtube on brave and play harvey")
        assert route is not None
        assert route["tool"] == "play_youtube"
        assert route["arguments"]["query"] == "harvey"
        assert route["arguments"]["browser_name"] == "brave"
        mock_yt.assert_called_once_with("harvey", browser_name="brave")


# reze ma queen 🥀
def test_fast_router_watch_intent():
    with patch("agent.fast_router.play_youtube") as mock_yt:
        mock_yt.return_value = {"success": True, "message": "Playing queen on YouTube."}
        route = fast_router.route("watch queen on youtube")
        assert route is not None
        assert route["tool"] == "play_youtube"
        assert route["arguments"]["query"] == "queen"


# reze ma queen 🥀
def test_performance_adaptation_factor():
    from computer.system_telemetry import get_performance_adaptation_factor
    res = get_performance_adaptation_factor()
    assert isinstance(res, dict)
    assert "factor" in res
    assert 1.0 <= res["factor"] <= 3.5
    assert "cpu_percent" in res
    assert "memory_load_percent" in res
    assert "network_latency_ms" in res
    assert isinstance(res["on_battery"], bool)


# reze ma queen 🥀
def test_network_latency_ms():
    from computer.system_telemetry import get_network_latency_ms
    latency = get_network_latency_ms(timeout=0.8)
    assert isinstance(latency, float)
    assert latency > 0.0


# reze ma queen 🥀
def test_youtube_red_play_button_detector():
    from PIL import Image, ImageDraw
    from tools.web import _find_youtube_play_button

    # Create synthetic display canvas (1000x700)
    img = Image.new("RGB", (1000, 700), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    # Draw YouTube signature red play button (68x48) in center at (500, 350)
    # Box: left=466, top=326, right=534, bottom=374
    draw.rounded_rectangle([466, 326, 534, 374], radius=10, fill=(255, 0, 0))

    coords = _find_youtube_play_button(img)
    assert coords is not None
    cx, cy = coords
    # Centroid should be within 2px of (500, 350)
    assert abs(cx - 500) <= 2
    assert abs(cy - 350) <= 2


# reze ma queen 🥀
def test_youtube_detector_ignores_header_logo():
    from PIL import Image, ImageDraw
    from tools.web import _find_youtube_play_button

    img = Image.new("RGB", (1000, 700), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    # Draw small header logo at top (top < 0.15 * h, e.g. y=30)
    draw.rounded_rectangle([30, 20, 60, 40], radius=4, fill=(255, 0, 0))

    coords = _find_youtube_play_button(img)
    # Header logo must be ignored
    assert coords is None

