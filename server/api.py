"""Local FastAPI server for Desktop Agent."""

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


import io
import os
import threading
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


class TaskRequest(BaseModel):
    goal: str
    max_actions: Optional[int] = 50


@app.on_event("startup")
def startup_event():
    global current_executor
    config = load_config()
    brain = AgentBrain(config=config)
    current_executor = AgentExecutor(brain=brain, config=config)
    kill_switch.start_listener()


@app.on_event("shutdown")
def shutdown_event():
    kill_switch.stop_listener()


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    """Get current agent runtime state, task progress, and Raphael sub-skill metrics."""
    try:
        active_win = get_active_window(check_kill_switch=False)
    except Exception:
        active_win = {"title": "Desktop"}

    is_stopped = kill_switch.is_triggered()
    status_str = "stopped" if is_stopped else (current_state.status if current_state else "idle")

    return {
        "status": status_str,
        "task_id": current_state.task_id if current_state else None,
        "goal": current_state.goal if current_state else None,
        "step": current_state.step if current_state else 0,
        "max_actions": current_state.max_actions if current_state else 50,
        "active_window": active_win.get("title", "Desktop"),
        "is_paused": kill_switch.is_paused(),
        "is_stopped": is_stopped,
        "recent_actions": current_state.get_recent_history(limit=5) if current_state else [],
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


def _run_task_worker(goal: str, max_actions: int):
    global current_state, current_executor
    kill_switch.reset()
    current_state = AgentState(goal=goal, max_actions=max_actions)
    voice.play_sound("notice", block=False)
    if current_executor:
        current_executor.run(goal=goal, state=current_state)


@app.post("/api/task")
def start_task(req: TaskRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Start an autonomous desktop agent task in background."""
    global task_thread
    if current_state and current_state.status == "running":
        raise HTTPException(status_code=400, detail="A task is already actively running. Stop or wait for it to complete.")

    kill_switch.reset()
    background_tasks.add_task(_run_task_worker, req.goal, req.max_actions or 50)

    return {
        "message": f"Task initiated: '{req.goal}'",
        "status": "started",
    }


@app.post("/api/stop")
def stop_agent() -> Dict[str, Any]:
    """Trigger emergency stop immediately."""
    kill_switch.trigger("Triggered via REST API /api/stop")
    if current_state:
        current_state.status = "stopped"
    return {"status": "stopped", "message": "Emergency kill switch activated."}


@app.post("/api/pause")
def pause_agent() -> Dict[str, Any]:
    """Pause execution."""
    kill_switch.pause()
    return {"status": "paused"}


@app.post("/api/resume")
def resume_agent() -> Dict[str, Any]:
    """Resume execution."""
    kill_switch.resume()
    return {"status": "resumed"}


@app.post("/api/reset")
def reset_agent() -> Dict[str, Any]:
    """Reset emergency stop state and return to idle."""
    kill_switch.reset()
    if current_state:
        current_state.status = "idle"
    return {"status": "idle", "message": "Emergency kill switch reset. Agent ready."}


@app.get("/api/screen")
@app.get("/api/screenshot")
def get_screen_image():
    """Retrieve real-time JPEG screenshot."""
    try:
        img = take_screenshot(resize_max=(1280, 720), check_kill_switch=False)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return Response(content=buf.getvalue(), media_type="image/jpeg")
    except Exception as e:
        logger.debug(f"Screenshot capture fallback: {e}")
        from PIL import Image
        img = Image.new("RGB", (1280, 720), color=(15, 15, 25))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return Response(content=buf.getvalue(), media_type="image/jpeg")


@app.get("/api/windows")
def get_windows():
    """List open visible application windows."""
    return list_open_windows(only_visible=True)


@app.get("/api/telemetry")
def get_telemetry():
    """Get native Windows CPU, RAM, and Battery telemetry."""
    from computer.system_telemetry import get_system_telemetry
    return get_system_telemetry()


@app.get("/api/memory")
def get_memory():
    """Get persistent long-term memory facts and preferences."""
    try:
        from memory.long_term import memory_store
        return {"memories": memory_store.list_all()}
    except Exception as e:
        return {"memories": {}, "error": str(e)}


@app.get("/api/audio/list")
def list_audio_presets():
    """List available Raphael voice and sound presets."""
    return {"sounds": list(SOUND_PRESETS.keys())}


@app.post("/api/audio/play/{sound_name}")
def play_audio_preset(sound_name: str):
    """Trigger Raphael voice line or sound effect."""
    success = voice.play_sound(sound_name, block=False)
    if not success:
        raise HTTPException(status_code=404, detail=f"Sound '{sound_name}' not available.")
    return {"status": "playing", "sound": sound_name}


@app.get("/api/compliance")
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
def get_hud_page():
    """Serve the reactive HUD interface."""
    import os
    from fastapi.responses import HTMLResponse
    hud_file = os.path.join(os.path.dirname(__file__), "hud.html")
    with open(hud_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

