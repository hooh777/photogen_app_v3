#!/bin/bash

# PhotoGen App v3 - Complete Auto-Installer for macOS/Linux
# This installer is designed for USERS who want to:
# - Use PhotoGen for image generation  
# - Have everything installed automatically
# - Not worry about technical details

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Clear screen and show header
clear
echo -e "${GREEN}${BOLD}"
echo "=========================================="
echo "  PhotoGen App v3 - COMPLETE INSTALLER"
echo "=========================================="
echo -e "${NC}"
echo ""
echo "This installer is designed for USERS who want to:"
echo "- Use PhotoGen for image generation"
echo "- Have everything installed automatically"
echo "- Not worry about technical details"
echo ""
echo -e "${YELLOW}DEVELOPERS:${NC} Please use manual installation instead"
echo "See README.md for UV/pip installation instructions"
echo ""
echo "This will automatically:"
echo "- Install Python if needed (via Homebrew on macOS)"
echo "- Detect your system capabilities"  
echo "- Install all dependencies"
echo "- Create launch shortcuts"
echo "- Test everything"
echo ""
echo "No technical knowledge required!"
echo ""

# Prompt for confirmation
read -p "Proceed with user installation? (Y/N): " choice
case "$choice" in
    [Yy]* )
        echo "Starting installation..."
        ;;
    * )
        echo "Installation cancelled."
        exit 0
        ;;
esac

# Function to show progress
show_progress() {
    local message="$1"
    local current="$2"
    local total="$3"
    
    clear
    echo -e "${GREEN}${BOLD}"
    echo "=========================================="
    echo "  PhotoGen App v3 - INSTALLATION"
    echo "=========================================="
    echo -e "${NC}"
    echo ""
    echo "Current Step: $message"
    echo ""
    
    # Calculate progress percentage and bar
    local progress=$((current * 100 / total))
    local bars=$((current * 20 / total))
    local progressbar=""
    
    for ((i=1; i<=bars; i++)); do
        progressbar+="#"
    done
    for ((i=bars+1; i<=20; i++)); do
        progressbar+="-"
    done
    
    echo "Progress: [$progressbar] ${progress}%"
    echo ""
    echo "Step $current of $total"
    echo ""
    sleep 1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    else
        echo -e "${RED}Error: Unsupported operating system${NC}"
        exit 1
    fi
}

# Function to install Homebrew on macOS
install_homebrew() {
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew (package manager for macOS)..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        echo "Homebrew already installed"
    fi
}

# Function to install Python
install_python() {
    local python_version="$1"
    
    if [[ "$OS" == "macOS" ]]; then
        install_homebrew
        echo "Installing Python $python_version via Homebrew..."
        
        if [[ "$python_version" == "3.11"* ]]; then
            brew install python@3.11 || true
            # Create symlinks for python3 and pip3 if needed
            if [[ -f "/opt/homebrew/bin/python3.11" ]]; then
                PYTHON_CMD="/opt/homebrew/bin/python3.11"
                PIP_CMD="/opt/homebrew/bin/pip3.11"
            fi
        elif [[ "$python_version" == "3.12"* ]]; then
            brew install python@3.12 || true
            if [[ -f "/opt/homebrew/bin/python3.12" ]]; then
                PYTHON_CMD="/opt/homebrew/bin/python3.12"
                PIP_CMD="/opt/homebrew/bin/pip3.12"
            fi
        else
            brew install python3 || true
        fi
        
    elif [[ "$OS" == "Linux" ]]; then
        echo "Installing Python $python_version via package manager..."
        
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            sudo apt-get update
            if [[ "$python_version" == "3.11"* ]]; then
                sudo apt-get install -y python3.11 python3.11-pip python3.11-venv
                PYTHON_CMD="python3.11"
                PIP_CMD="pip3.11"
            elif [[ "$python_version" == "3.12"* ]]; then
                sudo apt-get install -y python3.12 python3.12-pip python3.12-venv
                PYTHON_CMD="python3.12"
                PIP_CMD="pip3.12"
            else
                sudo apt-get install -y python3 python3-pip python3-venv
            fi
        elif command -v yum &> /dev/null; then
            # RedHat/CentOS/Fedora
            if [[ "$python_version" == "3.11"* ]]; then
                sudo yum install -y python3.11 python3.11-pip
                PYTHON_CMD="python3.11"
                PIP_CMD="pip3.11"
            elif [[ "$python_version" == "3.12"* ]]; then
                sudo yum install -y python3.12 python3.12-pip
                PYTHON_CMD="python3.12"
                PIP_CMD="pip3.12"
            else
                sudo yum install -y python3 python3-pip
            fi
        else
            echo -e "${RED}Unsupported Linux distribution. Please install Python manually.${NC}"
            manual_python_guide
            return 1
        fi
    fi
    
    # Verify Python installation
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        echo -e "${RED}Python installation failed or not found in PATH${NC}"
        return 1
    fi
    
    echo "Python installed successfully!"
    return 0
}

