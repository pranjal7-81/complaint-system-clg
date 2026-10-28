@echo off
title Re-run End-to-End Pipeline
echo ========================================================
echo    Customer Complaint Intelligence - Full Pipeline Runner
echo ========================================================
echo.

set "PY_CMD=python"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    ) else (
        echo [ERROR] Python not found.
        pause
        exit /b
    )
)

%PY_CMD% scripts\run_pipeline.py
echo.
echo Pipeline execution finished!
pause
