"""
Quick Start Guide for Scientific Batch Prompt Testing
Demonstrates how to run and analyze batch tests for prompt enhancement effectiveness.
"""
import os
import sys
from datetime import datetime


def check_requirements():
    """Check if all required components are available"""
    
    required_dirs = [
        "test_images",
        "core/handlers"
    ]
    
    required_files = [
        "batch_prompt_testing.py",
        "batch_test_analyzer.py", 
        "analyze_generation_result.py",
        "core/handlers/generation_manager.py",
        "core/handlers/scale_analyzer.py"
    ]
    
    print("🔍 Checking requirements...")
    
    missing_items = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_items.append(f"Directory: {dir_path}")
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_items.append(f"File: {file_path}")
    
    if missing_items:
        print("❌ Missing requirements:")
        for item in missing_items:
            print(f"   - {item}")
        return False
    
    print("✅ All requirements met!")
    return True


def show_test_images():
    """Show available test images"""
    
    test_images_dir = "test_images"
    
    if not os.path.exists(test_images_dir):
        print(f"❌ Test images directory not found: {test_images_dir}")
        return
    
    image_files = [f for f in os.listdir(test_images_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"📁 Found {len(image_files)} test images:")
    for i, img_file in enumerate(sorted(image_files)[:10], 1):  # Show first 10
        print(f"   {i:2d}. {img_file}")
    
    if len(image_files) > 10:
        print(f"   ... and {len(image_files) - 10} more")


def run_sample_test():
    """Run a small sample test to verify the system works"""
    
    print("\n🧪 SAMPLE TEST EXECUTION")
    print("=" * 50)
    
    # Check if we can import our modules
    try:
        from batch_prompt_testing import BatchPromptTester
        print("✅ BatchPromptTester imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BatchPromptTester: {e}")
        return False
    
    try:
        from batch_test_analyzer import BatchTestAnalyzer
        print("✅ BatchTestAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BatchTestAnalyzer: {e}")
        print("ℹ️ Note: Analyzer requires matplotlib and pandas for visualizations")
    
    # Create a tester instance
    try:
        tester = BatchPromptTester()
        print("✅ BatchPromptTester instance created")
        
        # Show test case structure
        test_cases = tester.create_test_cases()
        print(f"✅ Generated {len(test_cases)} test cases")
        
        if test_cases:
            print("\n📋 Sample test case structure:")
            sample = test_cases[0]
            print(f"   Test ID: {sample['test_id']}")
            print(f"   Enhancement: {sample['enhancement_level']['name']}")
            print(f"   Prompt Category: {sample['prompt_config']['category']}")
            print(f"   Image Pair: {sample['image_pair']['pair_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test cases: {e}")
        return False


def show_usage_instructions():
    """Show detailed usage instructions"""
    
    print("\n📖 USAGE INSTRUCTIONS")
    print("=" * 50)
    
    print("""
## 1. Run Batch Testing

To run the full 20-test scientific batch:

```bash
python batch_prompt_testing.py --api-key YOUR_API_KEY --model "Pro API"
```

This will:
- Create 20 test cases with 4 enhancement levels
- Test different prompt categories and image pairs
- Generate images with fixed seeds for reproducibility
- Run comprehensive post-generation analysis
- Save all results to timestamped directory

## 2. Monitor Progress

The system provides real-time monitoring showing:
- Current test progress (X/20)
- Image pair being tested
- Prompt category and enhancement level
- Success/failure status
- Quality assessment results

## 3. Analyze Results

After batch testing completes, analyze results with:

```bash
python batch_test_analyzer.py --test-session-dir batch_test_results/test_session_TIMESTAMP
```

This generates:
- Comprehensive analysis report
- Performance comparison charts
- Problem pattern identification
- Enhancement effectiveness insights

## 4. Review Generated Content

Each test session creates:
- `generated_images/` - All generated and merged images
- `analysis_results/` - Individual test analysis JSON files
- `comparison_reports/` - Comprehensive reports and charts
- `session_logs/` - Complete session data

## 5. Manual Review Process

For each test case, manually review:
1. **Generated Image**: Visual quality and correctness
2. **Analysis JSON**: Vision model's detailed assessment
3. **Comparison**: Original vs enhanced prompt results

The JSON analysis includes:
- Object count (duplication detection)
- Scale accuracy assessment  
- Integration quality evaluation
- Prompt effectiveness analysis
""")


def main():
    """Main execution flow"""
    
    print("🧪 SCIENTIFIC BATCH PROMPT TESTING - QUICK START")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please ensure all required files and directories are available.")
        return
    
    # Show available test images
    print()
    show_test_images()
    
    # Run sample test
    if run_sample_test():
        print("\n✅ System verification successful!")
    else:
        print("\n❌ System verification failed. Please check your setup.")
        return
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n🎯 WHAT TO EXPECT FROM BATCH TESTING:")
    print("   - 20 comprehensive test cases")
    print("   - 4 enhancement levels: baseline → scale → duplication → full")
    print("   - 5 prompt categories: human_holding, table_placement, studio, lifestyle, detailed")
    print("   - Real-time monitoring with quality assessments")
    print("   - Comprehensive analysis reports with visual comparisons")
    print("   - Problem pattern identification and improvement suggestions")
    
    print(f"\n🚀 READY TO START!")
    print("   Run: python batch_prompt_testing.py --api-key YOUR_API_KEY")
    print("   This will create a new test session with timestamped results.")


if __name__ == "__main__":
    main()
