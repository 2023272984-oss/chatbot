@echo off
echo ========================================
echo 🏥 MediAssist Healthcare Chatbot
echo ========================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Please install Python from: https://python.org
    pause
    exit
)
echo.
echo Installing required packages...
pip install google-generativeai --quiet
echo.
echo Starting MediAssist...
python healthcare_chatbot_fixed.py
pause