@echo off
title PhotoGen App - Smart Installation (Enhanced)
color 0F
echo.
echo ========================================
echo    PhotoGen App v3 - Smart Installer
echo ========================================
echo.
echo 🤖 INTELLIGENT SYSTEM DETECTION
echo This script will automatically:
echo - Detect your hardware capabilities
echo - Check for required software
echo - Recommend the optimal installation
echo - Handle all dependencies automatically
echo - Provide troubleshooting guidance
echo.
echo Compatible with: Windows 10/11, Any CPU, Any RAM
echo GPU Support: NVIDIA GPUs with CUDA (optional)
echo.
set /p choice="Start intelligent detection? (Y/N): "
if /I "%choice%" NEQ "Y" (
    echo Detection cancelled. You can still run:
    echo - install-gpu.bat (for GPU users)
    echo - install-cpu.bat (for CPU-only users)
    pause
    exit /b 0
)

echo.
echo [1/4] Analyzing your system...
echo ================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    set PYTHON_OK=0
    echo ❌ Python: Not found
) else (
    set PYTHON_OK=1
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    echo ✅ Python: %PYTHON_VER%
)

REM Check for NVIDIA GPU and drivers
nvidia-smi >nul 2>&1
if errorlevel 1 (
    set GPU_FOUND=0
    echo ❌ NVIDIA GPU: Not detected or drivers missing
) else (
    set GPU_FOUND=1
    echo ✅ NVIDIA GPU: Detected
    for /f "skip=1 tokens=1,2" %%a in ('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits') do (
        set GPU_NAME=%%a
        set GPU_MEMORY=%%b
        echo    └─ Model: %%a
        echo    └─ VRAM: %%b MB
        goto :gpu_done
    )
    :gpu_done
)

REM Check CUDA installation
nvcc --version >nul 2>&1
if errorlevel 1 (
    set CUDA_OK=0
    echo ❌ CUDA: Not detected
) else (
    set CUDA_OK=1
    for /f "tokens=5" %%i in ('nvcc --version ^| findstr "release"') do (
        set CUDA_VER=%%i
        echo ✅ CUDA: %%i
    )
)

REM Get system RAM (improved detection)
for /f "tokens=2 delims=:" %%i in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do (
    set /a RAM_GB=%%i/1024/1024/1024
)
echo ✅ System RAM: %RAM_GB%GB

REM Check disk space
for /f "tokens=3" %%i in ('dir /-c ^| find "bytes free"') do set FREE_SPACE=%%i
set /a FREE_GB=%FREE_SPACE:~0,-9%
if %FREE_GB% GTR 0 (
    echo ✅ Free Space: ~%FREE_GB%GB
) else (
    echo ⚠️ Free Space: Limited
)

echo.
echo [2/4] Installation recommendation...
echo ====================================

if %PYTHON_OK%==0 (
    echo.
    echo ❌ CRITICAL: Python not found!
    echo.
    echo 📋 Required Action:
    echo 1. Download Python 3.8+ from: https://www.python.org/downloads/
    echo 2. During installation, CHECK "Add Python to PATH"
    echo 3. Restart this installer after Python is ready
    echo.
    pause
    exit /b 1
)

if %GPU_FOUND%==1 (
    if %CUDA_OK%==1 (
        if %RAM_GB% GEQ 12 (
            echo 🚀 OPTIMAL CHOICE: GPU Installation
            echo.
            echo ✨ Your system is perfect for local AI processing:
            echo   • %GPU_NAME%
            echo   • %GPU_MEMORY% MB VRAM
            echo   • %RAM_GB%GB System RAM
            echo   • CUDA %CUDA_VER%
            echo.
            echo 🎯 Benefits:
            echo   • Privacy-focused local processing
            echo   • High-quality image generation
            echo   • No API costs for basic features
            echo   • Plus all cloud API features
            echo.
            set RECOMMENDED=GPU
        ) else (
            echo 🤔 MIXED: GPU Available but Limited RAM
            echo.
            echo Your system:
            echo   • Has GPU: %GPU_NAME%
            echo   • RAM: %RAM_GB%GB (recommended: 12GB+)
            echo.
            echo 📋 Options:
            echo   A) GPU install (may be slower due to RAM limits)
            echo   B) CPU install (recommended for stability)
            echo.
            set RECOMMENDED=CHOICE
        )
    ) else (
        echo ⚠️ GPU DETECTED but CUDA Missing
        echo.
        echo Your system has NVIDIA GPU but CUDA is not installed.
        echo.
        echo 📋 Options:
        echo   A) Install CUDA then run GPU installation
        echo   B) Use CPU installation (faster setup)
        echo.
        echo CUDA Download: https://developer.nvidia.com/cuda-downloads
        echo.
        set RECOMMENDED=CPU
    )
) else (
    echo 💻 PERFECT: CPU Installation Recommended
    echo.
    echo ✨ Your system is ideal for API-based processing:
    echo   • %RAM_GB%GB System RAM
    echo   • Universal compatibility
    echo   • Faster installation
    echo   • Lower resource usage
    echo.
    echo 🎯 Benefits:
    echo   • Works on any hardware
    echo   • Professional-quality results
    echo   • Quick setup and reliable
    echo   • Access to latest AI models
    echo.
    set RECOMMENDED=CPU
)

