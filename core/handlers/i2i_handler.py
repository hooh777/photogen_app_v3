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
    
    def register_event_handlers(self):
        """Register all UI event handlers with multi-image workflow"""
        
        # Multi-image upload handler (new single upload point)
        self.ui['i2i_source_uploader'].upload(
            self.handle_multi_image_upload,
            inputs=[self.ui['i2i_source_uploader']],
            outputs=[
                self.ui['uploaded_images_preview'],    # gallery
                self.ui['i2i_canvas_image_state'],     # background state
                self.ui['i2i_object_image_state'],     # object state
                self.ui['i2i_interactive_canvas'],     # canvas display
                self.ui['step1_status'],               # status markdown
                self.ui['i2i_auto_prompt_btn']         # button visibility
            ]
        )
        
        # Legacy object uploader - now deprecated but kept for compatibility
        self.ui['i2i_object_uploader'].change(
            lambda x: None,  # No-op, preview gallery handles display
            inputs=[self.ui['i2i_object_uploader']],
            outputs=[]
        )
        
        # Gallery selection for editing mode
        self.ui['uploaded_images_preview'].select(
            self.handle_gallery_selection,
            inputs=[],  # SelectData is passed automatically, no inputs needed
            outputs=[
                self.ui['uploaded_images_preview'],    # keep gallery updated
                self.ui['preview_mode_container'],     # show preview mode
                self.ui['i2i_canvas_image_state']      # update canvas state
            ]
        )
        
        # Edit selected image button
        self.ui['edit_selected_btn'].click(
            self.enable_editing_mode,
            inputs=[self.ui['i2i_canvas_image_state']],
            outputs=[
                self.ui['i2i_interactive_canvas'],     # make canvas interactive
                self.ui['canvas_mode_info'],           # update info text
                self.ui['preview_mode_container'],     # hide preview mode
                self.ui['editing_mode_container']      # show editing mode
            ]
        )
        
        # Back to composition button  
        self.ui['back_to_compose_btn'].click(
            self.back_to_composition_step1,  # First clear the gallery
            outputs=[
                self.ui['uploaded_images_preview']     # clear gallery first
            ],
            show_progress=False
        ).then(
            self.back_to_composition_step2,  # Then hide other elements and repopulate
            outputs=[
                self.ui['preview_mode_container'],     # hide preview mode
                self.ui['editing_mode_container'],     # hide editing mode
                self.ui['canvas_controls_container'],  # hide canvas controls
                self.ui['uploaded_images_preview'],    # repopulate gallery
                self.ui['step1_status']                # reset status message
            ],
            show_progress=False
        )

        # Single-click area selection
        self.ui['i2i_interactive_canvas'].select(
            self.handle_click_with_prompt_button, 
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
        
        # Selection reset
        self.ui['i2i_reset_selection_btn'].click(
            self.reset_selection,
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
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
                self.ui['disable_auto_enhancement']
            ], 
            outputs=[self.ui['output_gallery'], self.ui['last_generated_image_state']] if 'last_generated_image_state' in self.ui else [self.ui['output_gallery']]
        ).then(
            # Clear selection state on new generation
            lambda: None,
            outputs=[self.ui['selected_gallery_image_state']] if 'selected_gallery_image_state' in self.ui else []
        )
        
        # Prompt status updates
        self.ui['i2i_prompt'].change(
            self.update_prompt_status,
            inputs=[self.ui['i2i_prompt']],
            outputs=[self.ui['step2_status']]
        )
        
        # Token counter (if available)
        if 'i2i_token_counter' in self.ui:
            self.ui['i2i_prompt'].change(
                self.update_token_count,
                inputs=[self.ui['i2i_prompt']],
                outputs=[self.ui['i2i_token_counter']]
            )

    # === Delegation Methods to Focused Managers ===
    
    # Canvas operations → CanvasManager
    def update_canvas_with_merge(self, base_img, obj_img, top_left, bottom_right):
        return self.canvas_manager.update_canvas_with_merge(base_img, obj_img, top_left, bottom_right)
    
    def handle_click(self, base_img, obj_img, top_left, bottom_right, evt: gr.SelectData):
        return self.canvas_manager.handle_click(base_img, obj_img, top_left, bottom_right, evt)
    
    def handle_click_with_prompt_button(self, base_img, obj_img, top_left, bottom_right, evt: gr.SelectData):
        # Get the canvas update from the original handler
        canvas_result = self.canvas_manager.handle_click(base_img, obj_img, top_left, bottom_right, evt)
        
        # Show the smart prompt button after area selection
        return (
            canvas_result[0],  # updated canvas
            canvas_result[1],  # pin coords
            canvas_result[2],  # anchor coords
            gr.update(visible=True)  # show auto-prompt button
        )
    
    def reset_selection(self, base_img, obj_img):
        return self.canvas_manager.reset_selection(base_img, obj_img)
    
    # State management → StateManager
    def store_background(self, img, existing_object=None):
        return self.state_manager.store_background(img, existing_object)

    def store_object(self, img):
        return self.state_manager.store_object(img)
    
    def update_prompt_status(self, prompt_text):
        return self.state_manager.update_prompt_status(prompt_text)
    
    def update_token_count(self, prompt_text):
        return self.state_manager.update_token_count(prompt_text, self.generator)
    
    # Auto-prompt generation → AutoPromptManager
    def auto_generate_prompt(self, base_img, object_img, top_left, bottom_right, existing_prompt, provider_name, allow_human_surfaces=False):
        return self.auto_prompt_manager.generate_auto_prompt(base_img, object_img, top_left, bottom_right, existing_prompt, provider_name, allow_human_surfaces)
    
    # Image generation → GenerationManager
    def run_i2i(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress(), disable_auto_enhancement=False):
        return self.generation_manager.run_generation(source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress, disable_auto_enhancement)
    
    def run_i2i_with_state_update(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress(), disable_auto_enhancement=False):
        """Wrapper for run_i2i that also returns the last generated image for state tracking."""
        result_list = self.run_i2i(source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress, disable_auto_enhancement)
        
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
            return [], None, None, None, "**Status:** Ready to upload images 📁", gr.update(visible=False)
        
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
            return [], None, None, None, "**Status:** Error processing images ❌", gr.update(visible=False)
        
        # Set up states but don't show canvas automatically
        if len(processed_images) == 1:
            # Single image - ready for editing
            background_state = processed_images[0]
            object_state = None
            status_msg = f"**Status:** 1 image uploaded - Click image above to start editing 🖼️"
            auto_prompt_visible = gr.update(visible=True)
            
        else:
            # Multiple images - ready for composition
            background_state = processed_images[0]
            object_state = processed_images[1] if len(processed_images) > 1 else None
            status_msg = f"**Status:** {len(processed_images)} images uploaded - Ready for composition 🎨"
            auto_prompt_visible = gr.update(visible=True)
        
        # Don't show canvas automatically - user must select image first
        canvas_image = None
        
        # Store images for gallery selection
        self.uploaded_images = processed_images
        
        logging.info(f"✅ Multi-image upload: {len(processed_images)} images processed")
        
        return (
            preview_images,           # uploaded_images_preview
            background_state,         # i2i_canvas_image_state  
            object_state,            # i2i_object_image_state
            canvas_image,            # i2i_interactive_canvas
            status_msg,              # step1_status
            auto_prompt_visible      # i2i_auto_prompt_btn visibility
        )
    
    def handle_gallery_selection(self, evt: gr.SelectData):
        """Handle when user clicks on an image in the preview gallery"""
        try:
            if self.uploaded_images and len(self.uploaded_images) > evt.index:
                selected_image = self.uploaded_images[evt.index]
                
                logging.info(f"🖼️ Gallery selection: Index {evt.index}, Total images: {len(self.uploaded_images)}, Type: {type(selected_image)}")
                
                # Keep all images in gallery but highlight the selected one
                gallery_update = gr.update(value=self.uploaded_images, selected_index=evt.index)
                logging.info("🖼️ Updating gallery to show all images with selection")
                
                return (
                    gallery_update,                                           # keep full gallery with selection
                    gr.update(visible=True),                                  # preview_mode_container
                    selected_image                                            # i2i_canvas_image_state
                )
            else:
                logging.warning(f"Gallery selection index {evt.index} out of range or no uploaded images")
                return gr.update(), gr.update(visible=False), None
        except Exception as e:
            logging.error(f"Gallery selection error: {e}")
            return gr.update(), gr.update(visible=False), None
    
    def enable_editing_mode(self, canvas_image):
        """Enable interactive editing mode for the selected image"""
        if canvas_image is None:
            return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        
        return (
            gr.update(value=canvas_image, interactive=True, visible=True),    # make canvas interactive
            gr.update(value="**Editing Mode** - Click on image areas for targeted editing 🎯", visible=True),  # canvas_mode_info
            gr.update(visible=False),                                         # hide preview mode
            gr.update(visible=True)                                           # show editing mode
        )
    
    def back_to_composition(self):
        """Return to composition view, reset selection back to initial upload state"""
        # Debug: Check what we have in uploaded_images
        logging.info(f"🔙 Back to composition - uploaded_images count: {len(self.uploaded_images)}")
        
        # Try aggressive gallery reset - completely recreate the component state
        if self.uploaded_images:
            # Use a dictionary update to force complete refresh
            gallery_update = gr.update(
                value=list(self.uploaded_images),
                selected_index=None,
                visible=True,
                interactive=False,  # Ensure it's non-interactive for selection
                allow_preview=True,
                columns=3,
                height=200
            )
            logging.info("🔙 Aggressive gallery reset with complete component state")
        else:
            gallery_update = gr.update(
                value=[],
                selected_index=None,
                visible=True,
                interactive=False,
                allow_preview=True,
                columns=3,
                height=200
            )
            logging.info("🔙 No uploaded images to show")
        
        # Reset status message based on number of uploaded images
        if len(self.uploaded_images) == 1:
            status_msg = "**Status:** 1 image uploaded - Click image above to start editing 🖼️"
        elif len(self.uploaded_images) > 1:
            status_msg = f"**Status:** {len(self.uploaded_images)} images uploaded - Click any image above to start editing 🎨"
        else:
            status_msg = "**Status:** Upload images to start 📸"
        
        return (
            gr.update(visible=False),                                         # hide canvas completely
            gr.update(visible=False),                                         # hide info
            gr.update(visible=False),                                         # hide preview mode
            gr.update(visible=False),                                         # hide editing mode
            gallery_update,                                                   # reset gallery selection
            status_msg                                                        # reset status message
        )
    
    def back_to_composition_step1(self):
        """Step 1: Clear the gallery to force refresh"""
        logging.info("🔙 Step 1: Clearing gallery")
        return gr.update(value=[], selected_index=None)
    
    def back_to_composition_step2(self):
        """Step 2: Hide elements and repopulate gallery"""
        logging.info(f"🔙 Step 2: Repopulating gallery with {len(self.uploaded_images)} images")
        
        # Repopulate gallery with uploaded images
        if self.uploaded_images:
            gallery_update = gr.update(
                value=list(self.uploaded_images),
                selected_index=None,
                visible=True,
                interactive=False,
                allow_preview=True,
                columns=3,
                height=200
            )
        else:
            gallery_update = gr.update(value=[], selected_index=None, visible=True)
        
        # Reset status message
        if len(self.uploaded_images) == 1:
            status_msg = "**Status:** 1 image uploaded - Click image above to start editing 🖼️"
        elif len(self.uploaded_images) > 1:
            status_msg = f"**Status:** {len(self.uploaded_images)} images uploaded - Click any image above to start editing 🎨"
        else:
            status_msg = "**Status:** Upload images to start 📸"
        
        return (
            gr.update(visible=False),                                         # hide preview mode
            gr.update(visible=False),                                         # hide editing mode
            gr.update(visible=False),                                         # hide canvas controls
            gallery_update,                                                   # repopulate gallery
            status_msg                                                        # reset status message
        )
