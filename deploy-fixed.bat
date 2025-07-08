@echo off
echo ========================================
echo    Deer-Flow + n8n Deploy Script
echo ========================================
echo.

echo [1/6] Checking Docker environment...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not installed or not running
    echo Please install and start Docker Desktop first
    pause
    exit /b 1
)
echo OK: Docker environment is ready

echo.
echo [2/6] Checking required files...
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)
if not exist "src\server\app.py" (
    echo ERROR: Main application file not found
    pause
    exit /b 1
)
echo OK: File check completed

echo.
echo [3/6] Creating necessary directories...
if not exist "outputs" mkdir outputs
if not exist "outputs\reports" mkdir outputs\reports
if not exist "logs" mkdir logs
if not exist "n8n-workflows" mkdir n8n-workflows
echo OK: Directory creation completed

echo.
echo [4/6] Stopping existing containers (if any)...
docker-compose -f docker-compose.n8n.yml down >nul 2>&1
echo OK: Cleanup completed

echo.
echo [5/6] Building and starting services...
echo This may take several minutes, please wait...
docker-compose -f docker-compose.n8n.yml up --build -d

if %errorlevel% neq 0 (
    echo ERROR: Deployment failed, please check the error messages above
    echo.
    echo Common solutions:
    echo 1. Make sure Docker Desktop is fully started
    echo 2. Check if ports 5678, 8000, 5432, 6379 are available
    echo 3. Try restarting Docker Desktop
    pause
    exit /b 1
)

echo.
echo [6/6] Waiting for services to start...
timeout /t 30 /nobreak >nul

echo.
echo ========================================
echo           Deployment Complete!
echo ========================================
echo.
echo Access URLs:
echo   - n8n Workflow Platform: http://localhost:5678
echo   - Deer-Flow API Health: http://localhost:8000/api/reports/health
echo   - System Monitoring: http://localhost:8000/api/reports/metrics
echo.
echo n8n Login Info:
echo   - Username: admin
echo   - Password: changeme123
echo.
echo Useful Commands:
echo   - View logs: docker-compose -f docker-compose.n8n.yml logs -f
echo   - Stop services: docker-compose -f docker-compose.n8n.yml down
echo   - Restart services: docker-compose -f docker-compose.n8n.yml restart
echo.
echo Press any key to continue...
pause >nul 