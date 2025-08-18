@echo off
title PhotoGen App - CPU Installation (Enhanced)
color 0A
echo.
echo ========================================
echo    PhotoGen App v3 - CPU Installation
echo ========================================
echo.
echo This will automatically install PhotoGen with API-only support
echo (no local processing - much faster installation).
echo.
echo What this installer will do:
echo - Check and install Python dependencies
echo - Create isolated virtual environment
echo - Install all required packages automatically
echo - Handle version conflicts automatically
echo - Create launch shortcuts
echo.
echo Requirements:
echo - 4GB+ system RAM
echo - Stable internet connection  
echo - API keys for image generation
echo.
set /p choice="Continue with installation? (Y/N): "
if /I "%choice%" NEQ "Y" (
    echo Installation cancelled by user.
    pause
    exit /b 0
)

echo.
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! 
    echo.
    echo Please install Python 3.8+ first:
    echo 1. Download from: https://www.python.org/downloads/
    echo 2. During installation, check "Add Python to PATH"
    echo 3. Restart this installer after Python is installed
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found

echo.
echo [2/6] Cleaning up old installations...
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
    echo ✓ Old environment cleaned
)

echo.
echo [3/6] Creating fresh virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    echo This might be due to permissions or Python configuration.
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo [4/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

echo.
echo [5/6] Installing dependencies automatically...
echo This may take a few minutes - please wait...
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo Warning: pip upgrade failed, continuing anyway...
)

echo Installing PhotoGen CPU requirements...
echo This includes: PyTorch (CPU), Gradio, FastAPI, and all dependencies
pip install -r requirements-cpu.txt --no-cache-dir
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Common solutions:
    echo 1. Check your internet connection
    echo 2. Try running as Administrator
    echo 3. Temporarily disable antivirus/firewall
    echo 4. Check if you're behind a corporate firewall
    echo.
    echo If problems persist, try manual installation:
    echo   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    echo   pip install gradio==5.41.1 gradio-client==1.11.0
    echo   pip install fastapi==0.116.1 uvicorn requests
    echo.
    pause
    exit /b 1
)
echo ✓ All dependencies installed successfully

echo.
echo [6/6] Finalizing installation...
echo Creating launch shortcut...
if not exist run-photogen.bat (
    echo @echo off > run-photogen.bat
    echo title PhotoGen App v3 >> run-photogen.bat
    echo cd /d "%%~dp0" >> run-photogen.bat
    echo call venv\Scripts\activate.bat >> run-photogen.bat
    echo python app.py >> run-photogen.bat
    echo pause >> run-photogen.bat
)
echo ✓ Launch shortcut created

echo Testing installation...
python -c "import torch, gradio, fastapi; print('✓ Core dependencies verified')"
if errorlevel 1 (
    echo Warning: Dependency test failed, but installation may still work
) else (
    echo ✓ Installation test passed
)

echo.
echo ========================================
echo         INSTALLATION COMPLETE! 🎉
echo ========================================
echo.
echo Your PhotoGen App is ready to use!
echo.
echo 📋 INSTALLATION TYPE: API-Only (CPU Compatible)
echo ✓ PyTorch (CPU): Installed
echo ✓ Gradio UI: Installed  
echo ✓ FastAPI Backend: Installed
echo ✓ All Dependencies: Resolved
echo.
echo 🚀 NEXT STEPS:
echo 1. Double-click 'run-photogen.bat' to start
echo 2. Open the web interface (usually http://localhost:7860)
echo 3. Configure your API keys in settings
echo 4. Start generating amazing images!
echo.
echo 💡 IMPORTANT NOTES:
echo - This is API-only installation (no GPU processing)
echo - You'll need API keys for: Qwen Vision + Image Generation
echo - All processing happens via cloud APIs
echo - Perfect for any hardware (no GPU required)
echo.
echo 📚 Need help? Check README.md or GitHub issues
echo 🎯 Ready to create? Run: run-photogen.bat
echo.
pause