# Function to show manual Python installation guide
manual_python_guide() {
    echo ""
    echo -e "${YELLOW}Manual Python Installation Guide:${NC}"
    echo "=================================="
    echo ""
    if [[ "$OS" == "macOS" ]]; then
        echo "1. Install Homebrew:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "2. Install Python:"
        echo "   brew install python@3.11"
        echo "3. Restart this installer when done"
    elif [[ "$OS" == "Linux" ]]; then
        echo "1. Update package manager:"
        echo "   sudo apt update  # or sudo yum update"
        echo "2. Install Python:"
        echo "   sudo apt install python3.11 python3.11-pip python3.11-venv"
        echo "   # or sudo yum install python3.11 python3.11-pip"
        echo "3. Restart this installer when done"
    fi
    echo ""
    read -p "Press Enter after installing Python manually..."
    return 1
}

# Function to detect GPU (NVIDIA only for now)
detect_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        if nvidia-smi &> /dev/null; then
            echo "1"  # GPU detected
        else
            echo "0"  # nvidia-smi exists but no GPU
        fi
    else
        echo "0"  # No NVIDIA GPU
    fi
}

# Function to install dependencies with UV
install_with_uv() {
    local install_type="$1"
    
    echo "Installing UV package manager (ultra-fast dependency installation)..."
    $PIP_CMD install uv --quiet --disable-pip-version-check
    
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}Warning: UV installation failed, falling back to pip...${NC}"
        return 1
    fi
    
    echo "UV installed successfully! This will make installation much faster."
    
    if [[ "$install_type" == "GPU" ]]; then
        echo "Installing GPU dependencies with UV..."
        if [[ -f "requirements-gpu.txt" ]]; then
            uv pip install -r requirements-gpu.txt --index-strategy unsafe-best-match
        else
            echo -e "${RED}ERROR: requirements-gpu.txt not found!${NC}"
            return 1
        fi
    else
        echo "Installing CPU dependencies with UV..."
        if [[ -f "requirements-cpu.txt" ]]; then
            uv pip install -r requirements-cpu.txt --index-strategy unsafe-best-match
        else
            echo -e "${RED}ERROR: requirements-cpu.txt not found!${NC}"
            return 1
        fi
    fi
    
    echo "Dependencies installed successfully with UV!"
    return 0
}

# Function to install dependencies with pip
install_with_pip() {
    local install_type="$1"
    
    echo "Using traditional pip installation..."
    $PIP_CMD install --upgrade pip --quiet
    
    if [[ "$install_type" == "GPU" ]]; then
        echo "Installing GPU dependencies with pip..."
        if [[ -f "requirements-gpu.txt" ]]; then
            $PIP_CMD install -r requirements-gpu.txt --no-cache-dir --disable-pip-version-check
        else
            echo -e "${RED}ERROR: requirements-gpu.txt not found!${NC}"
            return 1
        fi
    else
        echo "Installing CPU dependencies with pip..."
        if [[ -f "requirements-cpu.txt" ]]; then
            $PIP_CMD install -r requirements-cpu.txt --no-cache-dir --disable-pip-version-check
        else
            echo -e "${RED}ERROR: requirements-cpu.txt not found!${NC}"
            return 1
        fi
    fi
    
    echo "Dependencies installed successfully with pip!"
    return 0
}

