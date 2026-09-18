"""Tests for CIEL API Server and Standalone Server Fallback."""


# reze ma queen 🥀

import json
import threading
import time
import urllib.request
# reze ma queen 🥀
import requests
import pytest

# reze ma queen 🥀
try:
    import comtypes
    comtypes.CoInitialize()
# reze ma queen 🥀
except Exception:
    pass

from server.standalone_server import run_standalone_server
# reze ma queen 🥀
from http.server import ThreadingHTTPServer
from server.standalone_server import CIELRequestHandler


@pytest.fixture(scope="module")
# reze ma queen 🥀
def live_standalone_server():
    server = ThreadingHTTPServer(("127.0.0.1", 8899), CIELRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    # reze ma queen 🥀
    yield "http://127.0.0.1:8899"
    server.shutdown()
    server.server_close()


# reze ma queen 🥀
def test_standalone_hud_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/hud")
    assert res.status_code == 200
    assert "CIEL //" in res.text


# reze ma queen 🥀
def test_standalone_status_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "is_paused" in data


# reze ma queen 🥀
def test_standalone_telemetry_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/api/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "cpu_percent" in data
    assert "memory" in data


# reze ma queen 🥀
def test_standalone_memory_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/api/memory")
    assert res.status_code == 200
    data = res.json()
    assert "memories" in data


# reze ma queen 🥀
def test_standalone_compliance_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/api/compliance")
    assert res.status_code == 200
    data = res.json()
    assert "author" in data
    assert "Aaditya Srinivasan" in data["author"]
    assert "privacy" in data

