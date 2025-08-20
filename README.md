# PhotoGen App v3

> **🎯 Quick Navigation:**  
> **👥 Just want to use PhotoGen?** → [For Users](#👥-for-users-just-want-to-use-photogen)  
> **🛠️ Want to develop/modify code?** → [For Developers](#🛠️-for-developers-want-to-modifycontribute)

## Key Features

### **Multi-Modal Image Generation**
- **Text-to-Image (T2I)**: Create stunning images from text descriptions
- **Image-to-Image (I2I)**: Transform and enhance existing images
- **Multi-Image Composition**: Combine up to 10 images into cohesive scenes

### **AI-Powered Workflow**
- **FLUX.1 Kontext Integration**: State-of-the-art image generation models
- **Smart Prompt Generation**: AI vision analysis with Qwen-VL-Max
- **Interactive Canvas**: Click and select areas for targeted editing
- **Contextual Understanding**: Intelligent object placement and scene composition

### **Flexible Processing Options**
- **Local Processing**: Privacy-focused on-device generation (GPU with CUDA required)
- **Pro API Integration**: High-quality cloud processing (works on any hardware)
- **CPU-Compatible**: Full API functionality without GPU requirements
- **Smart Detection**: Automatic hardware detection and optimization

## Quick Start

---

## 👥 For Users (Just Want to Use PhotoGen)

**If you just want to use PhotoGen for image generation, this is for you!**

### **Windows Installation (Recommended)**

```bash
# 1. Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# 2. Double-click or run the installer
install-complete.bat
```

**What the installer does automatically:**
- ✅ **Installs Python** if you don't have it (your choice of version)
- ✅ **Detects your hardware** (NVIDIA GPU or CPU-only)
- ✅ **Installs everything** needed for PhotoGen
- ✅ **Creates shortcuts** for easy launching
- ✅ **Tests installation** to make sure it works

**That's it! No technical knowledge required.**

### **After Installation:**
- **Double-click** the desktop shortcut, OR
- **Double-click** `run-photogen.bat` in the PhotoGen folder
- **Web interface opens automatically** at http://localhost:7860

---

## 🛠️ For Developers (Want to Modify/Contribute)

**If you want to develop, modify, or contribute to PhotoGen:**

### **Method 1: UV (Recommended - Much Faster)**

```bash
# Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# Install UV if not already installed.
pip install uv

## Or follow the guide to install it
https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2


# Create virtual environment
uv venv venv
call venv\Scripts\activate.bat  # Windows
# source venv/bin/activate      # Linux/macOS

# Choose your installation type:

# GPU development (local + API processing)
uv pip install -e ".[gpu]"

# CPU development (API-only)  
uv pip install -e "."

# Full development (includes testing/linting tools)
uv pip install -e ".[dev]"

# Everything (GPU + all dev tools)
uv pip install -e ".[all]"

# Run PhotoGen
python app.py
```

**UV Benefits for Developers:**
- ⚡ **10-100x faster** dependency installation (2-3 min vs 8-12 min)
- 🔧 **Better dependency resolution** - handles conflicts intelligently  
- 💾 **Intelligent caching** - reuses downloads across projects
- 🚀 **Modern Python tooling** built for development workflows

### **Method 2: pip (Traditional Fallback)**

```bash
# Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat  # Windows
# source venv/bin/activate      # Linux/macOS

# GPU development
pip install -r requirements-gpu.txt

# OR CPU development  
pip install -r requirements-cpu.txt

# Run PhotoGen
python app.py
```

### **Developer Resources:**
- 📖 **[DEVELOPER_GUIDE_UV.md](DEVELOPER_GUIDE_UV.md)** - Complete UV usage guide
- 🧪 **Testing**: `pytest` (if installed with `[dev]` extras)
- 🎨 **Code formatting**: `black .` (if installed with `[dev]` extras)
- 🔍 **Linting**: `flake8 .` (if installed with `[dev]` extras)

---

## Installation Files Overview

### **Files for Users (Simple .bat Installation)**
- **`install-complete.bat`**: **THE installer for users**
  - Only installation method recommended for users
  - Handles Python installation, dependency management, shortcuts
  - No technical knowledge required

### **Files for Developers (Manual Installation)**

**Modern Approach (Recommended):**
- **`pyproject.toml`**: Modern Python project configuration
  - `uv pip install -e ".[gpu]"` - GPU development
  - `uv pip install -e ".[dev]"` - Development tools  
  - `uv pip install -e ".[all]"` - Everything
  - Contains all dependencies - no separate requirements files needed

**Traditional pip Approach (Fallback):**
- **`requirements-gpu.txt`**: GPU dependencies for traditional pip
- **`requirements-cpu.txt`**: CPU dependencies for traditional pip

**Developer Resources:**
- **`DEVELOPER_GUIDE_UV.md`**: Complete UV usage guide

### First Launch Setup

1. **Launch the app**: Run `python app.py` or run-photogen.bat, and open the provided URL
2. **Configure API Keys**: 
   - Go to "AI Vision / Enhancer Settings" for vision analysis
   - Go to "Pro Model Settings" for image generation APIs
3. **Start Creating**: Upload images and begin generating!

## System Requirements

*These requirements apply whether you use the simple `.bat` installer (users) or manual installation (developers)*

### **GPU Setup (Local + API Processing)**
- **OS**: Windows 10/11, Linux, macOS
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 3070/4060 or better recommended)
- **CUDA**: Version 12.1 or higher (automatically handled by installer)
- **RAM**: 16GB+ system RAM recommended
- **Storage**: 10GB+ free space for AI models
- **Features**: Full local processing + all API capabilities

**Perfect for:** Privacy-focused workflows, high-volume generation, offline usage

### **CPU Setup (API-Only Processing)**
- **OS**: Windows 10/11, Linux, macOS  
- **Hardware**: Any CPU (GPU not required)
- **RAM**: 4GB+ system RAM recommended
- **Storage**: 2GB+ free space
- **Internet**: Stable connection for API calls
- **Features**: Full AI vision analysis and image generation via APIs

**Perfect for:** Laptops, older computers, budget setups, cloud instances

## API Configuration

### **Required API Keys**

#### **AI Vision Analysis (Required)**
- **Qwen-VL-Max (Alibaba Cloud)**: For smart prompt generation
  - Get key: [Alibaba Cloud Console](https://dashscope.console.aliyun.com/)
  - Used for: Image analysis and prompt enhancement

#### **Image Generation APIs (Choose One)**
- **Black Forest Labs**: Premium FLUX Pro API
  - Get key: [Black Forest Labs](https://api.bfl.ml/)
  - Quality: Highest, Speed: Fast
  
- **GRS AI**: Cost-effective FLUX alternative
  - Get key: [GRS AI](https://api.grsai.com/)
  - Quality: High, Speed: Fast, Cost: Lower

### **API Key Security**
- All API keys are encrypted using Fernet encryption
- Keys are stored locally in encrypted format
- Never transmitted in plain text

## How to Use PhotoGen

### **Basic Workflow**

1. **Step 1: Upload Images**
   - Drag & drop or browse to upload up to 10 images
   - Supported formats: PNG, JPG, JPEG, WEBP

2. **Step 2: Compose Your Scene**
   - Select images from the gallery to work with
   - Click areas on the Interactive Canvas for targeted editing
   - Use AI-generated prompts or write your own

3. **Step 3: Generate**
   - Choose between Local or Pro API processing
   - Adjust advanced settings if needed
   - Click "Generate" and watch the magic happen!

### **Advanced Features**

#### **Multi-Image Composition**
- Upload multiple images (people, objects, backgrounds)
- Select which image serves as the background
- Use AI to intelligently place objects in scenes

#### **Smart Prompt Generation**
- AI analyzes your images and selection areas
- Generates contextual prompts automatically  
- Understands spatial relationships and object placement

#### **Interactive Canvas**
- Click and drag to select specific areas for editing
- Visual feedback with selection boxes
- Reset selections anytime

## Configuration

### **Model Selection**
- **Local**: Uses downloaded FLUX.1 models (GPU required)
- **Pro (Black Forest Labs)**: Premium cloud API
- **Pro (GRS AI)**: Cost-effective cloud alternative

### **Image Dimensions (Not available currently)** 
- Match Input: Uses source image dimensions
- Standard ratios: 1:1, 16:9, 9:16, 4:3, 3:4
- Automatic optimization for quality and performance

### **Advanced Settings**
- **Inference Steps**: 1-50 (higher = better quality, slower)
- **Guidance Scale**: 0-10 (higher = more prompt adherence)

## Troubleshooting

### **Common Issues**

#### **Quick Solutions (Use the Complete Installer)**
```bash
# For complete zero-setup installation:
install-complete.bat   # Handles everything automatically
```

#### **Installation Problems**
The enhanced installers now handle most issues automatically:

**Issue**: `Cannot import FluxKontextPipeline` or similar import errors
**Solution**: The complete installer prevents this automatically
```bash
# The complete installer prevents this by:
# 1. Installing Python if needed
# 2. Detecting your hardware automatically (GPU vs CPU)
# 3. Installing correct dependencies for your system
# 4. Testing installation before completion
install-complete.bat
```

**Issue**: "Python not found" or "Python not installed"
**Solution**: The complete installer handles Python installation
```bash
# Complete installer will:
# - Check if Python is installed
# - Offer to auto-install Python 3.11 or 3.12
# - Guide manual installation if needed
# - Continue with PhotoGen setup automatically
install-complete.bat
```

**Issue**: Version conflicts (Gradio, FastAPI, PyTorch)
**Solution**: Installers now use pinned, tested versions
```bash
# Fixed versions in requirements:
# gradio==5.41.1, fastapi==0.116.1, etc.
# No more dependency conflicts!
```

**Issue**: CUDA/GPU detection problems
**Solution**: Enhanced GPU verification and fallback
```bash
# The complete installer now:
# - Checks NVIDIA drivers automatically
# - Verifies CUDA installation  
# - Tests GPU accessibility
# - Provides specific error guidance
# - Falls back to CPU installation if needed
install-complete.bat
```

#### **Manual Troubleshooting (If Complete Installer Fails)**
```bash
# Check CUDA installation (for GPU users)
nvidia-smi

# Manual PyTorch installation with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Check your system type
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

#### **API Connection Issues**
- Verify API keys are correctly entered and saved
- Check internet connection and firewall settings
- Ensure API quotas/credits are available  
- Try switching between API providers (Black Forest Labs vs GRS AI)

#### **Performance Optimization**
- **CPU Users**: API-only mode provides best performance and reliability
- **GPU Users**: Ensure CUDA drivers and toolkit are up to date
- **All Users**: Close unnecessary applications before generation
- **Pro Tip**: Cloud API processing is often faster and more reliable than local

### **Getting Help**
- **Installation Issues**: Re-run `install-complete.bat` - it handles most problems automatically
- **GitHub Issues**: Check [Issues](https://github.com/hooh777/photogen_app_v3/issues) for known problems
- **Configuration**: Review `config.yaml` for model and API settings
- **Debug Mode**: Enable debug logging in app settings for detailed error information
- **Community**: Join discussions in the GitHub repository

## Technical Details

### **Architecture**
- **Frontend**: Gradio-based web interface
- **Backend**: Python with FastAPI/Uvicorn
- **Models**: FLUX.1 Kontext for image generation
- **Vision**: Qwen-VL-Max for image analysis
- **Security**: Fernet encryption for API keys

### **File Structure**
```
photogen_app_v3/
├── app.py                    # Main application entry
├── config.yaml              # Model and API configuration
├── requirements-gpu.txt      # GPU installation dependencies
├── requirements-cpu.txt      # CPU-only dependencies
├── install-complete.bat      # Complete one-click installer (Windows)
├── install.sh               # Installation script (Linux/macOS)
├── run-photogen.bat         # Launch script (created by installer)
├── api_keys.json.enc        # Encrypted API keys storage
├── secret.key               # Encryption key for API storage
├── test_cpu_compatibility.py # CPU compatibility test script
├── verify_installation.py   # Installation verification script
├── .env.example             # Environment variables template
├── core/                    # Core application modules
│   ├── __init__.py
│   ├── constants.py         # Application constants
│   ├── enhancer.py          # Image enhancement logic
│   ├── generator.py         # Image generation logic (CPU/GPU compatible)
│   ├── secure_storage.py    # Encrypted API key management
│   ├── ui.py               # User interface components
│   ├── utils.py            # Utility functions
│   ├── vision_streamlined.py # AI vision analysis
│   └── handlers/           # Event handling and workflows
│       ├── auto_prompt_manager.py  # Automatic prompt generation
│       ├── canvas_manager.py       # Interactive canvas management
│       ├── generation_manager.py   # Image generation coordination
│       ├── i2i_handler.py          # Image-to-image processing
│       ├── i2i_handler_new.py      # Enhanced I2I processing
│       └── state_manager.py        # Application state management
├── test_images/             # Test images and reference materials
├── outputs/                # Generated images storage
├── workflow diagram/       # Technical documentation and diagrams
└── venv/                   # Virtual environment (created by installer)
```