# Function to create launch script
create_launch_script() {
    cat > run-photogen.sh << 'EOF'
#!/bin/bash

# PhotoGen App v3 - Launch Script

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

clear
echo -e "${GREEN}${BOLD}"
echo "=========================================="
echo "   PhotoGen App v3 - Starting..."
echo "=========================================="
echo -e "${NC}"
echo ""
echo "Starting PhotoGen App..."
echo "Please wait while we initialize everything..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo -e "${RED}ERROR: Virtual environment not found!${NC}"
    echo "Please run install.sh first."
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "Loading AI models and starting web server..."
echo "The web interface will open automatically in 5 seconds."
echo ""
echo "Manual URL: http://localhost:7860"
echo ""

# Start Python app in background
python app.py &
APP_PID=$!

# Wait 5 seconds for app to fully start
sleep 5

# Open browser (try different methods based on OS)
echo "Opening PhotoGen in your web browser..."
if command -v open &> /dev/null; then
    # macOS
    open http://localhost:7860
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:7860
elif command -v google-chrome &> /dev/null; then
    # Linux with Chrome
    google-chrome http://localhost:7860
elif command -v firefox &> /dev/null; then
    # Linux with Firefox
    firefox http://localhost:7860
else
    echo "Please open http://localhost:7860 in your web browser manually"
fi

echo ""
echo -e "${GREEN}${BOLD}"
echo "=========================================="
echo "   PhotoGen App v3 - RUNNING"
echo "=========================================="
echo -e "${NC}"
echo ""
echo "- Web Interface: http://localhost:7860"
echo "- Status: Running in background"
echo "- To stop: Press Ctrl+C or close this terminal"
echo ""
echo "App is ready! Check your web browser."
echo ""

# Wait for user to stop the app
wait $APP_PID
EOF

    chmod +x run-photogen.sh
}

# Function to create desktop shortcut (macOS)
create_desktop_shortcut_macos() {
    local app_path="$(pwd)"
    local shortcut_path="$HOME/Desktop/PhotoGen App.command"
    
    cat > "$shortcut_path" << EOF
#!/bin/bash
cd "$app_path"
./run-photogen.sh
EOF
    
    chmod +x "$shortcut_path"
    echo "Desktop shortcut created: PhotoGen App.command"
}

# Function to create desktop shortcut (Linux)
create_desktop_shortcut_linux() {
    local app_path="$(pwd)"
    local shortcut_path="$HOME/Desktop/PhotoGen App.desktop"
    
    cat > "$shortcut_path" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PhotoGen App
Comment=AI Image Generation App
Exec=bash -c "cd '$app_path' && ./run-photogen.sh"
Icon=applications-graphics
Terminal=true
Categories=Graphics;Photography;
EOF
    
    chmod +x "$shortcut_path"
    echo "Desktop shortcut created: PhotoGen App.desktop"
}

