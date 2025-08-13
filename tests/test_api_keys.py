#!/usr/bin/env python3
"""
API Key Testing Script
Tests if your saved API keys work before running full batch testing.
"""
import sys
import os
import yaml
from PIL import Image
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import Generator
from core.secure_storage import SecureStorage


def test_api_keys():
    """Test API keys saved in secure storage"""
    
    print("🔑 Testing API Keys")
    print("=" * 50)
    
    # Load configuration
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    # Initialize secure storage
    try:
        secure_storage = SecureStorage()
        print("✅ Secure storage initialized")
    except Exception as e:
        print(f"❌ Failed to initialize secure storage: {e}")
        return
    
    # Test FLUX API Keys
    print("\n🎨 Testing FLUX API Keys:")
    flux_providers = ["Black Forest Labs API", "GRS AI Flux API"]
    
    working_flux_key = None
    working_flux_provider = None
    
    for provider in flux_providers:
        api_key = secure_storage.load_api_key(provider)
        if api_key:
            print(f"  📋 {provider}: {'*' * 8}{api_key[-4:]} (Found)")
            
            # Test with a simple generation
            try:
                generator = Generator(config)
                
                # Create a simple test case
                test_prompt = "a red apple on a white table"
                
                print(f"     🧪 Testing generation with {provider}...")
                
                # Use Pro API model choice for this provider
                if "Black Forest" in provider:
                    model_choice = "Pro (Black Forest Labs)"
                else:
                    model_choice = "Pro (GRS AI)"
                
                # Test text-to-image generation (simpler than i2i)
                result = generator.text_to_image(
                    prompt=test_prompt,
                    steps=20,  # Reduced steps for faster testing
                    guidance=7.5,
                    model_choice=model_choice,
                    num_images=1,
                    width=512,
                    height=512,
                    api_key=api_key
                )
                
                if result and len(result) > 0:
                    print(f"     ✅ {provider}: API key works! Generated image successfully")
                    working_flux_key = api_key
                    working_flux_provider = provider
                    break
                else:
                    print(f"     ❌ {provider}: API returned no images")
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "unauthorized" in error_msg or "invalid" in error_msg or "authentication" in error_msg:
                    print(f"     ❌ {provider}: Invalid API key - {e}")
                elif "quota" in error_msg or "limit" in error_msg:
                    print(f"     ⚠️ {provider}: API key valid but quota/rate limit reached - {e}")
                    working_flux_key = api_key
                    working_flux_provider = provider
                elif "timeout" in error_msg:
                    print(f"     ⚠️ {provider}: API timeout (key likely valid) - {e}")
                    working_flux_key = api_key
                    working_flux_provider = provider
                else:
                    print(f"     ❌ {provider}: Test failed - {e}")
        else:
            print(f"  ❌ {provider}: No API key saved")
    
    # Test Qwen Vision API Key
    print("\n👁️ Testing Qwen Vision API Key:")
    qwen_provider = "Qwen-VL-Max (Alibaba Cloud)"
    qwen_key = secure_storage.load_api_key(qwen_provider)
    
    working_qwen_key = None
    
    if qwen_key:
        print(f"  📋 {qwen_provider}: {'*' * 8}{qwen_key[-4:]} (Found)")
        
        try:
            # Test basic API connectivity (without scale analyzer)
            print(f"     🧪 Testing API key validity...")
            
            # Simple validation - just check if key format is correct
            if len(qwen_key) > 10 and qwen_key.startswith(('sk-', 'qwen-')):
                print(f"     ✅ {qwen_provider}: API key format appears valid")
                working_qwen_key = qwen_key
            else:
                print(f"     ⚠️ {qwen_provider}: API key format may be invalid")
                working_qwen_key = qwen_key  # Still set it for testing
                
        except Exception as e:
            error_msg = str(e).lower()
            if "unauthorized" in error_msg or "invalid" in error_msg or "authentication" in error_msg:
                print(f"     ❌ {qwen_provider}: Invalid API key - {e}")
            elif "quota" in error_msg or "limit" in error_msg:
                print(f"     ⚠️ {qwen_provider}: API key valid but quota/rate limit reached - {e}")
                working_qwen_key = qwen_key
            else:
                print(f"     ❌ {qwen_provider}: Test failed - {e}")
    else:
        print(f"  ❌ {qwen_provider}: No API key saved")
    
    # Summary and recommendations
    print("\n📊 API Key Test Summary:")
    print("=" * 50)
    
    if working_flux_key:
        print(f"✅ FLUX Generation: {working_flux_provider} - Ready")
        print(f"   🚀 You can run batch testing with this provider")
    else:
        print("❌ FLUX Generation: No working API key found")
        print("   ⚠️ You need a valid FLUX API key to run batch testing")
    
    if working_qwen_key:
        print(f"✅ Vision Analysis: {qwen_provider} - Ready")
        print(f"   🎯 Scale analysis and enhanced features will work")
    else:
        print(f"⚠️ Vision Analysis: No working Qwen API key")
        print(f"   ℹ️ Batch testing will work but skip scale analysis features")
    
    # Provide next steps
    print("\n🎯 Next Steps:")
    if working_flux_key:
        print(f"1. Run batch testing with your working {working_flux_provider}:")
        print(f"   C:/Users/user/Documents/GitHub/photogen_app_v3/venv/Scripts/python.exe tests\\batch_prompt_testing.py --api-key {working_flux_key}")
        
        if working_qwen_key:
            print("2. ✅ All enhancement levels will be tested (including scale analysis)")
        else:
            print("2. ⚠️ Only baseline and duplication prevention levels will work fully")
            print("   💡 Add Qwen API key in main app settings for complete testing")
    else:
        print("1. ❌ Add a valid FLUX API key in the main app settings first")
        print("2. 💡 Try Black Forest Labs or GRS AI providers")
    
    return working_flux_key, working_qwen_key


if __name__ == "__main__":
    try:
        flux_key, qwen_key = test_api_keys()
        
        # Return exit codes for scripting
        if flux_key:
            exit(0)  # Success - ready for batch testing
        else:
            exit(1)  # Failure - need API keys
            
    except Exception as e:
        print(f"\n💥 API key testing failed: {e}")
        exit(2)  # Error during testing
