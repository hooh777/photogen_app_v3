import gradio as gr
from core import constants as const
from core import utils


class T2IHandler:
    def __init__(self, ui, generator, secure_storage):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage

    def register_event_handlers(self):
        self.ui['t2i_generate_btn'].click(
            self.run_t2i, 
            inputs=[
                self.ui['t2i_prompt'], self.ui['t2i_style_select'], self.ui['t2i_aspect_ratio'],
                self.ui['t2i_steps'], self.ui['t2i_guidance'], 
                self.ui['t2i_model_select'], self.ui['t2i_num_images']
            ], 
            outputs=self.ui['output_gallery']
        )
        
    def run_t2i(self, prompt, style, aspect_ratio, steps, guidance, model_choice, num_images, progress=gr.Progress(track_tqdm=True)):
        if not prompt or not prompt.strip():
            raise gr.Error("Please enter a prompt.")
        
        # Conditionally add the style to the prompt
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