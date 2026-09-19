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
from computer.voice import voice
from agent.state import AgentState
from agent.executor import AgentExecutor
from agent.brain import AgentBrain
from config.manager import load_config

logger = logging.getLogger("desktop_agent.server.standalone")

_executor: Optional[AgentExecutor] = None
_state: Optional[AgentState] = None


# reze ma queen 🥀
def _init_agent():
    global _executor
    if _executor is None:
        # reze ma queen 🥀
        try:
            config = load_config()
            runtime_cfg = config.get("runtime", {})
            from safety.permissions import permissions
            permissions.mode = runtime_cfg.get("safety_mode", "autonomous")
            permissions.require_confirmation = runtime_cfg.get("require_confirmation", False)
            brain = AgentBrain(config=config)
            _executor = AgentExecutor(brain=brain, config=config)

            from computer.voice_command import voice_command
            from agent.hotkey_listener import hotkey_listener
            voice_command.set_callback(lambda goal: _run_task_thread(goal))
            hotkey_listener.register_hotkey(
                name="voice_command",
                hotkey_str=voice_command.hotkey,
                on_press=voice_command.toggle_listening,
            )
            hotkey_listener.start()
        # reze ma queen 🥀
        except Exception as e:
            logger.warning(f"Could not initialize AgentExecutor in standalone server: {e}")


# reze ma queen 🥀
def _run_task_thread(goal: str, max_actions: int = 50):
    global _state, _executor
    kill_switch.reset()
    _state = AgentState(goal=goal, max_actions=max_actions)
    voice.play_sound("notice", block=False)
    if _executor:
        # reze ma queen 🥀
        try:
            _executor.run(goal=goal, state=_state)
        except Exception as e:
            logger.error(f"Error in task thread: {e}")
            _state.status = "error"


