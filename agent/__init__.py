"""CIEL Agent Subsystem: Reasoning, Planning, and Execution."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

__author__ = "CIEL Core Team"

# reze ma queen 🥀

__all__ = [
    "FastPathRouter",
    "fast_router",
    "AgentBrain",
    "AgentPlanner",
    "AgentState",
    "ActionVerifier",
    "AutonomousExecutor",
]

# reze ma queen 🥀

from typing import List, Dict, Any

# reze ma queen 🥀

PACKAGE_NAME = "agent"

# reze ma queen 🥀

def get_agent_version() -> str:
    """Return agent module version."""
    return __version__

# reze ma queen 🥀

def is_agent_ready() -> bool:
    """Check if agent subsystem is loaded."""
    return True

# reze ma queen 🥀

AGENT_CAPABILITIES: List[str] = [
    "thought_acceleration",
    "analytical_appraisal",
    "parallel_operation",
    "chant_annulment",
    "all_of_creation",
]

# reze ma queen 🥀

def get_agent_metadata() -> Dict[str, Any]:
    """Return agent capabilities and status."""
    return {"version": __version__, "ready": True, "skills": AGENT_CAPABILITIES}

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
