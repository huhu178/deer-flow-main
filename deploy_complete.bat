@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 Deer-Flow AI研究系统 - 完整部署脚本
echo ========================================
echo.

REM 获取本机IP地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4" ^| find "192.168."') do (
    set LOCAL_IP=%%a
    goto :found_ip
)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4" ^| find "10."') do (
    set LOCAL_IP=%%a
    goto :found_ip
)
set LOCAL_IP=127.0.0.1

:found_ip
set LOCAL_IP=%LOCAL_IP: =%
echo 📍 检测到本机IP地址: %LOCAL_IP%
echo.

REM 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

REM 检查依赖安装
echo 📦 检查Python依赖...
pip list | findstr fastapi >nul
if errorlevel 1 (
    echo 正在安装Python依赖，请稍候...
    pip install -r requirements.txt
)
echo ✅ Python依赖已安装
echo.

REM 创建输出目录
echo 📁 创建输出目录结构...
if not exist "outputs\reports" mkdir outputs\reports
if not exist "outputs\archives" mkdir outputs\archives
if not exist "outputs\logs" mkdir outputs\logs
echo ✅ 目录结构已创建
echo.

REM 生成配置文件
echo ⚙️ 生成配置文件...
echo DEER_FLOW_HOST=%LOCAL_IP% > .env.deployment
echo DEER_FLOW_PORT=8000 >> .env.deployment
echo FRONTEND_PORT=3000 >> .env.deployment
echo REPORT_STORAGE_PATH=./outputs/reports >> .env.deployment
echo LOG_LEVEL=INFO >> .env.deployment
echo ✅ 配置文件已生成
echo.

REM 配置前端环境变量
echo 🌐 配置前端环境...
cd web
echo NEXT_PUBLIC_API_URL=http://%LOCAL_IP%:8000 > .env.local
echo NODE_ENV=production >> .env.local
echo NEXT_PUBLIC_STATIC_WEBSITE_ONLY=false >> .env.local

REM 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Node.js，请先安装Node.js
    cd ..
    pause
    exit /b 1
)

REM 安装前端依赖
if not exist "node_modules" (
    echo 正在安装前端依赖，请稍候...
    npm install
)

REM 构建前端
echo 🔨 构建前端应用...
npm run build
cd ..
echo ✅ 前端构建完成
echo.

REM 生成启动脚本
echo 📝 生成启动脚本...

REM 后端启动脚本
echo @echo off > start_backend.bat
echo echo 🔥 启动Deer-Flow后端服务... >> start_backend.bat
echo echo. >> start_backend.bat
echo echo 后端API地址: http://%LOCAL_IP%:8000 >> start_backend.bat
echo echo 文档地址: http://%LOCAL_IP%:8000/docs >> start_backend.bat
echo echo 报告管理: http://%LOCAL_IP%:8000/api/reports/stats >> start_backend.bat
echo echo n8n接口: http://%LOCAL_IP%:8000/api/reports/webhook/n8n >> start_backend.bat
echo echo. >> start_backend.bat
echo echo 按 Ctrl+C 停止服务 >> start_backend.bat
echo echo. >> start_backend.bat
echo uvicorn src.server.app:app --host 0.0.0.0 --port 8000 --reload >> start_backend.bat

REM 前端启动脚本
echo @echo off > web\start_frontend.bat
echo echo 🌐 启动Deer-Flow前端服务... >> web\start_frontend.bat
echo echo. >> web\start_frontend.bat
echo echo 前端地址: http://%LOCAL_IP%:3000 >> web\start_frontend.bat
echo echo 本地访问: http://localhost:3000 >> web\start_frontend.bat
echo echo. >> web\start_frontend.bat
echo echo 确保后端服务已启动 ^(端口8000^) >> web\start_frontend.bat
echo echo 按 Ctrl+C 停止服务 >> web\start_frontend.bat
echo echo. >> web\start_frontend.bat
echo npm run start >> web\start_frontend.bat

REM 创建完整启动脚本
echo @echo off > start_all_services.bat
echo chcp 65001 ^>nul >> start_all_services.bat
echo echo ========================================== >> start_all_services.bat
echo echo 🚀 Deer-Flow AI研究系统 - 启动所有服务 >> start_all_services.bat
echo echo ========================================== >> start_all_services.bat
echo echo. >> start_all_services.bat
echo echo 📍 系统访问地址: >> start_all_services.bat
echo echo   - 前端界面: http://%LOCAL_IP%:3000 >> start_all_services.bat
echo echo   - 后端API: http://%LOCAL_IP%:8000 >> start_all_services.bat
echo echo   - API文档: http://%LOCAL_IP%:8000/docs >> start_all_services.bat
echo echo   - 报告管理: http://%LOCAL_IP%:8000/api/reports/list >> start_all_services.bat
echo echo. >> start_all_services.bat
echo echo 🔧 n8n集成接口: >> start_all_services.bat
echo echo   - Webhook: http://%LOCAL_IP%:8000/api/reports/webhook/n8n >> start_all_services.bat
echo echo   - 统计API: http://%LOCAL_IP%:8000/api/reports/stats >> start_all_services.bat
echo echo. >> start_all_services.bat
echo echo 正在启动服务，请稍候... >> start_all_services.bat
echo echo. >> start_all_services.bat
echo echo 启动后端服务... >> start_all_services.bat
echo start "Deer-Flow Backend" cmd /k start_backend.bat >> start_all_services.bat
echo timeout /t 5 /nobreak ^>nul >> start_all_services.bat
echo echo 启动前端服务... >> start_all_services.bat
echo start "Deer-Flow Frontend" cmd /k "cd /d web && start_frontend.bat" >> start_all_services.bat
echo echo. >> start_all_services.bat
echo echo ✅ 所有服务已启动！ >> start_all_services.bat
echo echo. >> start_all_services.bat
echo echo 📚 使用指南: >> start_all_services.bat
echo echo   1. 前端界面: 用于交互式AI研究 >> start_all_services.bat
echo echo   2. API接口: 用于n8n等自动化集成 >> start_all_services.bat
echo echo   3. 报告管理: 查看和下载生成的报告 >> start_all_services.bat
echo echo. >> start_all_services.bat
echo echo 📖 详细文档: 查看 N8N_Integration_Guide.md >> start_all_services.bat
echo echo. >> start_all_services.bat
echo pause >> start_all_services.bat

