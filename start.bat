@echo off
REM Code Intelligence System Startup Script for Windows

echo Starting Code Intelligence System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create data directory
if not exist "data" mkdir data

REM Start the server
echo.
echo Starting web server on http://localhost:8000
echo Press Ctrl+C to stop
echo.

cd code-intelligence
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
