# Batch Files Guide - Quick Snippet Overlay

Easy-to-use batch files for managing Quick Snippet Overlay.

---

## Available Batch Files

### 📦 INSTALL.ps1
**Purpose**: Install the application to your system

**Usage**:
```powershell
.\INSTALL.ps1
```

**What it does**:
- Copies executable to `%LOCALAPPDATA%\QuickSnippetOverlay\`
- Creates desktop shortcut
- Creates Start Menu entry
- Copies documentation

---

### ▶️ START-APP.bat
**Purpose**: Start the application

**Usage**: Double-click `START-APP.bat`

**What it does**:
- Checks if already running (prevents duplicates)
- Starts the application if not running
- Shows confirmation message

**When to use**:
- After restarting Windows
- After closing the app
- To manually launch without shortcuts

---

### ⏹️ STOP-APP.bat
**Purpose**: Stop the application

**Usage**: Double-click `STOP-APP.bat`

**What it does**:
- Checks if application is running
- Gracefully closes the application
- Shows confirmation message

**When to use**:
- Before updating the application
- To free up system resources
- When troubleshooting

---

### 🔄 RESTART-APP.bat
**Purpose**: Restart the application

**Usage**: Double-click `RESTART-APP.bat`

**What it does**:
- Stops the application (if running)
- Waits 2 seconds
- Starts the application
- Shows confirmation message

**When to use**:
- After editing `config.yaml`
- After editing snippets manually
- When the app seems unresponsive
- After Windows updates

---

### 🚀 ADD-TO-STARTUP.bat
**Purpose**: Make the app start automatically on Windows boot

**Usage**: Double-click `ADD-TO-STARTUP.bat`

**What it does**:
- Creates a shortcut in Windows Startup folder
- App will auto-start on every Windows login
- Shows confirmation message

**When to use**:
- After installing the app (if you want auto-start)
- One-time setup

**To remove from startup**:
1. Press `Win+R`
2. Type: `shell:startup`
3. Delete the "Quick Snippet Overlay" shortcut

---

## Quick Reference

| Task | Batch File | When |
|------|-----------|------|
| Install app | `INSTALL.ps1` | First time setup |
| Start app | `START-APP.bat` | After boot/close |
| Stop app | `STOP-APP.bat` | Before update/troubleshooting |
| Restart app | `RESTART-APP.bat` | After config changes |
| Auto-start on boot | `ADD-TO-STARTUP.bat` | One-time setup |

---

## Common Workflows

### First Time Setup
1. Run `INSTALL.ps1` (PowerShell)
2. Run `ADD-TO-STARTUP.bat` (optional, for auto-start)
3. Done! App will be in system tray

### After Editing config.yaml
1. Run `RESTART-APP.bat`
2. New settings will be loaded

### After Editing snippets.yaml
- No action needed! Auto-reloads within 500ms
- Or run `RESTART-APP.bat` to force reload

### Troubleshooting
1. Run `STOP-APP.bat`
2. Wait 5 seconds
3. Run `START-APP.bat`

---

## How to Check if App is Running

**Method 1: System Tray**
- Look for the app icon in bottom-right corner
- If icon is there, app is running

**Method 2: Task Manager**
- Press `Ctrl+Shift+Esc`
- Look for "QuickSnippetOverlay.exe" in Processes
- If listed, app is running

**Method 3: Test the Hotkey**
- Press `Ctrl+Shift+Space`
- If overlay appears, app is running
- If nothing happens, app is not running

---

## Locations

**Executable**:
```
%LOCALAPPDATA%\QuickSnippetOverlay\QuickSnippetOverlay.exe
```
Or: `C:\Users\mikeh\AppData\Local\QuickSnippetOverlay\QuickSnippetOverlay.exe`

**Configuration**:
```
%USERPROFILE%\.quick-snippet-overlay\config.yaml
```
Or: `C:\Users\mikeh\.quick-snippet-overlay\config.yaml`

**Snippets**:
```
%USERPROFILE%\.quick-snippet-overlay\snippets.yaml
```
Or: `C:\Users\mikeh\.quick-snippet-overlay\snippets.yaml`

**Startup Shortcut** (if added):
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Quick Snippet Overlay.lnk
```

---

## Troubleshooting

### "Application is already running" but I don't see it

**Solution**: The system tray icon might be hidden
1. Click the up arrow `^` in system tray
2. Look for the app icon
3. Or run `STOP-APP.bat` then `START-APP.bat`

### Batch file does nothing when I double-click

**Solution**: Run from Command Prompt to see errors
1. Press `Win+R`
2. Type: `cmd`
3. Navigate: `cd C:\Users\mikeh\software_projects\quick-snippet-overlay`
4. Run: `START-APP.bat`
5. Read any error messages

### "Application not found" error

**Solution**: Install the app first
1. Run `INSTALL.ps1` in PowerShell
2. Then try the batch files again

### Want to remove from startup

**Solution**:
1. Press `Win+R`
2. Type: `shell:startup`
3. Delete the "Quick Snippet Overlay" shortcut

---

## Tips

💡 **Pin START-APP.bat to Taskbar** for quick access:
1. Right-click `START-APP.bat`
2. Create shortcut
3. Drag shortcut to taskbar

💡 **Create keyboard shortcut**:
1. Right-click `START-APP.bat` → Create shortcut
2. Right-click the shortcut → Properties
3. Set "Shortcut key" (e.g., `Ctrl+Alt+S`)

💡 **Add to desktop** for easy access:
1. Right-click `RESTART-APP.bat`
2. Send to → Desktop (create shortcut)

---

## Advanced: Creating Your Own Batch Files

Template for custom batch files:

```batch
@echo off
REM Your custom script

set "APP_EXE=%LOCALAPPDATA%\QuickSnippetOverlay\QuickSnippetOverlay.exe"
set "CONFIG_FILE=%USERPROFILE%\.quick-snippet-overlay\config.yaml"

REM Check if running
tasklist /FI "IMAGENAME eq QuickSnippetOverlay.exe" 2>NUL | find /I /N "QuickSnippetOverlay.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo App is running
) else (
    echo App is not running
)

pause
```

---

**Quick Snippet Overlay Batch Files v1.0**
Last Updated: November 6, 2025
