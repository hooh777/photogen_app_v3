# Style Transfer Workflow

## Overview

The Style Transfer Workflow implements the pattern: **Selfie (Plain Background) + Style Reference (Scene Background) → Stylized Result**

This feature allows users to:
1. Take or use a selfie with a plain/simple background
2. Select a style reference image with an interesting scene/background
3. Generate a stylized result that places the person in the new environment while maintaining their identity

## How It Works

### 1. Selfie Analysis 📸
- **Person Detection**: Identifies pose, clothing, facial expression, age group
- **Background Analysis**: Determines if background is plain/simple for easy replacement
- **Lighting Analysis**: Extracts current lighting conditions and quality
- **Composition Analysis**: Understands perspective, framing, and focal points

### 2. Style Reference Analysis 🎨
- **Scene Description**: Analyzes environment, location type (indoor/outdoor)
- **Color Palette**: Extracts dominant colors and color schemes
- **Lighting Style**: Identifies lighting type, mood, and characteristics
- **Mood & Atmosphere**: Captures emotional tone and style keywords
- **Background Elements**: Catalogs objects, textures, patterns, architectural features

### 3. Intelligent Prompt Generation ✍️
- Combines person characteristics from selfie with style elements from reference
- Preserves identity, pose, and clothing while applying new background and lighting
- Includes technical quality instructions for photorealistic results
- Generates optimized prompts for seamless integration

## Usage Options

### 1. Command Line Interface

#### Basic Usage
```bash
python scripts/style_transfer_workflow.py selfie.jpg style_reference.jpg
```

#### Analysis Only (No Generation)
```bash
python scripts/style_transfer_workflow.py selfie.jpg style_reference.jpg --analyze-only
```

#### Custom Output Directory
```bash
python scripts/style_transfer_workflow.py selfie.jpg style_reference.jpg --output-dir "my_results"
```

#### Save Analysis Files
```bash
python scripts/style_transfer_workflow.py selfie.jpg style_reference.jpg --analyze-only --save-analyses
```

#### Setup API Key
```bash
python scripts/style_transfer_workflow.py --setup-key
```

### 2. Graphical User Interface

```bash
python scripts/style_transfer_gui.py
```

The GUI provides:
- Easy file selection for selfie and style reference
- Options for analysis-only mode
- Custom output directory selection
- Real-time progress indicators
- Detailed results display
- API key setup interface

### 3. Demo Script

```bash
python scripts/style_transfer_demo.py
```

Shows workflow concept and technical details:
```bash
python scripts/style_transfer_demo.py --technical
```

## Example Workflows

### 🌅 Beach Sunset Style
- **Input**: Selfie with plain white wall background
- **Style**: Beach sunset with warm orange/pink lighting
- **Result**: Person in same pose but with beach sunset background and matching warm lighting

### 🌲 Forest Adventure Style
- **Input**: Selfie with plain background
- **Style**: Dense forest with dappled sunlight
- **Result**: Person appears to be in the forest with natural lighting filtering through trees

### 🏙️ City Night Style
- **Input**: Selfie with simple background
- **Style**: City skyline at night with neon lights
- **Result**: Person with urban nighttime atmosphere and colorful city lights reflecting on them

## File Structure

```
core/
├── style_transfer.py          # Main StyleTransferProcessor class
└── ...

scripts/
├── style_transfer_workflow.py # Command-line interface
├── style_transfer_gui.py      # Graphical user interface
└── style_transfer_demo.py     # Demo and examples

outputs/
├── style_transfer_TIMESTAMP.png           # Generated images
├── style_transfer_log_TIMESTAMP.json      # Workflow logs
├── selfie_analysis_TIMESTAMP.json         # Selfie analysis results
├── style_analysis_TIMESTAMP.json          # Style reference analysis
└── transfer_prompt_TIMESTAMP.txt          # Generated prompts
```

## Technical Implementation

### Core Components

#### StyleTransferProcessor Class
- `analyze_selfie()`: Comprehensive selfie analysis
- `analyze_style_reference()`: Style reference analysis
- `generate_style_transfer_prompt()`: Intelligent prompt generation
- `process_style_transfer_workflow()`: Complete workflow execution

