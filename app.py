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
        """Register additional handlers for saving and enhancement."""
        # Simplified download button - no gallery selection needed
        if 'download_result_btn' in self.ui and 'download_output' in self.ui:
            # Simplified download method - gets state values as inputs
            def download_latest_image(gallery_images, last_generated_state):
                """Download the most recently generated image from inputs"""
                try:
                    # Primary method: get from last_generated_image_state input
                    logging.info(f"💾 Checking last_generated_state input: {type(last_generated_state)} - {last_generated_state is not None}")
                    if last_generated_state is not None:
                        logging.info(f"💾 Downloading from last_generated_state: {type(last_generated_state)}")
                        filepath = self.save_and_download_image(last_generated_state, "photogen")
                        if filepath and os.path.exists(filepath):
                            absolute_path = os.path.abspath(filepath)
                            logging.info(f"💾 Triggering download with gr.update: {absolute_path}")
                            return gr.update(value=absolute_path, visible=True)
                        else:
                            logging.error(f"💾 File not found or save failed: {filepath}")
                            return gr.update(visible=False)
                    
                    # Fallback: get from gallery input
                    logging.info(f"💾 Checking gallery_images input: {type(gallery_images)} - Length: {len(gallery_images) if gallery_images else 0}")
                    if gallery_images and len(gallery_images) > 0:
                        # Get the most recent image (last in the gallery)
                        recent_img = gallery_images[-1]
                        logging.info(f"💾 Downloading latest image from gallery: {type(recent_img)}")
                        filepath = self.save_and_download_image(recent_img, "photogen")
                        if filepath and os.path.exists(filepath):
                            absolute_path = os.path.abspath(filepath)
                            logging.info(f"💾 Triggering download with gr.update: {absolute_path}")
                            return gr.update(value=absolute_path, visible=True)
                        else:
                            logging.error(f"💾 File not found or save failed: {filepath}")
                            return gr.update(visible=False)
                    
                except Exception as e:
                    logging.error(f"💾 Download failed: {e}")
                    import traceback
                    logging.error(f"💾 Traceback: {traceback.format_exc()}")
                
                gr.Warning("No image available to download. Please generate an image first.")
                return gr.update(visible=False)
            
            # Register the download method with inputs - output directly to download
            self.ui['download_result_btn'].click(
                download_latest_image,
                inputs=[self.ui['output_gallery'], self.ui['last_generated_image_state']],
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
                    self.ui['selected_gallery_image_state'],
                    self.ui['last_generated_image_state'],
                    self.ui['i2i_canvas_image_state'],
                    self.ui['i2i_object_image_state'],
                    self.ui['i2i_pin_coords_state'],
                    self.ui['i2i_anchor_coords_state'],
                    self.ui['step1_status'],
                    self.ui['step2_status'],
                    self.ui['final_status']
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
        """Clear all state and reset the app to initial state."""
        logging.info("🗑️ Clearing all: resetting app state completely")
        
        # Clear uploaded images from i2i_handler
        if hasattr(self.i2i_handler, 'uploaded_images'):
            self.i2i_handler.uploaded_images = []
        
        gr.Info("�️ All data cleared! Upload new images to start fresh.")
        
        return (
            [],  # output_gallery - empty list
            "",  # i2i_prompt - empty string
            None,  # i2i_source_uploader - clear files
            [],  # uploaded_images_preview - empty gallery
            None,  # i2i_interactive_canvas - clear image
            "**Upload images above to start editing**",  # canvas_mode_info - update message
            None,  # selected_gallery_image_state - clear state
            None,  # last_generated_image_state - clear state
            None,  # i2i_canvas_image_state - clear state
            None,  # i2i_object_image_state - clear state
            None,  # i2i_pin_coords_state - clear selection coords
            None,  # i2i_anchor_coords_state - clear selection coords
            "**Status:** Upload images to start 📸",  # step1_status - reset
            "**Status:** Ready for your prompt ✏️",  # step2_status - reset
            "**Status:** Ready to generate! 🎉"  # final_status - reset
        )

    def save_and_download_image(self, img, img_type):
        """Saves image and returns path for immediate download."""
        logging.info(f"💾 Save and download image called - Type: {type(img)}")
        
        if img is None:
            gr.Warning("No image available to download.")
            return None
            
        os.makedirs(const.OUTPUTS_DIR, exist_ok=True)
        
        # Process the image to get PIL format
        pil_img = None
        if isinstance(img, tuple):
            img = img[0]
            
        if isinstance(img, dict):
            # Handle Gradio gallery format
            img_path = None
            for key in ['image', 'name', 'path', 'value']:
                if key in img:
                    potential_path = img[key]
                    if isinstance(potential_path, dict) and 'path' in potential_path:
                        img_path = potential_path['path']
                    else:
                        img_path = potential_path
                    break
            
            if img_path:
                try:
                    pil_img = Image.open(img_path)
                except Exception as e:
                    logging.error(f"💾 Could not open image file: {e}")
                    return None
        elif isinstance(img, str):
            try:
                pil_img = Image.open(img)
            except Exception as e:
                logging.error(f"💾 Could not open image file: {e}")
                return None
        elif isinstance(img, np.ndarray):
            pil_img = Image.fromarray(img)
        elif hasattr(img, 'save'):
            pil_img = img  # Already a PIL Image
        
        if pil_img is None:
            logging.error(f"💾 Could not process image type: {type(img)}")
            return None
        
        # Save the image
        filepath = f"{const.OUTPUTS_DIR}/{img_type}_output_{int(time.time())}.png"
        try:
            pil_img.save(filepath)
            logging.info(f"💾 Image saved successfully to: {filepath}")
            gr.Info(f"Image downloaded: {os.path.basename(filepath)}")
            return filepath
        except Exception as e:
            logging.error(f"💾 Failed to save image: {e}")
            gr.Error(f"Failed to save image: {e}")
            return None

    def launch(self):
        print("=" * 50)
        print("🚀 PhotoGen App v3 Starting...")
        print("=" * 50)
        print("⚡ Loading AI models and initializing...")
        print("🌐 Starting web interface...")
        print("📱 The app will be available at: http://localhost:7860")
        print("=" * 50)
        
        self.demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            inbrowser=False,  # Don't auto-open here, let run-photogen.bat handle it
            share=False,
            show_error=True,
            quiet=False,
            show_api=False
        )

if __name__ == "__main__":
    app = PhotoGenApp()
    app.launch()