REM 创建测试脚本
echo @echo off > test_api.bat
echo chcp 65001 ^>nul >> test_api.bat
echo echo 🧪 测试API接口... >> test_api.bat
echo echo. >> test_api.bat
echo echo 测试1: 获取系统统计 >> test_api.bat
echo curl -X GET "http://%LOCAL_IP%:8000/api/reports/stats" -H "accept: application/json" >> test_api.bat
echo echo. >> test_api.bat
echo echo 测试2: 列出报告 >> test_api.bat
echo curl -X GET "http://%LOCAL_IP%:8000/api/reports/list?limit=5" -H "accept: application/json" >> test_api.bat
echo echo. >> test_api.bat
echo echo 测试3: 创建测试报告 >> test_api.bat
echo curl -X POST "http://%LOCAL_IP%:8000/api/reports/create" -H "Content-Type: application/json" -d "{\"report_id\":\"test_report\",\"content\":\"# 测试报告\\n\\n这是一个API测试报告。\",\"metadata\":{\"type\":\"test\",\"created_by\":\"deploy_script\"}}" >> test_api.bat
echo echo. >> test_api.bat
echo pause >> test_api.bat

echo ✅ 启动脚本已生成
echo.

REM 显示分享信息
echo 🌐 网络访问信息
echo ========================================
echo 📱 移动设备/其他电脑访问地址:
echo    前端: http://%LOCAL_IP%:3000
echo    API:  http://%LOCAL_IP%:8000
echo.
echo 🔗 n8n集成地址:
echo    http://%LOCAL_IP%:8000/api/reports/webhook/n8n
echo.
echo 📊 管理界面:
echo    报告列表: http://%LOCAL_IP%:8000/api/reports/list
echo    系统统计: http://%LOCAL_IP%:8000/api/reports/stats
echo    API文档:  http://%LOCAL_IP%:8000/docs
echo ========================================
echo.

REM 生成分享链接文件
echo 📱 生成分享链接文件...
echo Deer-Flow AI研究系统 - 访问链接 > 访问链接.txt
echo ================================ >> 访问链接.txt
echo. >> 访问链接.txt
echo 🌐 Web访问地址: >> 访问链接.txt
echo 前端界面: http://%LOCAL_IP%:3000 >> 访问链接.txt
echo 后端API: http://%LOCAL_IP%:8000 >> 访问链接.txt
echo API文档: http://%LOCAL_IP%:8000/docs >> 访问链接.txt
echo. >> 访问链接.txt
echo 📊 管理接口: >> 访问链接.txt
echo 报告列表: http://%LOCAL_IP%:8000/api/reports/list >> 访问链接.txt
echo 系统统计: http://%LOCAL_IP%:8000/api/reports/stats >> 访问链接.txt
echo. >> 访问链接.txt
echo 🔧 n8n集成: >> 访问链接.txt
echo Webhook: http://%LOCAL_IP%:8000/api/reports/webhook/n8n >> 访问链接.txt
echo. >> 访问链接.txt
echo 📋 使用说明: >> 访问链接.txt
echo 1. 双击 start_all_services.bat 启动所有服务 >> 访问链接.txt
echo 2. 等待服务启动完成（约30秒） >> 访问链接.txt
echo 3. 使用上述链接访问系统 >> 访问链接.txt
echo 4. 详细集成指南: N8N_Integration_Guide.md >> 访问链接.txt

echo ✅ 分享链接文件已生成: 访问链接.txt
echo.

echo 🎯 部署完成！接下来的步骤:
echo ================================
echo 1. 双击 'start_all_services.bat' 启动服务
echo 2. 等待服务启动完成（约30秒）
echo 3. 访问 http://%LOCAL_IP%:3000 使用系统
echo 4. 分享 '访问链接.txt' 给其他用户
echo 5. 查看 'N8N_Integration_Guide.md' 了解n8n集成
echo.
echo 🔧 测试API: 双击 'test_api.bat'
echo 📚 使用指南: 查看项目根目录下的文档
echo.

REM 询问是否立即启动
set /p start_now="是否立即启动系统? (Y/N): "
if /i "%start_now%"=="Y" (
    echo.
    echo 🚀 正在启动系统...
    start_all_services.bat
) else (
    echo.
    echo 📝 稍后可以双击 'start_all_services.bat' 启动系统
)

echo.
echo 🎉 部署脚本执行完成！
pause 