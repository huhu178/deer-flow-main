@echo off
echo 启动Deer-Flow AI研究系统后端服务...
echo.
echo 后端服务将运行在: http://0.0.0.0:8000
echo 局域网访问地址: http://10.25.222.248:8000
echo.
echo 按 Ctrl+C 停止服务
echo.

cd /d %~dp0
python -m uvicorn src.server.app:app --host 0.0.0.0 --port 8000 --reload

pause 