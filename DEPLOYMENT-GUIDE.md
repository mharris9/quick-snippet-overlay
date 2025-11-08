# Quick Snippet Overlay - Deployment Guide

**Version**: 1.0.0
**Date**: November 6, 2025

This guide walks you through deploying Quick Snippet Overlay on your machine and optionally preparing it for distribution.

---

## Option 1: Personal Deployment (Run on Your Machine)

### Step 1: Test the Executable

1. **Locate the executable**:
   ```
   C:\Users\mikeh\software_projects\quick-snippet-overlay\dist\QuickSnippetOverlay.exe
   ```

2. **First run** (from File Explorer):
   - Navigate to the `dist` folder
   - Double-click `QuickSnippetOverlay.exe`
   - **Windows Defender SmartScreen Warning**:
     - You may see "Windows protected your PC"
     - Click "More info" → "Run anyway"
     - This happens because the executable is not code-signed

3. **Verify it's running**:
   - Check system tray (bottom-right) for the app icon
   - Press `Ctrl+Shift+Space` to open the overlay
   - The overlay should appear centered on your screen

4. **Test basic functionality**:
   - Type in the search box to test search
   - Press `Ctrl+N` to test "Add Snippet" dialog
   - Press `Ctrl+D` to test "Delete Snippets" dialog
   - Press `Esc` to close the overlay

5. **Check file creation**:
   - Configuration folder should be created at:
     ```
     C:\Users\mikeh\.quick-snippet-overlay\
     ```
   - Files created:
     - `config.yaml` (configuration)
     - `snippets.yaml` (empty snippet file)
     - `app.lock` (lock file while running)

### Step 2: Move to Permanent Location

Instead of running from the `dist` folder:

1. **Create application folder**:
   ```
   C:\Program Files\QuickSnippetOverlay\
   ```
   Or use a personal folder:
   ```
   C:\Apps\QuickSnippetOverlay\
   ```

2. **Copy the executable**:
   - Copy `QuickSnippetOverlay.exe` to your chosen folder
   - You can delete the `dist/build` folders after copying

3. **Test from new location**:
   - Double-click the executable from the new location
   - Verify it still works

### Step 3: Create Desktop Shortcut (Optional)

**Method 1: Right-click**
1. Right-click `QuickSnippetOverlay.exe`
2. Select "Create shortcut"
3. Drag shortcut to Desktop

**Method 2: PowerShell Script**
```powershell
$TargetFile = "C:\Program Files\QuickSnippetOverlay\QuickSnippetOverlay.exe"
$ShortcutFile = "$env:USERPROFILE\Desktop\Quick Snippet Overlay.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $TargetFile
$Shortcut.Save()
```

### Step 4: Add to Windows Startup (Optional)

**Option A: Startup Folder**
1. Press `Win+R`
2. Type: `shell:startup`
3. Create a shortcut to `QuickSnippetOverlay.exe` in this folder

**Option B: Task Scheduler (More Control)**
1. Open Task Scheduler
2. Create Basic Task:
   - Name: Quick Snippet Overlay
   - Trigger: When I log on
   - Action: Start a program
   - Program: `C:\Program Files\QuickSnippetOverlay\QuickSnippetOverlay.exe`
   - Finish

**Option C: Registry (Advanced)**
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
New String Value:
Name: QuickSnippetOverlay
Data: C:\Program Files\QuickSnippetOverlay\QuickSnippetOverlay.exe
```

### Step 5: Configure the Application

1. **Open configuration file**:
   ```
   C:\Users\mikeh\.quick-snippet-overlay\config.yaml
   ```

2. **Customize settings** (optional):
   ```yaml
   overlay_width: 800        # Make overlay wider
   overlay_height: 600       # Make overlay taller
   max_results: 20           # Show more results
   fuzzy_threshold: 50       # More lenient search
   ```

3. **Restart the application** for changes to take effect

---

## Option 2: Distribution Deployment (Share with Others)

### Preparation

Before sharing with others:

1. **Test on a clean machine** (if possible):
   - Virtual machine or different PC
   - Ensures no missing dependencies

2. **Create a release package**:
   ```
   QuickSnippetOverlay-v1.0.0/
   ├── QuickSnippetOverlay.exe
   ├── README.md
   ├── USER-GUIDE.md
   └── LICENSE
   ```

3. **Zip the package**:
   ```powershell
   Compress-Archive -Path "QuickSnippetOverlay-v1.0.0" -DestinationPath "QuickSnippetOverlay-v1.0.0.zip"
   ```

### Distribution Methods

#### Method 1: GitHub Release

1. **Create repository** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Release v1.0.0"
   git remote add origin https://github.com/yourusername/quick-snippet-overlay.git
   git push -u origin master
   ```

