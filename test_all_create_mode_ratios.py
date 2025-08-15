#!/usr/bin/env python3
"""
Comprehensive test for Create Mode aspect ratios to verify all selections work correctly
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.handlers.generation_manager import GenerationManager
from core.generator import Generator
from core.secure_storage import SecureStorage

def test_all_create_mode_aspect_ratios():
    """Test all aspect ratio options in Create Mode"""
    
    print("=== Testing All Create Mode Aspect Ratios ===")
    
    # Initialize components
    config = {'api': {'enabled': True}}
    generator = Generator(config)
    secure_storage = SecureStorage()
    gen_manager = GenerationManager(generator, secure_storage)
    
    # Test all aspect ratio options
    test_cases = [
        ("1:1 (Square)", 1024, 1024),
        ("16:9 (Landscape)", 1024, 576),
        ("9:16 (Portrait)", 576, 1024),
        ("4:3 (Standard)", 1024, 768),
        ("3:4 (Portrait)", 768, 1024),
        ("Match Input", 1024, 1024),  # Default fallback for Create Mode
    ]
    
    all_passed = True
    
    for aspect_ratio, expected_width, expected_height in test_cases:
        width, height = gen_manager._determine_dimensions(
            aspect_ratio=aspect_ratio,
            source_image=None,  # Create Mode
            is_create_mode=True
        )
        
        if width == expected_width and height == expected_height:
            print(f"✅ {aspect_ratio:20} → {width:4}×{height:4} ✓")
        else:
            print(f"❌ {aspect_ratio:20} → {width:4}×{height:4} (expected {expected_width}×{expected_height})")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("Testing all Create Mode aspect ratio selections...\n")
    
    success = test_all_create_mode_aspect_ratios()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 ALL ASPECT RATIOS WORK CORRECTLY IN CREATE MODE!")
        print("🎯 Users can now select any aspect ratio and get the correct dimensions")
    else:
        print("❌ Some aspect ratios failed. Check the implementation.")
