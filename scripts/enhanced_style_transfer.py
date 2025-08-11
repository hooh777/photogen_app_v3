#!/usr/bin/env python3
"""
Enhanced Style Transfer with Background Preservation Options

Provides multiple style transfer modes:
1. Full Background Replacement (original mode)
2. Style-Only Transfer (keep background, apply style)
3. Background Enhancement (keep + enhance background)
4. Selective Element Transfer (minimal background changes)
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.style_transfer import StyleTransferProcessor


class EnhancedStyleTransfer(StyleTransferProcessor):
    """Enhanced style transfer with background preservation options"""
    
    def generate_style_only_prompt(self, selfie_analysis: Dict, style_analysis: Dict) -> str:
        """
        Generate prompt that keeps background but applies style elements
        """
        try:
            # Extract key elements
            person_details = selfie_analysis.get("person_details", {})
            background_info = selfie_analysis.get("background_info", {})
            style_colors = style_analysis.get("color_palette", {})
            style_lighting = style_analysis.get("lighting_style", {})
            style_mood = style_analysis.get("mood_atmosphere", {})
            
            # Build prompt that preserves background structure
            prompt_parts = []
            
            # Person description (keep exact)
            if person_details.get("appearance"):
                prompt_parts.append(f"Person: {person_details['appearance']}")
            
            if person_details.get("pose"):
                prompt_parts.append(f"Pose: {person_details['pose']}")
            
            if person_details.get("clothing"):
                prompt_parts.append(f"Clothing: {person_details['clothing']}")
            
            # Background preservation instruction
            if background_info.get("description"):
                prompt_parts.append(f"Background: Keep original background structure - {background_info['description']}")
            
            # Style application (colors, lighting, mood only)
            if style_colors.get("dominant_colors"):
                prompt_parts.append(f"Apply color palette: {style_colors['dominant_colors']}")
            
            if style_lighting.get("type"):
                prompt_parts.append(f"Apply lighting style: {style_lighting['type']}")
            
            if style_mood.get("atmosphere"):
                prompt_parts.append(f"Apply mood/atmosphere: {style_mood['atmosphere']}")
            
            # Combine into final prompt
            base_prompt = ", ".join(prompt_parts)
            
            # Add style-only transfer instructions
            style_prompt = f"""
{base_prompt}

Style-only transfer requirements:
- PRESERVE the original background structure and layout
- MAINTAIN the same environment and setting
- APPLY only the color palette from style reference
- APPLY only the lighting style from style reference  
- APPLY only the mood/atmosphere from style reference
- Keep person's identity, pose, and clothing unchanged
- DO NOT change the background environment or add new objects
- Enhance the existing background with new lighting and colors
- Create natural color grading that matches the style reference

Style: photorealistic, enhanced color grading, atmospheric lighting
Quality: high resolution, natural color transitions, preserved details
"""
            
            return style_prompt.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate style-only prompt: {str(e)}")
    
    def generate_background_enhancement_prompt(self, selfie_analysis: Dict, style_analysis: Dict) -> str:
        """
        Generate prompt that enhances background with style elements
        """
        try:
            # Extract key elements
            person_details = selfie_analysis.get("person_details", {})
            background_info = selfie_analysis.get("background_info", {})
            scene_details = style_analysis.get("scene_description", {})
            style_colors = style_analysis.get("color_palette", {})
            style_lighting = style_analysis.get("lighting_style", {})
            
            prompt_parts = []
            
            # Person description (preserve)
            if person_details.get("pose"):
                prompt_parts.append(f"Person: {person_details['pose']}")
            if person_details.get("clothing"):
                prompt_parts.append(f"Clothing: {person_details['clothing']}")
            
            # Enhanced background description
            if background_info.get("description"):
                original_bg = background_info['description']
                if scene_details.get("environment"):
                    style_elements = scene_details['environment']
                    prompt_parts.append(f"Enhanced background: {original_bg} enhanced with atmospheric elements inspired by {style_elements}")
                else:
                    prompt_parts.append(f"Enhanced background: {original_bg} with enhanced lighting and atmosphere")
            
            # Style enhancement instructions
            if style_colors.get("dominant_colors"):
                prompt_parts.append(f"Color enhancement: {style_colors['dominant_colors']}")
            
            if style_lighting.get("type"):
                prompt_parts.append(f"Lighting enhancement: {style_lighting['type']}")
            
            base_prompt = ", ".join(prompt_parts)
            
            enhancement_prompt = f"""
{base_prompt}

