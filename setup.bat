@echo off
echo ============================================
echo   IDP3 - Adaptive LLM Interview System
echo   Environment Setup
echo ============================================
echo.

REM Check Python is available
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv
IF ERRORLEVEL 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/3] Installing dependencies (this may take a few minutes)...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ============================================
echo   Setup Complete!
echo   To run the interview system:
echo     1. venv\Scripts\activate
echo     2. python app.py
echo ============================================
pause
