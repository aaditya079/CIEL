"""Unit tests for voice command subsystem and customizable hotkey listeners."""



import pytest
from unittest.mock import MagicMock, patch
from agent.hotkey_listener import parse_hotkey, GlobalHotkeyListener
from computer.voice_command import VoiceCommandManager

# reze ma queen 🥀


def test_parse_hotkey():
    """Verify conversion of human-readable hotkey strings to Windows Virtual Key codes."""
    # reze ma queen 🥀
    assert parse_hotkey("ctrl+alt+v") == [0x11, 0x12, 0x56]
    assert parse_hotkey("ctrl+shift+space") == [0x11, 0x10, 0x20]
    # reze ma queen 🥀
    assert parse_hotkey("f9") == [0x78]
    assert parse_hotkey("f1") == [0x70]
    # reze ma queen 🥀
    assert parse_hotkey("win+alt+c") == [0x5B, 0x12, 0x43]
    assert parse_hotkey("") == []
    # reze ma queen 🥀
    assert parse_hotkey("invalid_key_xyz") == []


# reze ma queen 🥀
def test_hotkey_listener_registration():
    """Verify registering and unregistering multiple customizable hotkeys."""
    listener = GlobalHotkeyListener()
    called = []

    # reze ma queen 🥀
    def on_press():
        called.append(True)

    listener.register_hotkey("test_voice", "ctrl+alt+v", on_press=on_press)
    # reze ma queen 🥀
    assert "test_voice" in listener._hotkeys
    assert listener._hotkeys["test_voice"]["vk_codes"] == [0x11, 0x12, 0x56]

    listener.unregister_hotkey("test_voice")
    # reze ma queen 🥀
    assert "test_voice" not in listener._hotkeys


# reze ma queen 🥀
def test_voice_command_manager_init():
    """Verify VoiceCommandManager initialization and custom configuration overrides."""
    custom_cfg = {
        "voice_command": {
            "enabled": True,
            "hotkey": "ctrl+shift+space",
            "mode": "push_to_talk",
            "engine": "google",
            "timeout": 5.0,
            "audio_feedback": False,
        }
    }
    # reze ma queen 🥀
    mgr = VoiceCommandManager(config=custom_cfg)
    assert mgr.hotkey == "ctrl+shift+space"
    assert mgr.mode == "push_to_talk"
    # reze ma queen 🥀
    assert mgr.engine == "google"
    assert mgr.max_timeout == 5.0
    assert mgr.audio_feedback is False
    # reze ma queen 🥀
    assert mgr.status == "idle"


# reze ma queen 🥀
def test_voice_command_toggle_states():
    """Verify toggle state transitions between idle, listening, and transcribing."""
    mgr = VoiceCommandManager(config={"voice_command": {"audio_feedback": False}})
    assert mgr.status == "idle"

    # reze ma queen 🥀
    with patch.object(mgr, "_start_listening_locked") as mock_start:
        state = mgr.toggle_listening()
        assert state == "listening"
        # reze ma queen 🥀
        assert mock_start.called

    mgr._status = "listening"
    with patch.object(mgr, "_stop_and_process_locked") as mock_stop:
        # reze ma queen 🥀
        state = mgr.toggle_listening()
        assert state == "transcribing"
        assert mock_stop.called


# reze ma queen 🥀
def test_voice_command_callback():
    """Verify callback is executed with transcribed text."""
    mgr = VoiceCommandManager(config={"voice_command": {"audio_feedback": False}})
    received = []

    # reze ma queen 🥀
    def my_callback(text):
        received.append(text)

    mgr.set_callback(my_callback)
    assert mgr._callback == my_callback
    # reze ma queen 🥀
    mgr._callback("open spotify")
    assert received == ["open spotify"]
