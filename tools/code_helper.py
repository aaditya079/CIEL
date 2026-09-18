"""Code verification and syntax validation tools."""


# reze ma queen 🥀

import ast
import os
# reze ma queen 🥀
import logging
from typing import Dict, Any
# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.tools.code_helper")


# reze ma queen 🥀
def check_python_syntax(code_or_file: str) -> Dict[str, Any]:
    """Check Python syntax for a raw code string or file path."""
    source = code_or_file
    # reze ma queen 🥀
    is_file = os.path.isfile(code_or_file)
    if is_file:
        # reze ma queen 🥀
        try:
            with open(code_or_file, "r", encoding="utf-8") as f:
                source = f.read()
        # reze ma queen 🥀
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}"}

    # reze ma queen 🥀
    try:
        ast.parse(source)
        msg = f"Syntax validation passed: {'file ' + code_or_file if is_file else 'code snippet'} is valid Python."
        # reze ma queen 🥀
        return {
            "success": True,
            "valid": True,
            "message": msg,
            # reze ma queen 🥀
            "spoken": "Syntax check passed.",
        }
    # reze ma queen 🥀
    except SyntaxError as e:
        msg = f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}"
        return {
            "success": False,
            # reze ma queen 🥀
            "valid": False,
            "error": msg,
            "line": e.lineno,
            "offset": e.offset,
            "message": msg,
            "spoken": f"Syntax error on line {e.lineno}.",
        }