echo.
echo [3/4] Choose your installation...
echo ==================================

if "%RECOMMENDED%"=="GPU" (
    echo 🚀 Recommended: GPU Installation
    echo.
    set /p choice="Proceed with GPU installation? (Y/N/C for CPU instead): "
    if /I "%choice%"=="Y" (
        set INSTALL_TYPE=GPU
    ) else if /I "%choice%"=="C" (
        set INSTALL_TYPE=CPU
    ) else (
        echo Installation cancelled.
        pause
        exit /b 0
    )
) else if "%RECOMMENDED%"=="CPU" (
    echo 💻 Recommended: CPU Installation
    echo.
    set /p choice="Proceed with CPU installation? (Y/N/G for GPU instead): "
    if /I "%choice%"=="Y" (
        set INSTALL_TYPE=CPU
    ) else if /I "%choice%"=="G" (
        set INSTALL_TYPE=GPU
    ) else (
        echo Installation cancelled.
        pause
        exit /b 0
    )
) else (
    echo Choose installation type:
    echo A) GPU Installation (local processing)
    echo B) CPU Installation (API-only, recommended)
    echo.
    set /p choice="Your choice (A/B): "
    if /I "%choice%"=="A" (
        set INSTALL_TYPE=GPU
    ) else if /I "%choice%"=="B" (
        set INSTALL_TYPE=CPU
    ) else (
        echo Invalid choice. Defaulting to CPU installation.
        set INSTALL_TYPE=CPU
    )
)

echo.
echo [4/4] Starting %INSTALL_TYPE% installation...
echo ==========================================

if "%INSTALL_TYPE%"=="GPU" (
    echo 🚀 Launching GPU installer...
    echo This will take 5-15 minutes depending on your connection.
    echo.
    timeout /t 3 >nul
    call install-gpu.bat
) else (
    echo 💻 Launching CPU installer...
    echo This will take 2-5 minutes depending on your connection.
    echo.
    timeout /t 3 >nul
    call install-cpu.bat
)

echo.
echo ========================================
echo        SMART INSTALLATION COMPLETE!
echo ========================================
echo.
echo 🎉 PhotoGen App v3 is now ready to use!
echo.
echo Your installation type: %INSTALL_TYPE%
if "%INSTALL_TYPE%"=="GPU" (
    echo Features: Local processing + API access
) else (
    echo Features: Professional API-based processing
)
echo.
echo 🚀 Ready to start? Run: run-photogen.bat
echo.
pause
        echo Benefits:
        echo ✓ Full local model processing
        echo ✓ Privacy ^(no data sent to APIs^)
        echo ✓ Unlimited generations ^(no API costs^)
        echo ✓ API support as backup
        echo.
        set RECOMMENDATION=GPU
    ) else (
        echo 🎯 RECOMMENDED: CPU Installation
        echo.
        echo Your system has GPU but limited RAM ^(%RAM_GB%GB^).
        echo Local models require 16GB+ for optimal performance.
        echo.
        echo Benefits:
        echo ✓ Lighter system requirements
        echo ✓ Faster installation
        echo ✓ High-quality API-based generation
        echo.
        set RECOMMENDATION=CPU
    )
) else (
    echo 🎯 RECOMMENDED: CPU Installation
    echo.
    echo Your system:
    echo - No NVIDIA GPU detected
    echo - RAM: %RAM_GB%GB
    echo.
    echo Benefits:
    echo ✓ Perfect for your hardware
    echo ✓ Fast installation
    echo ✓ High-quality API-based generation
    echo.
    set RECOMMENDATION=CPU
)

echo [3/3] Choose Installation:
echo ========================
echo.
echo 1. Install recommended ^(%RECOMMENDATION%^)
echo 2. Install GPU version ^(local + API support^)
echo 3. Install CPU version ^(API-only support^)
echo 4. Exit
echo.
set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" (
    if "%RECOMMENDATION%"=="GPU" (
        echo.
        echo Starting GPU installation...
        call install-gpu.bat
    ) else (
        echo.
        echo Starting CPU installation...
        call install-cpu.bat
    )
) else if "%choice%"=="2" (
    echo.
    echo Starting GPU installation...
    call install-gpu.bat
) else if "%choice%"=="3" (
    echo.
    echo Starting CPU installation...
    call install-cpu.bat
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)
