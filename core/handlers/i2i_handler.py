import gradio as gr
import numpy as np
from PIL import Image, ImageDraw
from core import constants as const, utils, vision
import time
import os

class I2IHandler:
    def __init__(self, ui, generator, secure_storage):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage
    
    def register_event_handlers(self):
        self.ui['i2i_source_uploader'].upload(
            self.store_background,
            inputs=[self.ui['i2i_source_uploader']],
            outputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_interactive_canvas'],
                self.ui['i2i_object_image_state'], self.ui['i2i_pin_coords_state'], 
                self.ui['i2i_anchor_coords_state']
            ]
        )
        self.ui['i2i_object_uploader'].upload(
            self.store_object,
            inputs=[self.ui['i2i_object_uploader']],
            outputs=[self.ui['i2i_object_image_state']]
        ).then(self._redraw_canvas, inputs=self._get_redraw_inputs(), outputs=self.ui['i2i_interactive_canvas'])

        self.ui['i2i_interactive_canvas'].select(
            self.handle_click, 
            inputs=[
                self.ui['i2i_canvas_image_state'],
                self.ui['i2i_object_image_state'],
                self.ui['i2i_pin_coords_state'],
                self.ui['i2i_anchor_coords_state']
            ], 
            outputs=[
                self.ui['i2i_interactive_canvas'], 
                self.ui['i2i_pin_coords_state'],
                self.ui['i2i_anchor_coords_state']
            ]
        )
        
        self.ui['i2i_auto_prompt_btn'].click(
            self.auto_generate_prompt, 
            inputs=[
                self.ui['i2i_canvas_image_state'], 
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
                self.ui['i2i_prompt'],
                self.ui['provider_select'] # Pass the selected provider
            ], 
            outputs=self.ui['i2i_prompt']
        )

        self.ui['i2i_generate_btn'].click(self.run_i2i, inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], self.ui['i2i_prompt'], self.ui['i2i_style_select'], self.ui['aspect_ratio'], self.ui['i2i_steps'], self.ui['i2i_guidance'], self.ui['i2i_model_select']], outputs=[self.ui['i2i_interactive_canvas'], self.ui['i2i_actions_group']])
        self.ui['accept_btn'].click(self.accept_and_continue, inputs=self.ui['i2i_interactive_canvas'], outputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_interactive_canvas'], self.ui['i2i_actions_group']])
        self.ui['retry_btn'].click(self.discard_and_retry, inputs=self.ui['i2i_canvas_image_state'], outputs=[self.ui['i2i_interactive_canvas'], self.ui['i2i_actions_group']])
        self.ui['i2i_save_btn'].click(self.save_image, inputs=self.ui['i2i_interactive_canvas'], outputs=self.ui['i2i_download_output'])

    def _get_redraw_inputs(self):
        return [self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']]

    def store_background(self, img):
        return img, img, None, None, None

    def store_object(self, img):
        return img

    def handle_click(self, base_img, obj_img, top_left, bottom_right, evt: gr.SelectData):
        if base_img is None: raise gr.Error("Please upload a background image first.")
        click_coords = evt.index
        if top_left is None or (top_left and bottom_right):
            new_top_left = click_coords
            new_bottom_right = None
        else:
            new_top_left = top_left
            new_bottom_right = click_coords
        updated_canvas = self._redraw_canvas(base_img, obj_img, new_top_left, new_bottom_right)
        return updated_canvas, new_top_left, new_bottom_right
    
    def _redraw_canvas(self, base_img, obj_img, top_left, bottom_right):
        if base_img is None: return None
        canvas_copy = base_img.copy().convert("RGBA")
        draw = ImageDraw.Draw(canvas_copy, "RGBA")
        if obj_img:
            obj_w, obj_h = obj_img.size
            new_h = 100 
            new_w = int(obj_w * (new_h / obj_h)) if obj_h > 0 else 0
            if new_w > 0 and new_h > 0:
                resized_obj = obj_img.resize((new_w, new_h), Image.LANCZOS)
                alpha_mask = resized_obj.getchannel('A') if resized_obj.mode == 'RGBA' else Image.new('L', resized_obj.size, 255)
                alpha_mask = alpha_mask.point(lambda p: p * 0.5)
                paste_x = (base_img.width - new_w) // 2
                paste_y = (base_img.height - new_h) // 2
                canvas_copy.paste(resized_obj, (paste_x, paste_y), alpha_mask)
        if top_left and bottom_right:
            x1, y1 = top_left
            x2, y2 = bottom_right
            box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            draw.rectangle(box, fill=(0, 100, 255, 100), outline=(255, 255, 255, 200), width=2)
        elif top_left:
            x, y = top_left
            radius = 5
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 255, 200), outline='black')
        return canvas_copy.convert("RGB")
    
    def auto_generate_prompt(self, base_img, top_left, bottom_right, existing_prompt, provider_name):
        if base_img is None: raise gr.Error("Upload a background image first.")
        if not top_left or not bottom_right: raise gr.Error("Please define a box by setting a top-left and bottom-right corner.")
        if not provider_name: raise gr.Error("Please select a Vision/Enhancer Provider in the API Key Settings.")

        x1, y1 = top_left
        x2, y2 = bottom_right
        box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        cropped_region = base_img.crop(box)

        api_key = self.secure_storage.load_api_key(provider_name)

        if not api_key:
            raise gr.Error(f"API Key for {provider_name} is not set. Please add it in the settings.")
        
        gr.Info(f"Analyzing image region with {provider_name}...")
        description = vision.analyze_image_region(cropped_region, provider_name, api_key)
        
        new_prompt_part = f", with the object placed {description}"
        
        if existing_prompt and existing_prompt.strip():
            return existing_prompt + new_prompt_part
        else:
            return "A photo of the object" + new_prompt_part

    def run_i2i(self, source_image, object_image, prompt, style, aspect_ratio, steps, guidance, model_choice, progress=gr.Progress()):
        if source_image is None: raise gr.Error("Please upload a background image to edit.")
        if not prompt or not prompt.strip(): raise gr.Error("Please enter a prompt.")
        gr.Info("Loading model... this can take a minute on the first run.")
        if aspect_ratio == "Match Input":
            width, height = source_image.size
        else:
            width, height = utils.get_dimensions(aspect_ratio)
        full_prompt = prompt
        if style and style.strip():
            full_prompt = f"{prompt}, {style} style"
        gr.Info(f"Generating with prompt: {full_prompt}")
        input_image = utils.paste_object(source_image, object_image) if object_image else source_image
        source_np = np.array(input_image)
        api_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
        result_pil = self.generator.image_to_image(source_np, full_prompt, steps, guidance, model_choice, 1, width, height, api_key, progress)[0]
        return result_pil, gr.update(visible=True)

    def accept_and_continue(self, preview_image):
        return preview_image, preview_image, gr.update(visible=False)

    def discard_and_retry(self, source_image):
        return source_image, gr.update(visible=False)
        
    def save_image(self, img):
        if img is None:
            gr.Warning("No image to save.")
            return
        os.makedirs("outputs", exist_ok=True)
        pil_img = img if isinstance(img, Image.Image) else Image.fromarray(img)
        filepath = f"outputs/i2i_output_{int(time.time())}.png"
        pil_img.save(filepath)
        gr.Info(f"Image saved to {filepath}")
        return gr.update(value=filepath, visible=True)