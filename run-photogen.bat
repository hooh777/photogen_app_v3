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
echo ✓ Look for the local URL (usually http://127.0.0.1:7860)
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
