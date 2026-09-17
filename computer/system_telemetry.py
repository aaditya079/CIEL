"""System Telemetry: Native Windows hardware inspection via ctypes (zero dependencies)."""

import ctypes
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("desktop_agent.computer.telemetry")

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("SystemStatusFlag", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]

class FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", ctypes.c_ulong),
        ("dwHighDateTime", ctypes.c_ulong),
    ]

def _ft_to_int(ft: FILETIME) -> int:
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime

# Cache for CPU calculation
_last_idle_time: Optional[int] = None
_last_kernel_time: Optional[int] = None
_last_user_time: Optional[int] = None
_last_cpu_sample_time: float = 0.0
_cached_cpu_percent: float = 0.0


def get_memory_status() -> Dict[str, Any]:
    """Return memory metrics (load %, total GB, used GB, available GB)."""
    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            total_gb = stat.ullTotalPhys / (1024 ** 3)
            avail_gb = stat.ullAvailPhys / (1024 ** 3)
            used_gb = total_gb - avail_gb
            return {
                "memory_load_percent": stat.dwMemoryLoad,
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "available_gb": round(avail_gb, 2),
            }
    except Exception as e:
        logger.error(f"Error reading memory status: {e}")
    return {"memory_load_percent": 0, "total_gb": 0.0, "used_gb": 0.0, "available_gb": 0.0}


def get_power_status() -> Dict[str, Any]:
    """Return power metrics (battery %, AC line connected, charging state)."""
    try:
        status = SYSTEM_POWER_STATUS()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            ac_connected = status.ACLineStatus == 1
            battery_pct = status.BatteryLifePercent if status.BatteryLifePercent <= 100 else None
            is_charging = bool(status.BatteryFlag & 8)
            has_battery = not bool(status.BatteryFlag & 128) and battery_pct is not None
            return {
                "has_battery": has_battery,
                "ac_connected": ac_connected,
                "battery_percent": battery_pct,
                "is_charging": is_charging,
            }
    except Exception as e:
        logger.error(f"Error reading power status: {e}")
    return {"has_battery": False, "ac_connected": True, "battery_percent": None, "is_charging": False}


def get_cpu_usage(sample_interval: float = 0.15) -> float:
    """Return current CPU usage percent calculated via GetSystemTimes."""
    global _last_idle_time, _last_kernel_time, _last_user_time, _last_cpu_sample_time, _cached_cpu_percent

    now = time.time()
    # If sampled very recently (within 0.5s), return cached to avoid blocking
    if now - _last_cpu_sample_time < 0.5 and _last_idle_time is not None:
        return _cached_cpu_percent

    try:
        idle1, kernel1, user1 = FILETIME(), FILETIME(), FILETIME()
        idle2, kernel2, user2 = FILETIME(), FILETIME(), FILETIME()

        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle1), ctypes.byref(kernel1), ctypes.byref(user1))
        time.sleep(sample_interval)
        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle2), ctypes.byref(kernel2), ctypes.byref(user2))

        idle = _ft_to_int(idle2) - _ft_to_int(idle1)
        kernel = _ft_to_int(kernel2) - _ft_to_int(kernel1)
        user = _ft_to_int(user2) - _ft_to_int(user1)
        total = kernel + user

        if total > 0:
            cpu = ((total - idle) * 100.0) / total
            _cached_cpu_percent = round(max(0.0, min(100.0, cpu)), 1)
            _last_cpu_sample_time = now
            return _cached_cpu_percent
    except Exception as e:
        logger.error(f"Error reading CPU usage: {e}")

    return 0.0


def get_system_telemetry() -> Dict[str, Any]:
    """Consolidated system status dictionary and summary string."""
    cpu_pct = get_cpu_usage(sample_interval=0.1)
    mem = get_memory_status()
    pwr = get_power_status()

    # Screen resolution via user32
    try:
        screen_w = ctypes.windll.user32.GetSystemMetrics(0)
        screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    except Exception:
        screen_w, screen_h = 1920, 1080

    pwr_str = f"Battery: {pwr['battery_percent']}% ({'Charging' if pwr['is_charging'] else 'On AC' if pwr['ac_connected'] else 'On Battery'})" if pwr["has_battery"] else "Power: Desktop (AC line)"
    summary = f"CPU: {cpu_pct}% | RAM: {mem['memory_load_percent']}% ({mem['used_gb']} / {mem['total_gb']} GB) | {pwr_str}"

    return {
        "cpu_percent": cpu_pct,
        "memory": mem,
        "power": pwr,
        "display": {"width": screen_w, "height": screen_h},
        "summary": summary,
    }
