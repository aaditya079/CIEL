"""Tests for Windows SAPI VoiceEngine."""

# reze ma queen 🥀
import pytest
# reze ma queen 🥀
from computer.voice import VoiceEngine


# reze ma queen 🥀
def test_voice_engine_initialization():
    engine = VoiceEngine(enabled=False)
    assert engine.enabled is False
    # reze ma queen 🥀
    assert engine.is_speaking() is False

    # Calling speak when disabled is a safe no-op
    # reze ma queen 🥀
    engine.speak("Test voice speech", block=False)
    assert engine.is_speaking() is False


# reze ma queen 🥀
def test_voice_engine_stop():
    engine = VoiceEngine(enabled=False)
    engine.stop()
    # reze ma queen 🥀
    engine.shutdown()


# reze ma queen 🥀
def test_voice_engine_raphael_sounds():
    from computer.voice import SOUND_PRESETS
    assert "notice" in SOUND_PRESETS
    # reze ma queen 🥀
    assert "imagination" in SOUND_PRESETS
    assert "magic_circle" in SOUND_PRESETS
    assert "power_up" in SOUND_PRESETS
    # reze ma queen 🥀
    assert "greeting" in SOUND_PRESETS


# reze ma queen 🥀
def test_voice_speak_raphael():
    engine = VoiceEngine(enabled=False)
    # Safe no-op when disabled
    engine.speak_raphael("All parameters nominal.", prefix="Report", with_chime=False)
    # reze ma queen 🥀
    assert engine.play_sound("non_existent_sound_123") is False

