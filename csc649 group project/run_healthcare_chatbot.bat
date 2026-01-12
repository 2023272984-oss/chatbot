@echo off
echo 🏥 MediAssist Healthcare Chatbot
echo =================================
echo.
echo Installing dependencies...
pip install google-generativeai pillow --quiet
echo.
echo Starting MediAssist...
python healthcare_chatbot_fixed.py
pause