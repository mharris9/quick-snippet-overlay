# Quick Snippet Overlay - Installation Script
# Copies executable to Program Files and creates shortcuts

Write-Host "Quick Snippet Overlay - Installation" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Define paths
$SourceExe = "$PSScriptRoot\dist\QuickSnippetOverlay.exe"
$InstallDir = "$env:LOCALAPPDATA\QuickSnippetOverlay"
$TargetExe = "$InstallDir\QuickSnippetOverlay.exe"

# Check if source exists
if (-not (Test-Path $SourceExe)) {
    Write-Host "ERROR: Executable not found at $SourceExe" -ForegroundColor Red
    Write-Host "Please build the application first: pyinstaller quick-snippet-overlay.spec --clean" -ForegroundColor Yellow
    pause
    exit 1
}

# Create installation directory
Write-Host "Creating installation directory..." -ForegroundColor Yellow
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Copy executable
Write-Host "Copying executable to $InstallDir..." -ForegroundColor Yellow
Copy-Item $SourceExe $TargetExe -Force

# Copy documentation
Write-Host "Copying documentation..." -ForegroundColor Yellow
$Docs = @("README.md", "USER-GUIDE.md", "LICENSE")
foreach ($doc in $Docs) {
    $sourcePath = "$PSScriptRoot\$doc"
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath "$InstallDir\" -Force
    }
}

# Create Desktop shortcut
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = "$DesktopPath\Quick Snippet Overlay.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetExe
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Quick Snippet Overlay - Instant access to text snippets"
$Shortcut.Save()

# Create Start Menu shortcut
Write-Host "Creating Start Menu shortcut..." -ForegroundColor Yellow
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$StartMenuShortcut = "$StartMenuPath\Quick Snippet Overlay.lnk"
$Shortcut2 = $WScriptShell.CreateShortcut($StartMenuShortcut)
$Shortcut2.TargetPath = $TargetExe
$Shortcut2.WorkingDirectory = $InstallDir
$Shortcut2.Description = "Quick Snippet Overlay - Instant access to text snippets"
$Shortcut2.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installed to: $InstallDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launch from:" -ForegroundColor Yellow
Write-Host "  - Desktop shortcut" -ForegroundColor White
Write-Host "  - Start Menu search: 'Quick Snippet'" -ForegroundColor White
Write-Host "  - Press Ctrl+Shift+Space (global hotkey)" -ForegroundColor White
Write-Host ""
Write-Host "Would you like to start the application now? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "Starting Quick Snippet Overlay..." -ForegroundColor Green
    Start-Process $TargetExe
    Write-Host "Check your system tray for the icon!" -ForegroundColor Cyan
} else {
    Write-Host "You can start it later from the shortcuts." -ForegroundColor White
}

Write-Host ""
Write-Host "To add to Windows startup:" -ForegroundColor Yellow
Write-Host "  1. Press Win+R" -ForegroundColor White
Write-Host "  2. Type: shell:startup" -ForegroundColor White
Write-Host "  3. Create a shortcut to: $TargetExe" -ForegroundColor White
Write-Host ""

pause
