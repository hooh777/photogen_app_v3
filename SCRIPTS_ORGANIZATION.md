# PhotoGen Scripts Organization

This document explains the organization of scripts in the PhotoGen application.

## Folder Structure

### `/tests/` - Core Testing Scripts
**Purpose**: Main testing functionality and unit tests
- `batch_prompt_testing.py` - Main scientific batch testing system with AI vision analysis
- `test_api_keys.py` - API key validation tests

### `/scripts/testing/` - Testing Utilities & Validation
**Purpose**: Helper scripts for testing setup and validation
- `quick_start_batch_testing.py` - Quick start guide for batch testing
- `verify_ai_vision_integration.py` - Verifies AI vision integration changes

### `/scripts/analysis/` - Analysis & Reporting Tools
**Purpose**: Scripts for analyzing test results and generating reports
- `batch_test_analyzer.py` - Advanced batch test analysis with matplotlib/pandas
- `simple_batch_analyzer.py` - Text-based batch test analysis (no dependencies)
- `example_post_generation_analysis.py` - Example usage of post-generation analysis
- `view_post_generation_analysis.py` - Log viewer for post-generation analysis
- `view_scale_analysis.py` - Log viewer for scale analysis

### `/scripts/` - Utility Scripts
**Purpose**: Standalone tools and utilities
- `vision_tester.py` - **NEW**: Comprehensive vision model testing tool
- `test_vision_setup.py` - Vision tester setup verification
- `show_organization.py` - Display script organization
- `VISION_TESTER_GUIDE.md` - Complete usage guide for vision testing

### `/reports/` - Core Analysis Classes
**Purpose**: Core analysis functionality used by other scripts
- `analyze_generation_result.py` - Main post-generation analysis class
- `OBJECT_DUPLICATION_FIX.md` - Documentation for duplication fixes

### `/core/` - Application Core
**Purpose**: Core application logic and handlers
- Main application functionality
- UI handlers
- Generation managers
- Vision analysis modules

## Usage Examples

### Running Batch Tests
```bash
# Main batch testing with AI vision analysis
python tests/batch_prompt_testing.py --api-key YOUR_API_KEY --provider bfl

# Quick start guide
python scripts/testing/quick_start_batch_testing.py
```

### Analyzing Results
```bash
# Advanced analysis with plots
python scripts/analysis/batch_test_analyzer.py /path/to/test/results

# Simple text-based analysis
python scripts/analysis/simple_batch_analyzer.py /path/to/test/results

# View specific analysis logs
python scripts/analysis/view_post_generation_analysis.py
python scripts/analysis/view_scale_analysis.py
```

### Testing & Validation
```bash
# Validate setup
python scripts/testing/test_image_loading.py
python scripts/testing/validate_enhancement_levels.py

# Verify AI vision integration
python scripts/testing/verify_ai_vision_integration.py
```

## Key Features

### AI Vision Integration
The batch testing system now uses real AI vision analysis instead of static templates:
- Analyzes actual background and object images
- Generates contextual prompts based on visual content
- Considers placement coordinates and human surface detection
- Maintains style/length testing framework with AI enhancement

### Comprehensive Analysis
Multiple analysis tools for different needs:
- **Advanced**: Full statistical analysis with visualizations
- **Simple**: Text-based analysis with no external dependencies
- **Logs**: Detailed log viewers for debugging and insights

### Testing Framework
Scientific approach to prompt effectiveness:
- 4 enhancement levels (minimal/detailed × natural/technical)
- Balanced test case generation
- Reproducible results with fixed seeds
- Comprehensive success metrics

## Dependencies

### Core Requirements
- Python 3.8+
- PIL (Pillow)
- OpenAI client
- PyYAML

### Optional for Advanced Analysis
- matplotlib
- pandas
- seaborn

### Test Data Requirements
- Organized test images in `test_images/` folder
- API keys configured in secure storage
- Background images in `test_images/background/pure background/` and `test_images/background/with model/`
- Object images in `test_images/object/`
