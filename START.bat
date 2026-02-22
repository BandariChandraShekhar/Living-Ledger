@echo off
echo ============================================================
echo LIVING LEDGER - STARTUP
echo ============================================================
echo.

echo Step 1: Killing any existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo   Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo   Done!
echo.

echo Step 2: Starting server...
echo.
python api.py

pause
