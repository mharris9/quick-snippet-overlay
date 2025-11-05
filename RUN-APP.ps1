# Quick Snippet Overlay - Launch Script
# Run this script to start the application

Write-Host "Quick Snippet Overlay - Starting Application" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Clean up any stale processes and lock files
Write-Host "Checking for stale processes..." -ForegroundColor Green
Get-Process python* -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like "*Quick Snippet Overlay*"} | Stop-Process -Force -ErrorAction SilentlyContinue

$lockFile = "$env:USERPROFILE\.quick-snippet-overlay\app.lock"
if (Test-Path $lockFile) {
    Write-Host "Removing stale lock file..." -ForegroundColor Yellow
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

# Verify dependencies
Write-Host "Verifying dependencies..." -ForegroundColor Green
$packages = @("PySide6", "pynput", "pyperclip", "watchdog", "rapidfuzz", "PyYAML")
$missing = @()

foreach ($pkg in $packages) {
    $installed = & python -m pip list | Select-String -Pattern "^$pkg\s"
    if (-not $installed) {
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "ERROR: Missing dependencies: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "Please run: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Check configuration files
Write-Host "Checking configuration files..." -ForegroundColor Green

$snippetsDir = "C:\Users\mikeh\snippets"
$snippetsFile = "$snippetsDir\snippets.yaml"
$configFile = "$snippetsDir\config.yaml"

if (-not (Test-Path $snippetsFile)) {
    Write-Host "WARNING: snippets.yaml not found at $snippetsFile" -ForegroundColor Yellow
    Write-Host "Application will create default file on first run." -ForegroundColor Yellow
}

if (-not (Test-Path $configFile)) {
    Write-Host "WARNING: config.yaml not found at $configFile" -ForegroundColor Yellow
    Write-Host "Application will create default file on first run." -ForegroundColor Yellow
}

# Launch application
Write-Host ""
Write-Host "Launching Quick Snippet Overlay..." -ForegroundColor Green
Write-Host "Look for the system tray icon in your taskbar!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+Shift+Space to open the overlay" -ForegroundColor Cyan
Write-Host "Press Ctrl+C in this window to stop the application" -ForegroundColor Yellow
Write-Host ""

# Set PYTHONPATH to project root so imports work
$env:PYTHONPATH = (Get-Location).Path

# Run the application
python src\main.py
