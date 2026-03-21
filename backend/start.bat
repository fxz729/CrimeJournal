@echo off
chcp 65001 >nul
title CrimeJournal - Backend Server

echo ================================
echo   CrimeJournal Backend Launcher
echo ================================
echo.

cd /d "%~dp0"

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
)

echo [2/3] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查.env文件
if not exist ".env" (
    echo [WARNING] .env 文件不存在！
    echo 请复制 .env.example 为 .env 并填入你的API密钥
    echo 详见: API_KEYS_GUIDE.md
    echo.
    pause
    exit /b 1
)

REM 检查关键配置
python -c "from app.config import settings; print('Config loaded OK')" 2>nul
if errorlevel 1 (
    echo [ERROR] 配置加载失败，请检查.env文件
    pause
    exit /b 1
)

echo [3/3] 启动服务器...
echo.
echo 访问地址:
echo   - API:     http://localhost:8000
echo   - Docs:    http://localhost:8000/docs
echo   - Health:  http://localhost:8000/health
echo.
echo 按 Ctrl+C 停止服务器
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
