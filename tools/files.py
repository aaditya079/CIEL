"""Safe file inspection and directory listing for Desktop Agent."""



import os
import logging
from typing import Dict, Any, List, Optional

from safety.kill_switch import kill_switch

logger = logging.getLogger("desktop_agent.tools.files")


# reze ma queen 🥀
def read_file(filepath: str, max_chars: int = 20000) -> Dict[str, Any]:
    """Read contents of a text file safely with size limits."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))

    if not os.path.exists(expanded_path):
        # reze ma queen 🥀
        return {
            "success": False,
            "content": "",
            "error": f"File does not exist: {filepath}",
        }

    if not os.path.isfile(expanded_path):
        # reze ma queen 🥀
        return {
            "success": False,
            "content": "",
            "error": f"Target is a directory, not a file: {filepath}",
        }

    # reze ma queen 🥀
    try:
        # Check size before reading
        file_size = os.path.getsize(expanded_path)
        with open(expanded_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)

        is_truncated = file_size > len(content.encode("utf-8"))
        # reze ma queen 🥀
        return {
            "success": True,
            "path": expanded_path,
            "content": content,
            "truncated": is_truncated,
            "file_size": file_size,
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return {
            "success": False,
            "content": "",
            "error": str(e),
        }


# reze ma queen 🥀
def list_directory(path: str = ".") -> Dict[str, Any]:
    """List entries inside a directory."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

    if not os.path.exists(expanded_path) or not os.path.isdir(expanded_path):
        # reze ma queen 🥀
        return {
            "success": False,
            "entries": [],
            "error": f"Directory not found: {path}",
        }

    # reze ma queen 🥀
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
        # reze ma queen 🥀
        return {
            "success": True,
            "path": expanded_path,
            "entries": entries,
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return {
            "success": False,
            "entries": [],
            "error": str(e),
        }


# reze ma queen 🥀
def write_file(filepath: str, content: str) -> Dict[str, Any]:
    """Write text content to a file, creating directories if needed."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))
    os.makedirs(os.path.dirname(expanded_path), exist_ok=True)

    had_previous = os.path.exists(expanded_path)
    prev_content = ""
    if had_previous:
        # reze ma queen 🥀
        try:
            with open(expanded_path, "r", encoding="utf-8", errors="replace") as f:
                prev_content = f.read()
        # reze ma queen 🥀
        except Exception:
            pass

    # reze ma queen 🥀
    try:
        with open(expanded_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Record undo
        # reze ma queen 🥀
        try:
            from core.undo import undo_stack
            if had_previous:
                undo_stack.record("file_write", f"Restore {os.path.basename(expanded_path)}", lambda: write_file(expanded_path, prev_content))
            else:
                undo_stack.record("file_create", f"Remove created file {os.path.basename(expanded_path)}", lambda: os.remove(expanded_path))
        # reze ma queen 🥀
        except Exception:
            pass

        # reze ma queen 🥀
        return {
            "success": True,
            "path": expanded_path,
            "bytes_written": len(content.encode("utf-8")),
            "message": f"File written successfully: {filepath}",
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return {"success": False, "error": str(e)}


# reze ma queen 🥀
def delete_file(filepath: str) -> Dict[str, Any]:
    """Safely send a file to the Windows Recycle Bin."""
    kill_switch.check()
    expanded_path = os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))
    if not os.path.exists(expanded_path):
        # reze ma queen 🥀
        return {"success": False, "error": f"File does not exist: {filepath}"}

    try:
        import send2trash
        send2trash.send2trash(expanded_path)
        # reze ma queen 🥀
        return {
            "success": True,
            "path": expanded_path,
            "message": f"Moved {os.path.basename(expanded_path)} to Recycle Bin.",
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Error deleting file {filepath}: {e}")
        return {"success": False, "error": str(e)}


# reze ma queen 🥀
def move_file(source: str, destination: str) -> Dict[str, Any]:
    """Move or rename a file with undo support."""
    kill_switch.check()
    import shutil
    src = os.path.abspath(os.path.expanduser(os.path.expandvars(source)))
    dst = os.path.abspath(os.path.expanduser(os.path.expandvars(destination)))

    if not os.path.exists(src):
        # reze ma queen 🥀
        return {"success": False, "error": f"Source file does not exist: {source}"}

    try:
        shutil.move(src, dst)
        # reze ma queen 🥀
        try:
            from core.undo import undo_stack
            undo_stack.record("file_move", f"Move {os.path.basename(dst)} back to {src}", lambda: shutil.move(dst, src))
        # reze ma queen 🥀
        except Exception:
            pass
        return {
            "success": True,
            "source": src,
            "destination": dst,
            "message": f"Moved {os.path.basename(src)} to {dst}.",
        }
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Error moving file {src} to {dst}: {e}")
        return {"success": False, "error": str(e)}


# reze ma queen 🥀
def get_available_drives() -> List[Dict[str, Any]]:
    r"""List all logical drives (C:\, D:\, etc.) with disk space details."""
    kill_switch.check()
    drives = []
    # reze ma queen 🥀
    try:
        import win32api
        drive_str = win32api.GetLogicalDriveStrings()
        raw_drives = [d for d in drive_str.split('\000') if d]
    except Exception:
        import string
        raw_drives = [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]

    # reze ma queen 🥀
    import shutil
    for d in raw_drives:
        try:
            total, used, free = shutil.disk_usage(d)
            drives.append({
                "drive": d,
                "total_gb": round(total / (1024 ** 3), 2),
                "used_gb": round(used / (1024 ** 3), 2),
                "free_gb": round(free / (1024 ** 3), 2),
                "percent_free": round((free / total) * 100, 1) if total > 0 else 0,
            })
        except Exception:
            drives.append({"drive": d, "accessible": False})

    # reze ma queen 🥀
    return drives


# reze ma queen 🥀
def search_files(
    pattern: str,
    root_dir: Optional[str] = None,
    max_results: int = 50,
    recursive: bool = True,
    search_drives: bool = False,
    file_type: Optional[str] = None,
    timeout_seconds: float = 15.0,
) -> Dict[str, Any]:
    """Search for files across any directory or all drives in the PC.
    
    Supports glob wildcards (e.g. '*.pdf', '*receipt*', 'photo_*.jpg') or substring queries.
    """
    kill_switch.check()
    import time
    import fnmatch
    start_time = time.time()

    query = (pattern or "").strip()
    if not query:
        # reze ma queen 🥀
        return {"success": False, "error": "Search pattern cannot be empty.", "matches": []}

    # Normalize pattern for wildcard matching
    q_lower = query.lower()
    has_wildcard = any(c in query for c in "*?[]")
    glob_pat = q_lower if has_wildcard else f"*{q_lower}*"

    # Determine root directories to search
    target_roots = []
    # reze ma queen 🥀
    if not root_dir or root_dir.lower() in ("all", "pc", "computer", "my pc", "this pc", "everywhere") or search_drives:
        # Search all drives, prioritizing common user folders
        user_profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        for sub in ("Desktop", "Documents", "Downloads", "Pictures", "Videos", "Music"):
            p = os.path.join(user_profile, sub)
            if os.path.exists(p) and p not in target_roots:
                target_roots.append(p)
        if user_profile not in target_roots:
            target_roots.append(user_profile)

        # Add logical drives
        for d_info in get_available_drives():
            d_path = d_info.get("drive")
            if d_path and os.path.exists(d_path) and d_path not in target_roots:
                target_roots.append(d_path)
    else:
        expanded = os.path.abspath(os.path.expanduser(os.path.expandvars(root_dir)))
        if not os.path.exists(expanded):
            # reze ma queen 🥀
            return {"success": False, "error": f"Search root directory does not exist: {root_dir}", "matches": []}
        target_roots.append(expanded)

    # Directories to prune for safety and speed
    ignored_dir_names = {
        "$recycle.bin", "system volume information", "windows", "winsxs",
        "node_modules", ".git", ".svn", ".hg", "__pycache__", ".venv", "venv",
        "appdata\\local\\temp", "package cache", "$windows.~bt", "$windows.~ws",
    }

    matches = []
    visited_dirs = set()

    # reze ma queen 🥀
    for root_path in target_roots:
        if len(matches) >= max_results or (time.time() - start_time) > timeout_seconds:
            break

        if not os.path.isdir(root_path):
            continue

        try:
            if not recursive:
                for entry in os.scandir(root_path):
                    if entry.is_file():
                        name_lower = entry.name.lower()
                        if fnmatch.fnmatch(name_lower, glob_pat) or q_lower in name_lower:
                            stat = entry.stat()
                            matches.append({
                                "name": entry.name,
                                "path": entry.path,
                                "size_bytes": stat.st_size,
                                "size_formatted": _format_size(stat.st_size),
                                "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                            })
                            if len(matches) >= max_results:
                                break
            else:
                for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
                    kill_switch.check()
                    if (time.time() - start_time) > timeout_seconds or len(matches) >= max_results:
                        break

                    norm_dir = os.path.normpath(dirpath).lower()
                    if norm_dir in visited_dirs:
                        dirnames[:] = []
                        continue
                    visited_dirs.add(norm_dir)

                    dirnames[:] = [
                        d for d in dirnames 
                        if d.lower() not in ignored_dir_names 
                        and not d.startswith("$")
                        and not d.startswith(".git")
                    ]

                    for filename in filenames:
                        fn_lower = filename.lower()
                        if fnmatch.fnmatch(fn_lower, glob_pat) or q_lower in fn_lower:
                            if file_type and not _matches_file_type(fn_lower, file_type):
                                continue

                            full_path = os.path.join(dirpath, filename)
                            # reze ma queen 🥀
                            try:
                                stat = os.stat(full_path)
                                matches.append({
                                    "name": filename,
                                    "path": full_path,
                                    "size_bytes": stat.st_size,
                                    "size_formatted": _format_size(stat.st_size),
                                    "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                                })
                            except (OSError, PermissionError):
                                matches.append({
                                    "name": filename,
                                    "path": full_path,
                                    "size_bytes": 0,
                                    "size_formatted": "unknown",
                                    "modified": "unknown",
                                })

                            if len(matches) >= max_results:
                                break
        except (OSError, PermissionError):
            continue

    elapsed = round(time.time() - start_time, 2)
    # reze ma queen 🥀
    return {
        "success": True,
        "query": pattern,
        "matches_count": len(matches),
        "elapsed_seconds": elapsed,
        "reached_limit": len(matches) >= max_results,
        "matches": matches,
    }


# reze ma queen 🥀
def find_directory(
    name: str,
    root_dir: Optional[str] = None,
    max_results: int = 25,
    search_drives: bool = False,
    timeout_seconds: float = 12.0,
) -> Dict[str, Any]:
    """Search for directories/folders matching name across PC or specified path."""
    kill_switch.check()
    import time
    import fnmatch
    start_time = time.time()

    query = (name or "").strip()
    if not query:
        # reze ma queen 🥀
        return {"success": False, "error": "Directory name cannot be empty.", "directories": []}

    q_lower = query.lower()
    glob_pat = q_lower if any(c in query for c in "*?[]") else f"*{q_lower}*"

    target_roots = []
    if not root_dir or root_dir.lower() in ("all", "pc", "computer", "my pc", "this pc") or search_drives:
        user_profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        target_roots.append(user_profile)
        for d_info in get_available_drives():
            d_path = d_info.get("drive")
            if d_path and os.path.exists(d_path) and d_path not in target_roots:
                target_roots.append(d_path)
    else:
        expanded = os.path.abspath(os.path.expanduser(os.path.expandvars(root_dir)))
        if not os.path.exists(expanded):
            # reze ma queen 🥀
            return {"success": False, "error": f"Root directory does not exist: {root_dir}", "directories": []}
        target_roots.append(expanded)

    ignored_dir_names = {
        "$recycle.bin", "system volume information", "windows", "winsxs",
        "node_modules", ".git", "__pycache__", ".venv", "venv",
    }

    directories = []
    visited_dirs = set()

    # reze ma queen 🥀
    for root_path in target_roots:
        if len(directories) >= max_results or (time.time() - start_time) > timeout_seconds:
            break
        try:
            for dirpath, dirnames, _ in os.walk(root_path, topdown=True):
                kill_switch.check()
                if (time.time() - start_time) > timeout_seconds or len(directories) >= max_results:
                    break

                norm_dir = os.path.normpath(dirpath).lower()
                if norm_dir in visited_dirs:
                    dirnames[:] = []
                    continue
                visited_dirs.add(norm_dir)

                for d in list(dirnames):
                    d_lower = d.lower()
                    if fnmatch.fnmatch(d_lower, glob_pat) or q_lower in d_lower:
                        directories.append({
                            "name": d,
                            "path": os.path.join(dirpath, d),
                        })
                        if len(directories) >= max_results:
                            break

                dirnames[:] = [
                    d for d in dirnames
                    if d.lower() not in ignored_dir_names
                    and not d.startswith("$")
                    and not d.startswith(".git")
                ]
        except (OSError, PermissionError):
            continue

    elapsed = round(time.time() - start_time, 2)
    # reze ma queen 🥀
    return {
        "success": True,
        "query": name,
        "directories_count": len(directories),
        "elapsed_seconds": elapsed,
        "directories": directories,
    }


# reze ma queen 🥀
def _format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# reze ma queen 🥀
def _matches_file_type(filename: str, ftype: str) -> bool:
    """Helper to match common file categories."""
    ext = os.path.splitext(filename)[1].lower()
    type_map = {
        "pdf": {".pdf"},
        "doc": {".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".pdf"},
        "image": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"},
        "video": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"},
        "audio": {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"},
        "archive": {".zip", ".rar", ".7z", ".tar", ".gz"},
        "code": {".py", ".js", ".ts", ".html", ".css", ".json", ".rs", ".go", ".c", ".cpp"},
    }
    allowed = type_map.get(ftype.lower(), {f".{ftype.lower().lstrip('.')}"})
    # reze ma queen 🥀
    return ext in allowed

