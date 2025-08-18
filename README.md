# 📸 PhotoGen App v3

**Advanced AI-Powered Image Generation & Editing Platform**

PhotoGen is a sophisticated image creation and editing application that combines multiple AI technologies to help you generate, edit, and compose high-quality images using both local processing and cloud APIs.

## 🌟 Key Features

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

## 🆕 What's New in v3

### **Smart Installation System**
- **🤖 Intelligent Detection**: Automatically analyzes CPU, GPU, CUDA, RAM, and disk space
- **� Hardware Analysis**: Detailed compatibility assessment with recommendations
- **🔧 Automatic Dependencies**: Resolves version conflicts and handles all packages
- **🛡️ Error Prevention**: Comprehensive checks with actionable error solutions
- **📦 Dual Requirements**: Optimized `requirements-gpu.txt` and `requirements-cpu.txt`
- **⚡ One-Click Setup**: Complete automation from detection to launch shortcuts
- **🚀 Launch Scripts**: Ready-to-use `run-photogen.bat` created automatically

### **Enhanced CPU Compatibility**
- **💻 Universal Support**: Works on any hardware - no GPU required
- **🌐 Full API Access**: Complete feature set via cloud processing
- **⚡ Lightweight Install**: Minimal dependencies for CPU-only users
- **🛡️ Graceful Fallbacks**: Smart CUDA detection prevents compatibility issues
- **📡 API-First Design**: Optimized for cloud processing with local processing as bonus

### **Improved User Experience**
- **🎯 Streamlined UI**: Better button placement and cleaner interface
- **📱 Responsive Design**: Optimized layout for all screen sizes
- **💬 Clear Messaging**: Helpful error messages and status indicators
- **⚙️ Smart Defaults**: Optimized settings for better out-of-box experience

## 🚀 Quick Start

### Installation Options

#### **🚀 One-Click Installation (Windows Users)**
*Complete automated setup - installs Python if needed + everything else*

```bash
# Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# Run the complete installer (handles everything automatically)
install-complete.bat
```

**🧠 What the Complete Installer Does:**
- **Python Check**: Automatically installs Python if missing (your choice of version)
- **Smart Detection**: Detects NVIDIA GPU automatically
- **Automatic Setup**: If no GPU → CPU installation, If GPU → GPU installation
- **Full Installation**: Handles virtual environment, dependencies, configuration
- **Desktop Integration**: Creates desktop shortcut and launch scripts
- **Complete Testing**: Verifies everything works before finishing

**🚀 Python Installation Options:**
- **Auto-install Python 3.11** (Recommended - most compatible)
- **Auto-install Python 3.12** (Latest version)
- **Manual guidance** (opens Python website with instructions)
- **Skip** (if Python installed elsewhere)

**🎯 Installation Logic:**
- **No NVIDIA GPU detected** → Lightweight CPU installation (API-only, 2 minutes)
- **NVIDIA GPU detected** → Full GPU installation (Local processing + API, 5-10 minutes)

**🎯 Installation Features:**
- **Hardware Detection**: Automatic GPU/CUDA capability analysis
- **Dependency Management**: Resolves version conflicts automatically  
- **Progress Tracking**: Real-time feedback during installation
- **Error Handling**: Comprehensive troubleshooting with solutions
- **Verification Testing**: Confirms all components work correctly

**🔧 Manual Installation (Advanced Users)**
*For users who prefer manual control or non-Windows systems*

##### **Option 1: GPU Users (Local + API Support)**
*For users with NVIDIA GPUs who want full local processing capabilities*

```bash
# Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install GPU requirements
pip install -r requirements-gpu.txt

# Run the application
python app.py
```

##### **Option 2: CPU Users (API-Only Support)**
*For users without GPU who want to use API services only*

```bash
# Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install CPU requirements (much faster installation)
pip install -r requirements-cpu.txt

# Run the application
python app.py
```

### First Launch Setup

1. **Launch the app**: Run `python app.py` and open the provided URL
2. **Configure API Keys**: 
   - Go to "⚙️ AI Vision / Enhancer Settings" for vision analysis
   - Go to "⚙️ Pro Model Settings" for image generation APIs
3. **Start Creating**: Upload images and begin generating!

## 📋 System Requirements

