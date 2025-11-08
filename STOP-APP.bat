@echo off
REM Quick Snippet Overlay - Stop Application
REM =========================================

echo Stopping Quick Snippet Overlay...

REM Check if running
tasklist /FI "IMAGENAME eq QuickSnippetOverlay.exe" 2>NUL | find /I /N "QuickSnippetOverlay.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo.
    echo Application is not running.
    echo.
    pause
    exit /b 0
)

REM Kill the process
taskkill /F /IM QuickSnippetOverlay.exe >NUL 2>&1

echo.
echo Application stopped successfully!
echo.
pause
