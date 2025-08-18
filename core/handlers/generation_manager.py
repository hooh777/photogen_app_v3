"""
Generation Manager - Handles image generation workflow optimized for Pro model usage
Extracted from i2i_handler.py for better organization and Pro model focus
Enhanced with intelligent scale analysis for realistic object placement
"""
import gradio as gr
import numpy as np
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from core import constants as const, utils
# from .scale_analyzer import ScaleAnalyzer  # Removed - scale analyzer no longer available


class GenerationManager:
    """Manages image generation workflow with Pro model optimization, async support, and intelligent scale analysis"""
    
    def __init__(self, generator, secure_storage):
        self.generator = generator
        self.secure_storage = secure_storage
        self._executor = ThreadPoolExecutor(max_workers=2)  # For async operations
        # self.scale_analyzer = ScaleAnalyzer()  # Removed - scale analyzer no longer available
    
    def run_generation(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress()):
        """Streamlined generation optimized for Pro model workflow with async support"""
        if not prompt or not prompt.strip(): 
            raise gr.Error("Please enter a prompt.")
        
        # Pro model optimization - enhanced prompt processing
        logging.info(f"🎯 === PROMPT PROCESSING DEBUG ===")
        logging.info(f"🎯 Input Prompt: '{prompt}'")
        logging.info(f"🎯 Model Choice: {model_choice}")
        logging.info(f"🎯 Has Background: {source_image is not None}")
        logging.info(f"🎯 Has Object: {object_image is not None}")
        
        full_prompt = self._process_prompt_for_pro_model(prompt, object_image, source_image, model_choice)
        
        logging.info(f"🎯 Final Processed Prompt: '{full_prompt}'")
        logging.info(f"🎯 === END PROMPT PROCESSING DEBUG ===")
        
        # Truncate prompt if needed to prevent errors
        full_prompt = self._truncate_prompt_if_needed(full_prompt)
        
        # Determine generation mode and dimensions
        is_create_mode = source_image is None
        width, height = self._determine_dimensions(aspect_ratio, source_image, is_create_mode)
        
        gr.Info(f"{'Creating' if is_create_mode else 'Editing'} with prompt: {full_prompt}")
        
        # Get appropriate API key based on model choice
        api_key = self._get_api_key_for_model(model_choice)
        logging.info(f"🔑 API key for generation: {'✅ Found' if api_key else '❌ Empty'} (Model: {model_choice})")
        
        # Execute generation based on mode
        if is_create_mode:
            result_images = self._handle_create_mode(object_image, full_prompt, steps, guidance, model_choice, width, height, api_key, progress)
        else:
            result_images = self._handle_edit_mode(source_image, object_image, full_prompt, aspect_ratio, steps, guidance, model_choice, width, height, api_key, progress)
        
        # Return fresh result to avoid caching issues
        return self._prepare_result(result_images)
    
    def _process_prompt_for_pro_model(self, prompt, object_image, source_image, model_choice):
        """Enhanced prompt processing optimized for Pro model with intelligent scale analysis"""
        full_prompt = prompt
        is_pro_api = "pro" in model_choice.lower()
        
        # CRITICAL FIX: Detect manual prompts and preserve them exactly as written
        # Auto-generated prompts typically contain specific keywords from the vision system
        auto_prompt_indicators = [
            "eyeglass case", "person on the left", "person on the right", 
            "while both individuals", "continue their", "positioning detection",
            "generation_prompt", "scene description", "observed in the image"
        ]
        
        # Check if this looks like a manual user prompt (short, specific, no vision keywords)
        is_likely_manual_prompt = (
            len(prompt.split()) < 20 and  # Manual prompts are typically shorter
            not any(indicator in prompt.lower() for indicator in auto_prompt_indicators) and
            not prompt.lower().startswith(("the image shows", "in this image", "this scene"))
        )
        
        # For manual prompts with multi-image workflow: use exact prompt, no enhancements
        if is_likely_manual_prompt and object_image and source_image and is_pro_api:
            logging.info(f"🎯 MANUAL PROMPT DETECTED: Using exact user prompt without enhancements")
            logging.info(f"   📝 User Prompt: '{prompt}'")
            gr.Info(f"Using manual prompt exactly as written: {prompt}")
            return prompt  # Return the exact prompt without any modifications
        
        # Enhanced object integration keywords for both human and environmental placement
        integration_keywords = [
            "realistic physics", "proper contact points", "natural positioning", 
            "stable placement", "realistic shadows", "professional integration"
        ]
        
        # Check if integration keywords are already present
        has_integration_keywords = any(keyword in full_prompt.lower() for keyword in integration_keywords)
        
        # NEW: Intelligent scale analysis for Pro API
        # Scale analysis enhancement (simplified - scale analyzer removed)
        scale_guidance = ""
        if object_image and source_image and is_pro_api:
            try:
                # Simple fallback scale guidance without complex analysis
                logging.info("ℹ️ Scale analysis requested but analyzer not available - using basic guidance")
                scale_guidance = "ensure proper size and proportions for natural integration"
                gr.Info("🎯 Basic Scale Guidance: Applied standard sizing recommendations")
            except Exception as e:
                logging.error(f"❌ Scale guidance failed: {e}")
                scale_guidance = ""
        
        # Pro model specific enhancements (only for auto-generated prompts)
        if object_image and source_image and is_pro_api and not is_likely_manual_prompt:
            # Pro API with merged image needs stronger preservation and integration instructions
            if "preserve" not in full_prompt.lower() and "keep" not in full_prompt.lower():
                # CRITICAL: Focus on integration rather than object description to prevent duplication
                base_instruction = "Seamlessly integrate the SINGLE OBJECT from the left side of the input image into the background scene on the right"
                preservation_instruction = "maintain the object's exact appearance, size, and proportions from the reference"
                
                # Enhanced size preservation for human placement
                size_instruction = "preserve the original scale and dimensions of the object - do not resize or duplicate it"
                duplicate_prevention = "create only ONE instance of the object - do not generate multiple copies"
                
                integration_enhancement = "ensure natural physics with realistic placement, proper shadows, and natural contact points"
                pose_preservation = "maintain exact human pose and expression from the background image"
                
                # Combine all integration-focused enhancements
                enhancement_parts = [
                    base_instruction, 
                    preservation_instruction, 
                    size_instruction, 
                    duplicate_prevention,
                    pose_preservation,
                    integration_enhancement
                ]
                
                if scale_guidance:
                    # Modify scale guidance to be integration-focused
                    integration_guidance = f"integrate the object {scale_guidance.strip(', ')}"
                    enhancement_parts.append(integration_guidance)
                
                # Build integration-focused prompt that prevents object duplication
                integration_prompt = f"{', '.join(enhancement_parts)}"
                full_prompt = f"{integration_prompt}. Scene description: {full_prompt}. IMPORTANT: Use only the single object shown in the input image - do not create additional objects."
            
            # Add professional photography enhancement if not present
            if not has_integration_keywords:
                full_prompt = f"{full_prompt}, professional studio lighting, realistic shadows and contact points, commercial photography quality, single object integration only"
                
        elif object_image and source_image and not is_likely_manual_prompt:
            # Local model with multi-image support (only enhance auto-generated prompts)
            if "preserve" not in full_prompt.lower():
                full_prompt = f"Integrate the single object with realistic physics, maintaining original size and natural positioning while {full_prompt}"
            
            # Add integration enhancement for local models too
            if not has_integration_keywords:
                full_prompt = f"{full_prompt}, stable placement with proper contact points, realistic shadows, single object only"
        
        # Log final prompt processing result
        if is_likely_manual_prompt:
            logging.info(f"✅ MANUAL PROMPT: Preserved exactly as user wrote: '{full_prompt}'")
        else:
            logging.info(f"🤖 AUTO-GENERATED: Enhanced for Pro model: '{full_prompt}'")
        
        return full_prompt
    
    def _truncate_prompt_if_needed(self, full_prompt):
        """Truncate prompt to prevent token limit errors"""
        if hasattr(self.generator, 'tokenizer') and self.generator.tokenizer is not None:
            max_length = 77
            tokens = self.generator.tokenizer.encode(full_prompt)
            if len(tokens) > max_length:
                # Truncate to max_length tokens
                truncated_tokens = tokens[:max_length]
                full_prompt = self.generator.tokenizer.decode(truncated_tokens)
                gr.Warning(f"⚠️ Prompt was truncated from {len(tokens)} to {max_length} tokens to prevent errors.")
                logging.info(f"Prompt truncated from {len(tokens)} to {max_length} tokens")
        
        return full_prompt
    
    def _determine_dimensions(self, aspect_ratio, source_image, is_create_mode):
        """Determine optimal dimensions based on mode and aspect ratio"""
        if aspect_ratio == "Match Input" and not is_create_mode:
            width, height = source_image.size
        else:
            width, height = utils.get_dimensions(aspect_ratio)
        
        return width, height
    
    def _handle_create_mode(self, object_image, full_prompt, steps, guidance, model_choice, width, height, api_key, progress):
        """Handle Create Mode generation (Text-to-Image)"""
        if object_image:
            gr.Info("Creating new image (object composition in create mode coming soon)")
        
        # Use T2I generation logic
        result_images = self.generator.text_to_image(
            full_prompt, steps, guidance, model_choice, 1, width, height, api_key, progress
        )
        return result_images
    
    def _handle_edit_mode(self, source_image, object_image, full_prompt, aspect_ratio, steps, guidance, model_choice, width, height, api_key, progress):
        """Handle Edit Mode generation (Image-to-Image) optimized for Pro model"""
        if object_image:
            # Pro model optimization: Use background as main input
            input_image = source_image  # Always pass background as main input for Pro API
            gr.Info(f"🎯 Edit Mode: Background image with object context for AI generation")
            logging.info(f"🔍 Generation input - Background: {source_image.size}, Object: {object_image.size} (optimized for Pro model)")
        else:
            # No object - use original image
            input_image = source_image
            gr.Info(f"Using background only")
        
        source_np = np.array(input_image)
        
        # Pass to generator with Pro model optimization parameters
        result_images = self.generator.image_to_image(
            source_np, full_prompt, steps, guidance, model_choice, 1, width, height, api_key, 
            background_img=source_image, object_img=object_image, aspect_ratio_setting=aspect_ratio, progress=progress
        )
        
        return result_images
    
    def _prepare_result(self, result_images):
        """Prepare result with fresh PIL image to avoid caching issues"""
        if result_images and len(result_images) > 0:
            result_pil = result_images[0]
            
            # Create a copy to avoid reference issues
            fresh_result = result_pil.copy()
            
            # Add unique metadata to ensure Gradio treats it as a new image
            fresh_result.info['generation_timestamp'] = str(int(time.time() * 1000))  # millisecond precision
            fresh_result.info['generation_id'] = f"photogen_{int(time.time() * 1000)}"
            
            logging.info(f"🎯 Returning fresh result image: {fresh_result.size} {fresh_result.mode} with timestamp {fresh_result.info.get('generation_timestamp')}")
            return [fresh_result]
        else:
            logging.warning("🔥 No result image generated")
            return []

    def _get_api_key_for_model(self, model_choice):
        """Get the appropriate API key based on model choice"""
        logging.info(f"🔑 Getting API key for model choice: '{model_choice}'")
        
        if model_choice == const.LOCAL_MODEL:
            logging.info("🔑 Local model - no API key needed")
            return ""  # No API key needed for local models
        elif model_choice == "Pro (Black Forest Labs)":
            api_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
            logging.info(f"🔑 BFL API key loaded: {'✅ Found' if api_key else '❌ Empty'}")
            return api_key
        elif model_choice == "Pro (GRS AI)":
            api_key = self.secure_storage.load_api_key(const.GRS_AI_FLUX_API)
            logging.info(f"🔑 GRS AI API key loaded: {'✅ Found' if api_key else '❌ Empty'}")
            return api_key
        elif model_choice.startswith("Pro"):
            # Fallback for generic "Pro" choice or compatibility
            api_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
            logging.info(f"🔑 Fallback BFL API key loaded: {'✅ Found' if api_key else '❌ Empty'}")
            return api_key
        else:
            # Default case
            logging.info(f"🔑 Unknown model choice - returning empty key")
            return ""
    
    def _determine_dimensions(self, aspect_ratio, source_image, is_create_mode):
        """Determine appropriate dimensions based on aspect ratio setting and image"""
        # Handle new product mood shot dimensions
        if "4157×1843px" in aspect_ratio:  # Wide Product
            return (4157, 1843)
        elif "2362×4606px" in aspect_ratio:  # Tall Product
            return (2362, 4606)
        elif "1748×5244px" in aspect_ratio:  # Extra Tall Product
            return (1748, 5244)
        
        # For Create Mode (no background), use aspect ratio calculation directly
        if is_create_mode or source_image is None:
            return utils.get_dimensions(aspect_ratio)
        
        # For Edit Mode (with background), use generator's safe sizing with forced aspect ratio
        return self.generator._determine_safe_generation_size(
            source_image, aspect_ratio, "Pro", force_aspect_ratio=True
        )
    
    def _get_vision_api_key(self):
        """Get API key for vision model (Qwen-VL-Max)"""
        try:
            api_key = self.secure_storage.load_api_key(const.QWEN_VL_MAX)
            logging.info(f"🔑 Vision API key loaded: {'✅ Found' if api_key else '❌ Empty'}")
            return api_key
        except Exception as e:
            logging.error(f"❌ Failed to load vision API key: {e}")
            return ""
