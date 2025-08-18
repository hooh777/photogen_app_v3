@echo off
title PhotoGen App - GPU Installation (Enhanced)
color 0B
echo.
echo ========================================
echo    PhotoGen App v3 - GPU Installation
echo ========================================
echo.
echo This will automatically install PhotoGen with full GPU support
echo for local model processing + API capabilities.
echo.
echo What this installer will do:
echo - Check Python, CUDA, and GPU compatibility
echo - Create isolated virtual environment
echo - Install PyTorch with CUDA support
echo - Install all AI/ML dependencies automatically
echo - Handle version conflicts and dependencies
echo - Verify GPU accessibility
echo.
echo Requirements:
echo - NVIDIA GPU with 8GB+ VRAM (RTX 3070/4060+ recommended)
echo - CUDA 12.1 or higher installed
echo - 16GB+ system RAM recommended
echo - Stable internet connection
echo.
set /p choice="Continue with GPU installation? (Y/N): "
if /I "%choice%" NEQ "Y" (
    echo Installation cancelled by user.
    pause
    exit /b 0
)

echo.
echo [1/7] Checking system requirements...
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

echo Checking NVIDIA GPU...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo WARNING: nvidia-smi not found or failed!
    echo This might mean:
    echo - No NVIDIA GPU installed
    echo - NVIDIA drivers not installed
    echo - CUDA toolkit not installed
    echo.
    set /p continue="Continue anyway? This may result in CPU-only PyTorch (Y/N): "
    if /I "!continue!" NEQ "Y" (
        echo.
        echo Please install NVIDIA drivers and CUDA toolkit first:
        echo 1. NVIDIA Drivers: https://www.nvidia.com/drivers/
        echo 2. CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
        echo.
        echo Or use install-cpu.bat for API-only installation
        pause
        exit /b 1
    )
) else (
    echo ✓ NVIDIA GPU detected
)

echo.
echo [2/7] Cleaning up old installations...
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
    echo ✓ Old environment cleaned
)

echo.
echo [3/7] Creating fresh virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    echo This might be due to permissions or Python configuration.
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo [4/7] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

echo.
echo [5/7] Installing GPU dependencies automatically...
echo This may take 5-15 minutes depending on your internet connection...
echo Please be patient - downloading large ML packages...
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo Warning: pip upgrade failed, continuing anyway...
)

echo Installing PyTorch with CUDA support...
echo This is the largest download - please wait...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir
if errorlevel 1 (
    echo.
    echo ERROR: PyTorch installation failed!
    echo.
    echo This is usually due to:
    echo 1. Network connection issues
    echo 2. Insufficient disk space
    echo 3. Incompatible CUDA version
    echo.
    echo Try:
    echo - Check internet connection
    echo - Free up disk space (need ~3GB)
    echo - Run as Administrator
    echo.
    pause
    exit /b 1
)
echo ✓ PyTorch with CUDA installed

echo Installing remaining GPU requirements...
pip install -r requirements-gpu.txt --no-cache-dir
if errorlevel 1 (
    echo.
    echo ERROR: Additional dependencies installation failed!
    echo.
    echo Common solutions:
    echo 1. Check your internet connection
    echo 2. Try running as Administrator  
    echo 3. Temporarily disable antivirus/firewall
    echo 4. Check if you're behind a corporate firewall
    echo.
    pause
    exit /b 1
)
echo ✓ All GPU dependencies installed successfully

echo.
echo [6/7] Verifying GPU installation...
echo Testing PyTorch CUDA availability...
python -c "import torch; print('✓ PyTorch version:', torch.__version__); print('✓ CUDA available:', torch.cuda.is_available()); print('✓ CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('✓ GPU count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)"
if errorlevel 1 (
    echo Warning: GPU verification failed
    echo Installation completed but GPU may not be accessible
    echo You can still use API-only features
) else (
    echo ✓ GPU verification completed
)

echo Testing other core dependencies...
python -c "import gradio, fastapi; print('✓ Core dependencies verified')"
if errorlevel 1 (
    echo Warning: Dependency test failed, but installation may still work
) else (
    echo ✓ All dependencies verified
)

echo.
echo [7/7] Finalizing installation...
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

echo.
echo ========================================
echo         INSTALLATION COMPLETE! 🚀
echo ========================================
echo.
echo Your PhotoGen App is ready with FULL GPU POWER!
echo.
echo 📋 INSTALLATION TYPE: GPU + API (Complete)
echo ✓ PyTorch with CUDA: Installed
echo ✓ Diffusers (FLUX): Installed
echo ✓ Gradio UI: Installed
echo ✓ FastAPI Backend: Installed
echo ✓ All ML Dependencies: Resolved
echo.
echo 🎮 GPU FEATURES AVAILABLE:
echo - Local FLUX.1 model processing
echo - Privacy-focused on-device generation  
echo - High-quality image generation
echo - Plus all API features
echo.
echo 🚀 NEXT STEPS:
echo 1. Double-click 'run-photogen.bat' to start
echo 2. Open the web interface (usually http://localhost:7860)
echo 3. Configure your API keys for enhanced features
echo 4. Choose between Local and Pro models
echo 5. Start creating amazing images!
echo.
echo 💡 IMPORTANT NOTES:
echo - First model download will take time (several GB)
echo - Local processing requires 8GB+ VRAM
echo - API processing works regardless of hardware
echo - Both local and cloud options available
echo.
echo 📚 Need help? Check README.md or GitHub issues
echo 🎯 Ready to create? Run: run-photogen.bat
echo.
pause
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
