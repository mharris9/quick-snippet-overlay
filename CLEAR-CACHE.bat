@echo off
REM Clear Python bytecode cache to force reload of updated code

echo Clearing Python cache...
echo.

REM Remove __pycache__ directories
if exist "src\__pycache__" (
    echo Removing src\__pycache__...
    rd /s /q "src\__pycache__"
)

if exist "__pycache__" (
    echo Removing __pycache__...
    rd /s /q "__pycache__"
)

REM Remove .pyc files
echo Removing .pyc files...
del /s /q "*.pyc" 2>nul

REM Clear log file
echo Clearing log file...
if exist "quick-snippet-overlay.log" (
    echo. > "quick-snippet-overlay.log"
)

echo.
echo Cache cleared successfully!
echo.
echo Now run RUN-APP.bat to start with fresh code
echo.
pause
