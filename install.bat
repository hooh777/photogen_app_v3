@echo off
title PhotoGen App - Smart Installation
echo.
echo ========================================
echo    PhotoGen App v3 - Smart Installer
echo ========================================
echo.
echo This script will automatically detect your system
echo and recommend the best installation option.
echo.
pause

echo.
echo [1/3] Detecting your system...
echo.

REM Check for NVIDIA GPU
nvidia-smi >nul 2>&1
set GPU_FOUND=%errorlevel%

REM Check available RAM (rough estimate)
for /f "tokens=2 delims=:" %%i in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do set TOTAL_RAM=%%i
set /a RAM_GB=%TOTAL_RAM:~0,-9%

echo System Analysis:
echo ================

if %GPU_FOUND%==0 (
    echo ✓ NVIDIA GPU detected
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1
    set HAS_GPU=1
) else (
    echo ✗ No NVIDIA GPU detected
    set HAS_GPU=0
)

echo ✓ System RAM: ~%RAM_GB%GB
echo.

echo [2/3] Recommendation:
echo ===================

if %HAS_GPU%==1 (
    if %RAM_GB% GEQ 12 (
        echo 🎯 RECOMMENDED: GPU Installation
        echo.
        echo Your system has:
        echo - NVIDIA GPU for local processing
        echo - Sufficient RAM ^(%RAM_GB%GB^)
        echo.
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
