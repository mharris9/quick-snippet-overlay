@echo off
REM Quick Snippet Overlay - Start Application
REM ==========================================

echo Starting Quick Snippet Overlay...

REM Check if already running
tasklist /FI "IMAGENAME eq QuickSnippetOverlay.exe" 2>NUL | find /I /N "QuickSnippetOverlay.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo Application is already running!
    echo Check your system tray for the icon.
    echo.
    pause
    exit /b 0
)

REM Start the application
start "" "%LOCALAPPDATA%\QuickSnippetOverlay\QuickSnippetOverlay.exe"

echo.
echo Application started!
echo Check your system tray for the icon.
echo Press Ctrl+Shift+Space to open the overlay.
echo.
pause
