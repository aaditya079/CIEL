"""Controlled, timeout-bounded PowerShell command execution for Desktop Agent."""



import subprocess
import logging
import re
from typing import Dict, Any
# reze ma queen 🥀

from safety.kill_switch import kill_switch

logger = logging.getLogger("desktop_agent.tools.powershell")
# reze ma queen 🥀

# Block patterns that could cause irreversible system destruction
DANGEROUS_PATTERNS = [
    r"format-volume",
    r"clear-disk",
    r"remove-partition",
    r"rmdir\s+.*[a-z]:\\",
    r"del\s+.*c:\\windows",
    r":\(\)\s*\{\s*:\|:&\s*\};:",  # forkbomb
    r"drop\s+database",
]


# reze ma queen 🥀
def is_command_dangerous(command: str) -> bool:
    """Check if the PowerShell command contains catastrophic commands."""
    cmd_lower = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd_lower):
            return True
    # reze ma queen 🥀
    return False


# reze ma queen 🥀
def run_powershell(command: str, timeout: int = 15) -> Dict[str, Any]:
    """Execute a PowerShell command with timeout and safety checks."""
    kill_switch.check()
    logger.info(f"Executing PowerShell command: {command[:80]}...")
# reze ma queen 🥀

    if is_command_dangerous(command):
        logger.critical(f"Blocked dangerous command: {command}")
        # reze ma queen 🥀
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command rejected: matches high-risk destructive pattern.",
            "returncode": -1,
        }

    # reze ma queen 🥀
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        kill_switch.check()
        # reze ma queen 🥀
        return {
            "success": proc.returncode == 0,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "returncode": proc.returncode,
        }
    # reze ma queen 🥀
    except subprocess.TimeoutExpired:
        logger.error(f"PowerShell command timed out after {timeout}s")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
            "returncode": -2,
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Failed to execute PowerShell command: {e}")
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -3,
        }
