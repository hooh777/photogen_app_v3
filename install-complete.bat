@echo off
title PhotoGen App - Complete Auto-Installer
color 0A
cls
echo.
echo ==========================================
echo   PhotoGen App v3 - COMPLETE INSTALLER
echo ==========================================
echo.
echo This will automatically:
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

cls
echo.
echo ==========================================
echo   PhotoGen App v3 - INSTALLATION
echo ==========================================
echo.

REM Progress bar function
call :show_progress "Checking Python installation" 1 7

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo.
    echo ==========================================
    echo   PhotoGen App v3 - PYTHON SETUP
    echo ==========================================
    echo.
    echo Python not found on your system.
    echo.
    echo Python Installation Options:
    echo.
    echo [1] Auto-install Python 3.11 (Recommended)
    echo     - Downloads and installs automatically
    echo     - Takes 2-3 minutes
    echo.
    echo [2] Auto-install Python 3.12 (Latest)  
    echo     - Most recent version
    echo     - Takes 2-3 minutes
    echo.
    echo [3] Manual installation
    echo     - I'll guide you to download Python
    echo.
    echo [4] Skip (if Python is installed elsewhere)
    echo.
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
        cls
        echo.
        echo ==========================================
        echo   PhotoGen App v3 - ERROR
        echo ==========================================
        echo.
        echo ERROR: Python still not found!
        echo Please restart this installer after Python is installed.
        echo.
        pause
        exit /b 1
    )
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
call :show_progress "Python %PYTHON_VER% ready" 2 7

REM Check GPU and determine installation type automatically
set GPU_DETECTED=0
nvidia-smi >nul 2>&1
if %errorlevel% == 0 (
    set GPU_DETECTED=1
)

