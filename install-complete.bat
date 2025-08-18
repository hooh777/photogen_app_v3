@echo off
title PhotoGen App - Complete Auto-Installer
color 0A
echo.
echo ==========================================
echo   PhotoGen App v3 - COMPLETE INSTALLER
echo ==========================================
echo.
echo 🚀 This will automatically:
echo - Install Python if needed (with your choice)
echo - Detect your system capabilities
echo - Install all dependencies
echo - Create launch shortcuts
echo - Test everything
echo.
echo No technical knowledge required!
echo.
set /p choice="Install PhotoGen completely automatically? (Y/N): "
if /I "%choice%" NEQ "Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo.
echo [1/7] Checking Python installation...
echo ====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found on your system
    echo.
    echo 🐍 Python Installation Options:
    echo.
    echo [1] Auto-install Python 3.11 (Recommended)
    echo     - Downloads and installs automatically
    echo     - Configures PATH correctly
    echo     - Takes 2-3 minutes
    echo.
    echo [2] Auto-install Python 3.12 (Latest)
    echo     - Most recent version
    echo     - Downloads and installs automatically
    echo     - Takes 2-3 minutes
    echo.
    echo [3] Manual installation
    echo     - I'll guide you to download Python
    echo     - You install it yourself
    echo.
    echo [4] Skip (if Python is installed elsewhere)
    echo     - Continue without auto-installation
    echo.
    
    set /p python_choice="Choose option (1-4): "
    
    if "%python_choice%"=="1" (
        call :install_python "3.11.9"
    ) else if "%python_choice%"=="2" (
        call :install_python "3.12.5"
    ) else if "%python_choice%"=="3" (
        call :manual_python_guide
        goto :check_python_again
    ) else if "%python_choice%"=="4" (
        echo Continuing with existing Python installation...
        goto :check_python_again
    ) else (
        echo Invalid choice. Defaulting to Python 3.11...
        call :install_python "3.11.9"
    )
    
    :check_python_again
    python --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ❌ Python still not found!
        echo Please restart this installer after Python is installed.
        echo.
        pause
        exit /b 1
    )
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo ✅ Python %PYTHON_VER% found

echo.
echo [2/7] Checking system capabilities...
echo ===================================

REM Check GPU and determine installation type automatically
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ℹ️ No NVIDIA GPU detected - using CPU installation
    set INSTALL_TYPE=CPU
    set TYPE_NAME=CPU (API-Only)
    echo ✅ CPU installation selected: Lightweight, fast, works on any hardware
) else (
    echo ✅ NVIDIA GPU detected - using GPU installation  
    set INSTALL_TYPE=GPU
    set TYPE_NAME=GPU (Local + API)
    echo ✅ GPU installation selected: Local processing + API features
)

echo.
echo [3/7] Installation plan...
echo ========================
echo Python Version: %PYTHON_VER%
echo Installation Type: %TYPE_NAME%
echo Duration: 2-10 minutes (depending on type and connection)
echo.
timeout /t 3 >nul

echo [4/7] Creating virtual environment...
echo =====================================
if exist venv (
    echo Removing old environment...
    rmdir /s /q venv >nul 2>&1
)

python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment!
    echo.
    echo Try running as Administrator or check Python installation.
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo [5/7] Activating environment...
echo ==============================
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b 1
)
echo ✅ Environment activated

echo.
echo [6/7] Installing dependencies...
echo ==============================
echo This may take several minutes - please wait...
echo.

python -m pip install --upgrade pip --quiet

if "%INSTALL_TYPE%"=="GPU" (
    echo Installing GPU dependencies...
    echo - PyTorch with CUDA support
    echo - Diffusers and Transformers
    echo - FLUX models support
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
    echo 4. Use different installation type
    echo.
    pause
    exit /b 1
)
echo ✅ All dependencies installed

echo.
echo [7/7] Final setup and testing...
echo ===============================
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

REM Create desktop shortcut
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\PhotoGen App.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "%CD%\run-photogen.bat" >> create_shortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> create_shortcut.vbs
echo oLink.Description = "PhotoGen App v3 - AI Image Generation" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs
cscript create_shortcut.vbs >nul 2>&1
del create_shortcut.vbs >nul 2>&1
echo ✅ Desktop shortcut created

echo.
echo ==========================================
echo        INSTALLATION COMPLETE! 🎉
echo ==========================================
echo.
echo Python Version: %PYTHON_VER%
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
echo 🎯 LAUNCH OPTIONS:
echo 1. Double-click: "PhotoGen App" on your Desktop
echo 2. Double-click: run-photogen.bat (in this folder)
echo 3. Run: python app.py (from this folder)
echo.
echo 🔑 FIRST TIME SETUP:
echo 1. Launch PhotoGen App
echo 2. Go to "⚙️ AI Vision / Enhancer Settings"
echo 3. Add your API keys (get free keys from providers)
echo 4. Start creating amazing images!
echo.
echo 📚 Need help? Check README.md
echo 🐛 Issues? Visit: github.com/hooh777/photogen_app_v3/issues
echo.
pause
exit /b 0

:install_python
echo.
echo 🔄 Installing Python %~1...
echo =============================
set PYTHON_VERSION=%~1
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe

echo Downloading Python %PYTHON_VERSION%...
powershell -Command "& {[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python-installer.exe'}"

if not exist python-installer.exe (
    echo ❌ Failed to download Python installer
    echo.
    echo Falling back to manual installation...
    call :manual_python_guide
    goto :eof
)

echo ✅ Download complete
echo Installing Python (this may take a few minutes)...
echo ⚠️ Please wait - installer window may appear

python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
if errorlevel 1 (
    echo.
    echo ❌ Python installation failed or was cancelled
    echo.
    echo Trying alternative installation method...
    python-installer.exe /passive InstallAllUsers=0 PrependPath=1 Include_test=0
    
    if errorlevel 1 (
        echo ❌ Alternative installation also failed
        echo.
        call :manual_python_guide
        goto :eof
    )
)

echo ✅ Python %PYTHON_VERSION% installed successfully
echo Cleaning up installer...
del python-installer.exe >nul 2>&1

echo.
echo ⚠️ IMPORTANT: Restarting installer to use new Python...
echo Press any key to continue with PhotoGen installation...
pause >nul

REM Refresh environment variables
call :refresh_env

goto :eof

:manual_python_guide
echo.
echo 📋 Manual Python Installation Guide:
echo ==================================
echo.
echo 1. Open your web browser
echo 2. Go to: https://www.python.org/downloads/
echo 3. Click "Download Python" (latest version)
echo 4. Run the downloaded installer
echo 5. ✅ IMPORTANT: Check "Add Python to PATH"
echo 6. Click "Install Now"
echo 7. Restart this installer when done
echo.
echo Press any key to open the Python website...
pause >nul
start https://www.python.org/downloads/
echo.
echo After installing Python, restart this installer.
pause
exit /b 1

:refresh_env
REM Refresh PATH without restarting
for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH') do set "user_path=%%b"
for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "system_path=%%b"
set "PATH=%system_path%;%user_path%"
goto :eof
