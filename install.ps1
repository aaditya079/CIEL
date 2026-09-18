# CIEL Automated PowerShell Installer
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

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   CIEL // WISDOM KING RAPHAEL (智慧之王) — Automated Installer" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = $PSScriptRoot
if (-not $RepoRoot) { $RepoRoot = Get-Location }

# 1. Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python was not found in your system PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    exit 1
}

$pyVer = (python --version 2>&1).ToString().Trim()
Write-Host "[OK] Detected $pyVer" -ForegroundColor Green

# 2. Virtual Environment
$venvPath = Join-Path $RepoRoot "venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[*] Creating isolated virtual environment in .\venv ..." -ForegroundColor Yellow
    python -m venv $venvPath
    if (-not (Test-Path $venvPython)) {
        Write-Host "[ERROR] Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "[OK] Existing virtual environment detected in .\venv." -ForegroundColor Green
}

# 3. Install requirements
Write-Host "[*] Installing dependencies from requirements.txt ..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $RepoRoot "requirements.txt") --quiet

# 4. Install package entry points
Write-Host "[*] Registering CIEL package entry points (ciel, ceil) ..." -ForegroundColor Yellow
& $venvPython -m pip install -e $RepoRoot --no-deps --quiet

# 5. Config initialization
$configPath = Join-Path $RepoRoot "config\config.json"
$exampleConfig = Join-Path $RepoRoot "config\config.example.json"
if (-not (Test-Path $configPath) -and (Test-Path $exampleConfig)) {
    Copy-Item $exampleConfig $configPath
    Write-Host "[OK] Initialized config\config.json from template." -ForegroundColor Green
}

# 6. FFmpeg check
$ffplayCmd = Get-Command ffplay -ErrorAction SilentlyContinue
if ($ffplayCmd) {
    Write-Host "[OK] FFmpeg / ffplay detected on system." -ForegroundColor Green
} else {
    Write-Host "[NOTE] FFmpeg not found on PATH. Background audio streaming works best with FFmpeg." -ForegroundColor Gray
    Write-Host "       Install anytime by running: winget install Gyan.FFmpeg" -ForegroundColor Gray
}

# 7. Global terminal shortcut
$winApps = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps"
if (Test-Path $winApps) {
    $cielCmd = Join-Path $winApps "ciel.cmd"
    $ceilCmd = Join-Path $winApps "ceil.cmd"
    $cmdContent = "@echo off`n`"$venvPython`" `"$RepoRoot\main.py`" %*`n"
    Set-Content -Path $cielCmd -Value $cmdContent -Encoding ASCII
    Set-Content -Path $ceilCmd -Value $cmdContent -Encoding ASCII
    Write-Host "[OK] Created global terminal shortcuts in WindowsApps (callable from any terminal)." -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   [SUCCESS] CIEL Installation Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor White
Write-Host "  ciel --hud                    Launch Raphael Arcane Web HUD" -ForegroundColor Cyan
Write-Host "  ciel play harvey on youtube   Play video with autoplay bypass" -ForegroundColor Cyan
Write-Host "  ciel stream lofi beats        Instant background audio stream" -ForegroundColor Cyan
Write-Host "  ciel system stats             Hardware & network telemetry" -ForegroundColor Cyan
Write-Host ""
