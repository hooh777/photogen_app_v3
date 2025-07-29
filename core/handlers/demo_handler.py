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
        self.ui['demo_background_gallery'].select(self.select_background, outputs=[self.ui['selected_background_path'], self.ui['current_prompt_templates_state'], self.ui['p1_editable'], self.ui['p1_prefix'], self.ui['p1_suffix'], self.ui['p2_editable'], self.ui['p2_prefix'], self.ui['p2_suffix'], self.ui['p2_checkbox'], self.ui['p3_editable'], self.ui['p3_prefix'], self.ui['p3_suffix'], self.ui['p3_checkbox']])
        self.ui['demo_object_gallery'].select(self.store_object, inputs=None, outputs=self.ui['selected_object_path'])
        
        run_inputs = [
            self.ui['selected_background_path'], self.ui['selected_object_path'],
            self.ui['current_prompt_templates_state'], self.ui['p1_editable'],
            self.ui['p2_editable'], self.ui['p3_editable'], self.ui['p2_checkbox'],
            self.ui['p3_checkbox'], self.ui['demo_num_images']
        ]
        self.ui['demo_generate_btn'].click(self.run_demo_generation, inputs=run_inputs, outputs=self.ui['output_gallery'])

    def select_background(self, evt: gr.SelectData):
        selected_bg_config = self.config['demo_backgrounds'][evt.index]
        path = selected_bg_config['background_path']
        prompts = selected_bg_config['prompts']
        
        p1_prefix, _, p1_suffix = utils.parse_template(prompts[0]['template'])
        p2_prefix, _, p2_suffix = utils.parse_template(prompts[1]['template'])
        p3_prefix, _, p3_suffix = utils.parse_template(prompts[2]['template'])
        
        return (
            gr.update(value=path), prompts,
            gr.update(value="", placeholder=prompts[0]['placeholder']), p1_prefix, p1_suffix,
            gr.update(value="", placeholder=prompts[1]['placeholder']), p2_prefix, p2_suffix, gr.update(value=False),
            gr.update(value="", placeholder=prompts[2]['placeholder']), p3_prefix, p3_suffix, gr.update(value=False)
        )

    def store_object(self, evt: gr.SelectData):
        return self.config['demo_objects'][evt.index]['image']

    def run_demo_generation(self, bg_path, obj_path, current_templates, p1_input, p2_input, p3_input, use_p2, use_p3, num_images, progress=gr.Progress()):
        if not bg_path or not obj_path: raise gr.Error("Please select a background and an object.")
        if not current_templates: raise gr.Error("Please select a background to load prompt templates.")

        final_prompt_parts = []
        if not p1_input.strip(): raise gr.Error("Please fill in 'Base Description'.")
        template1 = current_templates[0]
        _, placeholder1, _ = utils.parse_template(template1['template'])
        final_prompt_parts.append(template1['template'].replace(f"{{{placeholder1}}}", p1_input))
        
        if use_p2:
            if not p2_input.strip(): raise gr.Error("Please fill in 'Position & Lighting' or disable it.")
            template2 = current_templates[1]
            _, placeholder2, _ = utils.parse_template(template2['template'])
            final_prompt_parts.append(template2['template'].replace(f"{{{placeholder2}}}", p2_input))

        if use_p3:
            if not p3_input.strip(): raise gr.Error("Please fill in 'Style & Tone' or disable it.")
            template3 = current_templates[2]
            _, placeholder3, _ = utils.parse_template(template3['template'])
            final_prompt_parts.append(template3['template'].replace(f"{{{placeholder3}}}", p3_input))
        
        prompt = ", ".join(final_prompt_parts)
        gr.Info(f"Generated Prompt: {prompt}")

        background_img = Image.open(bg_path)
        object_img = Image.open(obj_path)
        merged_image = utils.paste_object(background_img, object_img)
        merged_np = np.array(merged_image)
        width, height = merged_image.size

        api_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
        images = self.generator.image_to_image(
            merged_np, prompt, 28, 4.0, const.LOCAL_MODEL, num_images, width, height, api_key, progress
        )
        return images