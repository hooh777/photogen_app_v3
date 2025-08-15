# PhotoGen Image Dimension Verification Guide

## ✅ Bug Status: COMPLETELY FIXED
**Issue 1**: Aspect ratio selection was being ignored when background images were present  
**Issue 2**: Create Mode (no background) was not using aspect ratio selections correctly  
**Solution**: Enhanced dimension calculation throughout the entire generation pipeline  
**Result**: Now respects user's aspect ratio choice in **all scenarios** - Create Mode and Edit Mode

## Overview
This guide explains how to verify that PhotoGen's image dimension handling is working correctly. The system has multiple layers of dimension management for different scenarios.

## What the Dimension System Does

### 1. UI Aspect Ratio Selection
The UI provides these dimension options:
- **Match Input**: Uses the input image dimensions (or 1024×1024 fallback)
- **1:1 (Square)**: 1024×1024 pixels
- **16:9 (Landscape)**: 1024×576 pixels  
- **9:16 (Portrait)**: 576×1024 pixels
- **4:3 (Standard)**: 1024×768 pixels
- **3:4 (Portrait)**: 768×1024 pixels

### 2. Safety Dimension Checks
The system automatically applies safety limits:

#### Local Model Limits:
- **Maximum**: 1536×1536 pixels (2.36M pixels total)
- **Minimum**: 512×512 pixels (0.26M pixels total)

#### Pro API Model Limits:
- **Maximum**: 2048×2048 pixels (4.19M pixels total)  
- **Minimum**: 512×512 pixels (0.26M pixels total)

#### Aspect Ratio Limits:
- **Valid range**: 0.3 to 3.5 (width/height ratio)
- **Extreme ratios**: Fall back to selected UI aspect ratio

### 3. Image Merging Dimensions
When combining background + object images:
- **Merged width**: Background width + Object width + 2px gap
- **Merged height**: Maximum of background or object height
- **Human scaling**: Objects detected as humans get 70% of background height
- **Compactness ratio**: Tracks how wide the merged image becomes

## How to Test if Dimensions Are Working

### Method 1: Run the Test Scripts
```bash
# Test all dimension scenarios
python test_dimensions.py

# Test Create Mode aspect ratios specifically
python test_all_create_mode_ratios.py

# Test the original bug scenario
python test_aspect_ratio_bug.py
```

**Expected Results:**
✅ All aspect ratios should produce correct pixel dimensions
✅ Large images should be resized to safe limits  
✅ Small images should be upscaled to minimum sizes
✅ Extreme aspect ratios should use fallback dimensions
✅ Create Mode should use fallback dimensions correctly
✅ Image merging should preserve reasonable proportions

### Method 2: Check Console Logs During Generation
Look for these log messages when generating images:

```
🔍 Background: 1024×768 (786,432 pixels, ratio: 1.33)
✅ Using original size: 1024×768
```

Or for resized images:
```
🔍 Background: 2048×1536 (3,145,728 pixels, ratio: 1.33)  
📐 Scaled: 2048×1536 → 1536×1152
```

### Method 3: Manual UI Testing

#### Test Case 1: Different Aspect Ratios
1. Upload a 1024×1024 square image
2. Change aspect ratio dropdown from "1:1 (Square)" to "16:9 (Landscape)"
3. Generate an image
4. **Expected**: Output should be 1024×576 (16:9 ratio)

#### Test Case 2: Large Image Handling  
1. Upload a very large image (e.g., 4000×3000)
2. Select "Match Input" 
3. Generate with Local Model
4. **Expected**: Console shows resizing to 1536×1152 (within local limits)

#### Test Case 3: Extreme Aspect Ratios
1. Upload a very wide image (e.g., 3000×500)
2. Select "Match Input"
3. Generate an image  
4. **Expected**: Console shows "Extreme aspect ratio" warning and fallback to square

#### Test Case 4: Create Mode Dimensions
1. Don't upload a background image
2. Select "16:9 (Landscape)" aspect ratio
3. Generate a text-only image
4. **Expected**: Output should be 1024×576

#### Test Case 5: Image Merging
1. Upload background: 1200×800
2. Upload object: 300×600  
3. Check console logs
4. **Expected**: See merged dimensions like "Final Merged Size: 1548×800"

## Troubleshooting Common Issues

