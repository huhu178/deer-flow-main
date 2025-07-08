@echo off
title 部署DeerFlow前端到Netlify
echo.
echo ========================================
echo    部署DeerFlow前端到Netlify平台
echo ========================================
echo.

echo 🚀 这个脚本将帮助你把前端部署到公网，供团队使用
echo.

REM 检查是否安装了Netlify CLI
echo [1/5] 检查Netlify CLI...
netlify --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Netlify CLI未安装，正在安装...
    npm install -g netlify-cli
    if %errorlevel% neq 0 (
        echo ❌ Netlify CLI安装失败
        echo 💡 请手动运行: npm install -g netlify-cli
        pause
        exit /b 1
    )
    echo ✅ Netlify CLI安装成功
) else (
    echo ✅ Netlify CLI已安装
)

REM 检查依赖
echo.
echo [2/5] 检查项目依赖...
if not exist "node_modules" (
    echo 📦 正在安装依赖...
    pnpm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo ✅ 依赖已存在
)

REM 构建项目
echo.
echo [3/5] 构建项目...
echo 🔧 正在运行: pnpm build
pnpm build
if %errorlevel% neq 0 (
    echo ❌ 项目构建失败
    echo 💡 请检查代码是否有错误
    pause
    exit /b 1
)
echo ✅ 项目构建成功

REM 登录Netlify（如果需要）
echo.
echo [4/5] 检查Netlify登录状态...
netlify status >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 需要登录Netlify...
    echo 💡 浏览器将打开，请登录你的Netlify账户
    netlify login
    if %errorlevel% neq 0 (
        echo ❌ Netlify登录失败
        pause
        exit /b 1
    )
) else (
    echo ✅ 已登录Netlify
)

REM 部署到Netlify
echo.
echo [5/5] 部署到Netlify...
echo 🚀 正在部署，请稍候...

REM 检查是否已有站点配置
if exist ".netlify" (
    netlify deploy --prod --dir=.next
) else (
    echo 🆕 首次部署，正在创建新站点...
    netlify deploy --prod --dir=.next
)

if %errorlevel% neq 0 (
    echo ❌ 部署失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo            🎉 部署成功！
echo ========================================
echo.
echo 📋 接下来：
echo.
echo 1️⃣ 复制上方显示的网址（如: https://xxx.netlify.app）
echo 2️⃣ 把这个网址分享给你的后端同事
echo 3️⃣ 告诉他们在页面右上角点击"API配置"
echo 4️⃣ 让他们输入自己的本地后端地址（如: http://localhost:8000/api）
echo.
echo 💡 提示：
echo    - 每次你更新代码后，重新运行这个脚本即可更新线上版本
echo    - 网址是固定的，同事们不需要重新配置
echo    - 支持HTTPS，安全可靠
echo.

pause 