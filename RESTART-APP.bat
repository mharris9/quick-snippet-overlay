@echo off
REM Quick Snippet Overlay - Restart Application
REM ============================================

echo Restarting Quick Snippet Overlay...
echo.

REM Check if running
tasklist /FI "IMAGENAME eq QuickSnippetOverlay.exe" 2>NUL | find /I /N "QuickSnippetOverlay.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Stopping application...
    taskkill /F /IM QuickSnippetOverlay.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
    echo Stopped.
    echo.
) else (
    echo Application was not running.
    echo.
)

REM Start the application
echo Starting application...
start "" "%LOCALAPPDATA%\QuickSnippetOverlay\QuickSnippetOverlay.exe"

echo.
echo Application restarted!
echo Check your system tray for the icon.
echo Press Ctrl+Shift+Space to open the overlay.
echo.
pause