Background enhancement requirements:
- KEEP the original background as the base
- ENHANCE the background with atmospheric elements from style reference
- ADD subtle environmental effects (lighting, mood, atmosphere)
- MAINTAIN the original spatial layout and structure
- ENHANCE colors and lighting to match style reference mood
- Keep person exactly the same (pose, clothing, expression)
- Create seamless integration between enhanced background and person
- Add depth and atmosphere without changing the fundamental environment

Style: enhanced realism, atmospheric enhancement, cinematic lighting
Quality: high resolution, natural enhancement, preserved authenticity
"""
            
            return enhancement_prompt.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate enhancement prompt: {str(e)}")
    
    def generate_selective_transfer_prompt(self, selfie_analysis: Dict, style_analysis: Dict) -> str:
        """
        Generate prompt for minimal background changes with selective style elements
        """
        try:
            person_details = selfie_analysis.get("person_details", {})
            background_info = selfie_analysis.get("background_info", {})
            style_colors = style_analysis.get("color_palette", {})
            style_mood = style_analysis.get("mood_atmosphere", {})
            
            prompt_parts = []
            
            # Person (unchanged)
            if person_details.get("pose"):
                prompt_parts.append(f"Person: {person_details['pose']}")
            if person_details.get("clothing"):
                prompt_parts.append(f"Clothing: {person_details['clothing']}")
            
            # Background (minimal changes)
            if background_info.get("description"):
                prompt_parts.append(f"Background: {background_info['description']} with subtle style influences")
            
            # Selective style application
            color_note = ""
            mood_note = ""
            
            if style_colors.get("dominant_colors"):
                color_note = f"Subtle color influence: {style_colors['dominant_colors'][:100]}"
            
            if style_mood.get("atmosphere"):
                mood_note = f"Subtle mood influence: {style_mood['atmosphere'][:100]}"
            
            if color_note:
                prompt_parts.append(color_note)
            if mood_note:
                prompt_parts.append(mood_note)
            
            base_prompt = ", ".join(prompt_parts)
            
            selective_prompt = f"""
{base_prompt}

Selective transfer requirements:
- MINIMAL changes to original background
- KEEP background structure 95% the same
- Apply SUBTLE color adjustments inspired by style reference
- Apply GENTLE mood enhancement inspired by style reference
- NO major environmental changes
- NO new objects or architectural elements
- PRESERVE original lighting as primary source
- ADD only subtle atmospheric enhancement
- Focus on gentle color grading and mood adjustment
- Maintain natural, realistic appearance

