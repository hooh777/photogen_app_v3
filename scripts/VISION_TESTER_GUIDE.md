# Vision Model Testing Tool - Usage Guide

## 🎯 Purpose
Test Qwen-VL-Max vision model capabilities with comprehensive structured analysis and JSON output.

## 🚀 Quick Start

### 1. Setup API Key (First Time Only)
```bash
python scripts/vision_tester.py --setup-key
```

### 2. Test Single Image
```bash
# Comprehensive analysis
python scripts/vision_tester.py "test_images/your_image.jpg"

# Multiple analysis types
python scripts/vision_tester.py "test_images/your_image.jpg" --analysis comprehensive objects scene
```

### 3. Test Folder of Images
```bash
# Test all images in folder
python scripts/vision_tester.py "test_images/"

# Limit to first 5 images
python scripts/vision_tester.py "test_images/" --max-images 5

# Specific analysis types
python scripts/vision_tester.py "test_images/" --analysis objects description
```

### 4. Save Custom Output
```bash
python scripts/vision_tester.py "your_image.jpg" --output "my_test_results.json"
```

## 📋 Analysis Types

- **`comprehensive`** (default): Complete analysis including objects, people, environment, colors, composition
- **`objects`**: Focus on identifying and describing all objects in detail
- **`scene`**: Environment, lighting, setting, mood analysis
- **`description`**: Natural language description of the entire image

## 📊 Output Format

Results are saved as JSON files in `vision_test_results/` folder with structure:

```json
{
  "image_path": "path/to/image.jpg",
  "test_timestamp": "2025-08-11T...",
  "analysis_results": {
    "comprehensive": {
      "image_size": "1024x768",
      "raw_response": "Full AI response text...",
      "structured_analysis": {
        "summary": "Overall description",
        "objects": ["object1", "object2"],
        "people": ["person descriptions"],
        "environment": {"setting": "indoor", "lighting": "natural"},
        "colors": ["red", "blue"],
        "technical_notes": "Quality observations"
      },
      "api_usage": {
        "prompt_tokens": 150,
        "completion_tokens": 800,
        "total_tokens": 950
      }
    }
  }
}
```

## 🛠️ Examples

### Test Your App's Test Images
```bash
# Test all test images
python scripts/vision_tester.py "test_images/"

# Test specific background types
python scripts/vision_tester.py "test_images/background/pure background/"
python scripts/vision_tester.py "test_images/background/with model/"

# Test object images
python scripts/vision_tester.py "test_images/object/"
```

### Detailed Object Analysis
```bash
python scripts/vision_tester.py "test_images/object/" --analysis objects --max-images 10
```

### Scene Understanding
```bash
python scripts/vision_tester.py "test_images/background/" --analysis scene comprehensive
```

## 📁 Output Files

- **JSON Results**: `vision_test_results/vision_test_YYYYMMDD_HHMMSS.json`
- **Console Summary**: Immediate text summary of key findings
- **Structured Data**: Easy to parse for further analysis

## 🔧 Troubleshooting

### API Key Issues
```bash
# Check if key is set
python -c "from core.secure_storage import SecureStorage; print('Key exists:', bool(SecureStorage().load_api_key('Qwen-VL-Max')))"

# Reset key
python scripts/vision_tester.py --setup-key
```

### Large Folder Processing
```bash
# Process in batches
python scripts/vision_tester.py "large_folder/" --max-images 20 --output "batch1.json"
```

## 💡 Use Cases

1. **Test Vision Understanding**: See what the AI actually sees in your images
2. **Debug Auto-Prompt Issues**: Understand why certain prompts are generated
3. **Object Detection**: Verify object identification accuracy
4. **Scene Analysis**: Check environment and context understanding
5. **Batch Analysis**: Process multiple images for comparison
6. **API Usage Monitoring**: Track token consumption

## 🔍 Integration Notes

- Uses same secure storage as main app
- Same Qwen-VL-Max configuration
- Standalone - doesn't interfere with main app
- Results can be used to improve auto-prompt generation
