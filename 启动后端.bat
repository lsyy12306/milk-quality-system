@echo off
chcp 65001 >nul
echo ============================================
echo   牛奶品质分级系统 - 一键启动 (v2.1)
echo   后端服务 + 前端页面（同一端口 8000）
echo ============================================
echo.

set "PY=C:\Users\lishi\WorkBuddy\2026-10-15-10-05-25\milk-quality-system\.venvcn\Scripts\python.exe"
set "BACKEND=C:\Users\lishi\WorkBuddy\2026-10-15-10-05-25\milk-quality-system\backend"
set "DIST=C:\Users\lishi\WorkBuddy\2026-10-15-10-05-25\milk-quality-system\frontend\dist\index.html"

REM 构建产物守卫：后端托管前端，若 dist 缺失会静默退回 API JSON（看似"打不开"）
if not exist "%DIST%" (
    echo [警告] 缺少前端构建产物 frontend\dist\index.html，页面将无法显示。
    echo         请到 frontend 目录执行 npm run build 后重试。
    echo.
    pause
    exit /b 1
)

echo 正在启动后端服务（会弹出一个独立黑窗口）...
start "牛奶品质分级-后端" /D "%BACKEND%" "%PY%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

echo 等待服务启动...
timeout /t 6 >nul

echo 正在打开浏览器...
start http://localhost:8000

echo.
echo ============================================
echo   产品已启动！访问：http://localhost:8000
echo   接口文档：http://localhost:8000/docs
echo.
echo   保持「牛奶品质分级-后端」黑窗口开启即可，关闭它即停止服务。
echo   无需再单独启动前端。
echo ============================================
echo.
pause
