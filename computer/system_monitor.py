"""Background telemetry monitor for system threshold warnings and alerts."""

import time
import threading
import logging
from typing import Dict, Any, Optional

from computer.system_telemetry import get_system_telemetry
from computer.voice import voice

logger = logging.getLogger("desktop_agent.computer.system_monitor")

DEFAULT_THRESHOLDS = {
    "cpu_percent": 90.0,
    "memory_load_percent": 92.0,
    "battery_low_percent": 20.0,
}

_ALERT_COOLDOWN_SECONDS = 300  # 5 minutes between repeating alerts


class BackgroundSystemMonitor:
    """Stateful background thread that monitors system metrics and alerts user when needed."""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self._last_alert_time: Dict[str, float] = {}
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self, interval_seconds: float = 30.0):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True,
            name="CIEL_SystemMonitor",
        )
        self._thread.start()
        logger.info("Background hardware monitor started.")

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _can_alert(self, key: str) -> bool:
        return (time.time() - self._last_alert_time.get(key, 0)) > _ALERT_COOLDOWN_SECONDS

    def _record_alert(self, key: str):
        self._last_alert_time[key] = time.time()

    def check_now(self) -> Optional[str]:
        """Perform a single check and return alert message if any threshold is exceeded."""
        try:
            telemetry = get_system_telemetry()
            cpu = telemetry["cpu_percent"]
            mem = telemetry["memory"]["memory_load_percent"]
            pwr = telemetry["power"]

            # CPU threshold alert
            if cpu >= self.thresholds["cpu_percent"] and self._can_alert("cpu"):
                self._record_alert("cpu")
                msg = f"Warning: High CPU utilization at {cpu} percent."
                voice.speak(msg)
                return msg

            # RAM threshold alert
            if mem >= self.thresholds["memory_load_percent"] and self._can_alert("ram"):
                self._record_alert("ram")
                msg = f"Warning: High memory utilization at {mem} percent."
                voice.speak(msg)
                return msg

            # Battery low alert
            if pwr["has_battery"] and not pwr["is_charging"] and not pwr["ac_connected"]:
                bat = pwr["battery_percent"]
                if bat and bat <= self.thresholds["battery_low_percent"] and self._can_alert("battery"):
                    self._record_alert("battery")
                    msg = f"Warning: Battery is low at {bat} percent. Please connect power adapter."
                    voice.speak(msg)
                    return msg

        except Exception as e:
            logger.debug(f"Monitor check error: {e}")

        return None

    def _monitor_loop(self, interval: float):
        while not self._stop_event.is_set():
            self.check_now()
            self._stop_event.wait(timeout=interval)


system_monitor = BackgroundSystemMonitor()
