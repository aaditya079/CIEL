"""Local FastAPI server for Desktop Agent."""

import io
import threading
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel

from safety.kill_switch import kill_switch
from computer.screen import take_screenshot
from computer.windows import list_open_windows, get_active_window
from tools.registry import TOOL_DEFINITIONS
from agent.state import AgentState
from agent.executor import AgentExecutor
from agent.brain import AgentBrain
from config.manager import load_config

app = FastAPI(title="CIEL Autonomous Desktop Agent API", version="1.0.0")

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
    """Get current agent runtime state and task progress."""
    active_win = get_active_window()
    return {
        "status": current_state.status if current_state else "idle",
        "task_id": current_state.task_id if current_state else None,
        "goal": current_state.goal if current_state else None,
        "step": current_state.step if current_state else 0,
        "max_actions": current_state.max_actions if current_state else 50,
        "active_window": active_win.get("title", ""),
        "is_paused": kill_switch.is_paused(),
        "is_stopped": kill_switch.is_triggered(),
        "recent_actions": current_state.get_recent_history(limit=5) if current_state else [],
    }


def _run_task_worker(goal: str, max_actions: int):
    global current_state, current_executor
    kill_switch.reset()
    current_state = AgentState(goal=goal, max_actions=max_actions)
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


@app.get("/api/screen")
@app.get("/api/screenshot")
def get_screen_image():
    """Retrieve real-time JPEG screenshot."""
    try:
        img = take_screenshot(resize_max=(1280, 720))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return Response(content=buf.getvalue(), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/api/tools")
def get_tools():
    """List available tool definitions."""
    return TOOL_DEFINITIONS


@app.get("/hud")
@app.get("/")
def get_hud_page():
    """Serve the reactive HUD interface."""
    import os
    from fastapi.responses import HTMLResponse
    hud_file = os.path.join(os.path.dirname(__file__), "hud.html")
    with open(hud_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