# Main installation function
main() {
    detect_os
    
    clear
    echo -e "${GREEN}${BOLD}"
    echo "=========================================="
    echo "  PhotoGen App v3 - INSTALLATION"
    echo "=========================================="
    echo -e "${NC}"
    echo ""
    
    # Step 1: Check Python installation
    show_progress "Checking Python installation" 1 8
    
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        echo -e "${YELLOW}Python not found on your system.${NC}"
        echo "We need to install Python first."
        echo ""
        echo "Choose Python installation option:"
        echo "[1] Auto-install Python 3.11 (Recommended)"
        echo "[2] Auto-install Python 3.12 (Latest)"
        echo "[3] Manual installation guide"
        echo "[4] Skip (if Python is installed elsewhere)"
        echo ""
        
        read -p "Choose option (1-4): " python_choice
        
        case "$python_choice" in
            1)
                echo "Installing Python 3.11..."
                if ! install_python "3.11.9"; then
                    echo -e "${RED}Python installation failed!${NC}"
                    exit 1
                fi
                ;;
            2)
                echo "Installing Python 3.12..."
                if ! install_python "3.12.5"; then
                    echo -e "${RED}Python installation failed!${NC}"
                    exit 1
                fi
                ;;
            3)
                manual_python_guide
                exit 1
                ;;
            4)
                echo "Continuing with existing Python installation..."
                ;;
            *)
                echo "Invalid choice. Defaulting to Python 3.11..."
                if ! install_python "3.11.9"; then
                    echo -e "${RED}Python installation failed!${NC}"
                    exit 1
                fi
                ;;
        esac
    else
        echo "Python found! Continuing with installation..."
    fi
    
    # Verify Python is working
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        echo -e "${RED}ERROR: Python still not found!${NC}"
        echo "Please restart this installer after Python is installed."
        exit 1
    fi
    
    # Get Python version
    PYTHON_VER=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    show_progress "Python $PYTHON_VER ready" 2 8
    
    # Step 2: Detect GPU
    GPU_DETECTED=$(detect_gpu)
    
    if [[ "$GPU_DETECTED" == "1" ]]; then
        INSTALL_TYPE="GPU"
        TYPE_NAME="GPU (Local + API)"
        show_progress "NVIDIA GPU detected - GPU installation selected" 2 8
    else
        INSTALL_TYPE="CPU"
        TYPE_NAME="CPU (API-Only)"
        show_progress "No GPU detected - CPU installation selected" 2 8
    fi
    
    show_progress "Installation plan ready" 3 8
    
    # Step 3: Create virtual environment
    show_progress "Creating virtual environment" 4 8
    
    if [[ -d "venv" ]]; then
        rm -rf venv
    fi
    
    $PYTHON_CMD -m venv venv
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}ERROR: Failed to create virtual environment!${NC}"
        echo "Please check Python installation."
        exit 1
    fi
    
    # Step 4: Activate virtual environment
    show_progress "Activating environment" 5 8
    source venv/bin/activate
    
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}ERROR: Failed to activate virtual environment!${NC}"
        exit 1
    fi
    
    # Update pip and install UV
    $PIP_CMD install --upgrade pip --quiet
    
    # Step 5: Install dependencies
    show_progress "Installing dependencies - this may take 1-3 minutes" 6 8
    
    # Try UV first, fallback to pip
    USE_UV=0
    if install_with_uv "$INSTALL_TYPE"; then
        USE_UV=1
        echo "Dependencies installed successfully with UV (ultra-fast)!"
    else
        echo -e "${YELLOW}UV installation failed, using traditional pip...${NC}"
        if install_with_pip "$INSTALL_TYPE"; then
            echo "Dependencies installed successfully with pip!"
        else
            echo -e "${RED}ERROR: Installation failed!${NC}"
            echo ""
            echo "Common solutions:"
            echo "1. Check internet connection"
            echo "2. Try running with sudo (Linux)"
            echo "3. Try again (temporary server issues)"
            exit 1
        fi
    fi
    
    # Step 6: Create launch scripts
    show_progress "Creating launch shortcuts" 7 8
    create_launch_script
    
    # Create desktop shortcut based on OS
    if [[ "$OS" == "macOS" ]]; then
        create_desktop_shortcut_macos
    else
        create_desktop_shortcut_linux
    fi
    
    # Step 7: Test installation
    show_progress "Testing installation" 8 8
    
    # Test basic imports
    if $PYTHON_CMD -c "import torch, gradio, fastapi" &> /dev/null; then
        TEST_RESULT="Installation test passed"
    else
        TEST_RESULT="Warning: Some dependencies may have issues"
    fi
    
    # Final success message
    clear
    echo -e "${GREEN}${BOLD}"
    echo "=========================================="
    echo "       INSTALLATION COMPLETE!"
    echo "=========================================="
    echo -e "${NC}"
    echo ""
    echo "Installation Progress: [####################] 100%"
    echo ""
    echo "Python Version: $PYTHON_VER"
    echo "Installation Type: $TYPE_NAME"
    echo "Test Result: $TEST_RESULT"
    echo "Operating System: $OS"
    echo ""
    if [[ "$INSTALL_TYPE" == "GPU" ]]; then
        echo "Features Available:"
        echo "- Local FLUX model processing"
        echo "- Privacy-focused generation"  
        echo "- Plus all API features"
    else
        echo "Features Available:"
        echo "- Professional API processing"
        echo "- Works on any hardware"
        echo "- Fast and reliable"
    fi
    echo ""
    echo -e "${CYAN}${BOLD}LAUNCH OPTIONS:${NC}"
    if [[ "$OS" == "macOS" ]]; then
        echo "1. Double-click: \"PhotoGen App.command\" on your Desktop"
    else
        echo "1. Double-click: \"PhotoGen App.desktop\" on your Desktop"
    fi
    echo "2. Run: ./run-photogen.sh (in this folder)"
    echo ""
    echo -e "${YELLOW}${BOLD}FIRST TIME SETUP:${NC}"
    echo "1. Launch PhotoGen App"
    echo "2. Add your API keys in Settings"
    echo "3. Start creating amazing images!"
    echo ""
    read -p "Press Enter to finish..."
}

# Run main installation
main