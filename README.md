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
- **🔍 Hardware Auto-Detection**: Automatically detects GPU/CUDA capabilities
- **📦 Dual Requirements**: Separate `requirements-gpu.txt` and `requirements-cpu.txt`
- **⚡ One-Click Setup**: Intelligent installers handle everything automatically
- **🚀 Launch Scripts**: Simple `run-photogen.bat` for easy startup

### **Enhanced CPU Compatibility**
- **💻 Universal Support**: Works on any hardware - no GPU required
- **🌐 Full API Access**: Complete feature set via cloud processing
- **⚡ Lightweight Install**: Minimal dependencies for CPU-only users
- **🛡️ Graceful Fallbacks**: Smart detection prevents compatibility issues

### **Improved User Experience**
- **🎯 Streamlined UI**: Better button placement and cleaner interface
- **📱 Responsive Design**: Optimized layout for all screen sizes
- **💬 Clear Messaging**: Helpful error messages and status indicators
- **⚙️ Smart Defaults**: Optimized settings for better out-of-box experience

## 🚀 Quick Start

### Installation Options

#### **🚀 Easy Installation (Windows Users)**
*Recommended for most users - automated setup with intelligent system detection*

```bash
# Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# Run the intelligent installer (automatically detects your hardware)
install.bat

# Or choose specific installation type:
install-gpu.bat    # For users with NVIDIA GPUs (full local processing)
install-cpu.bat    # For users without GPU (API-only, lightweight)

# Launch PhotoGen anytime
run-photogen.bat
```

**🎯 Installation Features:**
- **Automatic Hardware Detection**: Detects GPU/CUDA availability
- **Virtual Environment Setup**: Creates isolated Python environment  
- **Dependency Management**: Installs only what you need
- **One-Click Launch**: Simple batch files for easy startup

#### **⚙️ Manual Installation**

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

#### **Installation Problems**
```bash
# For ImportError issues - choose the right installation:
install-gpu.bat    # If you have NVIDIA GPU + CUDA
install-cpu.bat    # If you want API-only mode

# Check your installation type:
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

#### **"Cannot import FluxKontextPipeline" Error**
This typically means you installed CPU-only dependencies but tried to use local models:
```bash
# Solution 1: Switch to API-only mode (recommended for most users)
install-cpu.bat

# Solution 2: Install full GPU requirements (if you have NVIDIA GPU)
install-gpu.bat
```

#### **GPU Installation Problems**
```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### **API Connection Issues**
- Verify API keys are correctly entered and saved
- Check internet connection
- Ensure API quotas/credits are available
- Try switching between API providers

#### **Memory Issues (GPU)**
- Reduce image resolution
- Close other GPU-intensive applications
- Consider using CPU-only installation instead

#### **Performance Optimization**
- **🖥️ CPU Users**: Use API-only mode for best performance and reliability
- **🎮 GPU Users**: Ensure CUDA is properly installed and up to date
- **⚡ All Users**: Close unnecessary browser tabs and applications
- **🎯 Smart Choice**: API processing is often faster than local for most users

### **Getting Help**
- Check the [Issues](https://github.com/hooh777/photogen_app_v3/issues) page
- Review configuration files (`config.yaml`)
- Enable debug logging for detailed error information

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
├── install.bat               # Smart installer (auto-detects hardware)
├── install-gpu.bat          # GPU installation script
├── install-cpu.bat          # CPU-only installation script  
├── run-photogen.bat         # Launch script
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