2. **Create release on GitHub**:
   - Go to repository → Releases → "Create a new release"
   - Tag: `v1.0.0`
   - Title: "Quick Snippet Overlay v1.0.0"
   - Description: (see Release Notes below)
   - Upload: `QuickSnippetOverlay.exe`
   - Publish release

3. **Share the link**:
   ```
   https://github.com/yourusername/quick-snippet-overlay/releases/tag/v1.0.0
   ```

#### Method 2: Direct Sharing

1. **Upload to cloud storage**:
   - Google Drive
   - Dropbox
   - OneDrive
   - WeTransfer

2. **Share link** with instructions:
   - Include USER-GUIDE.md
   - Warn about SmartScreen (not code-signed)

#### Method 3: Network Share (Enterprise)

1. **Copy to network location**:
   ```
   \\company-server\Apps\QuickSnippetOverlay\
   ```

2. **Create deployment script**:
   ```batch
   @echo off
   xcopy "\\company-server\Apps\QuickSnippetOverlay\*" "C:\Program Files\QuickSnippetOverlay\" /E /I /Y
   start "" "C:\Program Files\QuickSnippetOverlay\QuickSnippetOverlay.exe"
   ```

---

## Release Notes Template

Use this for GitHub releases or distribution announcements:

```markdown
# Quick Snippet Overlay v1.0.0

First production release of Quick Snippet Overlay - a Windows 11 application for instant access to text snippets via global hotkey.

## 🎉 Features

- **Global Hotkey**: Press `Ctrl+Shift+Space` from anywhere
- **Fuzzy Search**: Typo-tolerant search powered by rapidfuzz
- **Variable Substitution**: Dynamic snippets with `{{variable:default}}`
- **Quick Add**: Add snippets on-the-fly with `Ctrl+N`
- **Mass Delete**: Delete multiple snippets with `Ctrl+D`
- **Tag Autocomplete**: Smart tag suggestions
- **Multi-Monitor**: Centers on active monitor
- **Auto-Reload**: Changes to snippet file reload automatically

## 📥 Installation

### Option 1: Standalone Executable (Recommended)

1. Download `QuickSnippetOverlay.exe` (47MB)
2. Double-click to run
3. **Windows SmartScreen**: Click "More info" → "Run anyway" (executable not code-signed)
4. Check system tray for icon
5. Press `Ctrl+Shift+Space` to start using!

### Option 2: Build from Source

See [README.md](README.md) for development setup.

## 📖 Documentation

- [README.md](README.md) - Technical overview and developer guide
- [USER-GUIDE.md](USER-GUIDE.md) - Complete end-user documentation

## ⚙️ Requirements

- Windows 11 (Windows 10 may work but not tested)
- No Python installation required!

## 🐛 Known Issues

- Not code-signed (Windows Defender SmartScreen warning appears)
- No application icon (using default Windows icon)
- No installer (manual extraction required)

## 📝 Version Information

- **Version**: 1.0.0
- **Release Date**: November 6, 2025
- **Build**: PyInstaller 6.16.0
- **Python**: 3.13.1
- **PySide6**: 6.10.0

## 🙏 Credits

Built with [Claude Code](https://claude.ai/claude-code)

## 📄 License

MIT License - See [LICENSE](LICENSE) file
```

---

## Testing Checklist

Before considering deployment complete:

