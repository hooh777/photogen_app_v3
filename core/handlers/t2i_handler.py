import gradio as gr
from core import constants as const, utils

class T2IHandler:
    def __init__(self, ui, generator, secure_storage):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage

    def register_event_handlers(self):
        self.ui['t2i_generate_btn'].click(
            self.run_t2i, 
            inputs=[
                self.ui['t2i_prompt'], self.ui['t2i_style_select'], 
                self.ui['aspect_ratio'], self.ui['num_images'],
                self.ui['t2i_steps'], self.ui['t2i_guidance'], 
                self.ui['t2i_model_select']
            ], 
            outputs=self.ui['output_gallery']
        )

    def run_t2i(self, prompt, style, aspect_ratio, num_images, steps, guidance, model_choice, progress=gr.Progress(track_tqdm=True)):
        if not prompt or not prompt.strip():
            raise gr.Error("Please enter a prompt.")
        
        gr.Info("Loading model... this may take a minute on the first run.")
        
        full_prompt = prompt
        if style and style.strip():
            full_prompt = f"{prompt}, {style} style"
        
        gr.Info(f"Generating with prompt: {full_prompt}")
        width, height = utils.get_dimensions(aspect_ratio)
        api_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
        
        images = self.generator.text_to_image(
            full_prompt, steps, guidance, model_choice, num_images, width, height, api_key, progress
        )
        return images