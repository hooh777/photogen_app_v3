#!/usr/bin/env python3
"""
Style Transfer Demo Script

Demonstrates the complete workflow:
1. Selfie (Plain background) + 2. Style reference (scene background) → 3. Stylized result

This script shows you exactly how the workflow processes images and generates prompts.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.style_transfer import StyleTransferProcessor


def demo_workflow():
    """Demonstrate the style transfer workflow with example explanations"""
    
    print("🎨 PhotoGen Style Transfer Workflow Demo")
    print("=" * 50)
    print()
    print("📋 WORKFLOW CONCEPT:")
    print("1. 📸 Selfie (Plain Background)")
    print("   → Analyze person: pose, clothing, expression, lighting")
    print("   → Identify background: plain/simple for easy replacement")
    print()
    print("2. 🌅 Style Reference (Scene Background)")  
    print("   → Analyze scene: environment, colors, mood, lighting style")
    print("   → Extract style elements: atmosphere, color palette, setting")
    print()
    print("3. ✨ Generated Result")
    print("   → Combine person from selfie with style from reference")
    print("   → Maintain identity while applying new background & lighting")
    print("   → Create natural, realistic integration")
    print()
    
    # Check if we have test images available
    test_images_dir = Path("test_images")
    
    if not test_images_dir.exists():
        print("📂 Test Images Directory Not Found")
        print("To run a real demo, you would need:")
        print("  - A selfie with plain/simple background")
        print("  - A style reference image with interesting scene/background")
        print()
        print("Example file structure:")
        print("  test_images/")
        print("    selfies/")
        print("      plain_bg_selfie.jpg")
        print("    style_references/")
        print("      beach_sunset.jpg")
        print("      forest_scene.jpg")
        print("      city_lights.jpg")
        print()
        return
    
    # Look for example images
    example_selfie = None
    example_style = None
    
    # Check for any images in test_images
    for img_file in test_images_dir.glob("*.{jpg,jpeg,png}"):
        if not example_selfie:
            example_selfie = str(img_file)
        elif not example_style:
            example_style = str(img_file)
            break
    
    if example_selfie and example_style:
        print("🔍 Found Example Images - Running Demo Analysis")
        print("-" * 40)
        print(f"📸 Selfie: {Path(example_selfie).name}")
        print(f"🎨 Style Reference: {Path(example_style).name}")
        print()
        
        try:
            # Initialize processor
            processor = StyleTransferProcessor()
            
            print("🔍 Analyzing selfie...")
            selfie_analysis = processor.analyze_selfie(example_selfie)
            
            print("🎨 Analyzing style reference...")
            style_analysis = processor.analyze_style_reference(example_style)
            
            print("✍️ Generating style transfer prompt...")
            transfer_prompt = processor.generate_style_transfer_prompt(
                selfie_analysis, style_analysis
            )
            
            # Display results
            print("\n📊 ANALYSIS RESULTS:")
            print("=" * 20)
            
            # Selfie analysis summary
            print("\n📸 SELFIE ANALYSIS:")
            person_details = selfie_analysis.get('person_details', {})
            if person_details.get('pose'):
                print(f"👤 Pose: {person_details['pose'][:100]}...")
            if person_details.get('clothing'):
                print(f"👕 Clothing: {person_details['clothing'][:100]}...")
            if person_details.get('facial_expression'):
                print(f"😊 Expression: {person_details['facial_expression'][:100]}...")
            
            background_info = selfie_analysis.get('background_info', {})
            if background_info.get('description'):
                print(f"🖼️ Background: {background_info['description'][:100]}...")
            print(f"🎯 Plain Background: {'Yes' if background_info.get('is_plain') else 'No'}")
            
            # Style analysis summary
            print("\n🎨 STYLE REFERENCE ANALYSIS:")
            scene_details = style_analysis.get('scene_description', {})
            if scene_details.get('environment'):
                print(f"🌍 Environment: {scene_details['environment'][:100]}...")
            if scene_details.get('indoor_outdoor'):
                print(f"🏠 Location: {scene_details['indoor_outdoor']}")
            
            color_palette = style_analysis.get('color_palette', {})
            if color_palette.get('dominant_colors'):
                print(f"🎨 Colors: {color_palette['dominant_colors'][:100]}...")
            
            mood_info = style_analysis.get('mood_atmosphere', {})
            if mood_info.get('atmosphere'):
                print(f"✨ Mood: {mood_info['atmosphere'][:100]}...")
            
            # Generated prompt
            print("\n✍️ GENERATED STYLE TRANSFER PROMPT:")
            print("-" * 40)
            print(transfer_prompt)
            print()
            
            print("✅ Demo analysis complete!")
            print()
            print("🚀 NEXT STEPS:")
            print("1. Run the full workflow:")
            print(f"   python scripts/style_transfer_workflow.py \"{example_selfie}\" \"{example_style}\"")
            print()
            print("2. Use the GUI:")
            print("   python scripts/style_transfer_gui.py")
            print()
            print("3. Analyze only (no generation):")
            print(f"   python scripts/style_transfer_workflow.py \"{example_selfie}\" \"{example_style}\" --analyze-only")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            print()
            print("💡 Make sure you have:")
            print("1. API key configured: python scripts/style_transfer_workflow.py --setup-key")
            print("2. Required dependencies installed")
    
    else:
        print("📋 EXAMPLE WORKFLOW SCENARIOS:")
        print()
        print("🌅 Scenario 1: Beach Sunset Style")
        print("  📸 Input: Selfie with plain white wall background")
        print("  🎨 Style: Beach sunset with warm orange/pink lighting")
        print("  ✨ Result: Person in same pose but with beach sunset background")
        print("           matching warm lighting and colors")
        print()
        
        print("🌲 Scenario 2: Forest Adventure Style")
        print("  📸 Input: Selfie with plain background")
        print("  🎨 Style: Dense forest with dappled sunlight")
        print("  ✨ Result: Person appears to be in the forest with")
        print("           natural lighting filtering through trees")
        print()
        
        print("🏙️ Scenario 3: City Night Style")
        print("  📸 Input: Selfie with simple background")
        print("  🎨 Style: City skyline at night with neon lights")
        print("  ✨ Result: Person with urban nighttime atmosphere,")
        print("           colorful city lights reflecting on them")
        print()
        
        print("📝 TO GET STARTED:")
        print("1. Add example images to test_images/ directory")
        print("2. Configure API key: python scripts/style_transfer_workflow.py --setup-key")
        print("3. Run workflow: python scripts/style_transfer_workflow.py selfie.jpg style.jpg")
        print("4. Or use GUI: python scripts/style_transfer_gui.py")


def show_technical_details():
    """Show technical implementation details"""
    print()
    print("🔧 TECHNICAL IMPLEMENTATION:")
    print("=" * 30)
    print()
    print("📋 Analysis Pipeline:")
    print("1. Vision Analysis (Qwen-VL-Max)")
    print("   → Comprehensive scene understanding")
    print("   → Object/person detection and description")
    print("   → Color, lighting, mood extraction")
    print()
    print("2. Structured Data Extraction")
    print("   → Person details: pose, clothing, expression")
    print("   → Background analysis: complexity, type, colors")
    print("   → Style elements: mood, atmosphere, lighting style")
    print()
    print("3. Intelligent Prompt Generation")
    print("   → Combine person characteristics with style elements")
    print("   → Preserve identity while applying new background")
    print("   → Include technical quality instructions")
    print()
    print("4. Image Generation")
    print("   → Use optimized prompt with image generation model")
    print("   → High-resolution output with natural integration")
    print("   → Maintain photorealistic quality")
    print()
    
    print("🎯 Key Features:")
    print("• Automatic person/background separation analysis")
    print("• Style preservation with identity maintenance")
    print("• Intelligent lighting and color matching")
    print("• Batch processing capabilities")
    print("• Comprehensive workflow logging")
    print("• GUI and command-line interfaces")


if __name__ == "__main__":
    demo_workflow()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--technical":
        show_technical_details()
