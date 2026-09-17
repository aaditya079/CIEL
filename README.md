# CIEL: Autonomous Windows 11 Desktop Agent

![Windows 11](https://img.shields.io/badge/Windows-11-0078D4?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)
![Fast-Path](https://img.shields.io/badge/Execution-Sub--50ms%20Fast--Path-00ff88)
![Voice](https://img.shields.io/badge/Voice-Offline%20SAPI%20Speech-00f0ff)
![Tests](https://img.shields.io/badge/Tests-54%20Passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

**CIEL** is an autonomous desktop agent for Windows 11. It combines sub-50ms deterministic command routing, accessibility tree inspection, offline voice synthesis, and vision-language models to automate computer tasks reliably.

---

## Highlights

- **Wisdom King Raphael HUD (`ciel --hud`)**: Sacred-geometry arcane HUD inspired by *Wisdom King Raphael* (《智慧之王》) and *Manas: Ciel* from *That Time I Got Reincarnated as a Slime*. Displays real-time calculations across 5 Sub-Skills (*Thought Acceleration*, *Analytical Appraisal*, *Parallel Operation*, *Chant Annulment*, *All of Creation*), live observation viewport with targeting reticle, and soundboard controls.
- **Authentic Raphael Voice Pack & SAPI Speech**: Plays authentic anime chimes and voice clips (`notice.mp3`, `imagination.mp3`, `magic_circle.mp3`, `power_up.mp3`), paired with calm female Windows SAPI voice synthesis (Microsoft Zira) using canon announcement phrasing (`《告》 Notice:`, `《報告》 Report:`).
- **Fast-Path Command Routing (<50ms)**: High-frequency commands (volume, media keys, telemetry, Spotify/YouTube playback, weather, window management, reminders, games, flights, memory) execute via direct OS APIs without API tokens or network latency.
- **Offline SAPI Voice Engine**: Zero-latency speech feedback using the native Windows Speech API (`SAPI.SpVoice`). Provides spoken confirmations and daily briefings without external cloud endpoints.
- **Action Undo Stack**: Reversible desktop actions (file changes, Recycle Bin actions, volume adjustments, clipboard writes) can be rolled back instantly with `"ciel undo"`.
- **Persistent Long-Term Memory**: Stores facts, user preferences, and notes across sessions in JSON.
- **Daily Status Briefing**: Reports time, date, local weather, hardware health, and pending reminders via voice synthesis.
- **Flight Search**: Pre-populates and launches flight searches on Google Flights or Skyscanner.
- **Game Launcher & Updater**: Protocol-level interaction with Steam and Epic Games to check updates, open libraries, or launch games.
- **Clipboard Intelligence**: Inspect, copy, and clear clipboard contents from the command line.
- **Multimodal Vision & UIA Fallback**: For complex GUIs, CIEL falls back to Windows UI Automation (UIA) or takes desktop screenshots analyzed by Gemini 3.5 Flash or GPT-4o.
- **Failsafe Controls**: Slam the mouse to `(0, 0)` or press `Ctrl + Alt + X` to abort instantly. Global hotkey `Ctrl + Alt + C` summons the agent.

---

## Execution Hierarchy

CIEL evaluates commands through a tiered architecture to prioritize speed and minimize token costs:

| Tier | Layer | Latency | Description |
|---|---|---|---|
| **Tier 1** | **Fast-Path Router** | `< 50ms` | Direct OS APIs, media keys, Windows shell, and browser deep links without model inference. |
| **Tier 2** | **Windows UI Automation** | `< 200ms` | Accessibility tree inspection to click buttons, type in text fields, and switch tabs without coordinate guessing. |
| **Tier 3** | **Multimodal Vision** | `~ 1-2s` | Screen capture processed by Gemini or GPT-4o for custom GUIs lacking accessibility tags. |
| **Tier 4** | **Precision Coordinates** | `< 100ms` | Fallback mouse clicks and coordinate interactions when UI elements cannot be targeted directly. |

---

## Core Capabilities

### 1. Media & Playback
- `"ciel open spotify and play harvey"`: Launches Spotify, navigates search, and triggers playback.
- `"ciel play bohemian rhapsody on youtube"`: Launches YouTube with autoplay enabled.
- `"ciel volume 50"`, `"ciel mute"`, `"ciel louder"`, `"ciel pause"`, `"ciel skip"`.

### 2. Status Briefing & System Telemetry
- `"ciel morning briefing"` or `"ciel status report"`: Reads time, date, weather, hardware load, and active reminders aloud.
- `"ciel system stats"`: Real-time CPU usage, RAM utilization, and battery status.

### 3. Action Rollback (Undo)
- `"ciel undo"` / `"ciel undo that"`: Restores the previous state after file modifications, volume changes, or clipboard updates.

### 4. Long-Term Memory
- `"ciel remember that my favorite artist is queen"`: Saves to persistent store.
- `"ciel recall my favorite artist"`: Returns `"Queen"`.
- `"ciel what do you remember"`: Displays stored preferences and facts.

### 5. Flights & Games
- `"ciel flights from NYC to London on Friday"`: Opens flight search directly in your browser.
- `"ciel update steam games"`: Launches Steam download and update monitor.
- `"ciel open steam library"`, `"ciel play cs2"`.

### 6. Desktop & Window Management
- `"ciel lock screen"`, `"ciel show desktop"`, `"ciel task manager"`, `"ciel open settings"`.
- `"ciel sleep display"`, `"ciel maximize"`, `"ciel fullscreen"`.
- `"ciel sound settings"`, `"ciel volume mixer"`.

### 7. Browser & Reminders
- `"ciel new tab"`, `"ciel close tab"`, `"ciel reopen tab"`, `"ciel refresh"`.
- `"ciel remind me in 15 minutes to take a break"`.

---

## Installation & Setup

### Prerequisites
- **Operating System**: Windows 11 (or Windows 10)
- **Python**: Version 3.10, 3.11, or 3.12

### Quick Install
```powershell
git clone https://github.com/aaditya079/CIEL.git
cd CIEL
python -m pip install -r requirements.txt
```

### Global CLI Access
Invoke CIEL directly from any terminal prompt:

```powershell
ciel "open spotify and play harvey"
ciel --hud
```

### API Key Configuration (For Multimodal Vision)
Set your vision model API key for visual desktop tasks:

```powershell
# Save to config.json
python main.py --set-key "your-gemini-api-key"

# Or configure environment variables
$env:GEMINI_API_KEY="your-gemini-api-key"
$env:OPENAI_API_KEY="your-openai-api-key"
```

---

## Usage

### Command Line
```powershell
# Media playback
ciel play harvey on spotify
ciel play lofi beats on youtube

# System and audio
ciel volume 40
ciel mute
ciel system stats

# Daily briefing
ciel morning briefing
ciel weather in Tokyo

# Persistent memory
ciel remember that project directory is d:\bs\anti
ciel recall project directory

# Flights and games
ciel flights from San Francisco to Paris next month
ciel update steam games

# Undo last action
ciel undo
```

### HUD Web Interface
Launch the local web dashboard:

```powershell
ciel --hud
```

Access `http://localhost:8000/hud`:
- **System Telemetry**: Real-time CPU, RAM, and battery gauges.
- **Runtime Status**: Execution state indicator and current task progress.
- **Live Observation**: Real-time desktop screenshot preview.
- **Directive Input**: Interactive task dispatch box and event stream.
- **Kill Switch**: Immediate emergency halt button.

---

## Safety & Security Architecture

1. **3-Tier Permission Model (`--mode`)**:
   - `balanced` (default): Executes safe navigation, media, volume, and telemetry autonomously; prompts for PowerShell commands and application termination.
   - `strict`: Requires interactive confirmation for any state-altering action.
   - `autonomous`: Auto-approves standard operations; prompts only for destructive actions (file deletion, system shutdowns).
2. **Emergency Kill Switch (`Ctrl + Alt + X`)**: Halts execution immediately, releases keyboard and mouse locks, and stops background workers.
3. **Corner Slam Failsafe**: Moving the mouse cursor into `(0, 0)` triggers an immediate PyAutoGUI failsafe halt.
4. **Action Budget Limit**: Enforces `--max-actions` (default 50) to prevent infinite loops.

---

## Testing

Run the automated test suite:

```powershell
python -m pytest tests/ -v
```

All 54 unit and integration tests run offline without external API dependencies.

---

## Architecture Overview

```
CIEL Architecture
├── agent/
│   ├── fast_router.py       # Low-latency regex intent dispatcher
│   ├── brain.py             # Multimodal LLM client (Gemini, GPT-4o, Ollama)
│   ├── executor.py          # Observe-Decide-Act-Verify autonomous loop
│   ├── planner.py           # Goal decomposition and recovery
│   ├── hotkey_listener.py   # Global summon hotkey (Ctrl+Alt+C)
│   ├── state.py             # Runtime state and execution history
│   └── verifier.py          # Post-action verification
├── computer/
│   ├── voice.py             # Native Windows SAPI voice synthesizer
│   ├── system_telemetry.py  # CPU, RAM, and Battery metrics
│   ├── system_monitor.py    # Background threshold alert monitor
│   ├── ui.py                # Windows UI Automation (UIA) tree inspector
│   ├── windows.py           # Window discovery and focus control
│   ├── screen.py            # Desktop capture and resizing
│   ├── mouse.py             # Mouse movement and click handling
│   └── keyboard.py          # Keyboard input and key combinations
├── core/
│   └── undo.py              # Action rollback and state restoration
├── memory/
│   └── long_term.py         # Persistent JSON key-value and fact store
├── tools/
│   ├── proactive.py         # Daily briefing generator
│   ├── clipboard.py         # Clipboard inspection and manipulation
│   ├── flights.py           # Flight search query generator
│   ├── games.py             # Steam and Epic Games integrations
│   ├── audio.py             # Sound settings and volume mixer
│   ├── code_helper.py       # Python syntax validation
│   ├── spotify.py           # Spotify playback automation
│   ├── web.py               # YouTube autoplay and web search
│   ├── desktop_control.py   # Desktop and window management
│   ├── browser.py           # Browser navigation and tab management
│   ├── reminders.py         # Scheduled reminders and timers
│   ├── files.py             # File operations with Recycle Bin and undo
│   └── powershell.py        # Sandboxed PowerShell execution
└── server/
    ├── api.py               # FastAPI REST service and HUD endpoint
    ├── standalone_server.py # Standard-library HTTP server fallback
    └── hud.html             # Local HUD web interface
```

---

## Privacy, Lore & Fair Use Disclaimers

### 1. Local-Only Privacy Guarantee
- **100% Offline Processing**: CIEL processes all vision capture, telemetry, accessibility trees, and SAPI voice synthesis locally on your Windows 11 machine.
- **Zero Cloud Telemetry**: CIEL does not track user behavior or send background analytics to remote servers. Screen captures exist strictly in volatile memory during autonomous reasoning steps.
- **Failsafe Controls**: Press `Ctrl + Alt + X` or slam your mouse to `(0, 0)` at any moment to instantly trigger the emergency kill switch.

### 2. Fair Use & Intellectual Property Attribution
- **Character & Theme Lore**: *CIEL* is named in honor of **Manas: Ciel** (神智核) and **Wisdom King Raphael** (智慧之王) from *That Time I Got Reincarnated as a Slime* (*Tensei Shitara Slime Datta Ken*).
- **Intellectual Property Rights**: All character names, lore, iconography, and voice references are the registered trademarks and copyright of **Fuse / Mitz Vah / Kodansha / 8bit Project**.
- **Non-Commercial Fan Art & Fair Use**: This open-source desktop software is a strictly non-commercial academic fan tribute created under the fair use doctrine of Section 52 of the Indian Copyright Act 1957 and US 17 U.S.C. § 107.

---

## Author

Architected by **Aaditya Srinivasan** (B.Tech AI & Data Science, Madurai, Tamil Nadu, India).

---

## License

This project is licensed under the [MIT License](LICENSE).
