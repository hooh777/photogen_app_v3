"""
Streamlined I2I Handler - Main orchestrator optimized for Pro model workflow
Dramatically reduced from 983 lines to focus on essential coordination
"""
import os
import gradio as gr
import logging

# Import focused managers for better organization
from .canvas_manager import CanvasManager
from .auto_prompt_manager import AutoPromptManager
from .state_manager import StateManager
from .generation_manager import GenerationManager

# Import default canvas image
from ..ui import create_default_canvas_image


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
        
        # Handle file changes (including when files are removed with cross button)
        self.ui['i2i_source_uploader'].change(
            self.handle_file_change,
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
            self.auto_prompt_manager.generate_auto_prompt, 
            inputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'],
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
                self.ui['i2i_prompt'], self.ui['provider_select']
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

    # === Essential Methods - Direct Manager Access ===
    
    def run_i2i_with_state_update(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress()):
        """Wrapper for run_i2i that also returns the last generated image for state tracking."""
        result_list = self.generation_manager.run_generation(source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress)
        
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
        
        # Process uploaded files (max 10 images) with duplicate filename handling
        processed_images = []
        preview_images = []
        used_filenames = set()  # Track filenames to handle duplicates
        
        for file_obj in uploaded_files[:10]:  # Limit to 10 images
            try:
                if hasattr(file_obj, 'name'):
                    # File object with .name attribute
                    img = Image.open(file_obj.name)
                    original_filename = os.path.basename(file_obj.name)
                else:
                    # Direct file path
                    img = Image.open(file_obj)
                    original_filename = os.path.basename(file_obj)
                
                # Handle duplicate filenames by adding numbers
                unique_filename = self._get_unique_filename(original_filename, used_filenames)
                used_filenames.add(unique_filename)
                
                # Debug logging for filename handling
                if original_filename != unique_filename:
                    logging.info(f"🔄 Filename collision detected: '{original_filename}' -> '{unique_filename}'")
                else:
                    logging.info(f"📄 Processing file: '{original_filename}'")
                
                # Set the unique filename as metadata for tracking
                img.info['filename'] = unique_filename
                
                processed_images.append(img)
                # For gallery display - use tuple format (image, caption) to force separate entries
                preview_images.append((img, unique_filename))  # Filename as caption
                
            except Exception as e:
                logging.error(f"Error processing uploaded file: {e}")
                continue
        
        if not processed_images:
            return [], None, None, create_default_canvas_image(), "**Status:** Error processing images ❌", "**Upload valid images to start**", None, None
        
        # Set up states but don't show canvas automatically - user must select from gallery
        # Get filenames for status display
        adjusted_filenames = [img.info.get('filename', 'unknown') for img in processed_images]
        filename_display = ", ".join(adjusted_filenames[:3])  # Show first 3 filenames
        if len(adjusted_filenames) > 3:
            filename_display += f" (+{len(adjusted_filenames) - 3} more)"
        
        if len(processed_images) == 1:
            # Single image - ready for selection
            background_state = processed_images[0]
            object_state = None
            status_msg = f"**Status:** image uploaded: `{adjusted_filenames[0]}`"
            canvas_info = "**Select an image from the gallery above to start editing**"
            
        else:
            # Multiple images - ready for selection
            background_state = processed_images[0]  # Default background
            object_state = processed_images[1] if len(processed_images) > 1 else None
            status_msg = f"**Status:** {len(processed_images)} images uploaded: `{filename_display}` - Click any image below to edit! 🎨"
            canvas_info = f"**Select an image from the gallery above to start editing**"
        
        # Don't show image in canvas automatically - wait for gallery selection
        canvas_image = create_default_canvas_image()  # Show default white image instead of None
        
        # Store images for gallery selection
        self.uploaded_images = processed_images
        
        # Debug: Show final filename summary
        if processed_images:
            filenames = [img.info.get('filename', 'unknown') for img in processed_images]
            logging.info(f"📋 Final filename list: {filenames}")
            logging.info(f"📊 Used filenames set: {sorted(used_filenames)}")
            logging.info(f"🖼️ Gallery preview format: {len(preview_images)} items with captions")
        
        logging.info(f"✅ Multi-image upload: {len(processed_images)} images processed")
        logging.info(f"✅ Uploaded images stored: {[type(img) for img in self.uploaded_images]}")
        
        return (
            preview_images,          # uploaded_images_preview
            background_state,        # i2i_canvas_image_state  
            object_state,           # i2i_object_image_state
            canvas_image,           # i2i_interactive_canvas - None until selection
            status_msg,             # step1_status
            canvas_info,            # canvas_mode_info - instructions
            None,                   # i2i_pin_coords_state - clear previous selection
            None                    # i2i_anchor_coords_state - clear previous selection
        )

    def handle_file_change(self, uploaded_files):
        """
        Handle file changes including when files are removed via cross button.
        This is triggered whenever the file list changes (add/remove).
        
        Args:
            uploaded_files: Current list of uploaded file objects from gr.File
            
        Returns:
            Tuple of outputs for UI updates
        """
        logging.info(f"🔄 File change detected: {len(uploaded_files) if uploaded_files else 0} files")
        
        # Use the same logic as handle_multi_image_upload
        return self.handle_multi_image_upload(uploaded_files)
    
    def _get_unique_filename(self, filename, used_filenames):
        """
        Generate a unique filename by adding numbers if duplicates exist.
        
        Args:
            filename: Original filename
            used_filenames: Set of already used filenames
            
        Returns:
            str: Unique filename
        """
        if filename not in used_filenames:
            logging.info(f"✅ Filename '{filename}' is unique")
            return filename
        
        logging.info(f"⚠️ Filename '{filename}' already exists, generating unique version...")
        
        # Split filename and extension
        name, ext = os.path.splitext(filename)
        counter = 1
        
        # Keep trying until we find a unique name
        while True:
            new_filename = f"{name} ({counter}){ext}"
            if new_filename not in used_filenames:
                logging.info(f"✅ Generated unique filename: '{new_filename}'")
                return new_filename
            logging.info(f"⚠️ '{new_filename}' also exists, trying next number...")
            counter += 1

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
                        "",                                                       # canvas_mode_info - no instruction text
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
                        "",                                                       # canvas_mode_info - no instruction text
                        None,                                                     # i2i_pin_coords_state - clear pin coords
                        None                                                      # i2i_anchor_coords_state - clear anchor coords
                    )
            else:
                logging.warning(f"Gallery click index {evt.index} out of range")
                return None, None, create_default_canvas_image(), "**No image selected**", None, None
                
        except Exception as e:
            logging.error(f"Gallery click error: {e}")
            return None, None, create_default_canvas_image(), "**Error loading image**", None, None

    def handle_selfie_preset_selection(self, preset_selection):
        """Handle selfie background preset selection and return appropriate prompt."""
        logging.info(f"🎯 Selfie preset selected: {preset_selection}")
        
        # Define preset prompts for each background
        preset_prompts = {
            "None (Custom Prompt)": "",
            
            # Elevator variations
            "Elevator - Modern": "standing in a sleek modern elevator with brushed steel walls, LED lighting panels, and polished floor reflecting the person",
            "Elevator - Vintage": "standing in a classic vintage elevator with brass buttons, wood paneling, and warm ambient lighting",
            "Elevator - Glass/Panoramic": "standing in a glass panoramic elevator with city views visible through transparent walls and modern lighting",
            "Elevator - Industrial": "standing in an industrial freight elevator with exposed metal walls, heavy-duty controls, and utilitarian lighting",
            
            # Train variations
            "Train - Subway Car": "sitting in a modern subway train car with bright fluorescent lighting, metal handrails, and urban transit atmosphere",
            "Train - Luxury Train": "standing in an elegant luxury train car with rich wood interiors, plush seating, and sophisticated ambient lighting",
            "Train - Vintage Train Car": "standing in a vintage train car with classic wooden benches, brass fittings, and nostalgic railway atmosphere",
            "Train - Bullet Train Interior": "sitting in a sleek bullet train interior with modern seating, large windows, and high-tech ambient lighting",
            
            # Cafe variations
            "Cafe - Cozy Coffee Shop": "sitting in a cozy coffee shop with warm lighting, exposed brick walls, wooden tables, and coffee aroma atmosphere",
            "Cafe - Modern Minimalist": "standing in a modern minimalist cafe with clean lines, white walls, natural lighting, and contemporary furniture",
            "Cafe - Outdoor Patio": "sitting on an outdoor cafe patio with natural daylight, bistro tables, and urban street atmosphere",
            "Cafe - Bookstore Cafe": "standing in a bookstore cafe surrounded by bookshelves, reading nooks, and warm literary atmosphere",
            
            # Restaurant variations
            "Restaurant - Fine Dining": "standing in an upscale fine dining restaurant with elegant decor, soft ambient lighting, and sophisticated atmosphere",
            "Restaurant - Casual Bistro": "sitting in a casual bistro with comfortable seating, warm lighting, and relaxed dining atmosphere",
            "Restaurant - Rooftop Bar": "standing on a rooftop restaurant bar with city skyline views, modern furniture, and evening ambient lighting",
            "Restaurant - Kitchen Counter": "standing at a restaurant kitchen counter with stainless steel surfaces, professional lighting, and culinary atmosphere"
        }
        
        # Get the preset prompt
        preset_prompt = preset_prompts.get(preset_selection, "")
        
        logging.info(f"📝 Generated preset prompt: {preset_prompt[:100]}..." if len(preset_prompt) > 100 else f"📝 Generated preset prompt: {preset_prompt}")
        
        return preset_prompt




