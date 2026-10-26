@echo off
title Customer Complaint Intelligence System
echo ========================================================
echo    Customer Complaint Intelligence & Big Data Platform
echo ========================================================
echo.
echo [1/2] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b
)
echo.
echo [2/2] Launching Web Application (Streamlit)...
echo The app will open in your default browser at: http://localhost:8501
echo.
echo (Press Ctrl+C in this terminal window anytime to stop the server)
echo ========================================================
python -m streamlit run app.py
pause
