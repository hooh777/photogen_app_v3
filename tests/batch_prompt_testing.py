"""
Scientific Batch Testing System for Auto-Generated Prompts
Tests prompt enhancement effectiveness across multiple scenarios with comprehensive analysis.
"""
import json
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple
from PIL import Image
import shutil
from pathlib import Path

# Import our existing systems
from core.handlers.generation_manager import GenerationManager
# from analyze_generation_result import PostGenerationAnalyzer  # File not found


class BatchPromptTester:
    """Scientific batch testing system for prompt enhancement effectiveness"""
    
    def __init__(self):
        self.test_results_dir = "batch_test_results"
        self.test_images_dir = "test_images"
        self.generation_manager = GenerationManager()
        # self.post_analyzer = PostGenerationAnalyzer()  # Disabled - file not found
        
        # Test configuration
        self.fixed_seed = 42  # For reproducibility
        self.model_settings = {
            "steps": 30,
            "guidance": 7.5,
            "aspect_ratio": "Match Input"
        }
        
        # Ensure test results directory
        self.ensure_test_directory()
        
    def ensure_test_directory(self):
        """Create test results directory structure"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_session_dir = os.path.join(self.test_results_dir, f"test_session_{timestamp}")
        
        subdirs = [
            "generated_images",
            "merged_images", 
            "analysis_results",
            "comparison_reports",
            "session_logs"
        ]
        
        for subdir in subdirs:
            os.makedirs(os.path.join(self.test_session_dir, subdir), exist_ok=True)
            
        print(f"✅ Created test session directory: {self.test_session_dir}")
    
    def create_test_cases(self) -> List[Dict[str, Any]]:
        """Create comprehensive test cases from existing test images"""
        
        test_cases = []
        
        # Define test scenarios with different prompt enhancement levels
        enhancement_levels = [
            {
                "name": "baseline",
                "description": "Original prompt only - no enhancement",
                "use_scale_analysis": False,
                "use_duplication_prevention": False,
                "use_integration_enhancement": False
            },
            {
                "name": "scale_optimized", 
                "description": "Scale analysis + size guidance",
                "use_scale_analysis": True,
                "use_duplication_prevention": False,
                "use_integration_enhancement": False
            },
            {
                "name": "duplication_prevented",
                "description": "Duplication prevention + integration focus",
                "use_scale_analysis": False,
                "use_duplication_prevention": True,
                "use_integration_enhancement": True
            },
            {
                "name": "fully_enhanced",
                "description": "All enhancements: scale + duplication prevention + integration",
                "use_scale_analysis": True,
                "use_duplication_prevention": True,
                "use_integration_enhancement": True
            }
        ]
        
        # Define test prompts for different scenarios
        test_prompts = [
            {
                "category": "human_holding",
                "prompt": "person holding object naturally in their hand",
                "focus": "Human interaction, natural pose preservation"
            },
            {
                "category": "table_placement",
                "prompt": "object placed on wooden table surface",
                "focus": "Surface interaction, realistic physics"
            },
            {
                "category": "studio_photography",
                "prompt": "professional product photography with studio lighting",
                "focus": "Commercial quality, lighting consistency"
            },
            {
                "category": "casual_lifestyle",
                "prompt": "casual lifestyle photography with natural lighting",
                "focus": "Realistic integration, natural atmosphere"
            },
            {
                "category": "detailed_scene",
                "prompt": "colorful floral-patterned object with intricate details in elegant setting",
                "focus": "Complex object preservation, detailed integration"
            }
        ]
        
        # Get available test image pairs
        image_pairs = self._get_test_image_pairs()
        
        # Create test cases: each image pair × each prompt × each enhancement level
        test_id = 1
        for image_pair in image_pairs[:4]:  # Limit to 4 image pairs for 20 test cases
            for prompt_config in test_prompts:
                for enhancement in enhancement_levels:
                    if test_id > 20:  # Limit to 20 test cases as requested
                        break
                        
                    test_case = {
                        "test_id": test_id,
                        "image_pair": image_pair,
                        "prompt_config": prompt_config,
                        "enhancement_level": enhancement,
                        "model_settings": self.model_settings.copy(),
                        "seed": self.fixed_seed + test_id,  # Unique but reproducible seed
                        "status": "pending"
                    }
                    test_cases.append(test_case)
                    test_id += 1
                    
                if test_id > 20:
                    break
            if test_id > 20:
                break
        
        return test_cases[:20]  # Ensure exactly 20 test cases
    
    def _get_test_image_pairs(self) -> List[Dict[str, str]]:
        """Get available object-background image pairs from test_images directory"""
        
        # Look for numbered image pairs in test_images
        image_pairs = []
        test_images_path = Path(self.test_images_dir)
        
        if not test_images_path.exists():
            print(f"⚠️ Test images directory not found: {self.test_images_dir}")
            return []
        
        # Find image files
        image_files = [f for f in os.listdir(self.test_images_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # Group images (assuming pairs like 1.png, 2.png, etc.)
        numbered_images = [f for f in image_files if f.split('.')[0].isdigit()]
        numbered_images.sort(key=lambda x: int(x.split('.')[0]))
        
        # Create pairs (assuming even numbers are objects, odd are backgrounds, or vice versa)
        for i in range(0, len(numbered_images) - 1, 2):
            if i + 1 < len(numbered_images):
                object_img = numbered_images[i]
                background_img = numbered_images[i + 1]
                
                image_pairs.append({
                    "object_path": os.path.join(self.test_images_dir, object_img),
                    "background_path": os.path.join(self.test_images_dir, background_img),
                    "pair_name": f"{object_img.split('.')[0]}_{background_img.split('.')[0]}"
                })
        
        # Also check for specific named files
        specific_pairs = [
            ("crop_vita_tea.png", "GlassCase_[GU]_Side_nonmae.jpg"),
            ("thermalBottle-[Crimson]_R1.jpg", "thermalBottle-[Nude]-.jpg"),
            ("PP_[Momin]_Red_1.jpg", "GlassCase_[GU]_Side_nonmae.jpg")
        ]
        
        for obj_file, bg_file in specific_pairs:
            obj_path = os.path.join(self.test_images_dir, obj_file)
            bg_path = os.path.join(self.test_images_dir, bg_file)
            
            if os.path.exists(obj_path) and os.path.exists(bg_path):
                image_pairs.append({
                    "object_path": obj_path,
                    "background_path": bg_path,
                    "pair_name": f"{obj_file.split('.')[0]}_{bg_file.split('.')[0]}"
                })
        
        print(f"📁 Found {len(image_pairs)} image pairs for testing")
        return image_pairs
    
    def run_batch_test(self, api_key: str, model_choice: str = "Pro API", 
                      real_time_monitoring: bool = True) -> Dict[str, Any]:
        """
        Run comprehensive batch testing with real-time monitoring
        
        Args:
            api_key: API key for image generation and analysis
            model_choice: Model to use for generation
            real_time_monitoring: Enable real-time progress updates
        
        Returns:
            Comprehensive test session results
        """
        
        print("🧪 STARTING SCIENTIFIC BATCH PROMPT TESTING")
        print("=" * 60)
        
        # Create test cases
        test_cases = self.create_test_cases()
        print(f"📋 Created {len(test_cases)} test cases")
        
        # Initialize session tracking
        session_start = datetime.now()
        session_results = {
            "session_id": f"batch_test_{int(session_start.timestamp())}",
            "session_start": session_start.isoformat(),
            "test_configuration": {
                "total_test_cases": len(test_cases),
                "model_choice": model_choice,
                "model_settings": self.model_settings,
                "fixed_seed_base": self.fixed_seed
            },
            "test_cases": [],
            "summary_statistics": {},
            "session_directory": self.test_session_dir
        }
        
        # Execute test cases
        for i, test_case in enumerate(test_cases, 1):
            if real_time_monitoring:
                print(f"\n🔄 EXECUTING TEST {i}/{len(test_cases)}")
                print(f"   📷 Images: {test_case['image_pair']['pair_name']}")
                print(f"   📝 Prompt: {test_case['prompt_config']['category']}")
                print(f"   ⚙️ Enhancement: {test_case['enhancement_level']['name']}")
            
            try:
                # Execute single test case
                test_result = self._execute_test_case(test_case, api_key, model_choice)
                test_result["execution_order"] = i
                session_results["test_cases"].append(test_result)
                
                if real_time_monitoring:
                    status = "✅ SUCCESS" if test_result["success"] else "❌ FAILED"
                    print(f"   {status} - Duration: {test_result.get('execution_time', 0):.1f}s")
                    
                    if test_result["success"] and test_result.get("post_analysis"):
                        overall_assessment = test_result["post_analysis"].get("overall_assessment", {})
                        recommendation = overall_assessment.get("recommendation", "unknown")
                        print(f"   📊 Quality: {recommendation}")
                
                # Brief pause between tests to avoid overwhelming APIs
                time.sleep(2)
                
            except Exception as e:
                error_result = {
                    "test_id": test_case["test_id"],
                    "success": False,
                    "error": str(e),
                    "execution_order": i,
                    "execution_time": 0
                }
                session_results["test_cases"].append(error_result)
                
                if real_time_monitoring:
                    print(f"   ❌ ERROR: {str(e)}")
        
        # Generate session summary
        session_results["session_end"] = datetime.now().isoformat()
        session_results["total_execution_time"] = (datetime.now() - session_start).total_seconds()
        session_results["summary_statistics"] = self._generate_session_statistics(session_results["test_cases"])
        
        # Save session results
        self._save_session_results(session_results)
        
        # Generate comprehensive report
        self._generate_comprehensive_report(session_results)
        
        print(f"\n🎉 BATCH TESTING COMPLETED!")
        print(f"📁 Results saved to: {self.test_session_dir}")
        print(f"⏱️ Total time: {session_results['total_execution_time']:.1f} seconds")
        print(f"📊 Success rate: {session_results['summary_statistics']['success_rate']:.1f}%")
        
        return session_results
    
    def _execute_test_case(self, test_case: Dict[str, Any], api_key: str, 
                          model_choice: str) -> Dict[str, Any]:
        """Execute a single test case with comprehensive analysis"""
        
        test_start = datetime.now()
        test_id = test_case["test_id"]
        
        try:
            # Load images
            object_image = Image.open(test_case["image_pair"]["object_path"])
            background_image = Image.open(test_case["image_pair"]["background_path"])
            
            # Prepare prompt based on enhancement level
            base_prompt = test_case["prompt_config"]["prompt"]
            enhanced_prompt = self._create_enhanced_prompt(base_prompt, test_case["enhancement_level"], 
                                                         object_image, background_image, api_key)
            
            # Generate image
            generation_result = self._generate_test_image(
                object_image, background_image, enhanced_prompt, test_case, model_choice, api_key
            )
            
            if not generation_result["success"]:
                return {
                    "test_id": test_id,
                    "success": False,
                    "error": f"Generation failed: {generation_result.get('error', 'Unknown error')}",
                    "execution_time": (datetime.now() - test_start).total_seconds()
                }
            
            # Save generated and merged images
            generated_image = generation_result["generated_image"]
            merged_image = generation_result["merged_image"]
            
            generated_path = self._save_test_image(generated_image, test_id, "generated")
            merged_path = self._save_test_image(merged_image, test_id, "merged")
            
            # Run post-generation analysis
            post_analysis = self.post_analyzer.analyze_generation_result(
                generated_image=generated_image,
                merged_image=merged_image,
                original_object=object_image,
                original_background=background_image,
                user_prompt=base_prompt,
                enhanced_prompt=enhanced_prompt,
                api_key=api_key,
                pre_generation_analysis_id=generation_result.get("scale_analysis_id")
            )
            
            # Compile test result
            test_result = {
                "test_id": test_id,
                "success": True,
                "test_case_config": test_case,
                "prompts": {
                    "original_prompt": base_prompt,
                    "enhanced_prompt": enhanced_prompt
                },
                "generated_image_path": generated_path,
                "merged_image_path": merged_path,
                "post_analysis": post_analysis,
                "generation_metadata": generation_result.get("metadata", {}),
                "execution_time": (datetime.now() - test_start).total_seconds()
            }
            
            # Save individual test analysis
            self._save_test_analysis(test_result)
            
            return test_result
            
        except Exception as e:
            return {
                "test_id": test_id,
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - test_start).total_seconds()
            }
    
    def _create_enhanced_prompt(self, base_prompt: str, enhancement_level: Dict[str, Any],
                              object_image: Image.Image, background_image: Image.Image,
                              api_key: str) -> str:
        """Create enhanced prompt based on enhancement level configuration"""
        
        if enhancement_level["name"] == "baseline":
            # No enhancement - return original prompt
            return base_prompt
        
        enhanced_prompt = base_prompt
        
        # Scale analysis enhancement (simplified - scale analyzer removed)
        if enhancement_level.get("use_scale_analysis", False):
            try:
                # Simple fallback scale guidance without complex analysis
                print("ℹ️ Scale analysis requested but analyzer not available - using fallback")
                # Add basic scale guidance
                enhanced_prompt += " ensure proper size and proportions for natural integration"
            except Exception as e:
                print(f"⚠️ Scale analysis failed for test: {e}")
        
        # Add duplication prevention
        if enhancement_level.get("use_duplication_prevention", False):
            duplication_prevention = "create only ONE instance of the object, do not generate multiple copies"
            enhanced_prompt = f"Seamlessly integrate the SINGLE OBJECT, {duplication_prevention}. {enhanced_prompt}"
        
        # Add integration enhancement
        if enhancement_level.get("use_integration_enhancement", False):
            integration_addition = "ensure natural physics with realistic placement, proper shadows, and natural contact points"
            enhanced_prompt += f", {integration_addition}"
        
        return enhanced_prompt
    
    def _generate_test_image(self, object_image: Image.Image, background_image: Image.Image,
                           prompt: str, test_case: Dict[str, Any], model_choice: str, 
                           api_key: str) -> Dict[str, Any]:
        """Generate test image using the generation manager"""
        
        try:
            # Set fixed seed for reproducibility
            random.seed(test_case["seed"])
            
            # Use generation manager to create image
            result_images = self.generation_manager.generate_images(
                prompt=prompt,
                source_image=background_image,
                object_image=object_image,
                aspect_ratio=test_case["model_settings"]["aspect_ratio"],
                steps=test_case["model_settings"]["steps"],
                guidance=test_case["model_settings"]["guidance"],
                model_choice=model_choice,
                api_key=api_key,
                progress=lambda x: None  # Disable progress callback for batch processing
            )
            
            if result_images and len(result_images) > 0:
                return {
                    "success": True,
                    "generated_image": result_images[0],
                    "merged_image": result_images[1] if len(result_images) > 1 else None,
                    "metadata": {
                        "model_choice": model_choice,
                        "seed": test_case["seed"],
                        "settings": test_case["model_settings"]
                    }
                }
            else:
                return {"success": False, "error": "No images generated"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_test_image(self, image: Image.Image, test_id: int, image_type: str) -> str:
        """Save test image and return file path"""
        
        filename = f"test_{test_id:03d}_{image_type}.png"
        filepath = os.path.join(self.test_session_dir, "generated_images", filename)
        
        image.save(filepath, "PNG")
        return filepath
    
    def _save_test_analysis(self, test_result: Dict[str, Any]):
        """Save individual test analysis to JSON file"""
        
        test_id = test_result["test_id"]
        filename = f"test_{test_id:03d}_analysis.json"
        filepath = os.path.join(self.test_session_dir, "analysis_results", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, indent=2, ensure_ascii=False)
    
    def _generate_session_statistics(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive statistics for the test session"""
        
        total_tests = len(test_results)
        successful_tests = [r for r in test_results if r.get("success", False)]
        failed_tests = [r for r in test_results if not r.get("success", False)]
        
        # Basic statistics
        stats = {
            "total_tests": total_tests,
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": (len(successful_tests) / total_tests * 100) if total_tests > 0 else 0,
            "average_execution_time": sum(r.get("execution_time", 0) for r in test_results) / total_tests if total_tests > 0 else 0
        }
        
        # Enhancement level performance
        enhancement_performance = {}
        for test in successful_tests:
            enhancement_name = test.get("test_case_config", {}).get("enhancement_level", {}).get("name", "unknown")
            if enhancement_name not in enhancement_performance:
                enhancement_performance[enhancement_name] = {"count": 0, "satisfactory": 0}
            
            enhancement_performance[enhancement_name]["count"] += 1
            
            # Check if result was satisfactory
            post_analysis = test.get("post_analysis", {})
            overall_assessment = post_analysis.get("overall_assessment", {})
            if overall_assessment.get("recommendation") == "satisfactory":
                enhancement_performance[enhancement_name]["satisfactory"] += 1
        
        # Calculate satisfaction rates
        for enhancement in enhancement_performance:
            count = enhancement_performance[enhancement]["count"]
            satisfactory = enhancement_performance[enhancement]["satisfactory"]
            enhancement_performance[enhancement]["satisfaction_rate"] = (satisfactory / count * 100) if count > 0 else 0
        
        stats["enhancement_performance"] = enhancement_performance
        
        # Duplication detection statistics
        duplication_cases = 0
        for test in successful_tests:
            post_analysis = test.get("post_analysis", {})
            comparison_analysis = post_analysis.get("comparison_analysis", {})
            if comparison_analysis.get("duplication_detected", False):
                duplication_cases += 1
        
        stats["duplication_detection"] = {
            "cases_with_duplication": duplication_cases,
            "duplication_rate": (duplication_cases / len(successful_tests) * 100) if successful_tests else 0
        }
        
        return stats
    
    def _save_session_results(self, session_results: Dict[str, Any]):
        """Save complete session results to JSON file"""
        
        filename = f"session_results_{session_results['session_id']}.json"
        filepath = os.path.join(self.test_session_dir, "session_logs", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_results, f, indent=2, ensure_ascii=False)
    
    def _generate_comprehensive_report(self, session_results: Dict[str, Any]):
        """Generate comprehensive HTML report with images and analysis"""
        
        # This will be implemented in the next step
        # For now, create a markdown report
        
        report_content = self._create_markdown_report(session_results)
        
        report_filename = f"comprehensive_report_{session_results['session_id']}.md"
        report_filepath = os.path.join(self.test_session_dir, "comparison_reports", report_filename)
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Comprehensive report generated: {report_filepath}")
    
    def _create_markdown_report(self, session_results: Dict[str, Any]) -> str:
        """Create detailed markdown report"""
        
        stats = session_results["summary_statistics"]
        
        report = f"""# Scientific Batch Prompt Testing Report

## Session Overview
- **Session ID**: {session_results['session_id']}
- **Start Time**: {session_results['session_start']}
- **End Time**: {session_results['session_end']}
- **Total Duration**: {session_results['total_execution_time']:.1f} seconds
- **Test Cases**: {stats['total_tests']}
- **Success Rate**: {stats['success_rate']:.1f}%

## Test Configuration
- **Model**: {session_results['test_configuration']['model_choice']}
- **Fixed Seed Base**: {session_results['test_configuration']['fixed_seed_base']}
- **Model Settings**: {json.dumps(session_results['test_configuration']['model_settings'], indent=2)}

## Enhancement Level Performance

| Enhancement Level | Tests | Satisfactory | Satisfaction Rate |
|------------------|-------|--------------|-------------------|
"""
        
        for enhancement, perf in stats["enhancement_performance"].items():
            report += f"| {enhancement} | {perf['count']} | {perf['satisfactory']} | {perf['satisfaction_rate']:.1f}% |\n"
        
        report += f"""
## Duplication Detection Results
- **Cases with Duplication**: {stats['duplication_detection']['cases_with_duplication']}
- **Duplication Rate**: {stats['duplication_detection']['duplication_rate']:.1f}%

## Individual Test Results

"""
        
        for test in session_results["test_cases"]:
            if test.get("success", False):
                test_config = test.get("test_case_config", {})
                enhancement = test_config.get("enhancement_level", {}).get("name", "unknown")
                prompt_category = test_config.get("prompt_config", {}).get("category", "unknown")
                pair_name = test_config.get("image_pair", {}).get("pair_name", "unknown")
                
                post_analysis = test.get("post_analysis", {})
                overall_assessment = post_analysis.get("overall_assessment", {})
                recommendation = overall_assessment.get("recommendation", "unknown")
                
                report += f"""### Test {test['test_id']} - {enhancement}
- **Image Pair**: {pair_name}
- **Prompt Category**: {prompt_category}
- **Result Quality**: {recommendation}
- **Execution Time**: {test.get('execution_time', 0):.1f}s
- **Generated Image**: `{os.path.basename(test.get('generated_image_path', ''))}`

"""
        
        return report


def main():
    """Command-line interface for batch testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scientific batch testing for auto-generated prompts")
    parser.add_argument("--api-key", required=True, help="API key for image generation and analysis")
    parser.add_argument("--model", default="Pro API", help="Model choice for generation")
    parser.add_argument("--no-monitoring", action="store_true", help="Disable real-time monitoring")
    
    args = parser.parse_args()
    
    try:
        tester = BatchPromptTester()
        results = tester.run_batch_test(
            api_key=args.api_key,
            model_choice=args.model,
            real_time_monitoring=not args.no_monitoring
        )
        
        print(f"\n📊 TESTING COMPLETE!")
        print(f"📁 Results directory: {results['session_directory']}")
        
    except Exception as e:
        print(f"❌ Batch testing failed: {e}")


if __name__ == "__main__":
    main()
