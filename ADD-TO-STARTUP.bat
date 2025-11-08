@echo off
REM Quick Snippet Overlay - Add to Windows Startup
REM ===============================================

echo Adding Quick Snippet Overlay to Windows Startup...
echo.

REM Define paths
set "TARGET_EXE=%LOCALAPPDATA%\QuickSnippetOverlay\QuickSnippetOverlay.exe"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\Quick Snippet Overlay.lnk"

REM Check if executable exists
if not exist "%TARGET_EXE%" (
    echo ERROR: Application not found at:
    echo %TARGET_EXE%
    echo.
    echo Please run INSTALL.ps1 first to install the application.
    echo.
    pause
    exit /b 1
)

REM Create shortcut using PowerShell
echo Creating startup shortcut...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT_PATH%'); $SC.TargetPath = '%TARGET_EXE%'; $SC.WorkingDirectory = '%LOCALAPPDATA%\QuickSnippetOverlay'; $SC.Description = 'Quick Snippet Overlay - Auto-start'; $SC.Save()"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo SUCCESS! Application added to Windows Startup.
    echo.
    echo The app will now start automatically when you log in to Windows.
    echo.
    echo Shortcut location:
    echo %SHORTCUT_PATH%
    echo.
    echo To remove from startup:
    echo 1. Press Win+R
    echo 2. Type: shell:startup
    echo 3. Delete the "Quick Snippet Overlay" shortcut
    echo.
) else (
    echo.
    echo ERROR: Failed to create startup shortcut.
    echo Please try running this batch file as Administrator.
    echo.
)

pause
