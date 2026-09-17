"""Unit tests for tools and registry."""

import os
from tools.registry import TOOL_DEFINITIONS, dispatcher
from tools.powershell import run_powershell, is_command_dangerous
from tools.files import read_file, list_directory
from tools.apps import is_app_running


def test_tool_definitions_valid():
    assert len(TOOL_DEFINITIONS) >= 15
    for tool in TOOL_DEFINITIONS:
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool
        assert tool["parameters"]["type"] == "object"


def test_powershell_execution():
    res = run_powershell("echo 'Hello PowerShell'")
    assert res["success"] is True
    assert "Hello PowerShell" in res["stdout"]


def test_powershell_dangerous_command_blocked():
    assert is_command_dangerous("Format-Volume -DriveLetter D") is True
    assert is_command_dangerous("rmdir /s /q C:\\") is True
    assert is_command_dangerous("Get-Process") is False

    res = run_powershell("Format-Volume -DriveLetter D")
    assert res["success"] is False
    assert "destructive" in res["stderr"]


def test_file_tools():
    # Read this test file
    this_file = os.path.abspath(__file__)
    res = read_file(this_file)
    assert res["success"] is True
    assert "test_file_tools" in res["content"]

    # List directory
    dir_res = list_directory(os.path.dirname(this_file))
    assert dir_res["success"] is True
    entries = [e["name"] for e in dir_res["entries"]]
    assert os.path.basename(this_file) in entries


def test_dispatcher_execution():
    res = dispatcher.execute("wait", {"seconds": 0.05})
    assert res["success"] is True

    # Test unknown tool
    res = dispatcher.execute("non_existent_tool_123", {})
    assert res["success"] is False
    assert "Unknown tool" in res["error"]


def test_focus_window_registration():
    tool_names = [t["name"] for t in TOOL_DEFINITIONS]
    assert "focus_window" in tool_names
    # Dispatching focus_window for non-existent window should return boolean without exception
    res = dispatcher.execute("focus_window", {"title": "NonExistentWindowTitle12345"})
    assert res["success"] is True
    assert res["result"] is False

