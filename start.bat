@echo off
echo.
echo ========================================
echo   AI Role-Playing App - Quick Start
echo ========================================
echo.
echo Checking Python...
python --version
echo.
echo Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama is not running!
    echo Please start Ollama first:
    echo    ollama serve
    echo.
    echo Or download from: https://ollama.com/download
    pause
    exit /b 1
)
echo Ollama is running!
echo.
echo Starting application...
echo.
python run.py
pause
