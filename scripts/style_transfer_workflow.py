#!/usr/bin/env python3
"""
Style Transfer Workflow Script
Implements: Selfie + Style Reference → Stylized Result

Usage:
    python scripts/style_transfer_workflow.py <selfie_path> <style_reference_path> [options]

Examples:
    # Basic style transfer
    python scripts/style_transfer_workflow.py "selfie.jpg" "beach_scene.jpg"
    
    # With custom output directory
    python scripts/style_transfer_workflow.py "selfie.jpg" "sunset.jpg" --output-dir "my_results"
    
    # Analyze only (no generation)
    python scripts/style_transfer_workflow.py "selfie.jpg" "forest.jpg" --analyze-only
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.style_transfer import StyleTransferProcessor
from core.secure_storage import SecureStorage


def setup_api_key():
    """Setup API key for the first time"""
    print("🔑 Setting up API key...")
    
    secure_storage = SecureStorage()
    
    # Check if we already have a key
    existing_key = secure_storage.load_api_key("Qwen-VL-Max (Alibaba Cloud)")
    if existing_key:
        print("✅ API key already configured!")
        return True
    
    print("\nTo use the style transfer feature, you need to configure your Qwen-VL-Max API key.")
    print("You can get one from: https://dashscope.console.aliyun.com/")
    
    api_key = input("\nEnter your Qwen-VL-Max API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided.")
        return False
    
    try:
        secure_storage.save_api_key("Qwen-VL-Max (Alibaba Cloud)", api_key)
        print("✅ API key stored securely!")
        return True
    except Exception as e:
        print(f"❌ Failed to store API key: {e}")
        return False


def validate_image_path(path: str) -> bool:
    """Validate that image path exists and is a supported format"""
    if not os.path.exists(path):
        print(f"❌ Image not found: {path}")
        return False
    
    supported_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']
    file_ext = Path(path).suffix.lower()
    
    if file_ext not in supported_extensions:
        print(f"❌ Unsupported image format: {file_ext}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return False
    
    return True


def display_analysis_summary(analysis: dict, title: str):
    """Display a formatted summary of image analysis"""
    print(f"\n📊 {title}")
    print("=" * (len(title) + 4))
    
    # Basic info
    if 'image_path' in analysis:
        print(f"📁 Image: {Path(analysis['image_path']).name}")
    
    if title == "Selfie Analysis":
        # Person details
        person_details = analysis.get('person_details', {})
        if person_details.get('pose'):
            print(f"👤 Pose: {person_details['pose'][:100]}...")
        if person_details.get('clothing'):
            print(f"👕 Clothing: {person_details['clothing'][:100]}...")
        if person_details.get('facial_expression'):
            print(f"😊 Expression: {person_details['facial_expression'][:100]}...")
        
        # Background info
        background_info = analysis.get('background_info', {})
        if background_info.get('description'):
            print(f"🖼️ Background: {background_info['description'][:100]}...")
        if background_info.get('is_plain'):
            print(f"🎯 Plain Background: {'Yes' if background_info['is_plain'] else 'No'}")
    
    elif title == "Style Reference Analysis":
        # Scene details
        scene_details = analysis.get('scene_description', {})
        if scene_details.get('environment'):
            print(f"🌍 Environment: {scene_details['environment'][:100]}...")
        if scene_details.get('indoor_outdoor'):
            print(f"🏠 Location: {scene_details['indoor_outdoor']}")
        
        # Color palette
        color_palette = analysis.get('color_palette', {})
        if color_palette.get('dominant_colors'):
            print(f"🎨 Colors: {color_palette['dominant_colors'][:100]}...")
        
        # Mood
        mood_info = analysis.get('mood_atmosphere', {})
        if mood_info.get('atmosphere'):
            print(f"✨ Mood: {mood_info['atmosphere'][:100]}...")


def main():
    parser = argparse.ArgumentParser(
        description="Style Transfer Workflow: Selfie + Style Reference → Stylized Result",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/style_transfer_workflow.py selfie.jpg beach_scene.jpg
    python scripts/style_transfer_workflow.py portrait.png sunset.jpg --output-dir results
    python scripts/style_transfer_workflow.py selfie.jpg forest.jpg --analyze-only
        """
    )
    
    parser.add_argument('selfie_path', 
                       nargs='?',  # Make optional
                       help='Path to the selfie image (plain background)')
    
    parser.add_argument('style_reference_path', 
                       nargs='?',  # Make optional
                       help='Path to the style reference image (scene background)')
    
    parser.add_argument('--output-dir', '-o', 
                       default='outputs',
                       help='Output directory for results (default: outputs)')
    
    parser.add_argument('--analyze-only', '-a', 
                       action='store_true',
                       help='Only analyze images, do not generate styled result')
    
    parser.add_argument('--setup-key', 
                       action='store_true',
                       help='Setup API key')
    
    parser.add_argument('--save-analyses', '-s', 
                       action='store_true',
                       help='Save individual analysis results to JSON files')
    
    args = parser.parse_args()
    
    # Handle API key setup
    if args.setup_key:
        success = setup_api_key()
        sys.exit(0 if success else 1)
    
    # Check required arguments for non-setup operations
    if not args.selfie_path or not args.style_reference_path:
        print("❌ Both selfie_path and style_reference_path are required for processing.")
        print("Use --setup-key to configure API key only.")
        sys.exit(1)
    
    # Validate inputs
    print("🔍 Validating inputs...")
    
    if not validate_image_path(args.selfie_path):
        sys.exit(1)
    
    if not validate_image_path(args.style_reference_path):
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check API key
    secure_storage = SecureStorage()
    api_key = secure_storage.load_api_key("Qwen-VL-Max (Alibaba Cloud)")
    if not api_key:
        print("❌ No API key configured. Run with --setup-key first.")
        sys.exit(1)
    
    try:
        # Initialize style transfer processor
        print("🚀 Initializing style transfer processor...")
        processor = StyleTransferProcessor()
        
        if args.analyze_only:
            print("\n📸 ANALYSIS MODE - Analyzing images only")
            print("=" * 50)
            
            # Analyze selfie
            print("🔍 Analyzing selfie...")
            selfie_analysis = processor.analyze_selfie(args.selfie_path)
            display_analysis_summary(selfie_analysis, "Selfie Analysis")
            
            # Analyze style reference
            print("\n🎨 Analyzing style reference...")
            style_analysis = processor.analyze_style_reference(args.style_reference_path)
            display_analysis_summary(style_analysis, "Style Reference Analysis")
            
            # Generate and display prompt
            print("\n✍️ Generated Style Transfer Prompt:")
            print("-" * 40)
            transfer_prompt = processor.generate_style_transfer_prompt(
                selfie_analysis, style_analysis
            )
            print(transfer_prompt)
            
            # Save analyses if requested
            if args.save_analyses:
                timestamp = int(datetime.now().timestamp())
                
                selfie_analysis_path = os.path.join(args.output_dir, f"selfie_analysis_{timestamp}.json")
                with open(selfie_analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(selfie_analysis, f, indent=2, ensure_ascii=False)
                
                style_analysis_path = os.path.join(args.output_dir, f"style_analysis_{timestamp}.json")
                with open(style_analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(style_analysis, f, indent=2, ensure_ascii=False)
                
                prompt_path = os.path.join(args.output_dir, f"transfer_prompt_{timestamp}.txt")
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    f.write(transfer_prompt)
                
                print(f"\n💾 Analyses saved:")
                print(f"   Selfie: {selfie_analysis_path}")
                print(f"   Style:  {style_analysis_path}")
                print(f"   Prompt: {prompt_path}")
            
        else:
            print("\n🎨 FULL WORKFLOW - Generating stylized result")
            print("=" * 50)
            
            # Run complete workflow
            results = processor.process_style_transfer_workflow(
                args.selfie_path,
                args.style_reference_path,
                args.output_dir
            )
            
            # Display results summary
            print("\n📊 WORKFLOW RESULTS:")
            print("=" * 20)
            print(f"✅ Success: {results['generation_success']}")
            if 'output_prompt_file' in results:
                print(f"📁 Prompt File: {results['output_prompt_file']}")
            if 'note' in results:
                print(f"📝 Note: {results['note']}")
            print(f"📋 Log File: Available in outputs directory")
            
            # Display analyses summaries
            display_analysis_summary(results['analyses']['selfie'], "Selfie Analysis")
            display_analysis_summary(results['analyses']['style_reference'], "Style Reference Analysis")
            
            print(f"\n🎯 Generated Prompt Preview:")
            print("-" * 30)
            prompt_preview = results['generated_prompt'][:200] + "..." if len(results['generated_prompt']) > 200 else results['generated_prompt']
            print(prompt_preview)
        
        print(f"\n✅ Style transfer workflow completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during style transfer workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
