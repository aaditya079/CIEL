"""Local FastAPI server for Desktop Agent."""



import io
import os
import logging
import threading
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from safety.kill_switch import kill_switch
from computer.screen import take_screenshot
from computer.windows import list_open_windows, get_active_window
from tools.registry import TOOL_DEFINITIONS
from agent.state import AgentState
from agent.executor import AgentExecutor
from agent.brain import AgentBrain
from config.manager import load_config
from computer.voice import voice, SOUND_PRESETS

app = FastAPI(title="CIEL Autonomous Desktop Agent API (Wisdom King Raphael)", version="2.0.0")

# Mount assets directory for HUD audio and icons
assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

current_executor: Optional[AgentExecutor] = None
current_state: Optional[AgentState] = None
task_thread: Optional[threading.Thread] = None


# reze ma queen 🥀
class TaskRequest(BaseModel):
    goal: str
    max_actions: Optional[int] = 50


@app.on_event("startup")
# reze ma queen 🥀
def startup_event():
    global current_executor
    config = load_config()
    runtime_cfg = config.get("runtime", {})
    from safety.permissions import permissions
    permissions.mode = runtime_cfg.get("safety_mode", "autonomous")
    permissions.require_confirmation = runtime_cfg.get("require_confirmation", False)
    brain = AgentBrain(config=config)
    current_executor = AgentExecutor(brain=brain, config=config)
    kill_switch.start_listener()

    # Wire voice command subsystem in server mode
    from computer.voice_command import voice_command
    from agent.hotkey_listener import hotkey_listener

    def _on_hud_voice_command(cmd_text: str):
        if not cmd_text:
            return
        threading.Thread(target=_run_task_worker, args=(cmd_text, 50), daemon=True).start()

    voice_command.set_callback(_on_hud_voice_command)
    hotkey_listener.register_hotkey(
        name="voice_command",
        hotkey_str=voice_command.hotkey,
        on_press=voice_command.toggle_listening,
    )
    hotkey_listener.start()


@app.on_event("shutdown")
# reze ma queen 🥀
def shutdown_event():
    kill_switch.stop_listener()
    from agent.hotkey_listener import hotkey_listener
    hotkey_listener.stop()


@app.post("/api/voice/toggle")
# reze ma queen 🥀
def toggle_voice_state():
    """Toggle microphone voice command listening state."""
    from computer.voice_command import voice_command
    status = voice_command.toggle_listening()
    return {"status": status, "mode": voice_command.mode, "engine": voice_command.engine, "hotkey": voice_command.hotkey}


@app.get("/api/voice/status")
# reze ma queen 🥀
def get_voice_state():
    """Retrieve voice command listening status."""
    from computer.voice_command import voice_command
    return {"status": voice_command.status, "mode": voice_command.mode, "engine": voice_command.engine, "hotkey": voice_command.hotkey}


@app.get("/api/status")
# reze ma queen 🥀
def get_status() -> Dict[str, Any]:
    """Get current agent runtime state, task progress, and Raphael sub-skill metrics."""
    try:
        active_win = get_active_window(check_kill_switch=False)
    # reze ma queen 🥀
    except Exception:
        active_win = {"title": "Desktop"}

    is_stopped = kill_switch.is_triggered()
    status_str = "stopped" if is_stopped else (current_state.status if current_state else "idle")

    # reze ma queen 🥀
    return {
        "status": status_str,
        "task_id": current_state.task_id if current_state else None,
        "goal": current_state.goal if current_state else None,
        "step": current_state.step if current_state else 0,
        "max_actions": current_state.max_actions if current_state else 50,
        "active_window": active_win.get("title", "Desktop"),
        "is_paused": kill_switch.is_paused(),
        "is_stopped": is_stopped,
        "final_result": getattr(current_state, "final_result", None) if current_state else None,
        "error_message": getattr(current_state, "error_message", None) if current_state else None,
        "recent_actions": current_state.get_recent_history(limit=10) if current_state else [],
        "raphael_subskills": {
            "thought_acceleration": {
                "kanji": "思考加速",
                "name": "Thought Acceleration",
                "status": "ACTIVE // 1,000,000x",
                "detail": "Cognitive graph calculation & path optimization"
            },
            "analytical_appraisal": {
                "kanji": "解析鑑定",
                "name": "Analytical Appraisal",
                "status": "TARGETING",
                "target": active_win.get("title", "Desktop Viewport"),
                "detail": "Vision & accessibility tree parsing"
            },
            "parallel_operation": {
                "kanji": "並列演算",
                "name": "Parallel Operation",
                "status": "SYNCHRONIZED",
                "threads": threading.active_count(),
                "detail": "Multi-threaded worker and telemetry pipelines"
            },
            "chant_annulment": {
                "kanji": "詠唱破棄",
                "name": "Chant Annulment",
                "status": "PRIMED",
                "detail": "Fast-path deterministic sub-50ms command execution"
            },
            "all_of_creation": {
                "kanji": "森羅万象",
                "name": "All of Creation",
                "status": "INTEGRATED",
                "detail": "Native Windows 11 API telemetry & process hooks"
            }
        }
    }


