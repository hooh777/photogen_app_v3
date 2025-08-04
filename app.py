import gradio as gr
import yaml
import logging
import os
import time
import numpy as np
from PIL import Image
from core.generator import Generator
from core.ui import create_ui
from core.secure_storage import SecureStorage
from core import constants as const
from core.handlers.demo_handler import DemoHandler
from core.handlers.i2i_handler import I2IHandler
from core.enhancer import get_enhancer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoGenApp:
    def __init__(self):
        logging.info("Initializing PhotoGen App...")
        with open('config.yaml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.secure_storage = SecureStorage()
        self.generator = Generator(self.config)
        self.demo, self.ui, self.states = create_ui()

        self.demo_handler = DemoHandler(self.ui, self.generator, self.secure_storage, self.config)
        self.i2i_handler = I2IHandler(self.ui, self.generator, self.secure_storage)

        self._register_event_handlers()
        self._load_demo_assets()
        logging.info("✅ PhotoGen App Initialized.")

    def _load_demo_assets(self):
        """Load demo assets into galleries on startup."""
        if hasattr(self, 'demo_handler'):
            # Get available background images
            background_paths = []
            for bg_config in self.config.get('demo_backgrounds', []):
                bg_path = bg_config['background_path']
                if os.path.exists(bg_path):
                    background_paths.append(bg_path)
            
            # Get available object images
            object_paths = []
            for obj_config in self.config.get('demo_objects', []):
                obj_path = obj_config['image']
                if os.path.exists(obj_path):
                    object_paths.append(obj_path)
            
            # Update galleries with found images
            if background_paths:
                self.ui['demo_background_gallery'].value = background_paths
            if object_paths:
                self.ui['demo_object_gallery'].value = object_paths
    
    def _register_event_handlers(self):
        with self.demo:
            self.demo.load(self.load_app_state, outputs=[self.ui['provider_select'], self.ui['api_key_input'], self.ui['pro_api_key_input']])
            
            self.ui['mode_tabs'].select(
                self.switch_main_view, 
                None, 
                [self.ui['output_gallery'], self.ui['i2i_interactive_canvas']]
            )
            
            self.demo_handler.register_event_handlers()
            self.i2i_handler.register_event_handlers()
            self._register_api_key_handlers()
            self._register_additional_handlers()

    def _register_additional_handlers(self):
        """Register additional handlers for token counting, saving, and enhancement."""
        # Token counting for unified Create/Edit mode
        if 'i2i_token_counter' in self.ui:
            self.ui['i2i_prompt'].change(fn=self.update_token_count, inputs=self.ui['i2i_prompt'], outputs=self.ui['i2i_token_counter'])
        
        # Image saving
        if 'save_btn' in self.ui and 'download_output' in self.ui:
            self.ui['save_btn'].click(
                lambda imgs: self.save_image(imgs[0] if isinstance(imgs, list) else imgs, "photogen"),
                inputs=[self.ui['output_gallery']], 
                outputs=self.ui['download_output']
            )
        
        # Enhancement modal handlers
        if 'launch_enhancer_btn' in self.ui:
            self.ui['launch_enhancer_btn'].click(lambda: gr.update(visible=True), outputs=self.ui['enhancer_modal'])
            self.ui['close_enhancer_btn'].click(lambda: gr.update(visible=False), outputs=self.ui['enhancer_modal'])
            self.ui['enhance_btn'].click(
                self.run_enhancement, 
                inputs=[
                    self.ui['provider_select'], self.ui['api_key_input'],
                    self.ui['base_prompt_input'], self.ui['i2i_interactive_canvas']
                ], 
                outputs=[
                    self.ui['detailed_output'], self.ui['stylized_output'], self.ui['rephrased_output']
                ]
            )
            self.ui['use_detailed_btn'].click(lambda x: (x, gr.update(visible=False)), inputs=self.ui['detailed_output'], outputs=[self.ui['i2i_prompt'], self.ui['enhancer_modal']])
            self.ui['use_stylized_btn'].click(lambda x: (x, gr.update(visible=False)), inputs=self.ui['stylized_output'], outputs=[self.ui['i2i_prompt'], self.ui['enhancer_modal']])
            self.ui['use_rephrased_btn'].click(lambda x: (x, gr.update(visible=False)), inputs=self.ui['rephrased_output'], outputs=[self.ui['i2i_prompt'], self.ui['enhancer_modal']])

    def _register_api_key_handlers(self):
        self.ui['provider_select'].change(fn=self.load_saved_key, inputs=self.ui['provider_select'], outputs=self.ui['api_key_input'])
        self.ui['save_api_key_btn'].click(self.save_enhancer_api_key, inputs=[self.ui['provider_select'], self.ui['api_key_input']])
        self.ui['clear_api_key_btn'].click(lambda p: self.secure_storage.clear_api_key(p), inputs=[self.ui['provider_select']], outputs=self.ui['api_key_input'])
        
        self.ui['save_pro_api_key_btn'].click(self.save_pro_api_key, inputs=[self.ui['pro_api_key_input']])
        self.ui['clear_pro_api_key_btn'].click(lambda: self.secure_storage.clear_api_key(const.FLUX_PRO_API), outputs=self.ui['pro_api_key_input'])

    def switch_main_view(self, evt: gr.SelectData):
        """Shows/hides the correct output view based on the selected tab."""
        if evt.index == 1: # Index 1 is the "Create / Edit" tab
            return gr.update(visible=False), gr.update(visible=True)
        else: # "Demo" tab uses the gallery
            return gr.update(visible=True), gr.update(visible=False)

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
        if img is None:
            gr.Warning("No image to save.")
            return
        os.makedirs(const.OUTPUTS_DIR, exist_ok=True)
        
        if isinstance(img, tuple):
            img = img[0]

        pil_img = Image.fromarray(img) if isinstance(img, np.ndarray) else img
        filepath = f"{const.OUTPUTS_DIR}/{img_type}_output_{int(time.time())}.png"
        pil_img.save(filepath)
        gr.Info(f"Image saved to {filepath}")
        return gr.update(value=filepath, visible=True)
    
    def run_enhancement(self, provider, api_key, base_prompt, source_image):
        """Runs prompt enhancement using the selected LLM provider."""
        if not api_key:
            raise gr.Error("API Key is missing for the selected LLM Provider!")
        if not base_prompt or not base_prompt.strip():
            gr.Warning("Please enter your basic idea for the prompt.")
            return None, None, None
            
        enhancer = get_enhancer(provider, api_key)
        source_np = np.array(source_image) if source_image is not None else None
        
        gr.Info(f"Requesting prompt suggestions from {provider}...")
        return enhancer.enhance(base_prompt, image=source_np)

    def launch(self):
        self.demo.launch()

if __name__ == "__main__":
    app = PhotoGenApp()
    app.launch()