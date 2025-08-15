"""
Streamlined I2I Handler - Main orchestrator optimized for Pro model workflow
Dramatically reduced from 983 lines to focus on essential coordination
"""
import gradio as gr
import logging

# Import focused managers for better organization
from .canvas_manager import CanvasManager
from .auto_prompt_manager import AutoPromptManager
from .state_manager import StateManager
from .generation_manager import GenerationManager


class I2IHandler:
    """Streamlined I2I Handler optimized for Pro model workflow"""
    
    def __init__(self, ui, generator, secure_storage):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage
        
        # Initialize focused managers
        self.canvas_manager = CanvasManager()
        self.auto_prompt_manager = AutoPromptManager(secure_storage)
        self.state_manager = StateManager()
        self.generation_manager = GenerationManager(generator, secure_storage)
        
        # Store uploaded images for gallery selection
        self.uploaded_images = []
    
    def reset_handler_state(self):
        """Reset all handler state to initial values"""
        logging.info("🔄 Resetting I2I handler state completely")
        self.uploaded_images = []
        logging.info(f"🔄 Handler state reset - uploaded_images: {len(self.uploaded_images)}")
    
    def register_event_handlers(self):
        """Register all UI event handlers with multi-image workflow"""
        
        # Multi-image upload handler (simplified)
        self.ui['i2i_source_uploader'].upload(
            self.handle_multi_image_upload,
            inputs=[self.ui['i2i_source_uploader']],
            outputs=[
                self.ui['uploaded_images_preview'],    # gallery
                self.ui['i2i_canvas_image_state'],     # background state
                self.ui['i2i_object_image_state'],     # object state
                self.ui['i2i_interactive_canvas'],     # update canvas directly
                self.ui['step1_status'],               # status markdown
                self.ui['canvas_mode_info'],           # update canvas info
                self.ui['i2i_pin_coords_state'],       # clear previous selection
                self.ui['i2i_anchor_coords_state']     # clear previous selection
            ]
        )
        
        # Gallery selection handler - show selected image in canvas
        self.ui['uploaded_images_preview'].select(
            self.handle_gallery_click,
            outputs=[
                self.ui['i2i_canvas_image_state'],     # selected image state
                self.ui['i2i_object_image_state'],     # clear object state for single selection
                self.ui['i2i_interactive_canvas'],     # show selected image in canvas
                self.ui['canvas_mode_info'],           # update instructions
                self.ui['i2i_pin_coords_state'],       # clear previous selection
                self.ui['i2i_anchor_coords_state']     # clear previous selection
            ]
        )
        
        # Legacy object uploader - now deprecated but kept for compatibility
        self.ui['i2i_object_uploader'].change(
            lambda x: None,  # No-op, preview gallery handles display
            inputs=[self.ui['i2i_object_uploader']],
            outputs=[]
        )

        # Single-click area selection with inline handler
        def handle_click_with_prompt_button(base_img, obj_img, top_left, bottom_right, evt: gr.SelectData):
            # Get the canvas update from the canvas manager
            canvas_result = self.canvas_manager.handle_click(base_img, obj_img, top_left, bottom_right, evt)
            
            # Show the smart prompt button after area selection
            return (
                canvas_result[0],  # updated canvas
                canvas_result[1],  # pin coords
                canvas_result[2],  # anchor coords
                gr.update(visible=True)  # show auto-prompt button
            )
        
        self.ui['i2i_interactive_canvas'].select(
            handle_click_with_prompt_button, 
            inputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'],
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']
            ], 
            outputs=[
                self.ui['i2i_interactive_canvas'], 
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
                self.ui['i2i_auto_prompt_btn']  # Show smart prompt button after area selection
            ]
        )
        
        # Auto-prompt generation (optimized for 90% usage)
        self.ui['i2i_auto_prompt_btn'].click(
            self.auto_generate_prompt, 
            inputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'],
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
                self.ui['i2i_prompt'], self.ui['provider_select'], self.ui['allow_human_surfaces']
            ], 
            outputs=[self.ui['i2i_prompt'], self.ui['step2_status']]
        )
        
        # Selection reset with direct manager call
        self.ui['i2i_reset_selection_btn'].click(
            self.canvas_manager.reset_selection,
            inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state']],
            outputs=[
                self.ui['i2i_interactive_canvas'],
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']
            ]
        )

        # Main generation handler (Pro model optimized)
        self.ui['i2i_generate_btn'].click(
            self.run_i2i_with_state_update, 
            inputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], 
                self.ui['i2i_prompt'], self.ui['aspect_ratio'], self.ui['i2i_steps'], 
                self.ui['i2i_guidance'], self.ui['i2i_model_select'], 
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']
            ], 
            outputs=[self.ui['output_gallery'], self.ui['last_generated_image_state']] if 'last_generated_image_state' in self.ui else [self.ui['output_gallery']]
        ).then(
            # Clear selection state on new generation
            lambda: None,
            outputs=[self.ui['selected_gallery_image_state']] if 'selected_gallery_image_state' in self.ui else []
        )
        
        # Prompt status updates with direct manager call
        self.ui['i2i_prompt'].change(
            self.state_manager.update_prompt_status,
            inputs=[self.ui['i2i_prompt']],
            outputs=[self.ui['step2_status']]
        )
        
        # Token counter (if available) with inline function
        if 'i2i_token_counter' in self.ui:
            def update_token_count(prompt_text):
                return self.state_manager.update_token_count(prompt_text, self.generator)
            
            self.ui['i2i_prompt'].change(
                update_token_count,
                inputs=[self.ui['i2i_prompt']],
                outputs=[self.ui['i2i_token_counter']]
            )

    # === Essential Methods - Direct Manager Access ===
    
    # Auto-prompt generation → AutoPromptManager
    def auto_generate_prompt(self, base_img, object_img, top_left, bottom_right, existing_prompt, provider_name, allow_human_surfaces=False):
        return self.auto_prompt_manager.generate_auto_prompt(base_img, object_img, top_left, bottom_right, existing_prompt, provider_name, allow_human_surfaces)
    
    # Image generation → GenerationManager
    def run_i2i(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress()):
        return self.generation_manager.run_generation(source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress)
    
    def run_i2i_with_state_update(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress()):
        """Wrapper for run_i2i that also returns the last generated image for state tracking."""
        result_list = self.run_i2i(source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress)
        
        # Return both gallery list and the single image for last_generated_image_state
        last_image = result_list[0] if result_list else None
        logging.info(f"🎯 Storing last generated image: {type(last_image)} for direct save access")
        
        # Return for gallery and last image state
        if 'last_generated_image_state' in self.ui:
            return result_list, last_image
        else:
            return result_list
    
    def handle_multi_image_upload(self, uploaded_files):
        """
        New multi-image upload handler for unified workflow.
        Processes multiple uploaded files and sets up canvas accordingly.
        
        Args:
            uploaded_files: List of uploaded file objects from gr.File
            
        Returns:
            Tuple of outputs for UI updates
        """
        from PIL import Image
        import os
        
        if not uploaded_files:
            # No files uploaded - reset state
            return [], None, None, None, "**Status:** Ready to upload images 📁", "**Upload images above to start editing**", None, None
        
        # Process uploaded files (max 10 images)
        processed_images = []
        preview_images = []
        
        for file_obj in uploaded_files[:10]:  # Limit to 10 images
            try:
                if hasattr(file_obj, 'name'):
                    # File object with .name attribute
                    img = Image.open(file_obj.name)
                else:
                    # Direct file path
                    img = Image.open(file_obj)
                
                processed_images.append(img)
                preview_images.append(img)  # For gallery display
                
            except Exception as e:
                logging.error(f"Error processing uploaded file: {e}")
                continue
        
        if not processed_images:
            return [], None, None, None, "**Status:** Error processing images ❌", "**Upload valid images to start**", None, None
        
        # Set up states but don't show canvas automatically - user must select from gallery
        if len(processed_images) == 1:
            # Single image - ready for selection
            background_state = processed_images[0]
            object_state = None
            status_msg = f"**Status:** 1 image uploaded - Click the image below to edit! 🎯"
            canvas_info = "**Select an image from the gallery above to start editing**"
            
        else:
            # Multiple images - ready for selection
            background_state = processed_images[0]  # Default background
            object_state = processed_images[1] if len(processed_images) > 1 else None
            status_msg = f"**Status:** {len(processed_images)} images uploaded - Click any image below to edit! 🎨"
            canvas_info = f"**Select an image from the gallery above to start editing**"
        
        # Don't show image in canvas automatically - wait for gallery selection
        canvas_image = None
        
        # Store images for gallery selection
        self.uploaded_images = processed_images
        
        logging.info(f"✅ Multi-image upload: {len(processed_images)} images processed")
        logging.info(f"✅ Uploaded images stored: {[type(img) for img in self.uploaded_images]}")
        
        return (
            preview_images,           # uploaded_images_preview
            background_state,         # i2i_canvas_image_state  
            object_state,            # i2i_object_image_state
            canvas_image,            # i2i_interactive_canvas - None until selection
            status_msg,              # step1_status
            canvas_info,             # canvas_mode_info - instructions
            None,                    # i2i_pin_coords_state - clear previous selection
            None                     # i2i_anchor_coords_state - clear previous selection
        )

    def handle_gallery_click(self, evt: gr.SelectData):
        """Handle when user clicks on an image in the gallery - set as background, keep others as objects"""
        try:
            logging.info(f"🖼️ Gallery click: Index {evt.index}")
            
            if self.uploaded_images and len(self.uploaded_images) > evt.index:
                selected_image = self.uploaded_images[evt.index]
                
                # For multi-image workflow: selected image becomes background, others become objects
                if len(self.uploaded_images) > 1:
                    # Get the other images as potential objects (excluding selected background)
                    other_images = [img for i, img in enumerate(self.uploaded_images) if i != evt.index]
                    object_image = other_images[0] if other_images else None  # Use first other image as object
                    
                    logging.info(f"🖼️ Multi-image mode: Background={evt.index}, Object={'Available' if object_image else 'None'}")
                    
                    return (
                        selected_image,                                           # i2i_canvas_image_state - selected as background
                        object_image,                                             # i2i_object_image_state - first other image as object
                        selected_image,                                           # i2i_interactive_canvas - show background in canvas
                        "**Click areas on the image to place the object**",      # canvas_mode_info - multi-image instructions
                        None,                                                     # i2i_pin_coords_state - clear pin coords
                        None                                                      # i2i_anchor_coords_state - clear anchor coords
                    )
                else:
                    # Single image mode
                    logging.info(f"🖼️ Single image mode: {evt.index}")
                    
                    return (
                        selected_image,                                           # i2i_canvas_image_state - selected image  
                        None,                                                     # i2i_object_image_state - no object for single image
                        selected_image,                                           # i2i_interactive_canvas - show selected image in canvas
                        "**Click areas on the image to select for editing**",    # canvas_mode_info - single image instructions
                        None,                                                     # i2i_pin_coords_state - clear pin coords
                        None                                                      # i2i_anchor_coords_state - clear anchor coords
                    )
            else:
                logging.warning(f"Gallery click index {evt.index} out of range")
                return None, None, None, "**No image selected**", None, None
                
        except Exception as e:
            logging.error(f"Gallery click error: {e}")
            return None, None, None, "**Error loading image**", None, None




