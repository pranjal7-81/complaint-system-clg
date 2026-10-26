@echo off
title Re-run End-to-End Pipeline
echo ========================================================
echo    Customer Complaint Intelligence - Full Pipeline Runner
echo ========================================================
echo.
python scripts\run_pipeline.py
echo.
echo Pipeline execution finished!
pause