### **GPU Installation (Local + API)**
- **OS**: Windows 10/11, Linux, macOS
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 3070/4060 or better recommended)
- **CUDA**: Version 12.1 or higher
- **RAM**: 16GB+ system RAM recommended
- **Storage**: 10GB+ free space for models
- **Features**: Full local processing + all API capabilities

**✅ Perfect for:** Power users, privacy-focused workflows, high-volume generation

### **CPU Installation (API-Only)**
- **OS**: Windows 10/11, Linux, macOS  
- **Hardware**: Any CPU (GPU not required)
- **RAM**: 4GB+ system RAM recommended
- **Storage**: 2GB+ free space
- **Internet**: Stable connection for API calls
- **Features**: Full AI vision analysis and image generation via APIs

**✅ Perfect for:** Laptops, older computers, cloud instances, users prioritizing cost-effectiveness

## 🔑 API Configuration

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

## 🎨 How to Use PhotoGen

### **Basic Workflow**

1. **📸 Step 1: Upload Images**
   - Drag & drop or browse to upload up to 10 images
   - Supported formats: PNG, JPG, JPEG, WEBP

2. **✍️ Step 2: Compose Your Scene**
   - Select images from the gallery to work with
   - Click areas on the Interactive Canvas for targeted editing
   - Use AI-generated prompts or write your own

3. **🚀 Step 3: Generate**
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

## ⚙️ Configuration

### **Model Selection**
- **Local**: Uses downloaded FLUX.1 models (GPU required)
- **Pro (Black Forest Labs)**: Premium cloud API
- **Pro (GRS AI)**: Cost-effective cloud alternative

### **Image Dimensions**
- Match Input: Uses source image dimensions
- Standard ratios: 1:1, 16:9, 9:16, 4:3, 3:4
- Automatic optimization for quality and performance

### **Advanced Settings**
- **Inference Steps**: 1-50 (higher = better quality, slower)
- **Guidance Scale**: 0-10 (higher = more prompt adherence)

## 🔧 Troubleshooting

### **Common Issues**

#### **🚀 Quick Solutions (Use the Complete Installer)**
```bash
# For complete zero-setup installation:
install-complete.bat   # Handles everything automatically
```

#### **⚠️ Installation Problems**
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
# GPU installer now:
# - Checks NVIDIA drivers
# - Verifies CUDA installation  
# - Tests GPU accessibility
# - Provides specific error guidance
```

#### **🔧 Manual Troubleshooting (If Installers Fail)**
```bash
# Check CUDA installation (for GPU users)
nvidia-smi

# Manual PyTorch installation with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Check your system type
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

#### **🌐 API Connection Issues**
- Verify API keys are correctly entered and saved
- Check internet connection and firewall settings
- Ensure API quotas/credits are available  
- Try switching between API providers (Black Forest Labs vs GRS AI)

#### **🔋 Performance Optimization**
- **� CPU Users**: API-only mode provides best performance and reliability
- **🎮 GPU Users**: Ensure CUDA drivers and toolkit are up to date
- **🚀 All Users**: Close unnecessary applications before generation
- **🎯 Pro Tip**: Cloud API processing is often faster and more reliable than local

### **🛠️ Getting Help**
- **Smart Installer Issues**: Re-run `install.bat` - it handles most problems automatically
- **GitHub Issues**: Check [Issues](https://github.com/hooh777/photogen_app_v3/issues) for known problems
- **Configuration**: Review `config.yaml` for model and API settings
- **Debug Mode**: Enable debug logging in app settings for detailed error information
- **Community**: Join discussions in the GitHub repository

## 📚 Technical Details

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
├── install-complete.bat      # Complete one-click installer
├── run-photogen.bat         # Launch script (created by installer)
├── core/
│   ├── generator.py         # Image generation logic (CPU/GPU compatible)
│   ├── ui.py               # User interface components
│   ├── vision_streamlined.py # AI vision analysis
│   └── handlers/           # Event handling and workflows
├── assets/                 # Demo images and backgrounds
└── outputs/               # Generated images storage
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style and formatting
- Testing procedures
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Black Forest Labs** - FLUX.1 models
- **Alibaba Cloud** - Qwen-VL-Max vision model
- **MIT HAN Lab** - Nunchaku optimization
- **Hugging Face** - Diffusers library
- **Gradio** - Web interface framework

---

**Made with ❤️ by the PhotoGen Team**

*Transform your ideas into stunning visuals with the power of AI*