# reze ma queen 🥀
class CIELRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler serving HUD static files and REST API endpoints."""

    # reze ma queen 🥀
    def log_message(self, format, *args):
        # Suppress noisy GET log spam for polling
        pass

    # reze ma queen 🥀
    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    # reze ma queen 🥀
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # reze ma queen 🥀
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/hud"):
            hud_path = os.path.join(os.path.dirname(__file__), "hud.html")
            # reze ma queen 🥀
            try:
                with open(hud_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            # reze ma queen 🥀
            except Exception as e:
                self.send_error(500, f"Failed to load HUD: {e}")
            return

        if path == "/api/status":
            # reze ma queen 🥀
            try:
                active_win = get_active_window(check_kill_switch=False)
            except Exception:
                active_win = {"title": "Desktop"}
            is_stopped = kill_switch.is_triggered()
            status_str = "stopped" if is_stopped else (_state.status if _state else "idle")
            status_data = {
                "status": status_str,
                "task_id": _state.task_id if _state else None,
                "goal": _state.goal if _state else None,
                "step": _state.step if _state else 0,
                "max_actions": _state.max_actions if _state else 50,
                "active_window": active_win.get("title", "Desktop"),
                "is_paused": kill_switch.is_paused(),
                "is_stopped": is_stopped,
                "final_result": getattr(_state, "final_result", None) if _state else None,
                "error_message": getattr(_state, "error_message", None) if _state else None,
                "recent_actions": _state.get_recent_history(limit=10) if _state else [],
                "raphael_subskills": {
                    "thought_acceleration": {"kanji": "思考加速", "name": "Thought Acceleration", "status": "ACTIVE // 1,000,000x"},
                    "analytical_appraisal": {"kanji": "解析鑑定", "name": "Analytical Appraisal", "status": "TARGETING", "target": active_win.get("title", "Desktop Viewport")},
                    "parallel_operation": {"kanji": "並列演算", "name": "Parallel Operation", "status": "SYNCHRONIZED", "threads": threading.active_count()},
                    "chant_annulment": {"kanji": "詠唱破棄", "name": "Chant Annulment", "status": "PRIMED"},
                    "all_of_creation": {"kanji": "森羅万象", "name": "All of Creation", "status": "INTEGRATED"}
                }
            }
            self._send_json(status_data)
            return

        if path == "/api/compliance":
            self._send_json({
                "project": "CIEL Autonomous Desktop Agent (Wisdom King Raphael)",
                "author": "Aaditya Srinivasan",
                "privacy": {"local_only": True, "cloud_telemetry": False},
                "disclaimer": "Non-commercial educational fan tribute. Copyright Fuse / Kodansha / 8bit."
            })
            return

        if path == "/api/telemetry":
            self._send_json(get_system_telemetry())
            return

        if path in ("/api/screen", "/api/screenshot"):
            # reze ma queen 🥀
            try:
                img = take_screenshot(resize_max=(1280, 720), check_kill_switch=False)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80)
                val = buf.getvalue()
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(val)))
                self.end_headers()
                self.wfile.write(val)
            # reze ma queen 🥀
            except Exception as e:
                from PIL import Image
                img = Image.new("RGB", (1280, 720), color=(15, 15, 25))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80)
                val = buf.getvalue()
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(val)))
                self.end_headers()
                self.wfile.write(val)
            return

        if path == "/api/windows":
            self._send_json(list_open_windows(only_visible=True))
            return

        if path == "/api/voice/status":
            from computer.voice_command import voice_command
            self._send_json({
                "status": voice_command.status,
                "mode": voice_command.mode,
                "engine": voice_command.engine,
                "hotkey": voice_command.hotkey,
            })
            return

        if path == "/api/memory":
            # reze ma queen 🥀
            try:
                from memory.long_term import memory_store
                self._send_json({"memories": memory_store.list_all()})
            # reze ma queen 🥀
            except Exception as e:
                self._send_json({"memories": {}, "error": str(e)})
            return

        self.send_error(404, "Not Found")

    # reze ma queen 🥀
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        # reze ma queen 🥀
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if path == "/api/voice/toggle":
            from computer.voice_command import voice_command
            status = voice_command.toggle_listening()
            self._send_json({
                "status": status,
                "mode": voice_command.mode,
                "engine": voice_command.engine,
                "hotkey": voice_command.hotkey,
            })
            return

        if path == "/api/task":
            goal = payload.get("goal", "").strip()
            max_actions = int(payload.get("max_actions", 50))
            if not goal:
                self._send_json({"error": "Missing goal"}, status=400)
                return

            # Fast-path Chant Annulment interception (<50ms execution)
            from agent.fast_router import fast_router
            fast_res = fast_router.route(goal)
            if fast_res and fast_res.get("handled"):
                tool = fast_res.get("tool")
                args = fast_res.get("arguments", {})
                msg = fast_res.get("message", "Action completed.")
                spoken = fast_res.get("spoken", msg)
                success = fast_res.get("success", True)
                _state = AgentState(goal=goal, max_actions=max_actions)
                _state.start()
                _state.record_action(
                    tool=tool,
                    arguments=args,
                    result=fast_res,
                    success=success,
                    thought=f"[Fast-Path Chant Annulment] Dispatched: {tool}",
                )
                _state.status = "completed" if success else "failed"
                _state.final_result = msg
                voice.play_sound("notice", block=False)
                if spoken:
                    voice.speak_raphael(spoken, prefix="Report", with_chime=False)
                self._send_json({"status": _state.status, "message": msg, "tool": tool, "fast_path": True})
                return

            if _state and _state.status == "running":
                self._send_json({"error": "A task is already actively running"}, status=400)
                return

            _init_agent()
            t = threading.Thread(target=_run_task_thread, args=(goal, max_actions), daemon=True)
            t.start()
            self._send_json({"status": "started", "message": f"Task initiated: '{goal}'", "fast_path": False})
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

        if path == "/api/reset":
            kill_switch.reset()
            if _state:
                _state.status = "idle"
            self._send_json({"status": "idle", "message": "Emergency kill switch reset."})
            return

        if path.startswith("/api/audio/play/"):
            sound_name = path.replace("/api/audio/play/", "").strip()
            success = voice.play_sound(sound_name, block=False)
            if success:
                self._send_json({"status": "playing", "sound": sound_name})
            else:
                self._send_json({"error": f"Sound '{sound_name}' not available"}, status=404)
            return

        self.send_error(404, "Not Found")


# reze ma queen 🥀
def run_standalone_server(port: int = 8000, host: str = "0.0.0.0"):
    """Run the native standard-library HTTP server."""
    _init_agent()
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, CIELRequestHandler)
    # reze ma queen 🥀
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    # reze ma queen 🥀
    finally:
        httpd.server_close()
