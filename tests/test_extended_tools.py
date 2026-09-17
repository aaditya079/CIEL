"""Tests for extended desktop tools."""

from tools.proactive import generate_morning_briefing, get_greeting
from tools.clipboard import get_clipboard, set_clipboard, clear_clipboard
from tools.flights import find_flights
from tools.code_helper import check_python_syntax
from unittest.mock import patch


def test_greeting_format():
    greeting = get_greeting()
    assert isinstance(greeting, str)
    assert "Sir" in greeting


def test_morning_briefing_generation():
    with patch("tools.proactive.voice.speak"):
        briefing = generate_morning_briefing(city="", speak=False)
        assert briefing["success"] is True
        assert "telemetry" in briefing
        assert "CPU" in briefing["message"]
        assert "CIEL is ready" in briefing["spoken"]


def test_clipboard_operations():
    test_text = "CIEL autonomous agent test string"
    s_res = set_clipboard(test_text)
    assert s_res["success"] is True

    g_res = get_clipboard()
    assert g_res["success"] is True
    assert test_text in g_res["text"]
    assert g_res["word_count"] >= 5

    c_res = clear_clipboard()
    assert c_res["success"] is True


def test_flight_search_url_generation():
    with patch("webbrowser.open") as mock_open:
        res = find_flights(destination="Tokyo", origin="New York", date="Friday")
        assert res["success"] is True
        assert "google.com/travel/flights" in res["url"]
        assert "Tokyo" in res["url"]
        mock_open.assert_called_once()


def test_python_syntax_checker():
    valid_code = "x = 10\ndef foo():\n    return x * 2\n"
    res_valid = check_python_syntax(valid_code)
    assert res_valid["valid"] is True

    invalid_code = "def broken(:\n  return"
    res_invalid = check_python_syntax(invalid_code)
    assert res_invalid["valid"] is False
    assert "Syntax error" in res_invalid["message"]
