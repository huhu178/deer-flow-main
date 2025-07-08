@echo off
echo ========================================
echo    Deer-Flow Local Start Script
echo ========================================
echo.

echo [1/3] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python 3.9+ first
    pause
    exit /b 1
)
echo OK: Python environment ready

echo.
echo [2/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Starting Deer-Flow API server...
echo Server will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/reports/health
echo.
echo Press Ctrl+C to stop the server
echo.

cd src
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload 