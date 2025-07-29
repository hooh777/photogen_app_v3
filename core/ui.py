import gradio as gr
from core import constants as const

def create_ui():
    """Creates the final three-panel Gradio UI."""
    
    custom_css = """
    .gradio-container { max-width: none !important; }
    .main-content-area { min-height: 80vh; }
    """

    with gr.Blocks(theme=gr.themes.Soft(), title="PhotoGen", css=custom_css) as demo:
        # --- State Holders ---
        i2i_canvas_image_state = gr.State()
        i2i_object_image_state = gr.State()
        i2i_pin_coords_state = gr.State()
        i2i_anchor_coords_state = gr.State()
        
        gr.Markdown("# 📸 PhotoGen")
        
        with gr.Accordion("⚙️ AI Vision / Enhancer Settings", open=False):
            provider_select = gr.Dropdown(choices=[], value=None, label="Vision/Enhancer Provider")
            api_key_input = gr.Textbox(label="API Key", type="password", placeholder="Enter key and click Save")
            with gr.Row():
                save_api_key_btn = gr.Button("💾 Save Key")
                clear_api_key_btn = gr.Button("🗑️ Clear Key")

        with gr.Accordion("⚙️ Pro Model Settings", open=False):
            pro_api_key_input = gr.Textbox(label="Flux Pro API Key", type="password", placeholder="Enter key for the Pro image model")
            with gr.Row():
                save_pro_api_key_btn = gr.Button("💾 Save Pro Key")
                clear_pro_api_key_btn = gr.Button("🗑️ Clear Pro Key")

        with gr.Row(equal_height=False):
            # --- LEFT PANEL (CONTROLS) ---
            with gr.Column(scale=3, min_width=450):
                style_choices = ["Photographic", "Cinematic", "Anime", "Digital Art", "Fantasy", "Neon-Punk"]
                with gr.Tabs() as mode_tabs:
                    with gr.Tab("Create", id=0):
                        gr.Markdown("### Step 1: Describe Your Image")
                        t2i_prompt = gr.Textbox(label="Prompt", lines=5, placeholder="A photorealistic cinematic shot of a raccoon...")
                        t2i_style_select = gr.Dropdown(label="Style", choices=style_choices, value=None, allow_custom_value=True)
                        with gr.Accordion("Advanced Settings", open=False):
                            t2i_steps = gr.Slider(label="Inference Steps", minimum=1, maximum=50, value=28, step=1)
                            t2i_guidance = gr.Slider(label="Guidance Scale", minimum=0, maximum=10, value=4.0, step=0.1)
                            t2i_model_select = gr.Radio([const.LOCAL_MODEL, const.PRO_MODEL], label="Model", value=const.LOCAL_MODEL)
                        t2i_generate_btn = gr.Button("🚀 Generate", variant="primary")

                    with gr.Tab("Edit", id=1):
                        with gr.Accordion("Step 1: Input Images", open=True):
                            i2i_source_uploader = gr.Image(type="pil", label="Background Image")
                            i2i_object_uploader = gr.Image(type="pil", label="Object Image (Optional)")
                        
                        gr.Markdown("### Step 2: Describe Your Edit")
                        i2i_prompt = gr.Textbox(label="Prompt", lines=3, placeholder="Describe the edit or auto-generate below")
                        i2i_auto_prompt_btn = gr.Button("🤖 Auto-Generate Prompt", variant="secondary")
                        i2i_style_select = gr.Dropdown(label="Style", choices=style_choices, value=None, allow_custom_value=True)
                        
                        with gr.Accordion("Placement Controls", open=False):
                            gr.Markdown("Click twice on the canvas to define a selection box (top-left and bottom-right corners).")

            # --- CENTER PANEL (CANVAS / GALLERY) ---
            with gr.Column(scale=5, elem_classes="main-content-area"):
                output_gallery = gr.Gallery(label="Generated Images", visible=True, columns=2, height="auto")
                i2i_interactive_canvas = gr.Image(type="pil", label="Interactive Canvas", visible=False, height=600, interactive=True)
                with gr.Column(visible=False) as i2i_actions_group:
                    with gr.Row() as i2i_decision_group:
                        accept_btn = gr.Button("✅ Accept", variant="primary")
                        retry_btn = gr.Button("❌ Retry")
                    with gr.Row():
                        i2i_save_btn = gr.Button("💾 Save Image")
                        i2i_download_output = gr.DownloadButton(label="Download Image", visible=False)

            # --- RIGHT PANEL (OUTPUT SETTINGS) ---
            with gr.Column(scale=2, min_width=280):
                gr.Markdown("### Output Settings")
                num_images = gr.Slider(label="Number of Images", minimum=1, maximum=4, value=1, step=1)
                aspect_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
                aspect_ratio = gr.Radio(choices=["Match Input"] + aspect_ratios, value="1:1", label="Image Dimensions")

                with gr.Accordion("Advanced Settings (for Edit mode)", open=True):
                    i2i_steps = gr.Slider(label="Inference Steps", minimum=1, maximum=50, value=20, step=1)
                    i2i_guidance = gr.Slider(label="Guidance Scale", minimum=0, maximum=10, value=3.0, step=0.1)
                    i2i_model_select = gr.Radio([const.LOCAL_MODEL, const.PRO_MODEL], label="Model", value=const.LOCAL_MODEL)
                
                i2i_generate_btn = gr.Button("🚀 Generate Edit", variant="primary", visible=True)

    ui_components = {
        "mode_tabs": mode_tabs,
        "output_gallery": output_gallery, "i2i_interactive_canvas": i2i_interactive_canvas,
        "i2i_actions_group": i2i_actions_group,
        "i2i_decision_group": i2i_decision_group, "accept_btn": accept_btn, "retry_btn": retry_btn,
        "i2i_save_btn": i2i_save_btn, "i2i_download_output": i2i_download_output,
        "num_images": num_images, "aspect_ratio": aspect_ratio,

        "provider_select": provider_select, "api_key_input": api_key_input, "save_api_key_btn": save_api_key_btn, "clear_api_key_btn": clear_api_key_btn,
        "pro_api_key_input": pro_api_key_input, "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,

        "t2i_prompt": t2i_prompt, "t2i_style_select": t2i_style_select, "t2i_steps": t2i_steps,
        "t2i_guidance": t2i_guidance, "t2i_model_select": t2i_model_select, "t2i_generate_btn": t2i_generate_btn,

        "i2i_source_uploader": i2i_source_uploader, "i2i_object_uploader": i2i_object_uploader,
        "i2i_prompt": i2i_prompt, "i2i_style_select": i2i_style_select, "i2i_auto_prompt_btn": i2i_auto_prompt_btn,
        "i2i_steps": i2i_steps,
        "i2i_guidance": i2i_guidance, "i2i_model_select": i2i_model_select, "i2i_generate_btn": i2i_generate_btn,

        "i2i_canvas_image_state": i2i_canvas_image_state, "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state,
        "i2i_anchor_coords_state": i2i_anchor_coords_state,
    }
    return demo, ui_components, {}