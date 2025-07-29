import gradio as gr
import yaml
import logging
from core.generator import Generator
from core.ui import create_ui
from core.secure_storage import SecureStorage
from core import constants as const
from core.handlers.i2i_handler import I2IHandler
from core.handlers.t2i_handler import T2IHandler

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
        self.t2i_handler = T2IHandler(self.ui, self.generator, self.secure_storage)

        self._register_event_handlers()
        logging.info("✅ PhotoGen App Initialized.")
    
    def _register_event_handlers(self):
        with self.demo:
            self.demo.load(self.load_app_state, outputs=[self.ui['provider_select'], self.ui['api_key_input'], self.ui['pro_api_key_input']])
            
            self.ui['mode_tabs'].select(
                self.switch_main_view, 
                None, 
                [self.ui['output_gallery'], self.ui['i2i_interactive_canvas']]
            )
            
            self.i2i_handler.register_event_handlers()
            self.t2i_handler.register_event_handlers()
            self._register_api_key_handlers()

    def _register_api_key_handlers(self):
        self.ui['provider_select'].change(fn=self.load_saved_key, inputs=self.ui['provider_select'], outputs=self.ui['api_key_input'])
        self.ui['save_api_key_btn'].click(self.save_enhancer_api_key, inputs=[self.ui['provider_select'], self.ui['api_key_input']])
        self.ui['clear_api_key_btn'].click(lambda p: self.secure_storage.clear_api_key(p), inputs=[self.ui['provider_select']], outputs=self.ui['api_key_input'])
        
        self.ui['save_pro_api_key_btn'].click(self.save_pro_api_key, inputs=[self.ui['pro_api_key_input']])
        self.ui['clear_pro_api_key_btn'].click(lambda: self.secure_storage.clear_api_key(const.FLUX_PRO_API), outputs=self.ui['pro_api_key_input'])

    def switch_main_view(self, evt: gr.SelectData):
        """Shows/hides the correct output view based on the selected tab."""
        if evt.index == 1: # Index 1 is the "Edit" tab
            return gr.update(visible=False), gr.update(visible=True)
        else: # "Create" tab uses the gallery
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

    def launch(self):
        self.demo.launch()

if __name__ == "__main__":
    app = PhotoGenApp()
    app.launch()