@echo off
title PhotoGen App - Automatic Installation
color 0A
echo.
echo ========================================
echo   PhotoGen App v3 - AUTO INSTALLER
echo ========================================
echo.
echo 🤖 This will automatically:
echo - Detect your system capabilities
echo - Install everything needed
echo - Create launch shortcuts
echo - Test the installation
echo.
echo No more multiple prompts - just one decision!
echo.
set /p choice="Install PhotoGen automatically? (Y/N): "
if /I "%choice%" NEQ "Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo.
echo [1/6] Checking system requirements...
echo ====================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo.
    echo 📋 Please install Python first:
    echo 1. Download from: https://www.python.org/downloads/
    echo 2. Check "Add Python to PATH" during installation
    echo 3. Restart this installer
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo ✅ Python %PYTHON_VER% found

REM Check GPU and determine installation type
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ℹ️ No NVIDIA GPU detected - using CPU installation
    set INSTALL_TYPE=CPU
    set TYPE_NAME=CPU (API-Only)
) else (
    echo ✅ NVIDIA GPU detected - using GPU installation
    set INSTALL_TYPE=GPU
    set TYPE_NAME=GPU (Local + API)
)

echo.
echo [2/6] Installation plan...
echo ========================
echo Installation Type: %TYPE_NAME%
echo Duration: 2-10 minutes (depending on type and connection)
echo.
timeout /t 3 >nul

echo [3/6] Creating virtual environment...
echo =====================================
if exist venv (
    echo Removing old environment...
    rmdir /s /q venv >nul 2>&1
)

python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment!
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo [4/6] Activating environment...
echo ==============================
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b 1
)
echo ✅ Environment activated

echo.
echo [5/6] Installing dependencies...
echo ==============================
echo This may take several minutes - please wait...
echo.

python -m pip install --upgrade pip --quiet

if "%INSTALL_TYPE%"=="GPU" (
    echo Installing GPU dependencies...
    echo - PyTorch with CUDA support
    echo - Diffusers and Transformers
    echo - All other requirements
    echo.
    pip install -r requirements-gpu.txt --no-cache-dir
) else (
    echo Installing CPU dependencies...
    echo - PyTorch (CPU version)
    echo - Gradio and FastAPI
    echo - All other requirements
    echo.
    pip install -r requirements-cpu.txt --no-cache-dir
)

if errorlevel 1 (
    echo.
    echo ❌ Installation failed!
    echo.
    echo Common solutions:
    echo 1. Check internet connection
    echo 2. Run as Administrator
    echo 3. Try again (temporary server issues)
    echo.
    pause
    exit /b 1
)
echo ✅ All dependencies installed

echo.
echo [6/6] Final setup...
echo ==================
echo Creating launch shortcut...
echo @echo off > run-photogen.bat
echo title PhotoGen App v3 >> run-photogen.bat
echo cd /d "%%~dp0" >> run-photogen.bat
echo call venv\Scripts\activate.bat >> run-photogen.bat
echo python app.py >> run-photogen.bat
echo pause >> run-photogen.bat

echo ✅ Launch shortcut created

echo Testing installation...
python -c "import torch, gradio, fastapi; print('✅ Core dependencies working')"
if errorlevel 1 (
    echo ⚠️ Warning: Some dependencies may have issues, but installation completed
) else (
    echo ✅ Installation test passed
)

if "%INSTALL_TYPE%"=="GPU" (
    echo Testing GPU capabilities...
    python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
)

echo.
echo ========================================
echo        INSTALLATION COMPLETE! 🎉
echo ========================================
echo.
echo Installation Type: %TYPE_NAME%
echo.
if "%INSTALL_TYPE%"=="GPU" (
    echo 🚀 GPU Features Available:
    echo - Local FLUX model processing
    echo - Privacy-focused generation
    echo - Plus all API features
) else (
    echo 💻 CPU Features Available:
    echo - Professional API processing
    echo - Works on any hardware
    echo - Fast and reliable
)
echo.
echo 🎯 NEXT STEPS:
echo 1. Double-click: run-photogen.bat
echo 2. Configure API keys in the web interface
echo 3. Start creating amazing images!
echo.
echo 📚 Need help? Check README.md
echo.
pause
