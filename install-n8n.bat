@echo off
echo ========================================
echo    Install n8n + Connect to Deer-Flow
echo ========================================
echo.

echo [1/4] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found
    echo Please download and install Node.js from: https://nodejs.org/
    echo Choose the LTS version
    pause
    exit /b 1
)
echo OK: Node.js is installed

echo.
echo [2/4] Installing n8n globally...
npm install -g n8n

echo.
echo [3/4] Creating n8n configuration...
if not exist "n8n-data" mkdir n8n-data
echo N8N_BASIC_AUTH_ACTIVE=true > n8n-data\.env
echo N8N_BASIC_AUTH_USER=admin >> n8n-data\.env
echo N8N_BASIC_AUTH_PASSWORD=changeme123 >> n8n-data\.env
echo N8N_HOST=0.0.0.0 >> n8n-data\.env
echo N8N_PORT=5678 >> n8n-data\.env

echo.
echo [4/4] Starting n8n...
echo.
echo ========================================
echo           n8n is starting...
echo ========================================
echo.
echo Access n8n at: http://localhost:5678
echo Username: admin
echo Password: changeme123
echo.
echo To connect to your AI system, use:
echo API URL: http://localhost:8000/api/reports/webhook/n8n
echo.
echo Press Ctrl+C to stop n8n
echo.

cd n8n-data
n8n start 