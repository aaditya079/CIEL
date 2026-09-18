"""Safe file inspection and directory listing for Desktop Agent."""

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


import os
import logging
from typing import Dict, Any, List

from safety.kill_switch import kill_switch

logger = logging.getLogger("desktop_agent.tools.files")


def read_file(filepath: str, max_chars: int = 20000) -> Dict[str, Any]:
    """Read contents of a text file safely with size limits."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))

    if not os.path.exists(expanded_path):
        return {
            "success": False,
            "content": "",
            "error": f"File does not exist: {filepath}",
        }

    if not os.path.isfile(expanded_path):
        return {
            "success": False,
            "content": "",
            "error": f"Target is a directory, not a file: {filepath}",
        }

    try:
        # Check size before reading
        file_size = os.path.getsize(expanded_path)
        with open(expanded_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)

        is_truncated = file_size > len(content.encode("utf-8"))
        return {
            "success": True,
            "path": expanded_path,
            "content": content,
            "truncated": is_truncated,
            "file_size": file_size,
        }
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return {
            "success": False,
            "content": "",
            "error": str(e),
        }


def list_directory(path: str = ".") -> Dict[str, Any]:
    """List entries inside a directory."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

    if not os.path.exists(expanded_path) or not os.path.isdir(expanded_path):
        return {
            "success": False,
            "entries": [],
            "error": f"Directory not found: {path}",
        }

    try:
        entries: List[Dict[str, Any]] = []
        for name in os.listdir(expanded_path)[:100]:
            full = os.path.join(expanded_path, name)
            is_dir = os.path.isdir(full)
            entries.append({
                "name": name,
                "is_dir": is_dir,
                "size": 0 if is_dir else os.path.getsize(full),
            })
        return {
            "success": True,
            "path": expanded_path,
            "entries": entries,
        }
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return {
            "success": False,
            "entries": [],
            "error": str(e),
        }


def write_file(filepath: str, content: str) -> Dict[str, Any]:
    """Write text content to a file, creating directories if needed."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))
    os.makedirs(os.path.dirname(expanded_path), exist_ok=True)

    had_previous = os.path.exists(expanded_path)
    prev_content = ""
    if had_previous:
        try:
            with open(expanded_path, "r", encoding="utf-8", errors="replace") as f:
                prev_content = f.read()
        except Exception:
            pass

    try:
        with open(expanded_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Record undo
        try:
            from core.undo import undo_stack
            if had_previous:
                undo_stack.record("file_write", f"Restore {os.path.basename(expanded_path)}", lambda: write_file(expanded_path, prev_content))
            else:
                undo_stack.record("file_create", f"Remove created file {os.path.basename(expanded_path)}", lambda: os.remove(expanded_path))
        except Exception:
            pass

        return {
            "success": True,
            "path": expanded_path,
            "bytes_written": len(content.encode("utf-8")),
            "message": f"File written successfully: {filepath}",
        }
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return {"success": False, "error": str(e)}


def delete_file(filepath: str) -> Dict[str, Any]:
    """Safely send a file to the Windows Recycle Bin."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))
    if not os.path.exists(expanded_path):
        return {"success": False, "error": f"File does not exist: {filepath}"}

    try:
        import send2trash
        send2trash.send2trash(expanded_path)
        return {
            "success": True,
            "path": expanded_path,
            "message": f"Moved {os.path.basename(expanded_path)} to Recycle Bin.",
        }
    except Exception as e:
        logger.error(f"Error deleting file {filepath}: {e}")
        return {"success": False, "error": str(e)}


def move_file(source: str, destination: str) -> Dict[str, Any]:
    """Move or rename a file with undo support."""
    kill_switch.check()
    import shutil
    src = os.path.abspath(os.path.expanduser(os.path.expandvars(source)))
    dst = os.path.abspath(os.path.expanduser(os.path.expandvars(destination)))

    if not os.path.exists(src):
        return {"success": False, "error": f"Source file does not exist: {source}"}

    try:
        shutil.move(src, dst)
        try:
            from core.undo import undo_stack
            undo_stack.record("file_move", f"Move {os.path.basename(dst)} back to {src}", lambda: shutil.move(dst, src))
        except Exception:
            pass
        return {
            "success": True,
            "source": src,
            "destination": dst,
            "message": f"Moved {os.path.basename(src)} to {dst}.",
        }
    except Exception as e:
        logger.error(f"Error moving file {src} to {dst}: {e}")
        return {"success": False, "error": str(e)}