if %GPU_DETECTED% == 1 (
    set INSTALL_TYPE=GPU
    set TYPE_NAME=GPU (Local + API)
    call :show_progress "NVIDIA GPU detected - GPU installation selected" 2 7
) else (
    set INSTALL_TYPE=CPU
    set TYPE_NAME=CPU (API-Only)
    call :show_progress "No GPU detected - CPU installation selected" 2 7
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
timeout /t 1 >nul
call :show_progress "Creating virtual environment" 3 7

if exist venv (
    rmdir /s /q venv >nul 2>&1
)

python -m venv venv >nul 2>&1
if errorlevel 1 (
    cls
    echo.
    echo ==========================================
    echo   PhotoGen App v3 - ERROR
    echo ==========================================
    echo.
    echo ERROR: Failed to create virtual environment!
    echo Try running as Administrator or check Python installation.
    echo.
    pause
    exit /b 1
)

call :show_progress "Activating environment" 4 7
call venv\Scripts\activate.bat >nul 2>&1
if errorlevel 1 (
    cls
    echo.
    echo ==========================================
    echo   PhotoGen App v3 - ERROR
    echo ==========================================
    echo.
    echo ERROR: Failed to activate virtual environment!
    echo.
    pause
    exit /b 1
)

call :show_progress "Installing dependencies - this may take 5-10 minutes" 5 7
python -m pip install --upgrade pip --quiet >nul 2>&1

if "%INSTALL_TYPE%"=="GPU" (
    call :show_progress "Installing GPU dependencies (PyTorch, CUDA, FLUX)" 5 7
    pip install -r requirements-gpu.txt --no-cache-dir >nul 2>&1
) else (
    call :show_progress "Installing CPU dependencies (PyTorch, Gradio)" 5 7
    pip install -r requirements-cpu.txt --no-cache-dir >nul 2>&1
)

if errorlevel 1 (
    cls
    echo.
    echo ==========================================
    echo   PhotoGen App v3 - INSTALLATION FAILED
    echo ==========================================
    echo.
    echo Installation failed!
    echo.
    echo Common solutions:
    echo 1. Check internet connection
    echo 2. Run as Administrator  
    echo 3. Try again (temporary server issues)
    echo.
    pause
    exit /b 1
)

call :show_progress "Creating launch shortcuts" 6 7

REM Create launch shortcut
echo @echo off > run-photogen.bat
echo title PhotoGen App v3 >> run-photogen.bat
echo cd /d "%%~dp0" >> run-photogen.bat
echo call venv\Scripts\activate.bat >> run-photogen.bat
echo python app.py >> run-photogen.bat
echo pause >> run-photogen.bat

call :show_progress "Testing installation" 7 7

REM Test installation
python -c "import torch, gradio, fastapi" >nul 2>&1
if errorlevel 1 (
    set TEST_RESULT=Warning: Some dependencies may have issues
) else (
    set TEST_RESULT=Installation test passed
)

REM Create desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\PhotoGen App.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "%CD%\run-photogen.bat" >> create_shortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> create_shortcut.vbs
echo oLink.Description = "PhotoGen App v3 - AI Image Generation" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs
cscript create_shortcut.vbs >nul 2>&1
del create_shortcut.vbs >nul 2>&1

cls
echo.
echo ==========================================
echo        INSTALLATION COMPLETE!
echo ==========================================
echo.
echo Installation Progress: [████████████████████] 100%%
echo.
echo Python Version: %PYTHON_VER%
echo Installation Type: %TYPE_NAME%
echo Test Result: %TEST_RESULT%
echo.
if "%INSTALL_TYPE%"=="GPU" (
    echo Features Available:
    echo • Local FLUX model processing
    echo • Privacy-focused generation  
    echo • Plus all API features
) else (
    echo Features Available:
    echo • Professional API processing
    echo • Works on any hardware
    echo • Fast and reliable
)
echo.
echo LAUNCH OPTIONS:
echo 1. Double-click: "PhotoGen App" on your Desktop
echo 2. Double-click: run-photogen.bat (in this folder)
echo.
echo FIRST TIME SETUP:
echo 1. Launch PhotoGen App
echo 2. Add your API keys in Settings
echo 3. Start creating amazing images!
echo.
echo Press any key to finish...
pause >nul
exit /b 0

REM Progress bar function
:show_progress
cls
echo.
echo ==========================================
echo   PhotoGen App v3 - INSTALLATION
echo ==========================================
echo.
echo Current Step: %~1
echo.
set /a progress=%~2*100/%~3
set /a bars=%~2*20/%~3
set "progressbar="
for /L %%i in (1,1,%bars%) do set "progressbar=!progressbar!█"
for /L %%i in (%bars%,1,19) do set "progressbar=!progressbar!░"
setlocal enabledelayedexpansion
echo Progress: [!progressbar!] %progress%%%
echo.
echo Step %~2 of %~3
endlocal
timeout /t 2 >nul
goto :eof

:install_python
cls
echo.
echo ==========================================
echo   PhotoGen App v3 - INSTALLING PYTHON
echo ==========================================
echo.
echo Installing Python %~1...
echo.
set PYTHON_VERSION=%~1
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe

echo Downloading Python %PYTHON_VERSION%...
powershell -Command "& {[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python-installer.exe'}" >nul 2>&1

if not exist python-installer.exe (
    echo ERROR: Failed to download Python installer
    echo Falling back to manual installation...
    call :manual_python_guide
    goto :eof
)

echo Download complete
echo Installing Python (this may take a few minutes)...
echo WARNING: Please wait - installer window may appear

python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
if errorlevel 1 (
    echo.
    echo ERROR: Python installation failed or was cancelled
    echo.
    echo Trying alternative installation method...
    python-installer.exe /passive InstallAllUsers=0 PrependPath=1 Include_test=0
    
    if errorlevel 1 (
        echo ERROR: Alternative installation also failed
        echo.
        call :manual_python_guide
        goto :eof
    )
)

echo Python %PYTHON_VERSION% installed successfully
echo Cleaning up installer...
del python-installer.exe >nul 2>&1

echo.
echo IMPORTANT: Restarting installer to use new Python...
echo Press any key to continue with PhotoGen installation...
pause >nul

REM Refresh environment variables
call :refresh_env

goto :eof

:manual_python_guide
echo.
echo Manual Python Installation Guide:
echo ==================================
echo.
echo 1. Open your web browser
echo 2. Go to: https://www.python.org/downloads/
echo 3. Click "Download Python" (latest version)
echo 4. Run the downloaded installer
echo 5. IMPORTANT: Check "Add Python to PATH"
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
