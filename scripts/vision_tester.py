#!/usr/bin/env python3
"""
Vision Model Testing Tool - Standalone
Tests Qwen-VL-Max vision analysis capabilities with comprehensive structured output.
Supports single image or batch processing from folders.
"""
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image
import base64
from io import BytesIO
import logging

# Import existing secure storage
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.secure_storage import SecureStorage

# Import OpenAI for vision API
from openai import OpenAI


class VisionTester:
    """Standalone vision model testing tool"""
    
    def __init__(self):
        self.api_base = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-vl-max"
        self.secure_storage = SecureStorage()
        self.results_dir = "vision_test_results"
        self.ensure_results_directory()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
    def ensure_results_directory(self):
        """Create results directory if it doesn't exist"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            print(f"✅ Created results directory: {self.results_dir}")
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def analyze_single_image(self, image_path: str, api_key: str, 
                           analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze a single image with comprehensive vision analysis
        
        Args:
            image_path: Path to the image file
            api_key: Qwen-VL-Max API key
            analysis_type: Type of analysis (comprehensive, objects, scene, description)
        """
        try:
            # Load and prepare image
            image = Image.open(image_path)
            img_base64 = self._image_to_base64(image)
            
            # Get analysis prompt based on type
            prompt = self._get_analysis_prompt(analysis_type)
            
            # Call vision API
            client = OpenAI(api_key=api_key, base_url=self.api_base)
            
            logging.info(f"🔍 Analyzing image: {image_path}")
            
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            response_text = completion.choices[0].message.content
            
            # Structure the response
            result = {
                "image_path": image_path,
                "image_size": f"{image.size[0]}x{image.size[1]}",
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "raw_response": response_text,
                "structured_analysis": self._parse_vision_response(response_text, analysis_type),
                "api_usage": {
                    "prompt_tokens": completion.usage.prompt_tokens if completion.usage else 0,
                    "completion_tokens": completion.usage.completion_tokens if completion.usage else 0,
                    "total_tokens": completion.usage.total_tokens if completion.usage else 0
                }
            }
            
            logging.info(f"✅ Analysis completed for {image_path}")
            return result
            
        except Exception as e:
            logging.error(f"❌ Error analyzing {image_path}: {e}")
            return {
                "image_path": image_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_analysis_prompt(self, analysis_type: str) -> str:
        """Get the appropriate prompt based on analysis type"""
        
        prompts = {
            "comprehensive": """Analyze this image in detail and provide a comprehensive structured analysis. Include:

1. GENERAL DESCRIPTION: Overall scene description
2. OBJECTS: List all significant objects with their locations and descriptions
3. PEOPLE: Describe any people, their poses, clothing, and activities
4. ENVIRONMENT: Setting, location type, indoor/outdoor, lighting conditions
5. COLORS: Dominant colors and color scheme
6. COMPOSITION: Layout, perspective, focal points
7. STYLE: Photography style, mood, artistic elements
8. TECHNICAL: Image quality, resolution observations, any technical issues
9. CONTEXT: Likely purpose or context of the image

Please be detailed and specific in your analysis.""",

            "objects": """Focus on identifying and describing all objects in this image. For each object, provide:
- Object name/type
- Location in image (general position)
- Size relative to other objects
- Color and material
- Condition and notable features
- Relationship to other objects

Be thorough and systematic in your object identification.""",

            "scene": """Analyze the scene and environment in this image. Focus on:
- Location type and setting
- Indoor or outdoor environment
- Lighting conditions and sources
- Weather (if applicable)
- Time of day (if determinable)
- Overall atmosphere and mood
- Spatial relationships and layout
- Background and foreground elements

Provide a detailed scene analysis.""",

            "description": """Provide a detailed, natural description of this image as if describing it to someone who cannot see it. Include:
- What is happening in the image
- Who or what is present
- Where it appears to be taken
- The overall mood and feeling
- Important visual details
- Colors, textures, and visual elements

Write in clear, descriptive language."""
        }
        
        return prompts.get(analysis_type, prompts["comprehensive"])
    
    def _parse_vision_response(self, response_text: str, analysis_type: str) -> Dict[str, Any]:
        """Parse the vision response into structured data"""
        
        # Initialize structured data
        structured = {
            "summary": "",
            "objects": [],
            "people": [],
            "environment": {},
            "colors": [],
            "technical_notes": "",
            "confidence": "unknown"
        }
        
        try:
            # Split into lines and process
            lines = response_text.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers (numbered sections or keywords)
                if line.startswith('### 1.') or 'GENERAL DESCRIPTION' in line.upper():
                    current_section = "summary"
                    current_content = []
                elif line.startswith('### 2.') or 'OBJECTS:' in line:
                    current_section = "objects"
                    current_content = []
                elif line.startswith('### 3.') or 'PEOPLE:' in line:
                    current_section = "people"
                    current_content = []
                elif line.startswith('### 4.') or 'ENVIRONMENT:' in line:
                    current_section = "environment"
                    current_content = []
                elif line.startswith('### 5.') or 'COLORS:' in line:
                    current_section = "colors"
                    current_content = []
                elif line.startswith('### 8.') or 'TECHNICAL:' in line:
                    current_section = "technical_notes"
                    current_content = []
                elif line.startswith('###') and any(keyword in line.upper() for keyword in ['COMPOSITION', 'STYLE', 'CONTEXT']):
                    # Skip these sections or add to technical notes
                    current_section = "technical_notes"
                    current_content = []
                else:
                    # Add content to current section
                    if current_section and line:
                        current_content.append(line)
                        
                        # Process content when we hit a new section or end
                        if line.startswith('###') or line.startswith('**'):
                            continue
                            
                        # Add to appropriate section
                        if current_section == "summary" and not structured["summary"]:
                            # Take first substantial paragraph for summary
                            if len(line) > 50 and not line.startswith('-'):
                                structured["summary"] = line
                        elif current_section == "objects":
                            # Look for object descriptions
                            if line.startswith('- **') and any(keyword in line.lower() for keyword in ['wall', 'floor', 'camera', 'clothing', 'object']):
                                structured["objects"].append(line[3:])  # Remove "- **"
                        elif current_section == "people":
                            # Look for people descriptions
                            if line.startswith('- **') and any(keyword in line.lower() for keyword in ['appearance', 'pose', 'expression', 'activity', 'person']):
                                structured["people"].append(line[3:])  # Remove "- **"
                        elif current_section == "colors":
                            # Look for color descriptions
                            if line.startswith('- **') or 'color' in line.lower():
                                structured["colors"].append(line[3:] if line.startswith('- **') else line)
                        elif current_section == "technical_notes":
                            structured["technical_notes"] += line + " "
            
            # Enhanced parsing for better object detection
            if not structured["objects"]:
                # Alternative parsing - look for object mentions in raw text
                object_keywords = ['elevator', 'wall', 'floor', 'camera', 'clothing', 'necklace', 'top', 'bottom', 'interface']
                for line in lines:
                    if any(keyword in line.lower() for keyword in object_keywords):
                        if '- **' in line and ':' in line:
                            clean_line = line.split(':')[0].replace('- **', '').replace('**', '').strip()
                            if clean_line and clean_line not in structured["objects"]:
                                structured["objects"].append(clean_line)
            
            # Enhanced parsing for people
            if not structured["people"]:
                # Look for people-related content
                people_keywords = ['person', 'individual', 'appearance', 'pose', 'expression', 'stance', 'hair', 'facial']
                for line in lines:
                    if any(keyword in line.lower() for keyword in people_keywords):
                        if ('- **' in line and ':' in line) or line.startswith('- **'):
                            clean_line = line.replace('- **', '').replace('**', '').strip()
                            if clean_line and len(clean_line) > 10:
                                structured["people"].append(clean_line[:100] + "..." if len(clean_line) > 100 else clean_line)
                                if len(structured["people"]) >= 5:  # Limit to avoid too much content
                                    break
            
            # If still no summary, use first paragraph
            if not structured["summary"]:
                for line in lines:
                    if len(line.strip()) > 50 and not line.strip().startswith(('#', '-', '*')):
                        structured["summary"] = line.strip()[:200] + "..." if len(line.strip()) > 200 else line.strip()
                        break
                        
        except Exception as e:
            logging.warning(f"Error parsing response: {e}")
            structured["summary"] = response_text[:300] + "..." if len(response_text) > 300 else response_text
            structured["parsing_error"] = str(e)
        
        return structured
    
    def test_single_image(self, image_path: str, analysis_types: List[str] = None) -> Dict[str, Any]:
        """Test a single image with multiple analysis types"""
        
        if analysis_types is None:
            analysis_types = ["comprehensive"]
        
        # Get API key
        api_key = self.secure_storage.load_api_key("Qwen-VL-Max")
        if not api_key:
            raise ValueError("Qwen-VL-Max API key not found. Please configure it first.")
        
        print(f"🔍 Testing image: {image_path}")
        
        results = {
            "image_path": image_path,
            "test_timestamp": datetime.now().isoformat(),
            "analysis_results": {}
        }
        
        for analysis_type in analysis_types:
            print(f"   📋 Running {analysis_type} analysis...")
            result = self.analyze_single_image(image_path, api_key, analysis_type)
            results["analysis_results"][analysis_type] = result
        
        return results
    
    def test_folder(self, folder_path: str, analysis_types: List[str] = None, 
                   max_images: int = None) -> Dict[str, Any]:
        """Test all images in a folder"""
        
        folder_path = Path(folder_path)
        if not folder_path.exists():
            raise ValueError(f"Folder not found: {folder_path}")
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        image_files = [f for f in folder_path.iterdir() 
                      if f.is_file() and f.suffix.lower() in image_extensions]
        
        if not image_files:
            raise ValueError(f"No image files found in {folder_path}")
        
        # Limit number of images if specified
        if max_images:
            image_files = image_files[:max_images]
        
        print(f"📁 Testing {len(image_files)} images from: {folder_path}")
        
        batch_results = {
            "folder_path": str(folder_path),
            "test_timestamp": datetime.now().isoformat(),
            "total_images": len(image_files),
            "analysis_types": analysis_types or ["comprehensive"],
            "results": []
        }
        
        for i, image_file in enumerate(image_files, 1):
            print(f"\\n🖼️  Image {i}/{len(image_files)}: {image_file.name}")
            try:
                result = self.test_single_image(str(image_file), analysis_types)
                batch_results["results"].append(result)
            except Exception as e:
                print(f"❌ Error processing {image_file.name}: {e}")
                batch_results["results"].append({
                    "image_path": str(image_file),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return batch_results
    
    def save_results(self, results: Dict[str, Any], output_name: str = None) -> str:
        """Save test results to JSON file"""
        
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"vision_test_{timestamp}.json"
        
        output_path = Path(self.results_dir) / output_name
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_path}")
        return str(output_path)
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a text summary of the test results"""
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("VISION MODEL TEST SUMMARY REPORT")
        report_lines.append("=" * 60)
        
        if "folder_path" in results:
            # Batch results
            report_lines.append(f"Folder: {results['folder_path']}")
            report_lines.append(f"Total Images: {results['total_images']}")
            report_lines.append(f"Analysis Types: {', '.join(results['analysis_types'])}")
            
            successful = len([r for r in results['results'] if 'error' not in r])
            failed = len(results['results']) - successful
            
            report_lines.append(f"Successful: {successful}")
            report_lines.append(f"Failed: {failed}")
            report_lines.append("")
            
            # Sample results
            for i, result in enumerate(results['results'][:3], 1):
                if 'error' not in result:
                    report_lines.append(f"Sample {i}: {Path(result['image_path']).name}")
                    for analysis_type, analysis in result['analysis_results'].items():
                        if 'structured_analysis' in analysis:
                            summary = analysis['structured_analysis'].get('summary', 'No summary')[:100]
                            report_lines.append(f"  {analysis_type}: {summary}...")
                    report_lines.append("")
        else:
            # Single image results
            report_lines.append(f"Image: {results['image_path']}")
            for analysis_type, analysis in results['analysis_results'].items():
                report_lines.append(f"\\n{analysis_type.upper()} ANALYSIS:")
                if 'structured_analysis' in analysis:
                    struct = analysis['structured_analysis']
                    if struct.get('summary'):
                        report_lines.append(f"Summary: {struct['summary']}")
                    if struct.get('objects'):
                        report_lines.append(f"Objects: {', '.join(struct['objects'][:5])}")
                    if struct.get('people'):
                        report_lines.append(f"People: {', '.join(struct['people'])}")
        
        return "\\n".join(report_lines)


def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(description="Vision Model Testing Tool")
    parser.add_argument("path", nargs="?", help="Path to image file or folder")
    parser.add_argument("--analysis", nargs="+", 
                       choices=["comprehensive", "objects", "scene", "description"],
                       default=["comprehensive"],
                       help="Types of analysis to run")
    parser.add_argument("--max-images", type=int, 
                       help="Maximum number of images to process (for folders)")
    parser.add_argument("--output", help="Output filename for results")
    parser.add_argument("--setup-key", action="store_true", 
                       help="Setup Qwen-VL-Max API key")
    
    args = parser.parse_args()
    
    tester = VisionTester()
    
    # Setup API key if requested
    if args.setup_key:
        api_key = input("Enter your Qwen-VL-Max API key: ").strip()
        if api_key:
            tester.secure_storage.save_api_key("Qwen-VL-Max", api_key)
            print("✅ API key saved securely!")
        else:
            print("❌ No API key provided")
        return
    
    # Check if path is provided for analysis
    if not args.path:
        print("❌ Path argument is required for image analysis")
        print("Use --setup-key to configure API key first, or provide a path to analyze")
        parser.print_help()
        return
    
    # Check if API key exists
    api_key = tester.secure_storage.load_api_key("Qwen-VL-Max")
    if not api_key:
        print("❌ Qwen-VL-Max API key not found!")
        print("Please run: python vision_tester.py --setup-key")
        return
    
    try:
        path = Path(args.path)
        
        if path.is_file():
            # Test single image
            results = tester.test_single_image(str(path), args.analysis)
        elif path.is_dir():
            # Test folder
            results = tester.test_folder(str(path), args.analysis, args.max_images)
        else:
            print(f"❌ Path not found: {path}")
            return
        
        # Save results
        output_file = tester.save_results(results, args.output)
        
        # Generate and show summary
        summary = tester.generate_summary_report(results)
        print("\\n" + summary)
        
        print(f"\\n✅ Testing complete! Full results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
