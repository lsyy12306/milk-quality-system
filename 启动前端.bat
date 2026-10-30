@echo off
chcp 65001 >nul
echo ============================================
echo   牛奶品质分级系统 - 前端开发模式 (v2.1)
echo ============================================
echo.
echo   说明：后端已可直接托管前端页面（访问 http://localhost:8000）。
echo   本脚本仅用于「开发模式」（热更新 HMR）。日常使用请优先双击
echo   「启动后端.bat」一键启动，无需运行本脚本。
echo.
echo   如需同时运行开发版前端：请先双击「启动后端.bat」，
echo   再双击本脚本，访问 http://localhost:5173。
echo.
pause
cd /d C:\Users\lishi\WorkBuddy\2026-10-15-10-05-25\milk-quality-system\frontend
C:\Users\lishi\.workbuddy\binaries\node\versions\22.22.2\npm.cmd run dev
echo.
echo 前端开发服务已启动，请在浏览器访问: http://localhost:5173
start http://localhost:5173
pause
