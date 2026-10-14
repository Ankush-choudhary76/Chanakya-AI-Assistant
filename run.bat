@echo off
REM One-click launcher for Windows

echo 🏛️ Starting Chanakya AI Assistant...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.
    pause
    exit /b 1
)

python main.py %*
pause
