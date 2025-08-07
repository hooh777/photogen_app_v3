"""
Streamlined I2I Handler - Main orchestrator optimized for Pro model workflow
Dramatically reduced from 983 lines to focus on essential coordination
"""
import gradio as gr
import logging

# Import focused managers for better organization
from .canvas_manager import CanvasManager
from .auto_prompt_manager import AutoPromptManager
from .state_manager import StateManager
from .generation_manager import GenerationManager


class I2IHandler:
    """Streamlined I2I Handler optimized for Pro model workflow"""
    
    def __init__(self, ui, generator, secure_storage):
        self.ui = ui
        self.generator = generator
        self.secure_storage = secure_storage
        
        # Initialize focused managers
        self.canvas_manager = CanvasManager()
        self.auto_prompt_manager = AutoPromptManager(secure_storage)
        self.state_manager = StateManager()
        self.generation_manager = GenerationManager(generator, secure_storage)
    
    def register_event_handlers(self):
        """Register all UI event handlers with optimized workflow"""
        # Background upload handler
        self.ui['i2i_source_uploader'].upload(
            self.store_background,
            inputs=[self.ui['i2i_source_uploader'], self.ui['i2i_object_image_state']],
            outputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_interactive_canvas'],
                self.ui['i2i_object_image_state'], self.ui['i2i_pin_coords_state'], 
                self.ui['i2i_anchor_coords_state'], self.ui['i2i_auto_prompt_btn'],
                self.ui['step1_status'], self.ui['prompt_separator'], self.ui['allow_human_surfaces']
            ]
        )
        
        # Object upload handler with auto-canvas update
        self.ui['i2i_object_uploader'].upload(
            self.store_object,
            inputs=[self.ui['i2i_object_uploader']],
            outputs=[self.ui['i2i_object_image_state'], self.ui['step1_status']]
        ).then(
            self.update_canvas_with_merge,
            inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], 
                    self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']],
            outputs=[self.ui['i2i_interactive_canvas']]
        )

        # Single-click area selection
        self.ui['i2i_interactive_canvas'].select(
            self.handle_click, 
            inputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'],
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']
            ], 
            outputs=[
                self.ui['i2i_interactive_canvas'], 
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']
            ]
        )
        
        # Auto-prompt generation (optimized for 90% usage)
        self.ui['i2i_auto_prompt_btn'].click(
            self.auto_generate_prompt, 
            inputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'],
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state'],
                self.ui['i2i_prompt'], self.ui['provider_select'], self.ui['allow_human_surfaces']
            ], 
            outputs=[self.ui['i2i_prompt'], self.ui['step2_status']]
        )
        
        # Selection reset
        self.ui['i2i_reset_selection_btn'].click(
            self.reset_selection,
            inputs=[self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state']],
            outputs=[
                self.ui['i2i_interactive_canvas'],
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']
            ]
        )

        # Main generation handler (Pro model optimized)
        self.ui['i2i_generate_btn'].click(
            self.run_i2i_with_state_update, 
            inputs=[
                self.ui['i2i_canvas_image_state'], self.ui['i2i_object_image_state'], 
                self.ui['i2i_prompt'], self.ui['aspect_ratio'], self.ui['i2i_steps'], 
                self.ui['i2i_guidance'], self.ui['i2i_model_select'], 
                self.ui['i2i_pin_coords_state'], self.ui['i2i_anchor_coords_state']
            ], 
            outputs=[self.ui['output_gallery'], self.ui['last_generated_image_state']] if 'last_generated_image_state' in self.ui else [self.ui['output_gallery']]
        ).then(
            # Clear selection state on new generation
            lambda: None,
            outputs=[self.ui['selected_gallery_image_state']] if 'selected_gallery_image_state' in self.ui else []
        )
        
        # Prompt status updates
        self.ui['i2i_prompt'].change(
            self.update_prompt_status,
            inputs=[self.ui['i2i_prompt']],
            outputs=[self.ui['step2_status']]
        )
        
        # Token counter (if available)
        if 'i2i_token_counter' in self.ui:
            self.ui['i2i_prompt'].change(
                self.update_token_count,
                inputs=[self.ui['i2i_prompt']],
                outputs=[self.ui['i2i_token_counter']]
            )

    # === Delegation Methods to Focused Managers ===
    
    # Canvas operations → CanvasManager
    def update_canvas_with_merge(self, base_img, obj_img, top_left, bottom_right):
        return self.canvas_manager.update_canvas_with_merge(base_img, obj_img, top_left, bottom_right)
    
    def handle_click(self, base_img, obj_img, top_left, bottom_right, evt: gr.SelectData):
        return self.canvas_manager.handle_click(base_img, obj_img, top_left, bottom_right, evt)
    
    def reset_selection(self, base_img, obj_img):
        return self.canvas_manager.reset_selection(base_img, obj_img)
    
    # State management → StateManager
    def store_background(self, img, existing_object=None):
        return self.state_manager.store_background(img, existing_object)

    def store_object(self, img):
        return self.state_manager.store_object(img)
    
    def update_prompt_status(self, prompt_text):
        return self.state_manager.update_prompt_status(prompt_text)
    
    def update_token_count(self, prompt_text):
        return self.state_manager.update_token_count(prompt_text, self.generator)
    
    # Auto-prompt generation → AutoPromptManager
    def auto_generate_prompt(self, base_img, object_img, top_left, bottom_right, existing_prompt, provider_name, allow_human_surfaces=False):
        return self.auto_prompt_manager.generate_auto_prompt(base_img, object_img, top_left, bottom_right, existing_prompt, provider_name, allow_human_surfaces)
    
    # Image generation → GenerationManager
    def run_i2i(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress()):
        return self.generation_manager.run_generation(source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress)
    
    def run_i2i_with_state_update(self, source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress=gr.Progress()):
        """Wrapper for run_i2i that also returns the last generated image for state tracking."""
        result_list = self.run_i2i(source_image, object_image, prompt, aspect_ratio, steps, guidance, model_choice, top_left, bottom_right, progress)
        
        # Return both gallery list and the single image for last_generated_image_state
        last_image = result_list[0] if result_list else None
        logging.info(f"🎯 Storing last generated image: {type(last_image)} for direct save access")
        
        # Return for gallery and last image state
        if 'last_generated_image_state' in self.ui:
            return result_list, last_image
        else:
            return result_list
