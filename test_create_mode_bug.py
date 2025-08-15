#!/usr/bin/env python3
"""
Test the specific Create Mode bug: 3:4 (Portrait) should produce 768×1024, not 1024×1024
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.handlers.generation_manager import GenerationManager
from core.generator import Generator
from core.secure_storage import SecureStorage
from PIL import Image

def test_create_mode_3_4_portrait():
    """Test that 3:4 (Portrait) in Create Mode produces correct dimensions"""
    
    print("=== Testing Create Mode 3:4 (Portrait) Bug Fix ===")
    
    # Initialize components
    config = {'api': {'enabled': True}}
    generator = Generator(config)
    secure_storage = SecureStorage()
    gen_manager = GenerationManager(generator, secure_storage)
    
    # Test Create Mode (no background image)
    print(f"🎯 Testing Create Mode (no background)")
    print(f"🎯 Aspect ratio selection: '3:4 (Portrait)'")
    
    # This is what happens when user selects 3:4 in Create Mode
    width, height = gen_manager._determine_dimensions(
        aspect_ratio="3:4 (Portrait)",
        source_image=None,  # Create Mode - no background
        is_create_mode=True
    )
    
    print(f"📐 Generated dimensions: {width}×{height}")
    
    # Verify it's actually 3:4 portrait
    expected_width, expected_height = 768, 1024  # 3:4 portrait
    aspect_ratio = width / height
    expected_ratio = 3 / 4
    
    if width == expected_width and height == expected_height:
        print(f"✅ SUCCESS: Got expected {expected_width}×{expected_height}")
        print(f"✅ Aspect ratio: {aspect_ratio:.3f} (expected: {expected_ratio:.3f})")
        return True
    else:
        print(f"❌ FAILED: Expected {expected_width}×{expected_height}, got {width}×{height}")
        print(f"❌ Aspect ratio: {aspect_ratio:.3f} (expected: {expected_ratio:.3f})")
        return False

def test_edit_mode_still_works():
    """Test that Edit Mode with background still works with force_aspect_ratio"""
    
    print("\n=== Testing Edit Mode Still Works ===")
    
    # Initialize components
    config = {'api': {'enabled': True}}
    generator = Generator(config)
    secure_storage = SecureStorage()
    gen_manager = GenerationManager(generator, secure_storage)
    
    # Create a test background image (square)
    background = Image.new('RGB', (1024, 1024), color='blue')
    
    print(f"🔍 Background image: {background.size}")
    print(f"🎯 Aspect ratio selection: '16:9 (Landscape)'")
    
    # Test Edit Mode with background
    width, height = gen_manager._determine_dimensions(
        aspect_ratio="16:9 (Landscape)",
        source_image=background,
        is_create_mode=False
    )
    
    print(f"📐 Generated dimensions: {width}×{height}")
    
    # Should be 16:9, not background size
    expected_width, expected_height = 1024, 576
    if width == expected_width and height == expected_height:
        print(f"✅ SUCCESS: Correctly forced 16:9 aspect ratio {width}×{height}")
        return True
    else:
        print(f"❌ FAILED: Expected {expected_width}×{expected_height}, got {width}×{height}")
        return False

if __name__ == "__main__":
    print("Testing Create Mode and Edit Mode dimension fixes...\n")
    
    test1_passed = test_create_mode_3_4_portrait()
    test2_passed = test_edit_mode_still_works()
    
    print(f"\n{'='*50}")
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! Both Create Mode and Edit Mode bugs are FIXED!")
        print("🎯 User should now get 768×1024 when selecting '3:4 (Portrait)' in Create Mode")
    else:
        print("❌ Some tests failed. Bugs may not be fully fixed.")
