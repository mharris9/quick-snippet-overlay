@echo off
REM Quick Snippet Overlay - Launch Script (Batch Version)
REM Double-click this file to start the application

echo Quick Snippet Overlay - Starting Application
echo =============================================
echo.

REM Clean up any stale processes and lock files
echo Checking for stale processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Quick Snippet Overlay*" 2>nul >nul
if exist "%USERPROFILE%\.quick-snippet-overlay\app.lock" (
    echo Removing stale lock file...
    del "%USERPROFILE%\.quick-snippet-overlay\app.lock" 2>nul
)
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Set PYTHONPATH to project root
set PYTHONPATH=%CD%

REM Launch application
echo.
echo Launching Quick Snippet Overlay...
echo Look for the system tray icon in your taskbar!
echo.
echo Press Ctrl+Shift+Space to open the overlay
echo Close this window to stop the application
echo.

REM Run the application
python src\main.py

REM Cleanup on exit
echo.
echo Application stopped.
pause
