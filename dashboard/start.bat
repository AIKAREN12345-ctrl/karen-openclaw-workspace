@echo off
echo Starting Karen Dashboard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q flask flask-socketio flask-login requests psutil

echo.
echo ==========================================
echo  🤖 Karen Dashboard Starting...
echo ==========================================
echo.
echo  Local:   http://localhost:5000
echo  Network: http://100.75.72.26:5000
echo.
echo  Press Ctrl+C to stop
echo.

python app.py

pause
