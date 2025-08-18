@echo off
title PhotoGen App - GPU Installation
echo.
echo ========================================
echo    PhotoGen App v3 - GPU Installation
echo ========================================
echo.
echo This will install PhotoGen with full GPU support
echo for local model processing + API capabilities.
echo.
echo Requirements:
echo - NVIDIA GPU with 8GB+ VRAM
echo - CUDA 12.1 or higher
echo - 16GB+ system RAM
echo.
pause

echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo ✓ Virtual environment already exists
) else (
    python -m venv venv
    echo ✓ Virtual environment created
)

echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

echo.
echo [4/5] Installing GPU requirements...
echo This may take 5-10 minutes depending on your internet connection...
pip install --upgrade pip
pip install -r requirements-gpu.txt
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo ✓ GPU requirements installed successfully

echo.
echo [5/5] Installation complete!
echo.
echo ========================================
echo           INSTALLATION SUCCESS!
echo ========================================
echo.
echo Your PhotoGen App is ready to use!
echo.
echo Next steps:
echo 1. Double-click 'run-photogen.bat' to start the app
echo 2. Configure your API keys in the web interface
echo 3. Start creating amazing images!
echo.
echo For help: Check README.md or visit the GitHub repository
echo.
pause
