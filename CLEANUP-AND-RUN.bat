@echo off
REM Quick Snippet Overlay - Cleanup and Run
REM Use this if you get "Already Running" error

echo Quick Snippet Overlay - Cleanup and Start
echo ============================================
echo.

echo Step 1: Killing any existing Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo.

echo Step 2: Removing lock file...
if exist "%USERPROFILE%\.quick-snippet-overlay\app.lock" (
    del "%USERPROFILE%\.quick-snippet-overlay\app.lock"
    echo Lock file removed.
) else (
    echo No lock file found.
)
echo.

echo Step 3: Cleaning Python cache...
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
echo.

echo Step 4: Starting application...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Set PYTHONPATH to project root
set PYTHONPATH=%CD%

REM Launch application
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
