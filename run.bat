@echo off
title Customer Complaint Intelligence System
echo ========================================================
echo    Customer Complaint Intelligence & Big Data Platform
echo ========================================================
echo.

set "PY_CMD=python"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    ) else (
        echo [ERROR] Python is not installed or not in PATH!
        echo Please install Python 3.10+ from python.org
        pause
        exit /b
    )
)

echo [1/2] Verified Python interpreter:
%PY_CMD% --version
echo.
echo [2/2] Launching Web Application (Streamlit)...
echo The app will open in your default browser at: http://localhost:8501
echo.
echo (Press Ctrl+C in this terminal window anytime to stop the server)
echo ========================================================
%PY_CMD% -m streamlit run app.py
pause
