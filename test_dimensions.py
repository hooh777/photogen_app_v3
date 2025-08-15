#!/usr/bin/env python3
"""
Test script to verify PhotoGen dimension handling is working correctly.
This script tests the dimension logic without requiring full generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
import logging
from core import utils, generator, constants as const

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_get_dimensions():
    """Test the get_dimensions function with different aspect ratios"""
    print("=== Testing get_dimensions function ===")
    
    test_cases = [
        "Match Input",
        "1:1 (Square)", 
        "16:9 (Landscape)",
        "9:16 (Portrait)",
        "4:3 (Standard)",
        "3:4 (Portrait)",
        "Invalid Option"
    ]
    
    for test_case in test_cases:
        dimensions = utils.get_dimensions(test_case)
        print(f"✅ {test_case:<20} → {dimensions[0]}×{dimensions[1]} pixels")
    
    print()

def test_dimension_safety_checks():
    """Test the _determine_safe_generation_size function"""
    print("=== Testing Dimension Safety Checks ===")
    
    # Create a mock config for Generator
    mock_config = {
        'local_models': {
            't2i_model_path': 'mock',
            'i2i_model_path': 'mock'
        }
    }
    
    # Create a Generator instance (without loading models)
    gen = generator.Generator(mock_config)
    
    # Test cases with different image sizes
    test_images = [
        # Small image
        Image.new('RGB', (400, 300), 'white'),
        # Medium image  
        Image.new('RGB', (1024, 768), 'white'),
        # Large image
        Image.new('RGB', (2048, 1536), 'white'),
        # Very wide image (extreme aspect ratio)
        Image.new('RGB', (3000, 500), 'white'),
        # Very tall image (extreme aspect ratio)
        Image.new('RGB', (500, 3000), 'white'),
        # Square image
        Image.new('RGB', (1024, 1024), 'white'),
    ]
    
    aspect_ratios = ["1:1 (Square)", "16:9 (Landscape)", "Match Input"]
    model_choices = [const.LOCAL_MODEL, const.PRO_MODEL]
    
    for i, test_img in enumerate(test_images):
        original_size = test_img.size
        print(f"\n--- Test Image {i+1}: {original_size[0]}×{original_size[1]} ---")
        
        for model in model_choices:
            for aspect in aspect_ratios:
                try:
                    result_size = gen._determine_safe_generation_size(test_img, aspect, model, force_aspect_ratio=False)
                    status = "✅ PASS"
                    if result_size != original_size:
                        status = "⚠️ RESIZED"
                    print(f"  {model:<12} | {aspect:<20} → {result_size[0]:<4}×{result_size[1]:<4} | {status}")
                except Exception as e:
                    print(f"  {model:<12} | {aspect:<20} → ERROR: {e}")

def test_create_mode_dimensions():
    """Test dimensions when no background image is provided (Create Mode)"""
    print("\n=== Testing Create Mode Dimensions (No Background) ===")
    
    # Create a mock config for Generator
    mock_config = {
        'local_models': {
            't2i_model_path': 'mock',
            'i2i_model_path': 'mock'
        }
    }
    
    gen = generator.Generator(mock_config)
    
    aspect_ratios = [
        "1:1 (Square)",
        "16:9 (Landscape)", 
        "9:16 (Portrait)",
        "4:3 (Standard)",
        "Match Input"
    ]
    
    for aspect in aspect_ratios:
        # None background simulates Create Mode
        dimensions = gen._determine_safe_generation_size(None, aspect, const.PRO_MODEL, force_aspect_ratio=False)
        print(f"✅ Create Mode - {aspect:<20} → {dimensions[0]}×{dimensions[1]} pixels")

def test_merge_dimensions():
    """Test image merging dimension handling"""
    print("\n=== Testing Image Merge Dimension Handling ===")
    
    # Create test images with different sizes
    background = Image.new('RGB', (1200, 800), 'lightblue')
    object_img = Image.new('RGB', (300, 600), 'red')  # Tall object (like a person)
    
    print(f"Background: {background.size}")
    print(f"Object: {object_img.size}")
    
    # Test standard merge
    merged_standard = utils.merge_images_with_smart_scaling(background, object_img)
    print(f"✅ Standard merge: {merged_standard.size}")
    
    # Test with preserve_object_scale (for humans)
    merged_preserved = utils.merge_images_with_smart_scaling(
        background, object_img, preserve_object_scale=True
    )
    print(f"✅ Human-optimized merge: {merged_preserved.size}")
    
    # Test with custom target size
    target_size = (1024, 1024)
    merged_custom = utils.merge_images_with_smart_scaling(
        background, object_img, target_size=target_size
    )
    print(f"✅ Custom target {target_size}: {merged_custom.size}")

def main():
    """Run all dimension tests"""
    print("🔧 PhotoGen Dimension Testing Tool")
    print("=" * 50)
    
    try:
        test_get_dimensions()
        test_dimension_safety_checks()
        test_create_mode_dimensions()
        test_merge_dimensions()
        
        print("\n" + "=" * 50)
        print("✅ All dimension tests completed!")
        print("\n📋 What to check:")
        print("1. Aspect ratios produce expected pixel dimensions")
        print("2. Large images get resized to safe limits")
        print("3. Small images get upscaled to minimum sizes")
        print("4. Extreme aspect ratios get handled gracefully")
        print("5. Create Mode uses fallback dimensions correctly")
        print("6. Image merging preserves reasonable proportions")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
