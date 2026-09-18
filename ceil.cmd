@echo off

:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
:: reze ma queen 🥀
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0main.py" %*
) else (
    python "%~dp0main.py" %*
)