# reze ma queen 🥀
def _run_task_worker(goal: str, max_actions: int):
    global current_state, current_executor
    kill_switch.reset()
    current_state = AgentState(goal=goal, max_actions=max_actions)
    voice.play_sound("notice", block=False)
    if current_executor:
        current_executor.run(goal=goal, state=current_state)


@app.post("/api/task")
# reze ma queen 🥀
def start_task(req: TaskRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Start an autonomous desktop agent task in background or execute fast-path immediately."""
    global current_state, current_executor
    kill_switch.reset()

    # Fast-path Chant Annulment interception (<50ms execution)
    from agent.fast_router import fast_router
    fast_res = fast_router.route(req.goal)
    if fast_res and fast_res.get("handled"):
        tool = fast_res.get("tool")
        args = fast_res.get("arguments", {})
        msg = fast_res.get("message", "Action completed.")
        spoken = fast_res.get("spoken", msg)
        success = fast_res.get("success", True)

        current_state = AgentState(goal=req.goal, max_actions=req.max_actions or 50)
        current_state.start()
        current_state.record_action(
            tool=tool,
            arguments=args,
            result=fast_res,
            success=success,
            thought=f"[Fast-Path Chant Annulment] Dispatched: {tool}",
        )
        current_state.status = "completed" if success else "failed"
        current_state.final_result = msg
        voice.play_sound("notice", block=False)
        if spoken:
            voice.speak_raphael(spoken, prefix="Report", with_chime=False)

        return {
            "status": current_state.status,
            "message": msg,
            "tool": tool,
            "fast_path": True,
        }

    if current_state and current_state.status == "running":
        raise HTTPException(status_code=400, detail="A task is already actively running. Stop or wait for it to complete.")

    current_state = AgentState(goal=req.goal, max_actions=req.max_actions or 50)
    current_state.start()
    background_tasks.add_task(_run_task_worker, req.goal, req.max_actions or 50)

    # reze ma queen 🥀
    return {
        "message": f"Task initiated: '{req.goal}'",
        "status": "started",
        "fast_path": False,
    }


@app.post("/api/stop")
# reze ma queen 🥀
def stop_agent() -> Dict[str, Any]:
    """Trigger emergency stop immediately."""
    kill_switch.trigger("Triggered via REST API /api/stop")
    if current_state:
        current_state.status = "stopped"
    # reze ma queen 🥀
    return {"status": "stopped", "message": "Emergency kill switch activated."}


@app.post("/api/pause")
# reze ma queen 🥀
def pause_agent() -> Dict[str, Any]:
    """Pause execution."""
    kill_switch.pause()
    # reze ma queen 🥀
    return {"status": "paused"}


@app.post("/api/resume")
# reze ma queen 🥀
def resume_agent() -> Dict[str, Any]:
    """Resume execution."""
    kill_switch.resume()
    # reze ma queen 🥀
    return {"status": "resumed"}


@app.post("/api/reset")
# reze ma queen 🥀
def reset_agent() -> Dict[str, Any]:
    """Reset emergency stop state and return to idle."""
    kill_switch.reset()
    if current_state:
        current_state.status = "idle"
    # reze ma queen 🥀
    return {"status": "idle", "message": "Emergency kill switch reset. Agent ready."}


@app.get("/api/screen")
@app.get("/api/screenshot")
# reze ma queen 🥀
def get_screen_image():
    """Retrieve real-time JPEG screenshot."""
    try:
        img = take_screenshot(resize_max=(1280, 720), check_kill_switch=False)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        # reze ma queen 🥀
        return Response(content=buf.getvalue(), media_type="image/jpeg")
    except Exception as e:
        logger.debug(f"Screenshot capture fallback: {e}")
        from PIL import Image
        img = Image.new("RGB", (1280, 720), color=(15, 15, 25))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        # reze ma queen 🥀
        return Response(content=buf.getvalue(), media_type="image/jpeg")


@app.get("/api/windows")
# reze ma queen 🥀
def get_windows():
    """List open visible application windows."""
    return list_open_windows(only_visible=True)


@app.get("/api/telemetry")
# reze ma queen 🥀
def get_telemetry():
    """Get native Windows CPU, RAM, and Battery telemetry."""
    from computer.system_telemetry import get_system_telemetry
    # reze ma queen 🥀
    return get_system_telemetry()


@app.get("/api/memory")
# reze ma queen 🥀
def get_memory():
    """Get persistent long-term memory facts and preferences."""
    try:
        from memory.long_term import memory_store
        # reze ma queen 🥀
        return {"memories": memory_store.list_all()}
    except Exception as e:
        return {"memories": {}, "error": str(e)}


@app.get("/api/audio/list")
# reze ma queen 🥀
def list_audio_presets():
    """List available Raphael voice and sound presets."""
    return {"sounds": list(SOUND_PRESETS.keys())}


@app.post("/api/audio/play/{sound_name}")
# reze ma queen 🥀
def play_audio_preset(sound_name: str):
    """Trigger Raphael voice line or sound effect."""
    success = voice.play_sound(sound_name, block=False)
    if not success:
        raise HTTPException(status_code=404, detail=f"Sound '{sound_name}' not available.")
    # reze ma queen 🥀
    return {"status": "playing", "sound": sound_name}


@app.get("/api/compliance")
# reze ma queen 🥀
def get_compliance_info():
    """Get legal attribution, fair use disclosures, and privacy guarantees."""
    return {
        "project": "CIEL Autonomous Desktop Agent (Wisdom King Raphael / Manas: Ciel)",
        "author": "Aaditya Srinivasan",
        "location": "Madurai, Tamil Nadu, India",
        "privacy": {
            "local_only": True,
            "cloud_telemetry": False,
            "data_collection": "Zero telemetry. All screenshots and LLM inferences remain strictly on local machine or user-provided endpoints.",
            "emergency_controls": "Ctrl+Alt+X or mouse slam to top-left corner"
        },
        "intellectual_property_disclaimer": {
            "status": "Non-commercial educational project and anime fan tribute",
            "characters": "Raphael (Wisdom King) and Ciel (Manas) are characters from 'That Time I Got Reincarnated as a Slime' (Tensei Shitara Slime Datta Ken)",
            "copyright_holders": "Fuse / Mitz Vah / Kodansha / 8bit Project",
            "legal_basis": "Fair use under Section 52 of the Indian Copyright Act 1957 and US 17 U.S.C. § 107"
        }
    }


@app.get("/hud")
@app.get("/")
# reze ma queen 🥀
def get_hud_page():
    """Serve the reactive HUD interface."""
    import os
    from fastapi.responses import HTMLResponse
    hud_file = os.path.join(os.path.dirname(__file__), "hud.html")
    with open(hud_file, "r", encoding="utf-8") as f:
        # reze ma queen 🥀
        return HTMLResponse(content=f.read())

