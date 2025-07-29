import gradio as gr
import numpy as np
from PIL import Image, ImageDraw
from core import constants as const, utils

class I2IHandler:
    def __init__(self, ui, generator, secure_storage):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage
    
    def register_event_handlers(self):
        redraw_inputs = [
            self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'],
            self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
            self.ui['i2i_size_slider']
        ]
        
        self.ui['i2i_source_uploader'].upload(
            self.store_background,
            inputs=[self.ui['i2i_source_uploader']],
            outputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_interactive_canvas'], self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'], self.ui['i2i_object_image_state']]
        )
        self.ui['i2i_object_uploader'].upload(self.store_object, inputs=[self.ui['i2i_object_uploader']], outputs=[self.ui['i2i_object_image_state']]).then(
            self._redraw_canvas, inputs=redraw_inputs, outputs=self.ui['i2i_interactive_canvas']
        )
        self.ui['i2i_interactive_canvas'].select(
            self.handle_click, 
            inputs=redraw_inputs + [self.ui['i2i_tool_select']], 
            outputs=[self.ui['i2i_interactive_canvas'], self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']]
        )
        self.ui['i2i_size_slider'].release(self._redraw_canvas, inputs=redraw_inputs, outputs=self.ui['i2i_interactive_canvas'])

        self.ui['i2i_generate_btn'].click(self.run_i2i, inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], self.ui['i2i_prompt'], self.ui['i2i_style_select'], self.ui['i2i_aspect_ratio'], self.ui['i2i_steps'], self.ui['i2i_guidance'], self.ui['i2i_model_select']], outputs=[self.ui['i2i_interactive_canvas'], self.ui['i2i_decision_group']])
        self.ui['accept_btn'].click(self.accept_and_continue, inputs=self.ui['i2i_interactive_canvas'], outputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_interactive_canvas'], self.ui['i2i_decision_group']])
        self.ui['retry_btn'].click(self.discard_and_retry, inputs=self.ui['i2i_canvas_image_state'], outputs=[self.ui['i2i_interactive_canvas'], self.ui['i2i_decision_group']])

    def store_background(self, img):
        # Clears all coordinates and the object when a new background is uploaded
        return img, img, None, None, None

    def store_object(self, img):
        return img

    def handle_click(self, base_img, obj_img, pin_coords, anchor_coords, size_percent, tool, evt: gr.SelectData):
        if base_img is None: raise gr.Error("Please upload a background image first.")
        
        click_coords = evt.index
        new_pin_coords = click_coords if const.PIN_TOOL in tool else pin_coords
        new_anchor_coords = click_coords if const.ANCHOR_TOOL in tool else anchor_coords
        
        updated_canvas = self._redraw_canvas(base_img, obj_img, new_pin_coords, new_anchor_coords, size_percent)
        return updated_canvas, new_pin_coords, new_anchor_coords
    
    def _redraw_canvas(self, base_img, obj_img, pin_coords, anchor_coords, size_percent):
        """Draws the semi-transparent object preview, pin, and anchor on the canvas."""
        if base_img is None: return None
        
        canvas_copy = base_img.copy().convert("RGBA")
        
        # Draw the semi-transparent object preview
        if pin_coords and obj_img:
            obj_w, obj_h = obj_img.size
            anchor_height = 100 
            scale_factor = (size_percent / 100.0)
            new_h = int(anchor_height * scale_factor)
            new_w = int(obj_w * (new_h / obj_h)) if obj_h > 0 and new_h > 0 else 0
            
            if new_w > 0 and new_h > 0:
                resized_obj = obj_img.resize((new_w, new_h), Image.LANCZOS)
                alpha_mask = resized_obj.getchannel('A') if resized_obj.mode == 'RGBA' else Image.new('L', resized_obj.size, 255)
                # Make the preview 50% transparent
                alpha_mask = alpha_mask.point(lambda p: p * 0.5) 
                
                x, y = pin_coords
                top_left_x = x - new_w // 2
                top_left_y = y - new_h // 2
                canvas_copy.paste(resized_obj, (top_left_x, top_left_y), alpha_mask)

        # Draw the pin and anchor markers on top
        draw = ImageDraw.Draw(canvas_copy)
        if anchor_coords:
            x, y = anchor_coords
            radius = 12
            draw.rectangle((x - radius, y - radius, x + radius, y + radius), fill=(0, 0, 255, 200), outline='white', width=2)
            
        if pin_coords:
            x, y = pin_coords
            radius = 10
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 0, 0, 200), outline='white')
            
        return canvas_copy.convert("RGB")

    def run_i2i(self, source_image, object_image, prompt, style, aspect_ratio, steps, guidance, model_choice, progress=gr.Progress()):
        if source_image is None: raise gr.Error("Please upload a background image to edit.")
        if not prompt or not prompt.strip(): raise gr.Error("Please enter a prompt to describe your edit.")

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
        result_pil = self.generator.image_to_image(
            source_np, full_prompt, steps, guidance, model_choice, 1, width, height, api_key, progress
        )[0]
        
        return result_pil, gr.update(visible=True)

    def accept_and_continue(self, preview_image):
        return preview_image, preview_image, gr.update(visible=False)

    def discard_and_retry(self, source_image):
        return source_image, gr.update(visible=False)