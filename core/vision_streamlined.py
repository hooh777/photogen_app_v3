"""
Core Vision Module - Streamlined for Pro model auto-prompt workflow
Extracted essential functions from the large vision.py (1589 lines → focused essentials)
Optimized for 90% auto-prompt usage pattern
"""
from openai import OpenAI
from PIL import Image
import base64
from io import BytesIO
import logging


class VisionAnalyzer:
    """Streamlined vision analysis optimized for auto-prompt generation"""
    
    def __init__(self):
        self.api_base = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-vl-max"
    
    def generate_comprehensive_auto_prompt(self, background_image: Image.Image, object_image: Image.Image = None, 
                                          selection_coords: tuple = None, provider_name: str = "", api_key: str = ""):
        """
        Comprehensive auto-prompt generation - simplified without redundant human surfaces toggle.
        The AI already handles object placement naturally, and post-processing provides sufficient filtering.
        """
        if "Qwen-VL-Max" not in provider_name:
            raise ValueError(f"{provider_name} is not supported. Please use Qwen-VL-Max.")
        
        if not api_key:
            raise ValueError("API key is required for comprehensive auto-prompt generation.")
        
        try:
            logging.info("🚀 Starting comprehensive auto-prompt generation...")
            
            # Convert background image to base64
            bg_img_base64 = self._image_to_base64(background_image)
            
            # Convert object image to base64 if provided
            obj_img_base64 = None
            if object_image is not None:
                obj_img_base64 = self._image_to_base64(object_image)
            
            # Calculate position context (if coordinates provided)
            position_desc = ""
            if selection_coords:
                position_desc = self._calculate_position_description(selection_coords, background_image.size)
            
            # Create optimized prompt for Pro model (simplified - no human surface distinction)
            prompt_text = self._create_analysis_prompt(position_desc, has_object_image=(object_image is not None))
            
            # LOG THE ACTUAL PROMPT BEING SENT
            logging.info("🔍 Vision Model Prompt Being Sent:")
            logging.info(f"  📝 Full Prompt Text:\n{prompt_text}")
            logging.info(f"  📍 Position Description: '{position_desc}'")
            logging.info(f"  🖼️ Has Object Image: {object_image is not None}")
            
            # LOG IMAGE ANALYSIS REQUEST
            logging.info("🖼️ Vision Model Image Analysis Request:")
            if background_image:
                logging.info(f"  📷 Background Image: {background_image.size} {background_image.mode}")
            if object_image:
                logging.info(f"  📦 Object Image: {object_image.size} {object_image.mode}")
            
            # ADD VISION ANALYSIS REQUEST - Ask model to describe what it sees first
            analysis_prompt = f"""Analyze both images and respond in JSON format:

Image 1: Shows a scene with a blue selection box
Image 2: Shows an object to be placed

Respond with this exact JSON structure:
{{
    "analysis": {{
        "image1_description": {{
            "scene_description": "Who are the people (specify positions like 'person on the left/right' if multiple), where is the location, what are they doing, lighting/environment details",
            "selection_area": "What specifically is inside the blue selection box area, including whose body part it is if applicable"
        }},
        "image2_description": "What object you see in image 2 with details"
    }},
    "generation_prompt": "Clean 40-60 word prompt describing the object integration/placement in the scene. When multiple people are present, weave in multi-person context (e.g., 'while both individuals continue their activity', 'as the person on the left/right...') while maintaining focus on the selection area"
}}

Original task: {prompt_text}"""
            
            logging.info(f"📋 Enhanced JSON prompt with detailed scene analysis request sent")
            
            # Use the enhanced prompt that asks for JSON response
            final_prompt_text = analysis_prompt
            
            # Call vision API
            client = OpenAI(api_key=api_key, base_url=self.api_base)
            
            # Build message content - background image is always included
            message_content = [
                {"type": "text", "text": final_prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{bg_img_base64}"}}
            ]
            
            # Add object image only if provided
            if obj_img_base64:
                message_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{obj_img_base64}"}})
            
            # LOG DETAILED REQUEST INFO
            logging.info("🔍 Vision API Request Details:")
            logging.info(f"  📍 API Base: {self.api_base}")
            logging.info(f"  🤖 Model: {self.model}")
            logging.info(f"  🔑 API Key: {'✅ Provided' if api_key else '❌ Missing'}")
            logging.info(f"  📝 Final Prompt Length: {len(final_prompt_text)} characters")
            logging.info(f"  🖼️ Images: Background + {'Object' if obj_img_base64 else 'None'}")
            logging.info(f"  📊 Max Tokens: 500, Temperature: 0.3")  # Increased tokens for analysis
            
            completion = client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                max_tokens=500,  # Increased for image analysis + prompt
                temperature=0.3
            )
            
            # LOG DETAILED RESPONSE INFO
            logging.info("🔍 Vision API Response Details:")
            logging.info(f"  📦 Response Type: {type(completion)}")
            logging.info(f"  📊 Choices Count: {len(completion.choices) if completion.choices else 0}")
            
            if completion.choices and len(completion.choices) > 0:
                raw_response = completion.choices[0].message.content
                logging.info(f"  ✅ Raw Response: '{raw_response}'")
                logging.info(f"  📏 Response Length: {len(raw_response)} characters")
                
                # Parse JSON response
                try:
                    import json
                    # Try to extract JSON from the response
                    json_start = raw_response.find('{')
                    json_end = raw_response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = raw_response[json_start:json_end]
                        response_data = json.loads(json_str)
                        
                        # LOG WHAT THE VISION MODEL SAW
                        logging.info("👁️ VISION MODEL IMAGE ANALYSIS:")
                        if "analysis" in response_data:
                            analysis = response_data["analysis"]
                            if "image1_description" in analysis:
                                img1_desc = analysis["image1_description"]
                                if isinstance(img1_desc, dict):
                                    # New nested structure
                                    logging.info(f"  🏞️ Scene Description: {img1_desc.get('scene_description', 'Not found')}")
                                    logging.info(f"  📦 Selection Area: {img1_desc.get('selection_area', 'Not found')}")
                                else:
                                    # Legacy structure
                                    logging.info(f"  👁️ Image 1 (Blue Box): {img1_desc}")
                            if "image2_description" in analysis:
                                logging.info(f"  🎯 Image 2 (Object): {analysis['image2_description']}")
                        
                        # Extract the clean generation prompt
                        if "generation_prompt" in response_data:
                            auto_prompt = response_data["generation_prompt"].strip()
                            logging.info(f"  🎯 Clean Generation Prompt: '{auto_prompt}'")
                        else:
                            # Fallback if no generation_prompt field
                            auto_prompt = raw_response.strip()
                            logging.info(f"  ⚠️ No generation_prompt field found, using full response")
                            
                    else:
                        # Fallback if not JSON format
                        logging.info("  ⚠️ Response not in JSON format, using fallback extraction")
                        auto_prompt = raw_response.strip()
                        
                        # LOG WHAT THE VISION MODEL SAW (fallback)
                        logging.info("👁️ VISION MODEL IMAGE ANALYSIS:")
                        if "Image 1:" in raw_response or "blue selection box" in raw_response.lower():
                            lines = raw_response.split('\n')
                            for line in lines:
                                if any(keyword in line.lower() for keyword in ['image 1', 'image 2', 'blue', 'selection', 'box', 'see', 'observe']):
                                    logging.info(f"  👁️ {line.strip()}")
                        
                        # Extract just the final prompt part if the model provided analysis first
                        if "Then proceed with" in auto_prompt or "task:" in auto_prompt.lower():
                            parts = auto_prompt.split("task:")
                            if len(parts) > 1:
                                auto_prompt = parts[-1].strip()
                                logging.info(f"  ✂️ Extracted Final Prompt: '{auto_prompt}'")
                
                except json.JSONDecodeError as e:
                    logging.error(f"  ❌ JSON parsing failed: {e}")
                    auto_prompt = raw_response.strip()
                    logging.info("  🔄 Using raw response as fallback")
                
                logging.info(f"  🧹 After Processing: '{auto_prompt}'")
                
                # Check if human surfaces were detected before cleaning
                self._log_human_surface_detection(auto_prompt)
                
                # Always apply human surface corrections for safer object placement
                cleaned_prompt = self._clean_prompt_response(auto_prompt)
                logging.info(f"  🔧 After Cleaning: '{cleaned_prompt}'")
                auto_prompt = cleaned_prompt
                
                logging.info(f"✅ FINAL Generated auto-prompt: '{auto_prompt}'")
                return auto_prompt
            else:
                logging.warning("No response from vision model")
                return "object placed in selected location with natural lighting and realistic integration"
                
        except Exception as e:
            logging.error(f"❌ Comprehensive auto-prompt generation failed: {e}")
            logging.error(f"❌ Error Type: {type(e).__name__}")
            logging.error(f"❌ Error Details: {str(e)}")
            import traceback
            logging.error(f"❌ Full Traceback:\n{traceback.format_exc()}")
            return "object positioned naturally in the selected area with appropriate lighting and context"
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def _calculate_position_description(self, selection_coords: tuple, image_size: tuple) -> str:
        """Calculate position description for selection area"""
        x1, y1, x2, y2 = selection_coords
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        img_width, img_height = image_size
        rel_x = center_x / img_width
        rel_y = center_y / img_height
        
        # Determine position description
        horizontal_pos = "left" if rel_x < 0.33 else "right" if rel_x > 0.66 else "center"
        vertical_pos = "top" if rel_y < 0.33 else "bottom" if rel_y > 0.66 else "middle"
        
        if vertical_pos != "middle" or horizontal_pos != "center":
            return f"{vertical_pos}-{horizontal_pos}"
        else:
            return "center"
    
    def _create_analysis_prompt(self, position_desc: str, has_object_image: bool = True) -> str:
        """Create optimized analysis prompt - simplified without redundant human surface distinction"""
        
        if not has_object_image:
            # Single image mode - analyze just the selected area for enhancement/editing
            return f"""Create a 40-60 word prompt describing enhancement/modification of the blue selection area in the {position_desc}.

Focus on what you observe in the blue highlighted area and describe realistic improvements as a natural scene composition."""
        
        # Multi-image mode - focus on natural object integration with environmental surfaces
        return f"""Create a 40-60 word prompt describing natural object placement/integration in the blue selection area in the {position_desc}.

Focus on how the object integrates with environmental surfaces in the blue highlighted area. Describe the placement as a natural scene composition, not as instructions."""
    
    def _clean_prompt_response(self, prompt: str) -> str:
        """Clean up the generated prompt response for ultra-concise output"""
        # Remove common prefixes/suffixes
        prompt = prompt.replace("Here's the prompt:", "").replace("Prompt:", "").strip()
        prompt = prompt.strip('"').strip("'").strip()
        
        # Remove any explanatory text or excessive details
        if "Example:" in prompt:
            prompt = prompt.split("Example:")[0].strip()
        if "Focus on" in prompt:
            prompt = prompt.split("Focus on")[0].strip()
        if "REQUIREMENTS:" in prompt:
            prompt = prompt.split("REQUIREMENTS:")[0].strip()
            
        # Human surface detection and correction (simplified)
        human_surface_keywords = ["on skin", "on clothing", "on fabric"]
        environmental_replacements = {
            "on skin": "on table surface",
            "on clothing": "on nearby surface", 
            "on fabric": "on solid surface"
        }
        
        # Apply corrections if human surfaces detected
        for human_phrase, env_phrase in environmental_replacements.items():
            if human_phrase in prompt.lower():
                prompt = prompt.replace(human_phrase, env_phrase)
                logging.info(f"🔧 Corrected: '{human_phrase}' → '{env_phrase}'")
        
        # Ensure it doesn't end with period for consistency
        if prompt.endswith('.'):
            prompt = prompt[:-1]
        
        return prompt
    
    def _basic_clean_prompt_response(self, prompt: str) -> str:
        """Basic prompt cleaning for ultra-concise output when human surfaces are allowed"""
        # Remove common prefixes/suffixes
        prompt = prompt.replace("Here's the prompt:", "").replace("Prompt:", "").strip()
        prompt = prompt.strip('"').strip("'").strip()
        
        # Remove any explanatory text or excessive details
        if "Example:" in prompt:
            prompt = prompt.split("Example:")[0].strip()
        if "Focus on" in prompt:
            prompt = prompt.split("Focus on")[0].strip()
        if "REQUIREMENTS:" in prompt:
            prompt = prompt.split("REQUIREMENTS:")[0].strip()
            
        # Simplify common verbose phrases for conciseness
        concise_replacements = {
            "securely held in person's natural grip": "held naturally",
            "maintaining exact pose and expression": "maintaining pose",
            "professional studio lighting": "studio lighting",
            "realistic shadows and contact points": "realistic shadows",
            "with natural positioning": "naturally",
            "professional photography quality": "professional quality"
        }
        
        # Apply conciseness improvements
        for verbose_phrase, concise_phrase in concise_replacements.items():
            if verbose_phrase in prompt.lower():
                import re
                pattern = re.compile(re.escape(verbose_phrase), re.IGNORECASE)
                prompt = pattern.sub(concise_phrase, prompt)
                logging.info(f"🔧 Made concise: '{verbose_phrase}' → '{concise_phrase}'")
        
        # Ensure it doesn't end with period for consistency
        if prompt.endswith('.'):
            prompt = prompt[:-1]
        
        return prompt
    
    def _log_human_surface_detection(self, prompt: str) -> None:
        """Log when human surfaces are detected in the prompt and provide user feedback"""
        import gradio as gr
        
        human_indicators = [
            "skin", "clothing", "fabric", "hand", "body", "person's", "human"
        ]
        
        detected_indicators = [indicator for indicator in human_indicators if indicator in prompt.lower()]
        
        if detected_indicators:
            logging.info(f"🚨 Human surface indicators detected: {detected_indicators}")
            logging.info(f"Original prompt: '{prompt}'")
            # Provide helpful user feedback
            gr.Info("👥 Human figures detected! Automatically redirecting to environmental surfaces (tables, counters, etc.). Enable the '🤝 Allow objects on people' option if you want to place objects directly on people.")
        else:
            logging.info("✅ No human surface issues detected")


# Legacy compatibility functions for existing code
def generate_comprehensive_auto_prompt(background_image: Image.Image, object_image: Image.Image, 
                                      selection_coords: tuple, provider_name: str, api_key: str):
    """Legacy compatibility wrapper for the streamlined VisionAnalyzer - human surfaces toggle removed"""
    analyzer = VisionAnalyzer()
    return analyzer.generate_comprehensive_auto_prompt(
        background_image, object_image, selection_coords, provider_name, api_key
    )
