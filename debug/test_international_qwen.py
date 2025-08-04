#!/usr/bin/env python3
"""
Test the updated Qwen-VL-Max implementation with international Alibaba Cloud API.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vision import _analyze_with_qwen_vl_max
from PIL import Image, ImageDraw
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def create_test_image():
    """Create a simple test image with clear visual elements."""
    img = Image.new('RGB', (200, 200), 'lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw a green grass area
    draw.rectangle([0, 150, 200, 200], fill='green')
    
    # Draw some brown wood area
    draw.rectangle([50, 100, 150, 150], fill='brown')
    
    # Add some text
    try:
        draw.text((10, 10), "Test Scene", fill='black')
        draw.text((10, 160), "Grass Area", fill='white')
        draw.text((60, 110), "Wood", fill='white')
    except:
        pass  # Font issues are okay for testing
    
    return img

def test_international_qwen_api():
    """Test the new international Qwen-VL-Max API implementation."""
    print("🧪 TESTING INTERNATIONAL QWEN-VL-MAX API")
    print("=" * 50)
    
    # Get API key from user
    api_key = input("\n🔑 Please paste your Alibaba Cloud API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return
    
    print(f"✅ API Key received (length: {len(api_key)})")
    
    # Create test image
    print("\n📸 Creating test image...")
    test_img = create_test_image()
    print("✅ Test image created")
    
    # Test the vision analysis
    print("\n🔍 Testing Qwen-VL-Max International API...")
    try:
        result = _analyze_with_qwen_vl_max(test_img, api_key)
        print(f"✅ SUCCESS! Analysis result: '{result}'")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    """Main test function."""
    print("🌐 ALIBABA CLOUD INTERNATIONAL API TEST")
    print("=" * 60)
    
    print("""
📍 **What this tests:**
- New OpenAI-compatible API format
- International endpoint: dashscope-intl.aliyuncs.com
- Proper image encoding and message format
- Error handling and response parsing

📍 **If this works:**
- Your API key is valid for international accounts
- The new API format is correctly implemented
- PhotoGen Edit mode vision analysis will work

📍 **If this fails:**
- Check if you're using the international Alibaba Cloud console
- Verify Qwen-VL-Max model is enabled
- Consider switching to OpenAI GPT-4 Vision as alternative
    """)
    
    success = test_international_qwen_api()
    
    if success:
        print("\n🎉 INTERNATIONAL API WORKING!")
        print("✅ You can now use Qwen-VL-Max in PhotoGen Edit mode")
        print("✅ The vision analysis will work for auto-generating prompts")
    else:
        print("\n🔧 TROUBLESHOOTING OPTIONS:")
        print("1. **Check international console**: https://bailian.console.aliyun.com/")
        print("2. **Enable Qwen-VL-Max model** in the console")
        print("3. **Verify billing/credits** are set up")
        print("4. **Consider OpenAI GPT-4 Vision** as easier alternative")

if __name__ == "__main__":
    main()
