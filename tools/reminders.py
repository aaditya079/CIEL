"""Background scheduled reminders and timer alerts."""

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


import time
import threading
import logging
from typing import Dict, Any, List

from computer.voice import voice

logger = logging.getLogger("desktop_agent.tools.reminders")

_active_reminders: List[Dict[str, Any]] = []
_reminders_lock = threading.Lock()


def set_reminder(message: str, minutes: float) -> Dict[str, Any]:
    """Schedule a reminder to speak and notify after specified minutes."""
    clean_msg = (message or "").strip()
    if not clean_msg:
        return {"success": False, "error": "Reminder message cannot be empty."}

    duration_secs = max(1.0, float(minutes) * 60.0)
    target_time = time.time() + duration_secs

    reminder_entry = {
        "id": len(_active_reminders) + 1,
        "message": clean_msg,
        "minutes": minutes,
        "trigger_at": time.strftime("%H:%M:%S", time.localtime(target_time)),
    }

    def _timer_worker():
        time.sleep(duration_secs)
        logger.info(f"Triggering reminder: {clean_msg}")
        alert_text = f"Reminder: {clean_msg}"
        voice.speak(alert_text)
        with _reminders_lock:
            if reminder_entry in _active_reminders:
                _active_reminders.remove(reminder_entry)

    t = threading.Thread(target=_timer_worker, daemon=True, name=f"Reminder_{reminder_entry['id']}")
    t.start()

    with _reminders_lock:
        _active_reminders.append(reminder_entry)

    spoken_conf = f"Reminder set for {clean_msg} in {minutes:g} minutes."
    return {
        "success": True,
        "reminder": reminder_entry,
        "message": f"Reminder set for {clean_msg} in {minutes:g} minutes (at {reminder_entry['trigger_at']}).",
        "spoken": spoken_conf,
    }


def list_reminders() -> Dict[str, Any]:
    """List all currently pending active reminders."""
    with _reminders_lock:
        return {
            "success": True,
            "count": len(_active_reminders),
            "reminders": list(_active_reminders),
        }
