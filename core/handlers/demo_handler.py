import gradio as gr
import numpy as np
from PIL import Image
from core import utils, constants as const

class DemoHandler:
    def __init__(self, ui, generator, secure_storage, config):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage
        self.config = config

    def register_event_handlers(self):
        """Registers all event handlers for the Demo panel."""
        self.ui['demo_background_gallery'].select(self.store_background, inputs=None, outputs=self.ui['selected_background_path'])
        self.ui['demo_object_gallery'].select(self.store_object, inputs=None, outputs=self.ui['selected_object_path'])
        self.ui['demo_generate_btn'].click(
            self.run_demo_generation, 
            inputs=[
                self.ui['selected_background_path'], self.ui['selected_object_path'],
                self.ui['demo_style_select'], self.ui['demo_aspect_ratio'], 
                self.ui['demo_num_images']
            ], 
            outputs=self.ui['output_gallery']
        )
    def store_background(self, evt: gr.SelectData):
        return self.config['demo_backgrounds'][evt.index]['background_path']

    def store_object(self, evt: gr.SelectData):
        return self.config['demo_objects'][evt.index]['image']

    def run_demo_generation(self, bg_path, obj_path, style, aspect_ratio, num_images, progress=gr.Progress()):
        if not bg_path or not obj_path:
            raise gr.Error("Please select a background and an object from the demo galleries.")
        
        background_img = Image.open(bg_path)
        object_img = Image.open(obj_path)
        merged_image = utils.paste_object(background_img, object_img)
        merged_np = np.array(merged_image)

        # Conditionally add the style to the prompt
        prompt = "A beautiful scene featuring the selected object, high quality, 4k"
        if style and style.strip():
            prompt = f"{prompt}, {style} style"

        gr.Info(f"Generating demo with prompt: {prompt}")

        width, height = utils.get_dimensions(aspect_ratio)
        api_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
        
        images = self.generator.image_to_image(
            merged_np, prompt, 28, 4.0, const.LOCAL_MODEL, num_images, width, height, api_key, progress
        )
        return images