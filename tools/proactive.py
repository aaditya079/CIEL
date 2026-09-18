"""Daily status briefing and proactive system reporting.

Gathers time, date, local weather forecast, hardware metrics,
and scheduled reminders for synthesized voice readout.
"""

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


import datetime
import logging
from typing import Dict, Any, Optional

from computer.system_telemetry import get_system_telemetry
from computer.voice import voice
from tools.desktop_control import get_weather
from tools.reminders import list_reminders

logger = logging.getLogger("desktop_agent.tools.proactive")


def get_greeting() -> str:
    """Return appropriate greeting based on current local hour."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning, Sir."
    elif 12 <= hour < 18:
        return "Good afternoon, Sir."
    elif 18 <= hour < 22:
        return "Good evening, Sir."
    else:
        return "Greetings, Sir. Working late I see."


def generate_morning_briefing(city: str = "", speak: bool = True) -> Dict[str, Any]:
    """Compile and deliver a daily morning or status briefing."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d")
    greeting = get_greeting()

    # Hardware health
    telemetry = get_system_telemetry()
    cpu = telemetry.get("cpu_percent", 0)
    ram = telemetry.get("memory", {}).get("memory_load_percent", 0)
    power = telemetry.get("power", {})

    # Weather
    weather_info = get_weather(city)
    weather_spoken = weather_info.get("spoken", "")

    # Pending reminders
    reminders = list_reminders()
    reminder_count = len(reminders.get("reminders", []))
    reminder_text = (
        f"You have {reminder_count} active reminder."
        if reminder_count == 1
        else f"You have {reminder_count} active reminders."
        if reminder_count > 0
        else "No pending reminders on your schedule."
    )

    # Spoken transcript synthesis
    spoken_parts = [
        greeting,
        f"It is currently {time_str} on {date_str}.",
    ]
    if weather_spoken:
        spoken_parts.append(weather_spoken)

    sys_part = f"System performance is optimal. CPU load is at {cpu} percent, and memory utilization is {ram} percent."
    if power.get("has_battery"):
        sys_part += f" Battery is at {power.get('battery_percent')}%."
    spoken_parts.append(sys_part)
    spoken_parts.append(reminder_text)
    spoken_parts.append("All systems operational. CIEL is ready for your instructions.")

    full_spoken = " ".join(spoken_parts)

    if speak:
        voice.speak(full_spoken)

    return {
        "success": True,
        "greeting": greeting,
        "time": time_str,
        "date": date_str,
        "telemetry": telemetry,
        "weather": weather_info.get("message", ""),
        "reminders_count": reminder_count,
        "spoken": full_spoken,
        "message": f"=== CIEL DAILY BRIEFING ===\n{greeting}\nTime: {time_str} | Date: {date_str}\nWeather: {weather_info.get('message', 'N/A')}\nCPU: {cpu}% | RAM: {ram}%\nReminders: {reminder_count} active\nCIEL is online and standing by.",
    }
