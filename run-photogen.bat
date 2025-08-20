@echo off
title PhotoGen App
echo.
echo ========================================
echo         Starting PhotoGen App v3
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first to set up PhotoGen.
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting PhotoGen App...
echo.
echo ✓ PhotoGen will open in your default web browser
echo ✓ If it doesn't open automatically, use: http://localhost:7860
echo ✓ Alternative URL: http://127.0.0.1:7860
echo ⚠️  IMPORTANT: Do NOT use 0.0.0.0:7860 - browsers can't access it!
echo ✓ Press Ctrl+C in this window to stop the app
echo.
echo ========================================
echo    PhotoGen App is starting...
echo ========================================
echo.

python app.py

echo.
echo PhotoGen App has stopped.
pause