Style: subtle enhancement, natural color grading, minimal intervention
Quality: high resolution, authentic feel, gentle improvements
"""
            
            return selective_prompt.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate selective prompt: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Style Transfer with Background Preservation Options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transfer Modes:
    --mode full         : Complete background replacement (default)
    --mode style-only   : Keep background, apply style (colors/lighting/mood)
    --mode enhance      : Keep background, enhance with style elements  
    --mode selective    : Minimal changes, subtle style influence

Examples:
    python scripts/enhanced_style_transfer.py selfie.jpg style.jpg --mode style-only
    python scripts/enhanced_style_transfer.py selfie.jpg style.jpg --mode enhance
    python scripts/enhanced_style_transfer.py selfie.jpg style.jpg --mode selective
        """
    )
    
    parser.add_argument('selfie_path', 
                       nargs='?',
                       help='Path to the selfie image')
    
    parser.add_argument('style_reference_path', 
                       nargs='?',
                       help='Path to the style reference image')
    
    parser.add_argument('--mode', '-m',
                       choices=['full', 'style-only', 'enhance', 'selective'],
                       default='full',
                       help='Style transfer mode (default: full)')
    
    parser.add_argument('--output-dir', '-o', 
                       default='outputs',
                       help='Output directory for results (default: outputs)')
    
    parser.add_argument('--analyze-only', '-a', 
                       action='store_true',
                       help='Only analyze images and generate prompts')
    
    parser.add_argument('--setup-key', 
                       action='store_true',
                       help='Setup API key')
    
    args = parser.parse_args()
    
    # Handle API key setup
    if args.setup_key:
        print("🔑 Use the main style transfer script to setup API key:")
        print("python scripts/style_transfer_workflow.py --setup-key")
        return
    
    # Check required arguments
    if not args.selfie_path or not args.style_reference_path:
        print("❌ Both selfie_path and style_reference_path are required.")
        print("Use --setup-key to configure API key only.")
        return
    
    try:
        # Initialize enhanced processor
        print(f"🚀 Initializing enhanced style transfer processor...")
        print(f"📋 Mode: {args.mode}")
        
        processor = EnhancedStyleTransfer()
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        print("🔍 Analyzing selfie...")
        selfie_analysis = processor.analyze_selfie(args.selfie_path)
        
        print("🎨 Analyzing style reference...")
        style_analysis = processor.analyze_style_reference(args.style_reference_path)
        
        # Generate appropriate prompt based on mode
        print(f"✍️ Generating {args.mode} transfer prompt...")
        
        if args.mode == 'style-only':
            transfer_prompt = processor.generate_style_only_prompt(selfie_analysis, style_analysis)
            mode_description = "Style-only transfer (keep background, apply colors/lighting/mood)"
        elif args.mode == 'enhance':
            transfer_prompt = processor.generate_background_enhancement_prompt(selfie_analysis, style_analysis)
            mode_description = "Background enhancement (keep + enhance with style elements)"
        elif args.mode == 'selective':
            transfer_prompt = processor.generate_selective_transfer_prompt(selfie_analysis, style_analysis)
            mode_description = "Selective transfer (minimal changes, subtle style influence)"
        else:  # full
            transfer_prompt = processor.generate_style_transfer_prompt(selfie_analysis, style_analysis)
            mode_description = "Full background replacement (original mode)"
        
        # Display results
        print(f"\n📊 ENHANCED STYLE TRANSFER RESULTS")
        print("=" * 50)
        print(f"🎯 Mode: {mode_description}")
        print()
        
        # Display analysis summaries
        print("📸 SELFIE ANALYSIS:")
        person_details = selfie_analysis.get('person_details', {})
        if person_details.get('pose'):
            print(f"👤 Pose: {person_details['pose'][:100]}...")
        if person_details.get('clothing'):
            print(f"👕 Clothing: {person_details['clothing'][:100]}...")
        
        background_info = selfie_analysis.get('background_info', {})
        if background_info.get('description'):
            print(f"🖼️ Background: {background_info['description'][:100]}...")
        print(f"🎯 Plain Background: {'Yes' if background_info.get('is_plain') else 'No'}")
        
        print("\n🎨 STYLE REFERENCE ANALYSIS:")
        scene_details = style_analysis.get('scene_description', {})
        if scene_details.get('environment'):
            print(f"🌍 Environment: {scene_details['environment'][:100]}...")
        
        color_palette = style_analysis.get('color_palette', {})
        if color_palette.get('dominant_colors'):
            print(f"🎨 Colors: {color_palette['dominant_colors'][:100]}...")
        
        mood_info = style_analysis.get('mood_atmosphere', {})
        if mood_info.get('atmosphere'):
            print(f"✨ Mood: {mood_info['atmosphere'][:100]}...")
        
        # Show generated prompt
        print(f"\n✍️ GENERATED {args.mode.upper()} PROMPT:")
        print("-" * 50)
        print(transfer_prompt)
        
        # Save prompt
        from datetime import datetime
        timestamp = int(datetime.now().timestamp())
        prompt_filename = f"enhanced_style_transfer_{args.mode}_{timestamp}.txt"
        prompt_path = os.path.join(args.output_dir, prompt_filename)
        
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(f"Mode: {mode_description}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Selfie: {args.selfie_path}\n")
            f.write(f"Style Reference: {args.style_reference_path}\n\n")
            f.write("Generated Prompt:\n")
            f.write("-" * 20 + "\n")
            f.write(transfer_prompt)
        
        print(f"\n💾 Enhanced prompt saved to: {prompt_path}")
        print("✅ Enhanced style transfer analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    main()
