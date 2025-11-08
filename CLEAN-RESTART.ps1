# Clean Restart Script - Stops app, clears cache, and restarts

Write-Host "=== Quick Snippet Overlay - Clean Restart ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop any running Python processes for this app
Write-Host "Step 1: Stopping running app..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python process(es). Stopping..." -ForegroundColor Yellow
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "Processes stopped." -ForegroundColor Green
} else {
    Write-Host "No running Python processes found." -ForegroundColor Gray
}

# Step 2: Clear Python cache
Write-Host ""
Write-Host "Step 2: Clearing Python cache..." -ForegroundColor Yellow
$cacheCount = 0
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force
    $cacheCount++
}
if ($cacheCount -gt 0) {
    Write-Host "Cleared $cacheCount cache directories." -ForegroundColor Green
} else {
    Write-Host "No cache found (already clean)." -ForegroundColor Gray
}

# Step 3: Clear .pyc files
Write-Host ""
Write-Host "Step 3: Clearing .pyc files..." -ForegroundColor Yellow
$pycFiles = Get-ChildItem -Path . -Filter *.pyc -Recurse -Force
$pycCount = $pycFiles.Count
if ($pycCount -gt 0) {
    $pycFiles | Remove-Item -Force
    Write-Host "Cleared $pycCount .pyc files." -ForegroundColor Green
} else {
    Write-Host "No .pyc files found." -ForegroundColor Gray
}

# Step 4: Start the app
Write-Host ""
Write-Host "Step 4: Starting app..." -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Start app
Write-Host "Launching Quick Snippet Overlay..." -ForegroundColor Green
python src\main.py
