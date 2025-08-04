import gradio as gr
import numpy as np
from PIL import Image, ImageDraw
from core import constants as const, utils, vision
import time
import os
import logging

class I2IHandler:
    def __init__(self, ui, generator, secure_storage):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage
    
    def register_event_handlers(self):
        self.ui['i2i_source_uploader'].upload(
            self.store_background,
            inputs=[self.ui['i2i_source_uploader'], self.ui['i2i_object_image_state']],
            outputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_interactive_canvas'],
                self.ui['i2i_object_image_state'], self.ui['i2i_pin_coords_state'], 
                self.ui['i2i_anchor_coords_state'], self.ui['i2i_auto_prompt_btn'],
                self.ui['step1_status'], self.ui['area_selection_guide'], self.ui['prompt_separator']
            ]
        )
        self.ui['i2i_object_uploader'].upload(
            self.store_object,
            inputs=[self.ui['i2i_object_uploader']],
            outputs=[self.ui['i2i_object_image_state'], self.ui['step1_status']]
        ).then(
            self.update_canvas_with_merge,
            inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']],
            outputs=[self.ui['i2i_interactive_canvas']]
        )

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
                self.ui['i2i_object_image_state'],  # Add object image for enhanced analysis
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
                self.ui['i2i_prompt'],
                self.ui['provider_select'] # Pass the selected provider
            ], 
            outputs=[self.ui['i2i_prompt'], self.ui['step2_status']]
        )
        
        self.ui['i2i_reset_selection_btn'].click(
            self.reset_selection,
            inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state']],
            outputs=[
                self.ui['i2i_interactive_canvas'],
                self.ui['i2i_pin_coords_state'],
                self.ui['i2i_anchor_coords_state']
            ]
        )

        self.ui['i2i_generate_btn'].click(self.run_i2i, inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], self.ui['i2i_prompt'], self.ui['i2i_style_select'], self.ui['aspect_ratio'], self.ui['i2i_steps'], self.ui['i2i_guidance'], self.ui['i2i_model_select'], self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']], outputs=[self.ui['i2i_interactive_canvas'], self.ui['i2i_actions_group']])
        self.ui['accept_btn'].click(self.accept_and_continue, inputs=self.ui['i2i_interactive_canvas'], outputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_interactive_canvas'], self.ui['i2i_actions_group']])
        self.ui['retry_btn'].click(self.discard_and_retry, inputs=self.ui['i2i_canvas_image_state'], outputs=[self.ui['i2i_interactive_canvas'], self.ui['i2i_actions_group']])
        self.ui['i2i_save_btn'].click(self.save_image, inputs=self.ui['i2i_interactive_canvas'], outputs=self.ui['i2i_download_output'])
        
        # Add handler for prompt input to update status
        self.ui['i2i_prompt'].change(
            self.update_prompt_status,
            inputs=[self.ui['i2i_prompt']],
            outputs=[self.ui['step2_status']]
        )
        
        # Token counter handler (if available)
        if 'i2i_token_counter' in self.ui:
            self.ui['i2i_prompt'].change(
                self.update_token_count,
                inputs=[self.ui['i2i_prompt']],
                outputs=[self.ui['i2i_token_counter']]
            )

    def _get_redraw_inputs(self):
        return [self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']]

    def update_canvas_with_merge(self, base_img, obj_img, top_left, bottom_right):
        """Updates the canvas to show merged image when both background and object are available."""
        if base_img and obj_img:
            # Show the merged side-by-side image that the AI will see
            merged_image = utils.merge_multiple_images_high_quality([base_img, obj_img])
            return merged_image
        else:
            # Fall back to normal canvas redraw
            return self._redraw_canvas(base_img, obj_img, top_left, bottom_right)
    
    def store_background(self, img, existing_object=None):
        if img is not None:
            # Edit Mode - show auto-generate button and area selection
            auto_btn_visible = True
            step1_text = "**Status:** ✅ Background uploaded - Edit Mode activated!"
            area_guide_visible = True
            separator_visible = True
            
            # If we already have an object, show the merged image immediately
            if existing_object is not None:
                canvas_image = utils.merge_multiple_images_high_quality([img, existing_object])
                gr.Info("🎯 Edit Mode with merged view! The canvas now shows how the AI sees both images side-by-side.")
            else:
                canvas_image = img
                gr.Info("🎯 Edit Mode activated! Upload an object image to see the merged view.")
        else:
            # Create Mode - hide auto-generate button and area selection
            auto_btn_visible = False
            step1_text = "**Status:** 📁 Ready for Create Mode (no background needed)"
            area_guide_visible = False
            separator_visible = False
            # Show placeholder canvas for Create Mode
            canvas_image = self._redraw_canvas(None, existing_object, None, None)
            
        return (img, canvas_image, existing_object, None, None, 
                gr.update(visible=auto_btn_visible),
                step1_text,
                gr.update(visible=area_guide_visible),
                gr.update(visible=separator_visible))

    def store_object(self, img):
        if img is not None:
            status_text = "**Status:** ✅ Object uploaded successfully!"
        else:
            status_text = "**Status:** 📁 Ready to upload images"
        return img, status_text
    
    def update_prompt_status(self, prompt_text):
        if prompt_text and prompt_text.strip():
            return "**Status:** ✅ Prompt written - ready to generate!"
        else:
            return "**Status:** ✏️ Ready for your prompt"
    
    def update_token_count(self, prompt_text):
        """Updates the token count display for prompts."""
        # Access tokenizer through generator if available
        if hasattr(self.generator, 'tokenizer') and self.generator.tokenizer is not None:
            max_length = 77 
            if not prompt_text: 
                return f"Tokens: 0 / {max_length}"
            count = len(self.generator.tokenizer.encode(prompt_text))
            message = f"Tokens: {count} / {max_length}"
            if count > max_length: 
                message += " ⚠️ **Warning:** Prompt will be truncated!"
            return message
        else:
            return "Tokenizer not available"
    
    def reset_selection(self, base_img, obj_img):
        """Reset the selection coordinates and redraw the canvas."""
        logging.info("Resetting selection coordinates")
        updated_canvas = self._redraw_canvas(base_img, obj_img, None, None)
        return updated_canvas, None, None

    def handle_click(self, base_img, obj_img, top_left, bottom_right, evt: gr.SelectData):
        if base_img is None: raise gr.Error("Please upload a background image first.")
        
        # Get click coordinates and image dimensions
        click_coords = evt.index
        img_width, img_height = base_img.size
        
        logging.info(f"Raw click coordinates: {click_coords}")
        logging.info(f"Image dimensions: {img_width}x{img_height}")
        
        # Use coordinates as-is - the previous scaling detection was too aggressive
        x, y = click_coords
        
        # Also display this info to the user via Gradio info
        gr.Info(f"🎯 Click at {click_coords} on {img_width}x{img_height} image")
        
        # Handle edge cases more aggressively - expand the clickable area
        edge_tolerance = 10  # pixels tolerance for edge detection
        
        # If click is very close to edges, snap to edge
        if x < edge_tolerance:
            x = 0
            logging.info(f"Snapped to left edge: x = 0")
        elif x > img_width - edge_tolerance:
            x = img_width - 1
            logging.info(f"Snapped to right edge: x = {img_width - 1}")
        
        if y < edge_tolerance:
            y = 0
            logging.info(f"Snapped to top edge: y = 0")
        elif y > img_height - edge_tolerance:
            y = img_height - 1
            logging.info(f"Snapped to bottom edge: y = {img_height - 1}")
        
        # Final boundary constraint
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        
        constrained_coords = (x, y)
        
        logging.info(f"Final coordinates: {constrained_coords}")
        
        if top_left is None or (top_left and bottom_right):
            new_top_left = constrained_coords
            new_bottom_right = None
            logging.info(f"Set top-left corner: {new_top_left}")
        else:
            new_top_left = top_left
            new_bottom_right = constrained_coords
            logging.info(f"Set bottom-right corner: {new_bottom_right}")
        
        updated_canvas = self._redraw_canvas(base_img, obj_img, new_top_left, new_bottom_right)
        return updated_canvas, new_top_left, new_bottom_right
    
    def _redraw_canvas(self, base_img, obj_img, top_left, bottom_right):
        if base_img is None:
            # CREATE MODE: Show placeholder with object preview
            placeholder_width, placeholder_height = 512, 512
            placeholder = Image.new("RGB", (placeholder_width, placeholder_height), (240, 240, 240))
            draw = ImageDraw.Draw(placeholder, "RGBA")
            
            # Draw placeholder text and styling
            placeholder_color = (180, 180, 180)
            border_color = (200, 200, 200)
            
            # Dashed border for placeholder
            for i in range(0, placeholder_width, 20):
                draw.rectangle((i, 0, min(i + 10, placeholder_width), 2), fill=border_color)
                draw.rectangle((i, placeholder_height - 2, min(i + 10, placeholder_width), placeholder_height), fill=border_color)
            for i in range(0, placeholder_height, 20):
                draw.rectangle((0, i, 2, min(i + 10, placeholder_height)), fill=border_color)
                draw.rectangle((placeholder_width - 2, i, placeholder_width, min(i + 10, placeholder_height)), fill=border_color)
            
            # Add CREATE MODE text
            try:
                # Try to use a larger font if available
                from PIL import ImageFont
                try:
                    font_large = ImageFont.truetype("arial.ttf", 24)
                    font_small = ImageFont.truetype("arial.ttf", 16)
                except:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
            except:
                font_large = None
                font_small = None
            
            # Main title
            title_text = "CREATE MODE"
            title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (placeholder_width - title_width) // 2
            draw.text((title_x, 180), title_text, fill=(100, 100, 100), font=font_large)
            
            # Subtitle
            subtitle_text = "No background image uploaded"
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_small)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (placeholder_width - subtitle_width) // 2
            draw.text((subtitle_x, 220), subtitle_text, fill=(140, 140, 140), font=font_small)
            
            # Instructions
            instruction_text = "Upload a background to enter Edit Mode"
            instruction_bbox = draw.textbbox((0, 0), instruction_text, font=font_small)
            instruction_width = instruction_bbox[2] - instruction_bbox[0]
            instruction_x = (placeholder_width - instruction_width) // 2
            draw.text((instruction_x, 280), instruction_text, fill=(160, 160, 160), font=font_small)
            
            # Show object preview if available
            if obj_img:
                obj_w, obj_h = obj_img.size
                preview_size = 120
                new_h = preview_size
                new_w = int(obj_w * (new_h / obj_h)) if obj_h > 0 else 0
                if new_w > 0 and new_h > 0:
                    resized_obj = obj_img.resize((new_w, new_h), Image.LANCZOS)
                    # Center the object preview
                    paste_x = (placeholder_width - new_w) // 2
                    paste_y = 320
                    
                    # Add white background for object
                    draw.rectangle((paste_x - 5, paste_y - 5, paste_x + new_w + 5, paste_y + new_h + 5), 
                                 fill=(255, 255, 255), outline=(200, 200, 200), width=1)
                    
                    # Paste object image
                    if resized_obj.mode == 'RGBA':
                        placeholder.paste(resized_obj, (paste_x, paste_y), resized_obj)
                    else:
                        placeholder.paste(resized_obj, (paste_x, paste_y))
                    
                    # Object label
                    obj_label = "Object Preview"
                    obj_label_bbox = draw.textbbox((0, 0), obj_label, font=font_small)
                    obj_label_width = obj_label_bbox[2] - obj_label_bbox[0]
                    obj_label_x = (placeholder_width - obj_label_width) // 2
                    draw.text((obj_label_x, paste_y + new_h + 10), obj_label, fill=(120, 120, 120), font=font_small)
            
            return placeholder
        
        # EDIT MODE: Original canvas logic
        canvas_copy = base_img.copy().convert("RGBA")
        draw = ImageDraw.Draw(canvas_copy, "RGBA")
        
        # Get image dimensions for boundary checks
        img_width, img_height = base_img.size
        
        # Add a subtle border around the entire image to show clickable area
        edge_color = (200, 200, 200, 100)  # Light gray, semi-transparent
        border_width = 2
        
        # Draw border around entire image
        draw.rectangle((0, 0, img_width - 1, img_height - 1), 
                      fill=None, outline=edge_color, width=border_width)
        
        # Add corner indicators to show edge areas
        corner_size = 15
        corner_color = (150, 150, 150, 80)
        
        # Top-left corner indicator
        draw.rectangle((0, 0, corner_size, corner_size), 
                      fill=corner_color, outline=None)
        # Top-right corner indicator  
        draw.rectangle((img_width - corner_size, 0, img_width, corner_size), 
                      fill=corner_color, outline=None)
        # Bottom-left corner indicator
        draw.rectangle((0, img_height - corner_size, corner_size, img_height), 
                      fill=corner_color, outline=None)
        # Bottom-right corner indicator
        draw.rectangle((img_width - corner_size, img_height - corner_size, img_width, img_height), 
                      fill=corner_color, outline=None)
        
        # Disabled: Object overlay preview (commented out as requested)
        # if obj_img:
        #     obj_w, obj_h = obj_img.size
        #     new_h = 100 
        #     new_w = int(obj_w * (new_h / obj_h)) if obj_h > 0 else 0
        #     if new_w > 0 and new_h > 0:
        #         resized_obj = obj_img.resize((new_w, new_h), Image.LANCZOS)
        #         alpha_mask = resized_obj.getchannel('A') if resized_obj.mode == 'RGBA' else Image.new('L', resized_obj.size, 255)
        #         alpha_mask = alpha_mask.point(lambda p: p * 0.5)
        #         paste_x = (base_img.width - new_w) // 2
        #         paste_y = (base_img.height - new_h) // 2
        #         canvas_copy.paste(resized_obj, (paste_x, paste_y), alpha_mask)
        
        if top_left and bottom_right:
            # Constrain coordinates to image bounds
            x1 = max(0, min(top_left[0], img_width - 1))
            y1 = max(0, min(top_left[1], img_height - 1))
            x2 = max(0, min(bottom_right[0], img_width - 1))
            y2 = max(0, min(bottom_right[1], img_height - 1))
            
            # Calculate proper box coordinates
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            # Ensure minimum box size for visibility
            min_size = 5
            if (right - left) < min_size:
                center_x = (left + right) // 2
                left = max(0, center_x - min_size // 2)
                right = min(img_width, left + min_size)
            
            if (bottom - top) < min_size:
                center_y = (top + bottom) // 2
                top = max(0, center_y - min_size // 2)
                bottom = min(img_height, top + min_size)
            
            box = (left, top, right, bottom)
            
            # Draw selection box with enhanced visibility
            # Semi-transparent blue fill
            draw.rectangle(box, fill=(0, 100, 255, 80), outline=None)
            # White border for contrast
            draw.rectangle(box, fill=None, outline=(255, 255, 255, 255), width=3)
            # Blue border for style
            draw.rectangle(box, fill=None, outline=(0, 100, 255, 255), width=2)
            
            # Add corner markers for better visibility
            corner_marker_size = 8
            # Top-left corner
            draw.rectangle((left, top, left + corner_marker_size, top + corner_marker_size), 
                         fill=(255, 255, 255, 255), outline=(0, 100, 255, 255), width=1)
            # Bottom-right corner
            draw.rectangle((right - corner_marker_size, bottom - corner_marker_size, right, bottom), 
                         fill=(255, 255, 255, 255), outline=(0, 100, 255, 255), width=1)
            
        elif top_left:
            # Constrain first click point
            x = max(0, min(top_left[0], img_width - 1))
            y = max(0, min(top_left[1], img_height - 1))
            
            radius = 8
            # Draw crosshair for first click with enhanced visibility
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), 
                        fill=(255, 255, 255, 200), outline=(0, 100, 255, 255), width=3)
            # Add small center dot
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), 
                        fill=(0, 100, 255, 255), outline=None)
            
            # Draw crosshair lines to make it more visible
            line_length = 15
            draw.line([(x - line_length, y), (x + line_length, y)], 
                     fill=(255, 255, 255, 255), width=2)
            draw.line([(x, y - line_length), (x, y + line_length)], 
                     fill=(255, 255, 255, 255), width=2)
            
        return canvas_copy.convert("RGB")
    
    def auto_generate_prompt(self, base_img, object_img, top_left, bottom_right, existing_prompt, provider_name):
        # Check if we're in create mode (no background image)
        if base_img is None:
            raise gr.Error("Auto-prompt generation is only available in Edit Mode. Please upload a background image to use this feature, or write your prompt manually for Create Mode.")
        
        if not top_left or not bottom_right: 
            raise gr.Error("Please select an area first! 🎯 Look at the center workspace and click TWICE on your image: first click = top-left corner, second click = bottom-right corner. You'll see a blue box appear.")
        if not provider_name: 
            raise gr.Error("Please select a Vision/Enhancer Provider in the API Key Settings.")

        # Get image dimensions for boundary validation
        img_width, img_height = base_img.size
        
        # Constrain coordinates to image bounds
        x1 = max(0, min(top_left[0], img_width - 1))
        y1 = max(0, min(top_left[1], img_height - 1))
        x2 = max(0, min(bottom_right[0], img_width - 1))
        y2 = max(0, min(bottom_right[1], img_height - 1))
        
        # Calculate proper box coordinates (left, top, right, bottom)
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        # Ensure minimum box size (at least 10x10 pixels)
        min_size = 10
        if (right - left) < min_size:
            center_x = (left + right) // 2
            left = max(0, center_x - min_size // 2)
            right = min(img_width, left + min_size)
        
        if (bottom - top) < min_size:
            center_y = (top + bottom) // 2
            top = max(0, center_y - min_size // 2)
            bottom = min(img_height, top + min_size)
        
        box = (left, top, right, bottom)
        logging.info(f"Cropping box: {box} from image size {img_width}x{img_height}")
        
        # Crop the region - this should now work properly even for edge selections
        try:
            cropped_region = base_img.crop(box)
            if cropped_region.size[0] == 0 or cropped_region.size[1] == 0:
                raise gr.Error("Selected area is too small. Please select a larger area.")
        except Exception as e:
            logging.error(f"Error cropping image: {e}")
            raise gr.Error(f"Could not crop the selected area. Please try selecting a different region.")

        # Save cropped region for debugging (optional)
        debug_save = True  # Set to False in production
        if debug_save:
            try:
                os.makedirs("debug", exist_ok=True)
                debug_path = f"debug/vision_crop_{int(time.time())}.png"
                cropped_region.save(debug_path)
                logging.info(f"Saved cropped region to: {debug_path} (size: {cropped_region.size})")
            except Exception as e:
                logging.warning(f"Could not save debug image: {e}")

        api_key = self.secure_storage.load_api_key(provider_name)

        if not api_key:
            raise gr.Error(f"API Key for {provider_name} is not set. Please add it in the settings.")
        
        gr.Info(f"Analyzing image region with {provider_name}...")
        # Pass both background region and object image for enhanced contextual analysis
        description = vision.analyze_image_region(
            background_image=cropped_region, 
            object_image=object_img, 
            provider_name=provider_name, 
            api_key=api_key
        )
        
        # Provide feedback about the analysis
        if description and description != "on the selected surface":
            gr.Info(f"Vision analysis complete: '{description}'")
        else:
            gr.Warning("Vision analysis returned generic result. Try selecting a clearer region.")
        
        new_prompt_part = f", with the object placed {description}"
        
        if existing_prompt and existing_prompt.strip():
            final_prompt = existing_prompt + new_prompt_part
        else:
            final_prompt = "A photo of the object" + new_prompt_part
            
        gr.Info(f"Generated prompt: {final_prompt}")
        status_text = "**Status:** ✅ Smart prompt generated successfully!"
        return final_prompt, status_text

    def run_i2i(self, source_image, object_image, prompt, style, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress()):
        if not prompt or not prompt.strip(): 
            raise gr.Error("Please enter a prompt.")
        
        # Truncate prompt if it's too long to prevent indexing errors
        full_prompt = prompt
        if style and style.strip():
            full_prompt = f"{prompt}, {style} style"
        
        # Check and truncate if needed
        if hasattr(self.generator, 'tokenizer') and self.generator.tokenizer is not None:
            max_length = 77
            tokens = self.generator.tokenizer.encode(full_prompt)
            if len(tokens) > max_length:
                # Truncate to max_length tokens
                truncated_tokens = tokens[:max_length]
                full_prompt = self.generator.tokenizer.decode(truncated_tokens)
                gr.Warning(f"⚠️ Prompt was truncated from {len(tokens)} to {max_length} tokens to prevent errors.")
                logging.info(f"Prompt truncated from {len(tokens)} to {max_length} tokens")
        
        # Determine mode based on whether background image is provided
        is_create_mode = source_image is None
        
        if aspect_ratio == "Match Input" and not is_create_mode:
            width, height = source_image.size
        else:
            width, height = utils.get_dimensions(aspect_ratio)
        
        gr.Info(f"{'Creating' if is_create_mode else 'Editing'} with prompt: {full_prompt}")
        
        api_key = self.secure_storage.load_api_key(const.FLUX_PRO_API)
        
        if is_create_mode:
            # CREATE MODE: Text-to-Image generation
            if object_image:
                # If object image is provided, we can still compose it with generated background
                # For now, just generate and let user manually compose, or enhance this later
                gr.Info("Creating new image (object composition in create mode coming soon)")
            
            # Use T2I generation logic
            result_images = self.generator.text_to_image(
                full_prompt, steps, guidance, model_choice, 1, width, height, api_key, progress
            )
            result_pil = result_images[0] if result_images else None
        else:
            # EDIT MODE: Image-to-Image generation  
            if object_image:
                # Use side-by-side merging approach (what was working before)
                input_image = utils.merge_multiple_images_high_quality([source_image, object_image])
                gr.Info(f"Using side-by-side merge approach - you control all settings via UI")
            else:
                # No object - use original image
                input_image = source_image
                gr.Info(f"Using background only - you control all settings via UI")
            
            source_np = np.array(input_image)
            
            result_pil = self.generator.image_to_image(
                source_np, full_prompt, steps, guidance, model_choice, 1, width, height, api_key, progress
            )[0]
        
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