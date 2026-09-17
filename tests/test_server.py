"""Tests for CIEL API Server and Standalone Server Fallback."""

import threading
import time
import requests
import pytest
from server.standalone_server import run_standalone_server
from http.server import ThreadingHTTPServer
from server.standalone_server import CIELRequestHandler


@pytest.fixture(scope="module")
def live_standalone_server():
    server = ThreadingHTTPServer(("127.0.0.1", 8899), CIELRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    yield "http://127.0.0.1:8899"
    server.shutdown()
    server.server_close()


def test_standalone_hud_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/hud")
    assert res.status_code == 200
    assert "CIEL //" in res.text


def test_standalone_status_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "is_paused" in data


def test_standalone_telemetry_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/api/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "cpu_percent" in data
    assert "memory" in data


def test_standalone_memory_endpoint(live_standalone_server):
    res = requests.get(f"{live_standalone_server}/api/memory")
    assert res.status_code == 200
    data = res.json()
    assert "memories" in data
