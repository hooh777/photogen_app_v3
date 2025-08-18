"""
Auto-Prompt Manager - Handles comprehensive auto-prompt generation workflow
Extracted from i2i_handler.py for better organization and Pro model optimization
"""
import gradio as gr
import logging
from PIL import ImageDraw
from core.vision_streamlined import VisionAnalyzer


class AutoPromptManager:
    """Manages auto-prompt generation with Pro model optimization"""
    
    def __init__(self, secure_storage):
        self.secure_storage = secure_storage
        self.vision_analyzer = VisionAnalyzer()  # Use streamlined vision module
    
    def generate_auto_prompt(self, base_img, object_img, top_left, bottom_right, existing_prompt, provider_name):
        """Simplified auto-prompt generation - removed redundant human surfaces toggle"""
        # Validation checks
        self._validate_inputs(base_img, object_img, top_left, bottom_right, provider_name)
        
        # Process coordinates and create selection
        selection_coords = self._process_selection_coordinates(base_img, top_left, bottom_right)
        background_with_selection = self._create_selection_overlay(base_img, selection_coords)
        
        # Get API key
        api_key = self.secure_storage.load_api_key(provider_name)
        if not api_key:
            raise gr.Error(f"API Key for {provider_name} is not set. Please add it in the settings.")
        
        gr.Info(f"🚀 Generating comprehensive auto-prompt with {provider_name}...")
        
        # Generate comprehensive prompt
        try:
            final_prompt = self.vision_analyzer.generate_comprehensive_auto_prompt(
                background_image=background_with_selection,
                object_image=object_img,
                selection_coords=selection_coords,
                provider_name=provider_name,
                api_key=api_key
            )
            
            # Pro model optimization: Add preservation instructions
            if "pro" in provider_name.lower() or "Pro" in provider_name:
                final_prompt = self._optimize_for_pro_model(final_prompt)
            
            gr.Info(f"✅ Generated comprehensive prompt: {final_prompt}")
            status_text = "**Status:** ✅ Auto-prompt generated successfully!"
            return final_prompt, status_text
            
        except Exception as e:
            logging.error(f"Comprehensive auto-prompt generation failed: {e}")
            gr.Error(f"Auto-prompt generation failed: {str(e)}")
            return existing_prompt, "**Status:** ❌ Auto-prompt generation failed"
    
    def _validate_inputs(self, base_img, object_img, top_left, bottom_right, provider_name):
        """Validate all required inputs for auto-prompt generation"""
        if base_img is None:
            raise gr.Error("Auto-prompt generation is only available in Edit Mode. Please upload a background image to use this feature, or write your prompt manually for Create Mode.")
        
        # Object image is optional for single-image workflow
        if object_img is None:
            logging.info("🤖 Auto-prompt: Single image mode (no object image)")
        
        if not top_left or not bottom_right: 
            raise gr.Error("Please select an area first! 🎯 Click on the background image (left side) to select where to place the object.")
        
        if not provider_name: 
            raise gr.Error("Please select a Vision/Enhancer Provider in the API Key Settings.")
    
    def _process_selection_coordinates(self, base_img, top_left, bottom_right):
        """Process and validate selection coordinates"""
        img_width, img_height = base_img.size
        
        # Constrain coordinates to image bounds
        x1 = max(0, min(top_left[0], img_width - 1))
        y1 = max(0, min(top_left[1], img_height - 1))
        x2 = max(0, min(bottom_right[0], img_width - 1))
        y2 = max(0, min(bottom_right[1], img_height - 1))
        
        # Calculate proper box coordinates (left, top, right, bottom)
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        # Ensure minimum box size (at least 10x10 pixels)
        min_size = 10
        if (right - left) < min_size:
            center_x = (left + right) // 2
            left = max(0, center_x - min_size // 2)
            right = min(img_width, left + min_size)
        
        if (bottom - top) < min_size:
            center_y = (top + bottom) // 2
            top = max(0, center_y - min_size // 2)
            bottom = min(img_height, top + min_size)
        
        return (left, top, right, bottom)
    
    def _create_selection_overlay(self, base_img, selection_coords):
        """Create background image with selection box overlay for vision analysis"""
        background_with_selection = base_img.copy()
        draw = ImageDraw.Draw(background_with_selection)
        draw.rectangle(selection_coords, outline="blue", width=3)
        return background_with_selection
    
    def _optimize_for_pro_model(self, prompt):
        """Add Pro model specific optimizations to the prompt"""
        # Pro model works better with explicit preservation instructions
        if "preserve" not in prompt.lower() and "keep" not in prompt.lower():
            prompt = f"EXACTLY preserve the object from the reference image without changing its type, material, color, or shape. {prompt}. The object must remain identical to the reference - do not transform it into any other type of object."
        
        return prompt
