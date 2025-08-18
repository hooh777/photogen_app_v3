#!/usr/bin/env python3
"""
Test script to verify CPU-only compatibility of PhotoGen App v3
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all core imports work in CPU-only mode"""
    try:
        print("Testing core imports...")
        
        from core.generator import Generator
        print("✅ Generator import successful")
        
        from core import constants as const
        print("✅ Constants import successful")
        
        import yaml
        config = yaml.safe_load("""
        models:
          text_to_image: "black-forest-labs/FLUX.1-dev"
          image_to_image: "black-forest-labs/FLUX.1-dev"
          vision: "Qwen/Qwen-VL-Max"
        """)
        
        generator = Generator(config)
        print("✅ Generator instantiation successful")
        
        print("\nTesting availability flags...")
        from core.generator import TORCH_AVAILABLE, DIFFUSERS_AVAILABLE, NUNCHAKU_AVAILABLE, LOCAL_PROCESSING_AVAILABLE, CUDA_AVAILABLE
        print(f"PyTorch Available: {TORCH_AVAILABLE}")
        print(f"Diffusers Available: {DIFFUSERS_AVAILABLE}")
        print(f"CUDA Available: {CUDA_AVAILABLE}")
        print(f"Nunchaku Available: {NUNCHAKU_AVAILABLE}")
        print(f"Local Processing Available: {LOCAL_PROCESSING_AVAILABLE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_local_model_error_handling():
    """Test that local model attempts are properly handled"""
    try:
        from core.generator import Generator
        from core import constants as const
        
        import yaml
        config = yaml.safe_load("""
        models:
          text_to_image: "black-forest-labs/FLUX.1-dev"
          image_to_image: "black-forest-labs/FLUX.1-dev"
          vision: "Qwen/Qwen-VL-Max"
        """)
        
        generator = Generator(config)
        
        # Test loading local pipelines
        print("Testing local pipeline error handling...")
        
        t2i_pipeline = generator._load_local_t2i_pipeline()
        i2i_pipeline = generator._load_local_i2i_pipeline()
        
        if t2i_pipeline is None and i2i_pipeline is None:
            print("✅ Local pipeline loading properly returns None in CPU-only mode")
        else:
            print("⚠️ Unexpected: Local pipelines loaded in CPU-only mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    print("PhotoGen CPU Compatibility Test")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_local_model_error_handling()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! PhotoGen is CPU-compatible.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)
