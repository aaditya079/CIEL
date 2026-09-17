"""Native standard library HTTP server fallback for CIEL HUD and REST API.

Provides zero-dependency operation for `ciel --hud` and `ciel --serve` if
FastAPI or Uvicorn are ever unavailable.
"""

import json
import io
import os
import threading
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Optional

from safety.kill_switch import kill_switch
from computer.screen import take_screenshot
from computer.windows import list_open_windows, get_active_window
from computer.system_telemetry import get_system_telemetry
from agent.state import AgentState
from agent.executor import AgentExecutor
from agent.brain import AgentBrain
from config.manager import load_config

logger = logging.getLogger("desktop_agent.server.standalone")

_executor: Optional[AgentExecutor] = None
_state: Optional[AgentState] = None


def _init_agent():
    global _executor
    if _executor is None:
        try:
            config = load_config()
            brain = AgentBrain(config=config)
            _executor = AgentExecutor(brain=brain, config=config)
        except Exception as e:
            logger.warning(f"Could not initialize AgentExecutor in standalone server: {e}")


def _run_task_thread(goal: str, max_actions: int = 50):
    global _state, _executor
    kill_switch.reset()
    _state = AgentState(goal=goal, max_actions=max_actions)
    if _executor:
        try:
            _executor.run(goal=goal, state=_state)
        except Exception as e:
            logger.error(f"Error in task thread: {e}")
            _state.status = "error"


class CIELRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler serving HUD static files and REST API endpoints."""

    def log_message(self, format, *args):
        # Suppress noisy GET log spam for polling
        pass

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/hud"):
            hud_path = os.path.join(os.path.dirname(__file__), "hud.html")
            try:
                with open(hud_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Failed to load HUD: {e}")
            return

        if path == "/api/status":
            active_win = get_active_window()
            status_data = {
                "status": _state.status if _state else "idle",
                "task_id": _state.task_id if _state else None,
                "goal": _state.goal if _state else None,
                "step": _state.step if _state else 0,
                "max_actions": _state.max_actions if _state else 50,
                "active_window": active_win.get("title", ""),
                "is_paused": kill_switch.is_paused(),
                "is_stopped": kill_switch.is_triggered(),
                "recent_actions": _state.get_recent_history(limit=5) if _state else [],
            }
            self._send_json(status_data)
            return

        if path == "/api/telemetry":
            self._send_json(get_system_telemetry())
            return

        if path in ("/api/screen", "/api/screenshot"):
            try:
                img = take_screenshot(resize_max=(1280, 720))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80)
                val = buf.getvalue()
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(val)))
                self.end_headers()
                self.wfile.write(val)
            except Exception as e:
                self.send_error(500, str(e))
            return

        if path == "/api/windows":
            self._send_json(list_open_windows(only_visible=True))
            return

        if path == "/api/memory":
            try:
                from memory.long_term import memory_store
                self._send_json({"memories": memory_store.list_all()})
            except Exception as e:
                self._send_json({"memories": {}, "error": str(e)})
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if path == "/api/task":
            goal = payload.get("goal", "").strip()
            max_actions = int(payload.get("max_actions", 50))
            if not goal:
                self._send_json({"error": "Missing goal"}, status=400)
                return

            if _state and _state.status == "running":
                self._send_json({"error": "A task is already actively running"}, status=400)
                return

            _init_agent()
            t = threading.Thread(target=_run_task_thread, args=(goal, max_actions), daemon=True)
            t.start()
            self._send_json({"status": "started", "message": f"Task initiated: '{goal}'"})
            return

        if path == "/api/stop":
            kill_switch.trigger("Triggered via HUD Stop")
            if _state:
                _state.status = "stopped"
            self._send_json({"status": "stopped", "message": "Emergency kill switch activated."})
            return

        if path == "/api/pause":
            kill_switch.pause()
            self._send_json({"status": "paused"})
            return

        if path == "/api/resume":
            kill_switch.resume()
            self._send_json({"status": "resumed"})
            return

        self.send_error(404, "Not Found")


def run_standalone_server(port: int = 8000, host: str = "0.0.0.0"):
    """Run the native standard-library HTTP server."""
    _init_agent()
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, CIELRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
