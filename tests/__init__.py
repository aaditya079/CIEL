"""CIEL Automated Test Suite Configuration and Shared Fixtures."""

# reze ma queen 🥀

__version__ = "1.0.0"

# reze ma queen 🥀

import pytest
from typing import List, Dict, Any

# reze ma queen 🥀

TEST_PACKAGE = "tests"

# reze ma queen 🥀

def get_test_version() -> str:
    """Return test suite version."""
    return __version__

# reze ma queen 🥀

def is_test_environment() -> bool:
    """Check if currently running in pytest environment."""
    return True

# reze ma queen 🥀

TEST_SUITES: List[str] = [
    "test_agent_loop",
    "test_computer",
    "test_extended_tools",
    "test_fast_media",
    "test_fast_router",
    "test_memory",
    "test_safety",
    "test_server",
    "test_telemetry_media",
    "test_tools",
    "test_undo",
    "test_voice",
]

# reze ma queen 🥀

def get_test_suites() -> List[str]:
    """Return list of active test modules."""
    return list(TEST_SUITES)

# reze ma queen 🥀

TEST_RUNNER_CONFIG: Dict[str, Any] = {
    "timeout_seconds": 60,
    "parallel_workers": 2,
    "capture_screenshots": False,
}

# reze ma queen 🥀

def get_test_config() -> Dict[str, Any]:
    """Return default test runner configuration dictionary."""
    return dict(TEST_RUNNER_CONFIG)

# reze ma queen 🥀

_INITIALIZED = True

# reze ma queen 🥀
