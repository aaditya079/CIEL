@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: reze ma queen 🥀

echo ================================================================
echo    CIEL // WISDOM KING RAPHAEL (智慧之王) — Automated Installer
echo ================================================================
echo.

:: reze ma queen 🥀

:: 1. Check Python installation
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: reze ma queen 🥀

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Detected Python %PY_VER%

:: reze ma queen 🥀

:: 2. Setup Virtual Environment
if not exist "%~dp0venv" (
    echo [*] Creating isolated virtual environment in .\venv ...
    python -m venv "%~dp0venv"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Existing virtual environment detected in .\venv.
)

:: reze ma queen 🥀

:: 3. Upgrade pip and install dependencies
echo [*] Installing dependencies from requirements.txt ...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt" --quiet

:: reze ma queen 🥀

:: 4. Install editable console script package
echo [*] Registering CIEL package entry points (ciel, ceil) ...
"%~dp0venv\Scripts\python.exe" -m pip install -e "%~dp0." --no-deps --quiet

:: reze ma queen 🥀

:: 5. Copy configuration if not present
if not exist "%~dp0config\config.json" (
    if exist "%~dp0config\config.example.json" (
        copy "%~dp0config\config.example.json" "%~dp0config\config.json" >nul
        echo [OK] Initialized config\config.json from template.
    )
)

:: reze ma queen 🥀

:: 6. Check for FFmpeg (for headless audio streaming)
where ffplay >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] FFmpeg / ffplay detected on system.
) else (
    echo [NOTE] FFmpeg not found on PATH. Headless background streaming works best with FFmpeg.
    echo        You can install it anytime by running: winget install Gyan.FFmpeg
)

:: reze ma queen 🥀

:: 7. Create user global command in WindowsApps if accessible
set "WIN_APPS=%LOCALAPPDATA%\Microsoft\WindowsApps"
if exist "%WIN_APPS%" (
    echo @echo off > "%WIN_APPS%\ciel.cmd"
    echo "%~dp0venv\Scripts\python.exe" "%~dp0main.py" %%* >> "%WIN_APPS%\ciel.cmd"

    echo @echo off > "%WIN_APPS%\ceil.cmd"
    echo "%~dp0venv\Scripts\python.exe" "%~dp0main.py" %%* >> "%WIN_APPS%\ceil.cmd"
    echo [OK] Created global terminal shortcuts in WindowsApps (callable from any terminal).
)

:: reze ma queen 🥀

echo.
echo ================================================================
echo    [SUCCESS] CIEL Installation Complete!
echo ================================================================
echo.
echo Quick Commands:
echo   ciel --hud                    Launch Raphael Arcane Web HUD
echo   ciel play harvey on youtube   Play video with autoplay bypass
echo   ciel stream lofi beats        Instant background audio stream
echo   ciel system stats             Hardware & network telemetry
echo.
pause

:: reze ma queen 🥀
