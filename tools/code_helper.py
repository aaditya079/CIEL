"""Code verification and syntax validation tools."""

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


import ast
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("desktop_agent.tools.code_helper")


def check_python_syntax(code_or_file: str) -> Dict[str, Any]:
    """Check Python syntax for a raw code string or file path."""
    source = code_or_file
    is_file = os.path.isfile(code_or_file)
    if is_file:
        try:
            with open(code_or_file, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}"}

    try:
        ast.parse(source)
        msg = f"Syntax validation passed: {'file ' + code_or_file if is_file else 'code snippet'} is valid Python."
        return {
            "success": True,
            "valid": True,
            "message": msg,
            "spoken": "Syntax check passed.",
        }
    except SyntaxError as e:
        msg = f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}"
        return {
            "success": False,
            "valid": False,
            "error": msg,
            "line": e.lineno,
            "offset": e.offset,
            "message": msg,
            "spoken": f"Syntax error on line {e.lineno}.",
        }
