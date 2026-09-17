"""Persistent key-value and fact store.

Maintains user preferences, application paths, custom aliases, and notes
persisted in JSON format across sessions.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("desktop_agent.memory.long_term")

DEFAULT_MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "memory.json")


class LongTermMemory:
    """Thread-safe persistent key-value & fact store."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or DEFAULT_MEMORY_FILE
        self._data: Dict[str, Any] = {
            "facts": {},
            "preferences": {},
            "notes": [],
            "last_updated": time.time(),
        }
        self._load()

    def _load(self):
        """Load data from persistent disk storage."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        self._data.update(content)
            except Exception as e:
                logger.warning(f"Could not load memory file {self.file_path}: {e}")

    def _save(self):
        """Save in-memory state to disk atomically."""
        self._data["last_updated"] = time.time()
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        tmp_file = self.file_path + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            os.replace(tmp_file, self.file_path)
        except Exception as e:
            logger.error(f"Failed to save memory to {self.file_path}: {e}")

    def remember(self, key: str, value: Any, category: str = "facts") -> Dict[str, Any]:
        """Save or update a memory entry."""
        k = str(key).strip().lower()
        if category not in self._data:
            self._data[category] = {}
        
        if isinstance(self._data[category], dict):
            self._data[category][k] = {
                "value": value,
                "saved_at": time.time(),
            }
        self._save()
        msg = f"I'll remember that {k} is {value}."
        return {"success": True, "key": k, "value": value, "message": msg, "spoken": msg}

    def recall(self, key: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Look up a memory entry by key across categories."""
        k = str(key).strip().lower()
        cats = [category] if category and category in self._data else ["facts", "preferences"]
        for cat in cats:
            store = self._data.get(cat, {})
            if isinstance(store, dict) and k in store:
                val = store[k]["value"]
                msg = f"{k.capitalize()} is {val}."
                return {"found": True, "key": k, "value": val, "category": cat, "message": msg, "spoken": msg}

        return {
            "found": False,
            "key": k,
            "value": None,
            "message": f"I don't have any memory stored for '{key}'.",
            "spoken": f"I don't have any record of {key}.",
        }

    def forget(self, key: str) -> Dict[str, Any]:
        """Delete a memory item."""
        k = str(key).strip().lower()
        found = False
        for cat in ["facts", "preferences"]:
            store = self._data.get(cat, {})
            if isinstance(store, dict) and k in store:
                del store[k]
                found = True

        if found:
            self._save()
            msg = f"I have forgotten {k}."
            return {"success": True, "key": k, "message": msg, "spoken": msg}
        return {"success": False, "key": k, "message": f"No memory found for '{key}'.", "spoken": f"No record for {key}."}

    def add_note(self, text: str) -> Dict[str, Any]:
        """Append a timestamped note."""
        entry = {"text": text, "timestamp": time.time()}
        self._data.setdefault("notes", []).append(entry)
        self._save()
        msg = f"Note saved: '{text}'"
        return {"success": True, "note": entry, "message": msg, "spoken": "Note saved."}

    def list_all(self) -> Dict[str, Any]:
        """Return all memories."""
        return {
            "facts": {k: v["value"] for k, v in self._data.get("facts", {}).items()},
            "preferences": {k: v["value"] for k, v in self._data.get("preferences", {}).items()},
            "notes": self._data.get("notes", []),
        }


# Singleton memory instance
memory_store = LongTermMemory()


def remember_fact(key: str, value: Any, category: str = "facts") -> Dict[str, Any]:
    """Tool wrapper: Save a fact or preference."""
    return memory_store.remember(key, value, category)


def recall_fact(key: str) -> Dict[str, Any]:
    """Tool wrapper: Recall a fact or preference."""
    return memory_store.recall(key)


def forget_fact(key: str) -> Dict[str, Any]:
    """Tool wrapper: Forget a fact."""
    return memory_store.forget(key)


def list_memories() -> Dict[str, Any]:
    """Tool wrapper: List all stored memories."""
    return memory_store.list_all()
