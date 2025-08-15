#!/usr/bin/env python3
"""
Test the specific bug reported by the user:
"I clicked 16:9, and here is the message: 'Returning fresh result image: (1024, 1024) RGB'"

This test simulates the exact scenario to verify it's fixed.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.generator import Generator
from PIL import Image

def test_16_9_with_background():
    """Test that 16:9 selection produces 1024×576 even with background present"""
    
    print("=== Testing 16:9 Aspect Ratio Bug Fix ===")
    
    # Create a test background image (square)
    background = Image.new('RGB', (1024, 1024), color='blue')
    
    # Initialize generator with config (simulating Pro mode)
    config = {'api': {'enabled': True}}  # Simple config for testing
    generator = Generator(config)
    
    # Test the dimension calculation with background present
    print(f"🔍 Background image: {background.size}")
    print(f"🎯 User selection: '16:9 (Landscape)'")
    
    # This is what happens in the UI when user selects 16:9
    width, height = generator._determine_safe_generation_size(
        background_img=background,
        aspect_ratio_setting="16:9 (Landscape)",
        model_choice="Pro",  # Simulating Pro mode
        force_aspect_ratio=True  # This should force 16:9 even with background
    )
    
    print(f"📐 Generated dimensions: {width}×{height}")
    
    # Verify it's actually 16:9
    expected_width, expected_height = 1024, 576
    aspect_ratio = width / height
    expected_ratio = 16 / 9
    
    if width == expected_width and height == expected_height:
        print(f"✅ SUCCESS: Got expected {expected_width}×{expected_height}")
        print(f"✅ Aspect ratio: {aspect_ratio:.3f} (expected: {expected_ratio:.3f})")
        return True
    else:
        print(f"❌ FAILED: Expected {expected_width}×{expected_height}, got {width}×{height}")
        print(f"❌ Aspect ratio: {aspect_ratio:.3f} (expected: {expected_ratio:.3f})")
        return False

def test_match_input_still_works():
    """Test that 'Match Input' still uses background dimensions"""
    
    print("\n=== Testing 'Match Input' Still Works ===")
    
    # Create a test background image (non-square)
    background = Image.new('RGB', (800, 600), color='green')
    
    # Initialize generator
    config = {'api': {'enabled': True}}  # Simple config for testing
    generator = Generator(config)
    
    print(f"🔍 Background image: {background.size}")
    print(f"🎯 User selection: 'Match Input'")
    
    # This should use background dimensions
    width, height = generator._determine_safe_generation_size(
        background_img=background,
        aspect_ratio_setting="Match Input",
        model_choice="Pro",  # Simulating Pro mode
        force_aspect_ratio=False  # Should use background size
    )
    
    print(f"📐 Generated dimensions: {width}×{height}")
    
    if width == 800 and height == 600:
        print(f"✅ SUCCESS: Correctly matched input {width}×{height}")
        return True
    else:
        print(f"❌ FAILED: Expected 800×600, got {width}×{height}")
        return False

if __name__ == "__main__":
    print("Testing the specific aspect ratio bug reported by user...\n")
    
    test1_passed = test_16_9_with_background()
    test2_passed = test_match_input_still_works()
    
    print(f"\n{'='*50}")
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! The aspect ratio bug is FIXED!")
        print("🎯 User should now get 1024×576 when selecting '16:9 (Landscape)'")
    else:
        print("❌ Some tests failed. Bug may not be fully fixed.")
