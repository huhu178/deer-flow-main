@echo off
echo 启动Deer-Flow AI研究系统前端界面...
echo.
echo 前端服务将运行在: http://localhost:3000
echo 局域网访问地址: http://10.25.222.248:3000
echo.
echo 确保后端服务已启动 (端口8000)
echo 按 Ctrl+C 停止服务
echo.

cd /d %~dp0

REM 检查是否安装了依赖
if not exist "node_modules" (
    echo 正在安装前端依赖，请稍候...
    npm install
)

REM 启动开发服务器，允许外部访问
npm run dev -- --hostname 0.0.0.0 --port 3000

pause 