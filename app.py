import gradio as gr
import yaml
import logging
import os
import time
import numpy as np
from PIL import Image
from core import constants as const
from core.generator import Generator
from core.ui import create_ui
from core.secure_storage import SecureStorage
from core.handlers.i2i_handler import I2IHandler
from core.enhancer import get_enhancer
from core.vision_streamlined import (
    generate_comprehensive_auto_prompt
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoGenApp:
    def __init__(self):
        logging.info("Initializing PhotoGen App...")
        with open('config.yaml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.secure_storage = SecureStorage()
        self.generator = Generator(self.config)
        self.demo, self.ui, self.states = create_ui()

        self.i2i_handler = I2IHandler(self.ui, self.generator, self.secure_storage)

        self._register_event_handlers()
        logging.info("??PhotoGen App Initialized.")

    def _register_event_handlers(self):
        with self.demo:
            self.demo.load(self.load_app_state, outputs=[self.ui['provider_select'], self.ui['api_key_input'], self.ui['pro_api_key_input']])
            
            self.i2i_handler.register_event_handlers()
            self._register_api_key_handlers()
            self._register_additional_handlers()

    def _register_additional_handlers(self):
        """Register additional handlers for token counting, saving, and enhancement."""
        # Token counting for unified Create/Edit mode
        if 'i2i_token_counter' in self.ui:
            self.ui['i2i_prompt'].change(fn=self.update_token_count, inputs=self.ui['i2i_prompt'], outputs=self.ui['i2i_token_counter'])
        
        # Image saving - handle gallery selection and save button
        if 'save_btn' in self.ui and 'download_output' in self.ui:
            # Handle gallery selection with more robust event handling
            def on_gallery_select(evt: gr.SelectData):
                # evt.index contains the index, evt.value contains the image data
                try:
                    logging.info(f"🖼️ Gallery selection - Index: {evt.index}, Value type: {type(evt.value)}")
                    
                    # In newer Gradio versions, evt.value contains the image path/data
                    if evt.value is not None:
                        logging.info(f"🖼️ Using evt.value: {evt.value}")
                        return evt.value
                    
                    # Fallback: Try to get the image from gallery value using index
                    gallery_value = self.ui['output_gallery'].value
                    if gallery_value and len(gallery_value) > evt.index:
                        selected_image = gallery_value[evt.index]
                        logging.info(f"🖼️ Fallback - selected image at index {evt.index}: {type(selected_image)}")
                        return selected_image
                    else:
                        logging.warning(f"🖼️ No valid selection found")
                        return None
                        
                except Exception as e:
                    logging.error(f"🖼️ Gallery selection error: {e}")
                    return None
            
            # Register the gallery selection event  
            self.ui['output_gallery'].select(
                fn=on_gallery_select,
                outputs=[self.ui['selected_gallery_image_state']]
            )
            
            # Enhanced save method that combines all strategies
            def enhanced_save_image(selected_img):
                """Enhanced save method with multiple fallback strategies"""
                logging.info(f"💾 Enhanced save called - Selected: {type(selected_img)}")
                
                # Strategy 1: Use selected image if available
                if selected_img is not None:
                    logging.info("💾 Using selected image")
                    return self.save_image(selected_img, "photogen")
                
                # Strategy 2: Get from gallery directly
                try:
                    gallery_value = self.ui['output_gallery'].value
                    logging.info(f"💾 Gallery fallback - Type: {type(gallery_value)}, Length: {len(gallery_value) if gallery_value else 0}")
                    
                    if gallery_value and len(gallery_value) > 0:
                        # Save the most recent image
                        recent_img = gallery_value[-1]
                        logging.info(f"💾 Using most recent from gallery: {type(recent_img)}")
                        gr.Info("No image selected. Saving the most recent image from gallery...")
                        return self.save_image(recent_img, "photogen")
                except Exception as e:
                    logging.error(f"💾 Gallery access failed: {e}")
                
                # Strategy 3: Try last generated image state
                try:
                    if 'last_generated_image_state' in self.ui:
                        last_generated = self.ui['last_generated_image_state'].value
                        if last_generated is not None:
                            logging.info(f"💾 Using last generated: {type(last_generated)}")
                            gr.Info("Using the most recently generated image...")
                            return self.save_image(last_generated, "photogen")
                except Exception as e:
                    logging.error(f"💾 Last generated fallback failed: {e}")
                
                gr.Warning("No image available to save. Please generate an image first.")
                return None
            
            # Register the enhanced save method
            self.ui['save_btn'].click(
                enhanced_save_image,
                inputs=[self.ui['selected_gallery_image_state']], 
                outputs=self.ui['download_output']
            )

        # Clear All button functionality
        if 'clear_all_btn' in self.ui:
            self.ui['clear_all_btn'].click(
                self.clear_all,
                inputs=[],
                outputs=[
                    self.ui['output_gallery'],
                    self.ui['i2i_prompt'],
                    self.ui['i2i_source_uploader'],
                    self.ui['uploaded_images_preview'],
                    self.ui['i2i_interactive_canvas'],
                    self.ui['canvas_mode_info'],
                    self.ui['edit_selected_btn'],
                    self.ui['back_to_compose_btn'],
                    self.ui['selected_gallery_image_state'],
                    self.ui['last_generated_image_state'],
                    self.ui['i2i_canvas_image_state'],
                    self.ui['i2i_object_image_state'],
                    self.ui['step1_status'],
                    self.ui['step2_status']
                ]
            )

        # Simplified workflow - no complex handlers needed
        logging.info("Using simplified auto-prompt workflow - handlers reduced")

    def _register_api_key_handlers(self):
        self.ui['provider_select'].change(fn=self.load_saved_key, inputs=self.ui['provider_select'], outputs=self.ui['api_key_input'])
        self.ui['save_api_key_btn'].click(self.save_enhancer_api_key, inputs=[self.ui['provider_select'], self.ui['api_key_input']])
        self.ui['clear_api_key_btn'].click(lambda p: self.secure_storage.clear_api_key(p), inputs=[self.ui['provider_select']], outputs=self.ui['api_key_input'])
        
        # Pro API Provider handling - dynamic label updates
        self.ui['pro_api_provider_select'].change(
            fn=self.update_pro_api_label_and_load_key,
            inputs=[self.ui['pro_api_provider_select']],
            outputs=[self.ui['pro_api_key_input']]
        )
        
        self.ui['save_pro_api_key_btn'].click(self.save_pro_api_key, inputs=[self.ui['pro_api_provider_select'], self.ui['pro_api_key_input']])
        self.ui['clear_pro_api_key_btn'].click(self.clear_pro_api_key, inputs=[self.ui['pro_api_provider_select']], outputs=self.ui['pro_api_key_input'])

    def load_app_state(self):
        providers_from_config = self.config.get('enhancer_providers', [])
        if isinstance(providers_from_config, dict):
            enhancer_providers = list(providers_from_config.keys())
        elif isinstance(providers_from_config, list):
            enhancer_providers = providers_from_config
        else:
            enhancer_providers = []

        first_provider = enhancer_providers[0] if enhancer_providers else None
        enhancer_key = self.secure_storage.load_api_key(first_provider) if first_provider else ""
        
        # For Pro API, default to Black Forest Labs and load its key
        default_pro_provider = const.FLUX_PRO_API
        pro_model_key = self.secure_storage.load_api_key(default_pro_provider)
        
        return gr.update(choices=enhancer_providers, value=first_provider), enhancer_key, pro_model_key

    def load_saved_key(self, provider_name):
        return self.secure_storage.load_api_key(provider_name)

    def save_enhancer_api_key(self, provider_name, api_key):
        if not provider_name:
            gr.Warning("Please select a Provider first.")
            return
        self.secure_storage.save_api_key(provider_name, api_key)
        gr.Info(f"API key for {provider_name} has been saved securely.")

    def save_pro_api_key(self, provider_name, api_key):
        """Save API key for selected Pro provider"""
        if not provider_name:
            gr.Warning("Please select a Pro API Provider first.")
            return
        self.secure_storage.save_api_key(provider_name, api_key)
        gr.Info(f"API key for {provider_name} has been saved securely.")

    def clear_pro_api_key(self, provider_name):
        """Clear API key for selected Pro provider"""
        if not provider_name:
            return ""
        self.secure_storage.clear_api_key(provider_name)
        gr.Info(f"API key for {provider_name} has been cleared.")
        return ""

    def update_pro_api_label_and_load_key(self, provider_name):
        """Update UI label and load saved key when provider changes"""
        if not provider_name:
            return gr.update(label="Pro API Key", value="")
        
        # Load saved key for this provider
        saved_key = self.secure_storage.load_api_key(provider_name)
        
        # Update label to show current provider
        label = f"{provider_name} Key"
        
        return gr.update(label=label, value=saved_key)

    def clear_all(self):
        """Clear gallery, prompt, and uploaded images while preserving API keys and settings."""
        logging.info("🗑️ Clearing all: gallery, prompt, and uploaded images")
        
        # Clear uploaded images from i2i_handler
        if hasattr(self.i2i_handler, 'uploaded_images'):
            self.i2i_handler.uploaded_images = []
        
        gr.Info("Cleared gallery, prompt, and uploaded images!")
        
        return (
            [],  # output_gallery - empty list
            "",  # i2i_prompt - empty string
            None,  # i2i_source_uploader - clear files
            [],  # uploaded_images_preview - empty gallery
            None,  # i2i_interactive_canvas - clear image
            gr.update(visible=False),  # canvas_mode_info - hide
            gr.update(visible=False),  # edit_selected_btn - hide
            gr.update(visible=False),  # back_to_compose_btn - hide
            None,  # selected_gallery_image_state - clear state
            None,  # last_generated_image_state - clear state
            None,  # i2i_canvas_image_state - clear state
            None,  # i2i_object_image_state - clear state
            "**Status:** Upload images to start 📸",  # step1_status - reset
            "**Status:** Ready for your prompt ✏️"  # step2_status - reset
        )

    def update_token_count(self, prompt_text):
        """Updates the token count display for prompts."""
        if self.generator.tokenizer is None: 
            return "Tokenizer not available."
        max_length = 77 
        if not prompt_text: 
            return f"Tokens: 0 / {max_length}"
        count = len(self.generator.tokenizer.encode(prompt_text))
        message = f"Tokens: {count} / {max_length}"
        if count > max_length: 
            message += " ?��? **Warning:** Prompt will be truncated!"
        return message

    def save_image(self, img, img_type):
        """Saves generated images to the outputs directory."""
        logging.info(f"?�� Save image called - Type: {type(img)}, Value: {repr(img)[:200]}")
        
        if img is None:
            gr.Warning("Please select an image from the gallery first.")
            return
        os.makedirs(const.OUTPUTS_DIR, exist_ok=True)
        
        if isinstance(img, tuple):
            img = img[0]
            logging.info(f"?�� Extracted from tuple - Type: {type(img)}")

        # Handle different image types
        if isinstance(img, dict):
            # Handle Gradio gallery format where img is a dict with 'image' or 'name' key
            img_path = None
            if 'image' in img:
                img_data = img['image']
                # Check if 'image' contains another dict with 'path'
                if isinstance(img_data, dict) and 'path' in img_data:
                    img_path = img_data['path']
                    logging.info(f"?�� Using nested 'image.path' key: {img_path}")
                else:
                    img_path = img_data
                    logging.info(f"?�� Using 'image' key: {img_path}")
            elif 'name' in img:
                img_path = img['name']
                logging.info(f"?�� Using 'name' key: {img_path}")
            elif 'path' in img:
                img_path = img['path']
                logging.info(f"?�� Using 'path' key: {img_path}")
            elif 'value' in img:
                img_path = img['value']
                logging.info(f"?�� Using 'value' key: {img_path}")
            else:
                # Try to find any string value in the dict
                for key, value in img.items():
                    if isinstance(value, str) and (value.endswith('.png') or value.endswith('.jpg') or value.endswith('.jpeg') or value.endswith('.webp')):
                        img_path = value
                        logging.info(f"?�� Found image path in '{key}': {img_path}")
                        break
                    elif isinstance(value, dict) and 'path' in value:
                        img_path = value['path']
                        logging.info(f"?�� Found nested path in '{key}.path': {img_path}")
                        break
                
                if not img_path:
                    logging.error(f"?�� Could not extract image path from dict keys: {list(img.keys())}")
                    gr.Error("Could not extract image path from gallery selection.")
                    return
            
            try:
                pil_img = Image.open(img_path)
                logging.info(f"?�� Successfully loaded image from path: {img_path}")
            except Exception as e:
                logging.error(f"?�� Could not open image file: {e}")
                gr.Error(f"Could not open image file: {e}")
                return
        elif isinstance(img, str):
            # If it's a file path, load the image first
            try:
                pil_img = Image.open(img)
                logging.info(f"?�� Successfully loaded image from string path: {img}")
            except Exception as e:
                logging.error(f"?�� Could not open image file: {e}")
                gr.Error(f"Could not open image file: {e}")
                return
        elif isinstance(img, np.ndarray):
            pil_img = Image.fromarray(img)
            logging.info(f"?�� Converted numpy array to PIL image: {img.shape}")
        elif hasattr(img, 'save'):
            pil_img = img  # Assume it's already a PIL Image
            logging.info(f"?�� Using existing PIL image: {img.size}")
        else:
            logging.error(f"?�� Unknown image type: {type(img)}")
            gr.Error(f"Unknown image format: {type(img)}. Please try selecting the image again.")
            return
        
        filepath = f"{const.OUTPUTS_DIR}/{img_type}_output_{int(time.time())}.png"
        try:
            pil_img.save(filepath)
            logging.info(f"?�� Image saved successfully to: {filepath}")
            gr.Info(f"Image saved to {filepath}")
            return gr.update(value=filepath, visible=True)
        except Exception as e:
            logging.error(f"?�� Failed to save image: {e}")
            gr.Error(f"Failed to save image: {e}")
            return

    def launch(self):
        self.demo.launch()

if __name__ == "__main__":
    app = PhotoGenApp()
    app.launch()
