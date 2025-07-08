@echo off
chcp 65001
echo ========================================
echo    Deer-Flow + n8n 一键部署脚本
echo ========================================
echo.

echo [1/6] 检查Docker环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装或未启动，请先安装并启动Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker环境正常

echo.
echo [2/6] 检查必要文件...
if not exist "requirements.txt" (
    echo ❌ 未找到requirements.txt文件
    pause
    exit /b 1
)
if not exist "src\server\app.py" (
    echo ❌ 未找到主应用文件
    pause
    exit /b 1
)
echo ✅ 文件检查完成

echo.
echo [3/6] 创建必要目录...
if not exist "outputs" mkdir outputs
if not exist "outputs\reports" mkdir outputs\reports
if not exist "logs" mkdir logs
if not exist "n8n-workflows" mkdir n8n-workflows
echo ✅ 目录创建完成

echo.
echo [4/6] 停止现有容器（如果存在）...
docker-compose -f docker-compose.n8n.yml down >nul 2>&1
echo ✅ 清理完成

echo.
echo [5/6] 构建并启动服务...
echo 这可能需要几分钟时间，请耐心等待...
docker-compose -f docker-compose.n8n.yml up --build -d

if %errorlevel% neq 0 (
    echo ❌ 部署失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo [6/6] 等待服务启动...
timeout /t 30 /nobreak >nul

echo.
echo ========================================
echo           🎉 部署完成！
echo ========================================
echo.
echo 📊 访问地址：
echo   - n8n工作流平台: http://localhost:5678
echo   - Deer-Flow API: http://localhost:8000/api/reports/health
echo   - 系统监控: http://localhost:8000/api/reports/metrics
echo.
echo 🔐 n8n登录信息：
echo   - 用户名: admin
echo   - 密码: changeme123
echo.
echo 📝 常用命令：
echo   - 查看日志: docker-compose -f docker-compose.n8n.yml logs -f
echo   - 停止服务: docker-compose -f docker-compose.n8n.yml down
echo   - 重启服务: docker-compose -f docker-compose.n8n.yml restart
echo.
echo 按任意键继续...
pause >nul 