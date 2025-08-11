#!/usr/bin/env python3
"""
Quick test script for the Vision Tester
Verifies basic functionality without requiring API calls
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_vision_tester_setup():
    """Test that the vision tester can be imported and initialized"""
    
    print("🧪 Testing Vision Tester Setup...")
    
    try:
        # Test imports
        from scripts.vision_tester import VisionTester
        print("✅ Vision tester import successful")
        
        # Test initialization
        tester = VisionTester()
        print("✅ Vision tester initialization successful")
        
        # Test secure storage
        print(f"✅ Results directory: {tester.results_dir}")
        
        # Check if API key exists
        api_key = tester.secure_storage.load_api_key("Qwen-VL-Max")
        if api_key:
            print("✅ Qwen-VL-Max API key found in secure storage")
        else:
            print("⚠️  Qwen-VL-Max API key not found - run with --setup-key first")
        
        # Test prompt generation
        prompts = ["comprehensive", "objects", "scene", "description"]
        for prompt_type in prompts:
            prompt = tester._get_analysis_prompt(prompt_type)
            if len(prompt) > 50:
                print(f"✅ {prompt_type} prompt generated ({len(prompt)} chars)")
            else:
                print(f"❌ {prompt_type} prompt too short")
        
        # Check for test images
        test_dirs = ["test_images", "test_images/object", "test_images/background"]
        for test_dir in test_dirs:
            if Path(test_dir).exists():
                image_count = len(list(Path(test_dir).glob("*.png"))) + len(list(Path(test_dir).glob("*.jpg")))
                print(f"✅ Found {image_count} images in {test_dir}")
            else:
                print(f"⚠️  Directory not found: {test_dir}")
        
        print(f"\n🎯 SETUP VERIFICATION COMPLETE")
        print(f"📝 To use the vision tester:")
        if not api_key:
            print(f"   1. First run: python scripts/vision_tester.py --setup-key")
        print(f"   2. Test single image: python scripts/vision_tester.py path/to/image.jpg")
        print(f"   3. Test folder: python scripts/vision_tester.py test_images/")
        print(f"   4. See guide: scripts/VISION_TESTER_GUIDE.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_vision_tester_setup()
