@echo off
REM Quick Snippet Overlay - Clean Launch (Clears Python Cache First)
REM Use this if you're getting Qt initialization errors

echo Quick Snippet Overlay - Clean Start
echo =====================================
echo.

echo Cleaning Python cache...
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
if exist "tests\__pycache__" rmdir /s /q "tests\__pycache__"
for /r src %%i in (*.pyc) do del "%%i" 2>nul
echo Cache cleared.
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
