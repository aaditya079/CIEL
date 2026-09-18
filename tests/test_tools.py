"""Unit tests for tools and registry."""

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


def test_open_application_argument_aliases():
    from tools.apps import KNOWN_APPS
    # Ensure browsers are registered
    assert "brave" in KNOWN_APPS
    assert "firefox" in KNOWN_APPS
    assert "vscode" in KNOWN_APPS

    # Test open_application alias resolution without throwing TypeError
    res1 = dispatcher.execute("open_application", {"application_name": "NonExistentTestApp999", "wait_timeout": 0.1})
    assert res1["success"] is True

    res2 = dispatcher.execute("open_application", {"name": "NonExistentTestApp999", "wait_timeout": 0.1})
    assert res2["success"] is True


def test_click_with_clicks_and_extra_kwargs():
    # Test dispatcher handling click with clicks count and unexpected kwargs
    res = dispatcher.execute("click", {"x": 10, "y": 10, "button": "left", "clicks": 1, "unexpected_param": "ignored"})
    assert res["success"] is True
    assert res["result"] == (10, 10)


def test_spotify_play_button_cv2_logic():
    import numpy as np
    import cv2

    # Synthesize an image with:
    # 1. A small checkmark (10x10, area 100)
    # 2. A circular play button (50x50 circle, area ~ 1900)
    # 3. Random noise
    h, w = 1000, 1000
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # Green checkmark at (200, 400)
    cv2.rectangle(img, (400, 200), (410, 210), (30, 215, 96), -1)

    # Circular Play Button at (600, 300) with radius 25
    cv2.circle(img, (600, 300), 25, (30, 215, 96), -1)

    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]
    mask = (g > 150) & (r < 100) & (b < 140) & (g.astype(int) > 1.15 * (r.astype(int) + b.astype(int)))
    mask_u8 = (mask * 255).astype(np.uint8)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8)
    candidates = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        left = stats[i, cv2.CC_STAT_LEFT]
        top = stats[i, cv2.CC_STAT_TOP]
        width = stats[i, cv2.CC_STAT_WIDTH]
        height = stats[i, cv2.CC_STAT_HEIGHT]
        cx, cy = centroids[i]
        aspect = width / max(1, height)
        if 0.10 * h < top < 0.65 * h and 0.15 * w < left < 0.85 * w:
            if area >= 150 and 0.75 <= aspect <= 1.35:
                candidates.append((area, int(round(cx)), int(round(cy))))

    candidates.sort(key=lambda c: c[0], reverse=True)
    assert len(candidates) == 1
    best_area, best_cx, best_cy = candidates[0]
    assert abs(best_cx - 600) <= 2
    assert abs(best_cy - 300) <= 2