#### Key Features
- **Vision Analysis Integration**: Uses Qwen-VL-Max for comprehensive scene understanding
- **Structured Data Extraction**: Parses vision responses into organized categories
- **Intelligent Prompt Engineering**: Combines elements for optimal generation results
- **Comprehensive Logging**: Tracks entire workflow with detailed JSON logs
- **Error Handling**: Robust error handling with informative messages

### Analysis Categories

#### Person Details (from Selfie)
- Appearance and physical characteristics
- Pose and body language
- Clothing and accessories
- Facial expression and emotion
- Age group and gender (when relevant)

#### Background Information (from Selfie)
- Background type and complexity
- Whether background is plain/simple
- Colors and lighting in background
- Suitability for replacement

#### Scene Description (from Style Reference)
- Environment and location type
- Indoor vs outdoor setting
- Architectural and natural elements
- Overall scene composition

#### Style Elements (from Style Reference)
- Color palette and schemes
- Lighting style and direction
- Mood and atmospheric qualities
- Textures and patterns
- Visual style characteristics

## Best Practices

### Choosing Selfies
- **Plain Backgrounds Work Best**: Solid colors, simple walls, minimal patterns
- **Good Lighting**: Even lighting without harsh shadows
- **Clear Subject**: Person should be the main focus
- **Standard Poses**: Natural poses work better than complex positions

### Choosing Style References
- **Interesting Environments**: Scenic locations, atmospheric settings
- **Good Composition**: Well-composed scenes with clear background elements
- **Appropriate Lighting**: Lighting that could realistically illuminate a person
- **High Quality**: Clear, detailed images produce better style extraction

### Optimization Tips
- Use high-resolution images when possible
- Ensure good contrast between person and background in selfie
- Choose style references with lighting that matches desired mood
- Review analysis results before generation to understand extracted elements

## Troubleshooting

### Common Issues

#### "No API key configured"
```bash
python scripts/style_transfer_workflow.py --setup-key
```

#### "Image not found" or "Unsupported format"
- Check file paths are correct
- Ensure images are in supported formats: .jpg, .jpeg, .png, .webp, .bmp, .tiff

#### Poor analysis results
- Try images with better lighting
- Use higher resolution images
- Ensure clear subject separation from background

#### Generation issues
- Review generated prompt for accuracy
- Try different style reference images
- Check that API key has sufficient credits

### Getting Help

1. **Run Demo**: `python scripts/style_transfer_demo.py` for concept explanation
2. **Check Logs**: Review JSON log files in outputs directory
3. **Analysis Mode**: Use `--analyze-only` to test without generation
4. **Verbose Output**: Check console output for detailed processing information

## Integration

The style transfer workflow can be integrated into other applications:

```python
from core.style_transfer import StyleTransferProcessor

processor = StyleTransferProcessor()

# Analyze images
selfie_analysis = processor.analyze_selfie("path/to/selfie.jpg")
style_analysis = processor.analyze_style_reference("path/to/style.jpg")

# Generate prompt
prompt = processor.generate_style_transfer_prompt(selfie_analysis, style_analysis)

# Run complete workflow
results = processor.process_style_transfer_workflow(
    "path/to/selfie.jpg",
    "path/to/style.jpg",
    "output_directory"
)
```

## Future Enhancements

Potential improvements for the style transfer workflow:

1. **Background Segmentation**: Automatic person/background separation
2. **Lighting Adjustment**: Automatic lighting correction to match style
3. **Multi-Person Support**: Handle group selfies with multiple people
4. **Style Strength Control**: Adjustable intensity of style application
5. **Real-time Preview**: Quick preview generation before full resolution
6. **Batch Processing**: Process multiple selfies with same style reference
7. **Style Mixing**: Combine multiple style references
8. **Mobile App Integration**: Native mobile interface for selfie capture

## Contributing

To contribute to the style transfer workflow:

1. Test with various image types and scenarios
2. Improve vision analysis parsing for better element extraction
3. Enhance prompt generation with more sophisticated logic
4. Add new analysis categories or style elements
5. Optimize performance for faster processing
6. Improve error handling and user feedback
