# core/ui.py
import gradio as gr
from core import constants as const

def _create_inference_controls(default_steps=28, default_guidance=4.0, is_i2i=False):
    """Creates a shared set of sliders and model selectors."""
    guidance_val = 3.0 if is_i2i else default_guidance
    with gr.Group():
        steps = gr.Slider(label="Inference Steps", minimum=1, maximum=50, value=default_steps, step=1)
        guidance = gr.Slider(label="Guidance Scale", minimum=0, maximum=10, value=guidance_val, step=0.1)
        model_select = gr.Radio([const.LOCAL_MODEL, const.PRO_MODEL], label="Select Model", value=const.LOCAL_MODEL)
    return steps, guidance, model_select

def create_ui():
    """Creates and returns the Gradio Blocks UI and a dictionary of its components."""
    
    custom_css = """
    .optional-prompt-card {
        border: 2px solid #E5E7EB !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
        border-radius: 12px !important;
    }
    """

    with gr.Blocks(theme=gr.themes.Soft(), title="PhotoGen", css=custom_css) as demo:
        # --- State Holders ---
        selected_background_path = gr.Textbox(visible=False, label="selected_background_path_holder")
        selected_object_path = gr.Textbox(visible=False, label="selected_object_path_holder")
        current_prompt_templates_state = gr.State()
        merged_image_state = gr.State()
        i2i_canvas_image_state = gr.State()
        i2i_object_image_state = gr.State()
        i2i_pin_coords_state = gr.State()
        i2i_anchor_coords_state = gr.State()
        
        gr.Markdown("# 📸 PhotoGen: AI Photo Editor")

        with gr.Accordion("⚙️ AI Prompt Enhancer Settings", open=False):
            provider_select = gr.Dropdown(choices=[], value=None, label="LLM Provider")
            api_key_input = gr.Textbox(label="Enhancer API Key", type="password", placeholder="Enter key and click Save")
            with gr.Row():
                save_api_key_btn = gr.Button("💾 Save Enhancer Key")
                clear_api_key_btn = gr.Button("🗑️ Clear Enhancer Key")
        
        with gr.Accordion("⚙️ Pro Model Settings", open=False):
            pro_api_key_input = gr.Textbox(label="Flux Pro API Key", type="password", placeholder="Enter key for the Pro image model")
            with gr.Row():
                save_pro_api_key_btn = gr.Button("💾 Save Pro Key")
                clear_pro_api_key_btn = gr.Button("🗑️ Clear Pro Key")

        mode_selection = gr.Radio(
            [const.DEMO_MODE, const.I2I_MODE, const.T2I_MODE],
            label="What would you like to do today?",
            value=const.DEMO_MODE
        )
        
        with gr.Group(visible=False) as t2i_panel:
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### ✍️ Step 1: Write Your Prompt")
                    t2i_prompt = gr.Textbox(label="Prompt", lines=5, placeholder="A photorealistic cinematic shot of a raccoon...")
                    t2i_token_counter = gr.Markdown(value="Tokens: 0 / 77")
                    t2i_steps, t2i_guidance, t2i_model_select = _create_inference_controls()
                    t2i_generate_btn = gr.Button("🚀 Generate Image", variant="primary")
                with gr.Column(scale=1):
                    gr.Markdown("### 🖼️ Generated Image")
                    t2i_output_canvas = gr.Image(label="Output", interactive=False, height=600, type="numpy", format="png")
                    with gr.Row(visible=False) as t2i_actions_row:
                        t2i_save_btn = gr.Button("💾 Save Image")
                        t2i_download_output = gr.DownloadButton(label="Download Image", visible=False)

        with gr.Group(visible=False) as i2i_panel:
            with gr.Row(equal_height=False):
                with gr.Column(scale=1, min_width=500):
                    gr.Markdown("### ✎ Smart Canvas Controls")
                    i2i_source_uploader = gr.Image(type="pil", label="Step 1: Upload Background Image")
                    i2i_object_uploader = gr.Image(type="pil", label="Step 2: Upload Object Image (To Place)")
                    
                    gr.Markdown("##### Step 3: Visually Describe Placement")
                    i2i_pin_coord_output = gr.Textbox(label="Pin Coordinates (Click image to set)", interactive=False)
                    i2i_anchor_coord_output = gr.Textbox(label="Anchor Coordinates (Click image to set)", interactive=False)
                    i2i_size_slider = gr.Slider(label="Relative Size (%)", minimum=10, maximum=200, value=100, step=5)
                    
                    gr.Markdown("### Step 4: Describe Your Edit")
                    i2i_auto_prompt_btn = gr.Button("🤖 Auto-Generate Prompt from Visuals", variant="secondary")
                    i2i_prompt = gr.Textbox(label="Your Prompt", lines=5, placeholder="Click the button above to auto-generate a prompt...")
                    i2i_token_counter = gr.Markdown(value="Tokens: 0 / 77")
                    launch_enhancer_btn = gr.Button("✨ Or, Use AI Prompt Enhancer")
                    with gr.Group(visible=False) as enhancer_modal:
                        gr.Markdown("--- \n ## ✨ Prompt Enhancer")
                        base_prompt_input = gr.Textbox(label="Your Basic Idea", lines=2, placeholder="e.g., watercolor painting of a cat")
                        enhance_btn = gr.Button("Generate Suggestions")
                        with gr.Row():
                            with gr.Column():
                                detailed_output = gr.Textbox(lines=3, label="Detailed Suggestion")
                                use_detailed_btn = gr.Button("Use Detailed")
                            with gr.Column():
                                stylized_output = gr.Textbox(lines=3, label="Stylized Suggestion")
                                use_stylized_btn = gr.Button("Use Stylized")
                            with gr.Column():
                                rephrased_output = gr.Textbox(lines=3, label="Rephrased Suggestion")
                                use_rephrased_btn = gr.Button("Use Rephrased")
                        close_enhancer_btn = gr.Button("Close Enhancer")
                    
                    gr.Markdown("### Step 5: Generate")
                    i2i_steps, i2i_guidance, i2i_model_select = _create_inference_controls(is_i2i=True)
                    i2i_generate_btn = gr.Button("🚀 Generate Edit", variant="primary")

                with gr.Column(scale=1, min_width=500):
                    gr.Markdown("### 🖼️ Interactive Canvas")
                    i2i_tool_select = gr.Radio([const.PIN_TOOL, const.ANCHOR_TOOL], label="Select Tool", value=const.PIN_TOOL)
                    i2i_interactive_canvas = gr.Image(type="pil", label="Use the selected tool on the image", interactive=True, height=600)
                    
                    with gr.Row(visible=False) as i2i_decision_group:
                        accept_btn = gr.Button("✅ Accept Edit & Continue", variant="primary")
                        retry_btn = gr.Button("❌ Discard & Retry")
                    with gr.Row():
                        save_btn = gr.Button("💾 Save Final Image")
                        download_output = gr.DownloadButton(label="Download Image", visible=False)
                        start_over_btn = gr.Button("🔄 Start Over (Clear All)")

        with gr.Group(visible=True) as demo_panel:
            gr.Markdown("## ✨ Demo Mode")
            with gr.Row(equal_height=False):
                with gr.Column(scale=1, min_width=500):
                    gr.Markdown("#### Step 1: Pick a Background & Object")
                    demo_background_gallery = gr.Gallery(label="Backgrounds", columns=2, height="auto", container=False)
                    demo_object_gallery = gr.Gallery(label="Demo Objects", columns=3, height="auto", container=False)
                    demo_object_upload = gr.File(label="Or Upload Your Own Object", file_types=["image"])
                    
                    gr.Markdown("#### Step 2: Build Your Prompt")
                    with gr.Group():
                        gr.Markdown("##### Base Description (Required)")
                        with gr.Row(visible=True) as p1_row:
                            p1_prefix = gr.Textbox(show_label=False, container=False, interactive=False, scale=1)
                            p1_editable = gr.Textbox(show_label=False, container=False, scale=2)
                            p1_suffix = gr.Textbox(show_label=False, container=False, interactive=False, scale=1)

                    with gr.Group(elem_classes="optional-prompt-card"):
                        gr.Markdown("##### ✨ Position & Lighting")
                        with gr.Row(visible=True) as p2_row:
                            p2_prefix = gr.Textbox(show_label=False, container=False, interactive=False, scale=2)
                            p2_editable = gr.Textbox(show_label=False, container=False, scale=3)
                            p2_suffix = gr.Textbox(show_label=False, container=False, interactive=False, scale=2)
                            p2_checkbox = gr.Checkbox(label="Enable", value=False, show_label=False, min_width=80)

                    with gr.Group(elem_classes="optional-prompt-card"):
                        gr.Markdown("##### 🎨 Style & Tone")
                        with gr.Row(visible=True) as p3_row:
                            p3_prefix = gr.Textbox(show_label=False, container=False, interactive=False, scale=2)
                            p3_editable = gr.Textbox(show_label=False, container=False, scale=3)
                            p3_suffix = gr.Textbox(show_label=False, container=False, interactive=False, scale=2)
                            p3_checkbox = gr.Checkbox(label="Enable", value=False, show_label=False, min_width=80)

                with gr.Column(scale=1, min_width=500):
                    gr.Markdown("#### Step 3: Generate Final Image")
                    demo_output_canvas = gr.Image(label="Preview / Output", height=600)
                    demo_model_select = gr.Radio([const.LOCAL_MODEL, const.PRO_MODEL], label="Select Model", value=const.LOCAL_MODEL)
                    demo_generate_btn = gr.Button("🚀 Generate Scene", variant="primary")
                    
    ui_components = {
        "mode_selection": mode_selection, "t2i_panel": t2i_panel, "i2i_panel": i2i_panel, "demo_panel": demo_panel,
        "provider_select": provider_select, "api_key_input": api_key_input,
        "save_api_key_btn": save_api_key_btn, "clear_api_key_btn": clear_api_key_btn,
        "pro_api_key_input": pro_api_key_input,
        "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,
        "t2i_prompt": t2i_prompt, "t2i_steps": t2i_steps, "t2i_guidance": t2i_guidance,
        "t2i_generate_btn": t2i_generate_btn, "t2i_output_canvas": t2i_output_canvas,
        "t2i_actions_row": t2i_actions_row, "t2i_save_btn": t2i_save_btn, "t2i_download_output": t2i_download_output,
        "t2i_token_counter": t2i_token_counter, "t2i_model_select": t2i_model_select,
        
        "i2i_prompt": i2i_prompt, "i2i_steps": i2i_steps, "i2i_guidance": i2i_guidance,
        "i2i_generate_btn": i2i_generate_btn, "i2i_decision_group": i2i_decision_group,
        "i2i_token_counter": i2i_token_counter, "i2i_model_select": i2i_model_select,
        "accept_btn": accept_btn, "retry_btn": retry_btn,
        "save_btn": save_btn, "download_output": download_output, "start_over_btn": start_over_btn,
        "launch_enhancer_btn": launch_enhancer_btn, "enhancer_modal": enhancer_modal,
        "base_prompt_input": base_prompt_input, "enhance_btn": enhance_btn,
        "detailed_output": detailed_output, "stylized_output": stylized_output, "rephrased_output": rephrased_output,
        "use_detailed_btn": use_detailed_btn, "use_stylized_btn": use_stylized_btn, "use_rephrased_btn": use_rephrased_btn,
        "close_enhancer_btn": close_enhancer_btn,
        
        "demo_background_gallery": demo_background_gallery,
        "demo_object_gallery": demo_object_gallery,
        "demo_object_upload": demo_object_upload,
        "p1_row": p1_row, "p1_prefix": p1_prefix, "p1_editable": p1_editable, "p1_suffix": p1_suffix,
        "p2_row": p2_row, "p2_prefix": p2_prefix, "p2_editable": p2_editable, "p2_suffix": p2_suffix, "p2_checkbox": p2_checkbox,
        "p3_row": p3_row, "p3_prefix": p3_prefix, "p3_editable": p3_editable, "p3_suffix": p3_suffix, "p3_checkbox": p3_checkbox,
        "demo_generate_btn": demo_generate_btn,
        "demo_output_canvas": demo_output_canvas,
        "demo_model_select": demo_model_select,
        
        "selected_background_path": selected_background_path,
        "selected_object_path": selected_object_path,
        "current_prompt_templates_state": current_prompt_templates_state,
        "merged_image_state": merged_image_state,
        
        "i2i_source_uploader": i2i_source_uploader,
        "i2i_object_uploader": i2i_object_uploader,
        "i2i_tool_select": i2i_tool_select,
        "i2i_interactive_canvas": i2i_interactive_canvas,
        "i2i_pin_coord_output": i2i_pin_coord_output,
        "i2i_anchor_coord_output": i2i_anchor_coord_output,
        "i2i_size_slider": i2i_size_slider,
        "i2i_auto_prompt_btn": i2i_auto_prompt_btn,
        "i2i_canvas_image_state": i2i_canvas_image_state,
        "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state,
        "i2i_anchor_coords_state": i2i_anchor_coords_state,
    }
    return demo, ui_components, {}