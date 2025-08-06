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
from core.vision import analyze_scene_for_prompting, generate_auto_prompt, enhance_user_prompt, suggest_prompt_variations

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
        logging.info("✅ PhotoGen App Initialized.")

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
                # evt.value contains the selected image data, evt.index contains the index
                logging.info(f"🖼️ Gallery selection - Index: {evt.index}, Type: {type(evt.value)}, Value: {evt.value}")
                
                # Different ways to extract the image based on Gradio version/format
                if evt.value is not None:
                    # Clear any previous selection to ensure fresh state
                    logging.info(f"🖼️ Gallery selected image at index {evt.index}")
                    return evt.value
                else:
                    logging.warning(f"🖼️ Gallery selection returned None for index {evt.index}")
                    return None
            
            # Register the gallery selection event
            self.ui['output_gallery'].select(
                on_gallery_select,
                outputs=self.ui['selected_gallery_image_state']
            )
            
            # Also try to handle gallery click events if select doesn't work
            try:
                self.ui['output_gallery'].click(
                    on_gallery_select,
                    outputs=self.ui['selected_gallery_image_state']
                )
            except:
                pass  # Some Gradio versions might not support click on gallery
            
            # Handle save button click
            def save_selected_image(selected_img):
                logging.info(f"💾 Save button clicked - Selected image type: {type(selected_img)}, Value: {repr(selected_img)[:200]}")
                
                if selected_img is None:
                    # Fallback 1: Try to get the last generated image from state
                    logging.warning("💾 No image selected, trying last generated image state")
                    
                    try:
                        if 'last_generated_image_state' in self.ui:
                            last_generated = self.ui['last_generated_image_state'].value
                            if last_generated is not None:
                                logging.info(f"💾 Using last generated image: {type(last_generated)}")
                                gr.Info("Saving the most recently generated image...")
                                return self.save_image(last_generated, "photogen")
                    except Exception as e:
                        logging.error(f"💾 Last generated image fallback failed: {e}")
                    
                    # Fallback 2: Try to get gallery value directly
                    gr.Warning("No image selected. Attempting to save the most recent image from gallery...")
                    
                    try:
                        gallery_value = self.ui['output_gallery'].value
                        logging.info(f"💾 Gallery fallback - Type: {type(gallery_value)}, Value: {repr(gallery_value)[:200]}")
                        
                        if gallery_value and len(gallery_value) > 0:
                            # Take the first (most recent) image
                            recent_img = gallery_value[0] if isinstance(gallery_value, list) else gallery_value
                            logging.info(f"💾 Using most recent image from gallery: {type(recent_img)}")
                            return self.save_image(recent_img, "photogen")
                    except Exception as e:
                        logging.error(f"💾 Gallery fallback failed: {e}")
                    
                    gr.Warning("No image available to save. Please generate an image first, then click on it in the gallery before saving.")
                    return None
                    
                return self.save_image(selected_img, "photogen")
            
            self.ui['save_btn'].click(
                save_selected_image,
                inputs=[self.ui['selected_gallery_image_state']], 
                outputs=self.ui['download_output']
            )

        # Auto Suggestions handlers
        self._register_auto_suggestions_handlers()

    def _register_api_key_handlers(self):
        self.ui['provider_select'].change(fn=self.load_saved_key, inputs=self.ui['provider_select'], outputs=self.ui['api_key_input'])
        self.ui['save_api_key_btn'].click(self.save_enhancer_api_key, inputs=[self.ui['provider_select'], self.ui['api_key_input']])
        self.ui['clear_api_key_btn'].click(lambda p: self.secure_storage.clear_api_key(p), inputs=[self.ui['provider_select']], outputs=self.ui['api_key_input'])
        
        self.ui['save_pro_api_key_btn'].click(self.save_pro_api_key, inputs=[self.ui['pro_api_key_input']])
        self.ui['clear_pro_api_key_btn'].click(lambda: self.secure_storage.clear_api_key(const.FLUX_PRO_API), outputs=self.ui['pro_api_key_input'])

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
        pro_model_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
        
        return gr.update(choices=enhancer_providers, value=first_provider), enhancer_key, pro_model_key

    def load_saved_key(self, provider_name):
        return self.secure_storage.load_api_key(provider_name)

    def save_enhancer_api_key(self, provider_name, api_key):
        if not provider_name:
            gr.Warning("Please select a Provider first.")
            return
        self.secure_storage.save_api_key(provider_name, api_key)
        gr.Info(f"API key for {provider_name} has been saved securely.")

    def save_pro_api_key(self, api_key):
        self.secure_storage.save_api_key(const.FLUX_PRO_API, api_key)
        gr.Info(f"{const.FLUX_PRO_API} key has been saved securely.")

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
            message += " ⚠️ **Warning:** Prompt will be truncated!"
        return message

    def save_image(self, img, img_type):
        """Saves generated images to the outputs directory."""
        logging.info(f"💾 Save image called - Type: {type(img)}, Value: {repr(img)[:200]}")
        
        if img is None:
            gr.Warning("Please select an image from the gallery first.")
            return
        os.makedirs(const.OUTPUTS_DIR, exist_ok=True)
        
        if isinstance(img, tuple):
            img = img[0]
            logging.info(f"💾 Extracted from tuple - Type: {type(img)}")

        # Handle different image types
        if isinstance(img, dict):
            # Handle Gradio gallery format where img is a dict with 'image' or 'name' key
            img_path = None
            if 'image' in img:
                img_data = img['image']
                # Check if 'image' contains another dict with 'path'
                if isinstance(img_data, dict) and 'path' in img_data:
                    img_path = img_data['path']
                    logging.info(f"💾 Using nested 'image.path' key: {img_path}")
                else:
                    img_path = img_data
                    logging.info(f"💾 Using 'image' key: {img_path}")
            elif 'name' in img:
                img_path = img['name']
                logging.info(f"💾 Using 'name' key: {img_path}")
            elif 'path' in img:
                img_path = img['path']
                logging.info(f"💾 Using 'path' key: {img_path}")
            elif 'value' in img:
                img_path = img['value']
                logging.info(f"💾 Using 'value' key: {img_path}")
            else:
                # Try to find any string value in the dict
                for key, value in img.items():
                    if isinstance(value, str) and (value.endswith('.png') or value.endswith('.jpg') or value.endswith('.jpeg') or value.endswith('.webp')):
                        img_path = value
                        logging.info(f"💾 Found image path in '{key}': {img_path}")
                        break
                    elif isinstance(value, dict) and 'path' in value:
                        img_path = value['path']
                        logging.info(f"💾 Found nested path in '{key}.path': {img_path}")
                        break
                
                if not img_path:
                    logging.error(f"💾 Could not extract image path from dict keys: {list(img.keys())}")
                    gr.Error("Could not extract image path from gallery selection.")
                    return
            
            try:
                pil_img = Image.open(img_path)
                logging.info(f"💾 Successfully loaded image from path: {img_path}")
            except Exception as e:
                logging.error(f"💾 Could not open image file: {e}")
                gr.Error(f"Could not open image file: {e}")
                return
        elif isinstance(img, str):
            # If it's a file path, load the image first
            try:
                pil_img = Image.open(img)
                logging.info(f"💾 Successfully loaded image from string path: {img}")
            except Exception as e:
                logging.error(f"💾 Could not open image file: {e}")
                gr.Error(f"Could not open image file: {e}")
                return
        elif isinstance(img, np.ndarray):
            pil_img = Image.fromarray(img)
            logging.info(f"💾 Converted numpy array to PIL image: {img.shape}")
        elif hasattr(img, 'save'):
            pil_img = img  # Assume it's already a PIL Image
            logging.info(f"💾 Using existing PIL image: {img.size}")
        else:
            logging.error(f"💾 Unknown image type: {type(img)}")
            gr.Error(f"Unknown image format: {type(img)}. Please try selecting the image again.")
            return
        
        filepath = f"{const.OUTPUTS_DIR}/{img_type}_output_{int(time.time())}.png"
        try:
            pil_img.save(filepath)
            logging.info(f"💾 Image saved successfully to: {filepath}")
            gr.Info(f"Image saved to {filepath}")
            return gr.update(value=filepath, visible=True)
        except Exception as e:
            logging.error(f"💾 Failed to save image: {e}")
            gr.Error(f"Failed to save image: {e}")
            return

    def _register_auto_suggestions_handlers(self):
        """Register event handlers for auto suggestions functionality."""
        if 'show_suggestions_btn' not in self.ui:
            return
            
        # Show/Hide suggestions panel and generate suggestions
        self.ui['show_suggestions_btn'].click(
            self.generate_auto_suggestions,
            inputs=[
                self.ui['i2i_source_uploader'], 
                self.ui['i2i_prompt'], 
                self.ui['provider_select'], 
                self.ui['api_key_input']
            ],
            outputs=[
                self.ui['scene_summary'],
                self.ui['scene_analysis_details'],
                self.ui['auto_generated_prompt'],
                self.ui['enhanced_user_prompt'],
                self.ui['variation_1'],
                self.ui['variation_2'],
                self.ui['variation_3'],
                self.ui['auto_suggestions_panel']
            ]
        )
        
        # Scene details toggle
        self.ui['scene_details_btn'].click(
            self.toggle_scene_details,
            outputs=[self.ui['scene_analysis_details']]
        )
        
        # Copy button handlers with feedback
        self.ui['copy_auto_prompt_btn'].click(
            self.copy_prompt_with_feedback,
            inputs=[self.ui['auto_generated_prompt']],
            outputs=[self.ui['i2i_prompt'], self.ui['copy_auto_icon']]
        )
        
        self.ui['copy_enhanced_prompt_btn'].click(
            self.copy_prompt_with_feedback,
            inputs=[self.ui['enhanced_user_prompt']],
            outputs=[self.ui['i2i_prompt'], self.ui['copy_enhanced_icon']]
        )
        
        self.ui['copy_var1_btn'].click(
            self.copy_prompt_with_feedback,
            inputs=[self.ui['variation_1']],
            outputs=[self.ui['i2i_prompt'], self.ui['copy_var1_icon']]
        )
        
        self.ui['copy_var2_btn'].click(
            self.copy_prompt_with_feedback,
            inputs=[self.ui['variation_2']],
            outputs=[self.ui['i2i_prompt'], self.ui['copy_var2_icon']]
        )
        
        self.ui['copy_var3_btn'].click(
            self.copy_prompt_with_feedback,
            inputs=[self.ui['variation_3']],
            outputs=[self.ui['i2i_prompt'], self.ui['copy_var3_icon']]
        )
        
        # Auto-generate suggestions when background image changes
        self.ui['i2i_source_uploader'].change(
            self.on_background_change,
            inputs=[self.ui['i2i_source_uploader']],
            outputs=[self.ui['show_suggestions_btn']]
        )

    def on_background_change(self, background_image):
        """Show the suggestions button when a background image is uploaded."""
        if background_image is not None:
            return gr.update(visible=True)
        else:
            return gr.update(visible=False)

    def toggle_suggestions_panel(self):
        """Toggle the auto suggestions panel visibility and generate suggestions."""
        return gr.update(visible=True, open=True)

    def toggle_scene_details(self):
        """Toggle the scene analysis details visibility."""
        return gr.update(visible=True)

    def copy_prompt_with_feedback(self, prompt_text):
        """Copy prompt to input field and show feedback."""
        if prompt_text:
            return prompt_text, gr.update(value="✅ Copied!", visible=True)
        else:
            return gr.update(), gr.update(value="❌ Nothing to copy", visible=True)

    def generate_auto_suggestions(self, background_image, user_prompt, provider, api_key):
        """Generate all auto suggestions based on the background image and user prompt."""
        if not background_image:
            return self._empty_suggestions()
            
        if not api_key:
            gr.Warning("Please set up your Vision/Enhancer API key first!")
            return self._empty_suggestions()
        
        try:
            gr.Info("🔍 Analyzing scene and generating suggestions...")
            
            # Step 1: Analyze scene
            scene_analysis = analyze_scene_for_prompting(background_image, provider, api_key)
            if not scene_analysis:
                gr.Warning("Failed to analyze scene. Please try again.")
                return self._empty_suggestions()
            
            # Step 2: Generate auto prompt (using a default object if no user prompt)
            test_object = user_prompt if user_prompt.strip() else "object"
            auto_prompt = generate_auto_prompt(scene_analysis, test_object)
            
            # Step 3: Enhanced user prompt (if user has typed something)
            enhanced_prompt = ""
            if user_prompt.strip():
                enhanced_prompt = enhance_user_prompt(user_prompt, scene_analysis)
            
            # Step 4: Generate variations
            base_for_variations = enhanced_prompt if enhanced_prompt else auto_prompt
            variations = suggest_prompt_variations(base_for_variations, scene_analysis, 3)
            
            # Step 5: Create scene summary
            env = scene_analysis.get('environment', {})
            selection = scene_analysis.get('selection_area', {})
            lighting = scene_analysis.get('lighting', {})
            style = scene_analysis.get('style_mood', {})
            
            scene_summary = f"**Detected:** {env.get('type', 'unknown')} scene, {selection.get('surface_material', 'unknown')} surface, {lighting.get('quality', 'unknown')} {lighting.get('type', 'unknown')} lighting, {style.get('overall_style', 'unknown')} style"
            
            return (
                scene_summary,
                scene_analysis,
                auto_prompt,
                enhanced_prompt,
                variations[0] if len(variations) > 0 else "",
                variations[1] if len(variations) > 1 else "",
                variations[2] if len(variations) > 2 else "",
                gr.update(visible=True, open=True),  # Show suggestions panel
            )
            
        except Exception as e:
            logging.error(f"Auto suggestions generation failed: {e}")
            gr.Error(f"Failed to generate suggestions: {str(e)}")
            return self._empty_suggestions()

    def _empty_suggestions(self):
        """Return empty suggestions when generation fails."""
        return (
            "**Detected:** No scene analyzed yet",
            {},
            "",
            "",
            "",
            "",
            "",
            gr.update(visible=False),
        )

    def launch(self):
        self.demo.launch()

if __name__ == "__main__":
    app = PhotoGenApp()
    app.launch()