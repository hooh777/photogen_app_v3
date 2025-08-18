"""
State Manager - Handles image storage, state management, and validation
Extracted from i2i_handler.py for better organization
"""
import gradio as gr
import logging
from core import utils


class StateManager:
    """Manages image states, uploads, and UI state updates"""
    
    def __init__(self):
        pass
    
    def store_background(self, img, existing_object=None):
        """Store background image and update UI state for Edit/Create mode"""
        if img is not None:
            # Edit Mode - show auto-generate button and human surfaces checkbox
            auto_btn_visible = True
            checkbox_visible = True
            step1_text = "**Status:** ✅ Background uploaded - Edit Mode activated!"
            separator_visible = True
            
            # If we already have an object, show the side-by-side display
            if existing_object is not None:
                # Side-by-side display for simplified workflow
                canvas_image = utils.create_side_by_side_display(img, existing_object)
                bg_size = img.size
                gr.Info(f"🎯 Edit Mode with side-by-side view! Background: {bg_size[0]}×{bg_size[1]}. Click the background (left side) to select placement area.")
            else:
                canvas_image = img
                bg_size = img.size
                gr.Info(f"🎯 Edit Mode activated! Background: {bg_size[0]}×{bg_size[1]}. Upload an object to see side-by-side view.")
        else:
            # Create Mode - hide auto-generate button and human surfaces checkbox
            auto_btn_visible = False
            checkbox_visible = False
            step1_text = "**Status:** 📁 Ready for Create Mode (no background needed)"
            separator_visible = False
            # Show placeholder canvas for Create Mode
            canvas_image = self._create_placeholder_canvas(existing_object)
            
        return (img, canvas_image, existing_object, None, None, 
                gr.update(visible=auto_btn_visible),
                step1_text,
                gr.update(visible=separator_visible),
                gr.update(visible=checkbox_visible))

    def store_object(self, img):
        """Store object image and update status"""
        if img is not None:
            status_text = "**Status:** ✅ Object uploaded successfully!"
        else:
            status_text = "**Status:** 📁 Ready to upload images"
        return img, status_text
    
    def update_prompt_status(self, prompt_text):
        """Update prompt input status"""
        if prompt_text and prompt_text.strip():
            return "**Status:** ✅ Prompt written - ready to generate!"
        else:
            return "**Status:** ✏️ Ready for your prompt"
    
    def _create_placeholder_canvas(self, existing_object):
        """Create basic placeholder for Create mode - delegated to canvas manager if needed"""
        # This is a simplified version, full implementation in canvas_manager
        from PIL import Image
        placeholder = Image.new("RGB", (512, 512), (240, 240, 240))
        return placeholder