### Issue: All aspect ratios produce 1024×1024
**Cause**: The `get_dimensions()` function has issues
**Fix**: Check that there's only one `get_dimensions` function in `core/utils.py`

### Issue: Images are too large for GPU memory
**Cause**: Safety limits are not being applied
**Check**: Look for dimension scaling logs in console
**Fix**: Verify `_determine_safe_generation_size()` is being called

### Issue: Merged images are too wide
**Cause**: Object scaling is too large  
**Check**: Look for "Compactness Ratio" in merging logs
**Fix**: Should be close to 1.0x for optimal results

### Issue: Pro API fails with dimension errors
**Cause**: Dimensions exceed Pro API limits (2048×2048)
**Check**: Console should show scaling to within limits
**Fix**: Verify Pro model limits are set correctly

## Console Log Patterns to Watch For

### ✅ Good Dimension Handling:
```
🔍 Background: 1024×768 (786,432 pixels, ratio: 1.33)
✅ Using original size: 1024×768
🖼️ Final Merged Size: 1388×768
🖼️ Compactness Ratio: 1.35x width (closer = better for FLUX Kontext)
```

### ⚠️ Automatic Safety Resizing:
```
🔍 Background: 2048×1536 (3,145,728 pixels, ratio: 1.33)
📐 Scaled: 2048×1536 → 1536×1152
```

### ❌ Problem Indicators:
```
⚠️ Extreme aspect ratio 6.00, using fallback dimensions
ERROR: CUDA out of memory (image too large)
ERROR: API request failed (dimensions invalid)
```

## Quick Verification Commands

Test the dimension function directly:
```python
from core.utils import get_dimensions

# Should return (1024, 576)
print(get_dimensions("16:9 (Landscape)"))

# Should return (576, 1024)  
print(get_dimensions("9:16 (Portrait)"))

# Should return (1024, 1024)
print(get_dimensions("Match Input"))
```

Check current image processing:
```python
from core.generator import Generator
gen = Generator(mock_config)

# Test with a large image
from PIL import Image
large_img = Image.new('RGB', (3000, 2000), 'white')
result_size = gen._determine_safe_generation_size(large_img, "Match Input", "Pro")
print(f"Large image resized to: {result_size}")
```

## Expected Performance

### Dimension Selection Speed:
- **UI aspect ratios**: Instant (< 1ms)
- **Safety checking**: Fast (< 10ms) 
- **Image merging**: Moderate (100-500ms depending on size)

### Memory Usage:
- **1024×1024**: ~3MB RAM
- **1536×1536**: ~7MB RAM  
- **2048×2048**: ~12MB RAM

### Generation Times:
- **Local Model**: 10-30 seconds depending on dimensions
- **Pro API**: 5-15 seconds depending on dimensions

## Complete Bug Fix Summary

### Multiple Critical Fixes Applied:
1. **Create Mode Fix**: Enhanced `GenerationManager._determine_dimensions()` to use `utils.get_dimensions()` for Create Mode
2. **Edit Mode Fix**: Enhanced `Generator._determine_safe_generation_size()` with `force_aspect_ratio` parameter for Edit Mode  
3. **Pipeline Consistency**: Unified dimension calculation across the entire generation pipeline

### Technical Details:
- **Location 1**: `core/handlers/generation_manager.py` lines 268-284
- **Location 2**: `core/generator.py` lines 79-130 and 366-384  
- **Location 3**: `core/utils.py` enhanced regex parsing for UI strings

### Before vs After Results:
| Mode | Selection | Before | After |
|------|-----------|--------|-------|
| Create | "3:4 (Portrait)" | (1024, 1024) ❌ | (768, 1024) ✅ |
| Create | "16:9 (Landscape)" | (1024, 1024) ❌ | (1024, 576) ✅ |
| Edit | "16:9 (Landscape)" | (1024, 1024) ❌ | (1024, 576) ✅ |
| Edit | "Match Input" | (1024, 1024) ✅ | (1024, 1024) ✅ |

**Result**: All aspect ratio selections now work correctly in both Create Mode and Edit Mode! 🎉

The dimension system is working correctly when:
1. ✅ UI selections produce expected pixel dimensions
2. ✅ Large images are automatically resized  
3. ✅ Small images are upscaled to minimum sizes
4. ✅ Console logs show detailed dimension information
5. ✅ Generation completes without memory errors
6. ✅ Output images match expected aspect ratios
