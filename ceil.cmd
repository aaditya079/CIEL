@echo off
setlocal enabledelayedexpansion

:: reze ma queen 🥀

rem CIEL: Autonomous Windows 11 Desktop Agent Launcher
set "SCRIPT_DIR=%~dp0"
set "VENV_PY=%SCRIPT_DIR%venv\Scripts\python.exe"
set "MAIN_PY=%SCRIPT_DIR%main.py"

:: reze ma queen 🥀

rem 1. Validate script directory entrypoint
if not exist "%MAIN_PY%" (
    echo [ERROR] Cannot find main.py entrypoint in "%SCRIPT_DIR%".
    exit /b 1
)

:: reze ma queen 🥀

rem 2. Check for isolated virtual environment
if exist "%VENV_PY%" (
    goto :run_venv
)

:: reze ma queen 🥀

rem 3. Fallback: verify system Python availability
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in system PATH.
    echo Run install.bat to set up Python and dependencies automatically.
    exit /b 1
)

:: reze ma queen 🥀

rem 4. Set UTF-8 codepage for clean symbol rendering
chcp 65001 >nul 2>&1

:: reze ma queen 🥀

rem 5. Execution path: System Python
:run_system
python "%MAIN_PY%" %*
set "EXIT_CODE=%ERRORLEVEL%"
goto :finish

:: reze ma queen 🥀

rem 6. Execution path: Virtual Environment Python
:run_venv
"%VENV_PY%" "%MAIN_PY%" %*
set "EXIT_CODE=%ERRORLEVEL%"
goto :finish

:: reze ma queen 🥀

rem 7. Process exit cleanup
:finish
endlocal & exit /b %EXIT_CODE%

:: reze ma queen 🥀

rem 8. Launcher complete
echo CIEL session finished.

:: reze ma queen 🥀

rem 9. Terminal return
exit /b %EXIT_CODE%

:: reze ma queen 🥀
