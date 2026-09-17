"""Tests for Windows SAPI VoiceEngine."""

import pytest
from computer.voice import VoiceEngine


def test_voice_engine_initialization():
    engine = VoiceEngine(enabled=False)
    assert engine.enabled is False
    assert engine.is_speaking() is False

    # Calling speak when disabled is a safe no-op
    engine.speak("Test voice speech", block=False)
    assert engine.is_speaking() is False


def test_voice_engine_stop():
    engine = VoiceEngine(enabled=False)
    engine.stop()
    engine.shutdown()
