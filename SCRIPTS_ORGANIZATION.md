# PhotoGen Scripts Organization

**Note**: The scripts directory has been cleaned up. All testing and utility scripts have been removed to simplify the project structure.

## Current Project Structure

### Core Application Files
- `app.py` - Main application entry point
- `config.yaml` - Configuration file
- `requirements.txt` - Python dependencies

### `/core/` - Application Core
**Purpose**: Core application logic and handlers
- Main application functionality
- UI handlers (`ui.py`)
- Generation managers (`generator.py`)
- Vision analysis modules (`vision_streamlined.py`)
- Secure storage (`secure_storage.py`)
- Image enhancement (`enhancer.py`)
- Utility functions (`utils.py`)

### `/assets/` - Static Assets
**Purpose**: Background images and static resources

### `/test_images/` - Test Data
**Purpose**: Test images for development and validation (preserved)

### `/outputs/` - Generated Images
**Purpose**: Directory for saved generated images

### `/workflow diagram/` - Documentation
**Purpose**: Technical documentation and workflow diagrams

## Removed Components

The following directories and scripts have been removed during cleanup:
- `/scripts/` - All utility and testing scripts
- `/tests/` - All test files and batch testing systems  
- `/vision_test_results/` - Test result data
- Empty placeholder files in `/core/`
- Style transfer modules and scripts
- Depth processing modules
- Scale analysis tools

## Dependencies

### Core Requirements (from requirements.txt)
- Python 3.8+
- gradio
- torch
- PIL (Pillow)
- OpenAI client
- PyYAML
- Other dependencies as specified in requirements.txt

## Usage

To run the application:
```bash
python app.py
```

The application provides a web interface for:
- Multi-image upload and composition
- AI-powered prompt generation
- Image generation using Pro APIs (Black Forest Labs, GRS AI)
- Interactive canvas for targeted editing
- Direct download of generated images