- [ ] Executable runs without errors
- [ ] System tray icon appears
- [ ] Hotkey works (`Ctrl+Shift+Space`)
- [ ] Overlay opens and closes
- [ ] Search functionality works
- [ ] Can add a test snippet (`Ctrl+N`)
- [ ] Can copy a snippet to clipboard
- [ ] Can delete a snippet (`Ctrl+D`)
- [ ] Configuration file created
- [ ] Snippets file created
- [ ] No console window appears (GUI mode)
- [ ] Application quits properly (right-click tray → Quit)

---

## Troubleshooting Deployment

### Executable Won't Run

**Issue**: Double-clicking does nothing

**Solutions**:
1. Check Task Manager - is it already running?
2. Try running from Command Prompt:
   ```cmd
   cd C:\Users\mikeh\software_projects\quick-snippet-overlay\dist
   QuickSnippetOverlay.exe
   ```
   Look for error messages

3. Check Windows Event Viewer:
   - Event Viewer → Windows Logs → Application
   - Look for errors from QuickSnippetOverlay

### SmartScreen Blocking

**Issue**: "Windows protected your PC" - can't run

**Solution**:
- Click "More info"
- Click "Run anyway"
- This happens because executable is not code-signed
- To avoid: Purchase code signing certificate (see PACKAGING-NOTES.md)

### Missing DLL Errors

**Issue**: "The program can't start because [DLL] is missing"

**Solution**:
- Rebuild executable with PyInstaller
- Check hidden imports in `.spec` file
- Verify all dependencies bundled

### Application Crashes on Startup

**Issue**: Opens briefly then closes

**Solutions**:
1. Run from command prompt to see errors
2. Check lock file: `C:\Users\mikeh\.quick-snippet-overlay\app.lock`
3. Delete lock file if stale
4. Check config file syntax: `config.yaml`

---

## Post-Deployment

### Monitoring

**Check these periodically**:
- Lock file location: `C:\Users\mikeh\.quick-snippet-overlay\app.lock`
- Config file: `config.yaml`
- Snippets file: `snippets.yaml`
- Backup files: `snippets.yaml.backup.*`

### Updates

**For future versions**:
1. Close the application
2. Replace the executable with new version
3. Restart the application
4. Configuration and snippets preserved (separate folder)

### Uninstallation

**To remove**:
1. Close the application (right-click tray → Quit)
2. Delete executable:
   ```
   C:\Program Files\QuickSnippetOverlay\QuickSnippetOverlay.exe
   ```
3. Optionally delete data:
   ```
   C:\Users\mikeh\.quick-snippet-overlay\
   ```
4. Remove from startup (if added)
5. Delete shortcuts (if created)

---

## Quick Start Script

Create `INSTALL.bat` for automated setup:

```batch
@echo off
echo Quick Snippet Overlay - Installation
echo =====================================
echo.

REM Create application directory
set "INSTALL_DIR=C:\Program Files\QuickSnippetOverlay"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo Copying executable...
copy "QuickSnippetOverlay.exe" "%INSTALL_DIR%\" /Y

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\Quick Snippet Overlay.lnk'); $SC.TargetPath = '%INSTALL_DIR%\QuickSnippetOverlay.exe'; $SC.Save()"

REM Create Start Menu entry
echo Creating Start Menu entry...
copy "%INSTALL_DIR%\QuickSnippetOverlay.exe" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Quick Snippet Overlay.lnk"

echo.
echo Installation complete!
echo.
echo Launch from:
echo - Desktop shortcut
echo - Start Menu
echo - %INSTALL_DIR%\QuickSnippetOverlay.exe
echo.
pause
```

---

## Summary

**For Personal Use**:
1. Run `dist/QuickSnippetOverlay.exe`
2. Move to permanent location
3. Create shortcuts (optional)
4. Add to startup (optional)

**For Distribution**:
1. Test on clean machine
2. Create release package
3. Upload to GitHub/cloud storage
4. Share with users + USER-GUIDE.md

**Next Steps**:
- Add application icon (see PACKAGING-NOTES.md)
- Create Inno Setup installer (see PACKAGING-NOTES.md)
- Consider code signing for public distribution

---

**Deployment Guide v1.0.0**
Last Updated: November 6, 2025
