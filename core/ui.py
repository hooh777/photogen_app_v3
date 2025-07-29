import gradio as gr
from core import constants as const

def create_ui():
    """Creates the redesigned two-panel Gradio UI."""
    
    custom_css = """
    .gradio-container { max-width: none !important; }
    .main-content-area { min-height: 80vh; }
    """

    with gr.Blocks(theme=gr.themes.Soft(), title="PhotoGen", css=custom_css) as demo:
        # --- State Holders ---
        selected_background_path = gr.Textbox(visible=False)
        selected_object_path = gr.Textbox(visible=False)
        current_prompt_templates_state = gr.State()
        merged_image_state = gr.State()
        i2i_canvas_image_state = gr.State()
        i2i_object_image_state = gr.State()
        i2i_pin_coords_state = gr.State()
        i2i_anchor_coords_state = gr.State()
        
        gr.Markdown("# 📸 PhotoGen")

        # --- SETTINGS ACCORDIONS ---
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

        with gr.Row(equal_height=False):
            # --- LEFT PANEL ---
            with gr.Column(scale=1, min_width=450):
                aspect_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
                style_choices = ["Photographic", "Cinematic", "Anime", "Digital Art", "Fantasy", "Neon-Punk"]

                with gr.Tabs() as mode_tabs:
                    # --- CREATE (T2I) TAB ---
                    with gr.Tab("Create", id=0) as t2i_tab:
                        gr.Markdown("### Create a new image from text")
                        t2i_prompt = gr.Textbox(label="Prompt", lines=5, placeholder="A photorealistic cinematic shot of a raccoon...")
                        t2i_style_select = gr.Dropdown(
                            label="Style", 
                            choices=style_choices, 
                            value="Photographic",
                            allow_custom_value=True
                        )
                        t2i_aspect_ratio = gr.Radio(choices=aspect_ratios, value="1:1", label="Image Dimensions")
                        with gr.Accordion("Advanced Settings", open=False):
                            t2i_steps = gr.Slider(label="Inference Steps", minimum=1, maximum=50, value=28, step=1)
                            t2i_guidance = gr.Slider(label="Guidance Scale", minimum=0, maximum=10, value=4.0, step=0.1)
                            t2i_model_select = gr.Radio([const.LOCAL_MODEL, const.PRO_MODEL], label="Select Model", value=const.LOCAL_MODEL)
                        t2i_num_images = gr.Slider(label="Number of Images", minimum=1, maximum=4, value=2, step=1)
                        t2i_generate_btn = gr.Button("🚀 Generate", variant="primary")
                        t2i_token_counter = gr.Markdown("Tokens: 0 / 77")

                    # --- EDIT (I2I) TAB ---
                    with gr.Tab("Edit", id=1) as i2i_tab:
                        gr.Markdown("### Edit an existing image")
                        i2i_source_uploader = gr.Image(type="pil", label="1. Upload Background Image")
                        i2i_object_uploader = gr.Image(type="pil", label="2. (Optional) Upload Object to Place")
                        i2i_prompt = gr.Textbox(label="3. Describe your edit", lines=3)
                        i2i_style_select = gr.Dropdown(
                            label="Style", 
                            choices=style_choices, 
                            value="Photographic",
                            allow_custom_value=True
                        )
                        i2i_aspect_ratio = gr.Radio(choices=["Match Input"] + aspect_ratios, value="Match Input", label="Output Dimensions")
                        with gr.Accordion("Placement Controls (for object)", open=True):
                            i2i_tool_select = gr.Radio([const.PIN_TOOL, const.ANCHOR_TOOL], label="Tool", value=const.PIN_TOOL)
                            i2i_pin_coord_output = gr.Textbox(label="Pin Coords", interactive=False)
                            i2i_anchor_coord_output = gr.Textbox(label="Anchor Coords", interactive=False)
                            i2i_size_slider = gr.Slider(label="Relative Size (%)", minimum=10, maximum=200, value=100, step=5)
                        with gr.Accordion("Advanced Settings", open=False):
                            i2i_steps = gr.Slider(label="Inference Steps", minimum=1, maximum=50, value=20, step=1)
                            i2i_guidance = gr.Slider(label="Guidance Scale", minimum=0, maximum=10, value=3.0, step=0.1)
                            i2i_model_select = gr.Radio([const.LOCAL_MODEL, const.PRO_MODEL], label="Model", value=const.LOCAL_MODEL)
                        i2i_generate_btn = gr.Button("🚀 Generate Edit", variant="primary")
                        i2i_token_counter = gr.Markdown("Tokens: 0 / 77")

                    # --- DEMO TAB ---
                    with gr.Tab("Demo", id=2) as demo_tab:
                        gr.Markdown("### Demo Mode")
                        demo_background_gallery = gr.Gallery(label="1. Pick a Background", columns=2, height="auto", container=False)
                        demo_object_gallery = gr.Gallery(label="2. Pick an Object", columns=3, height="auto", container=False)
                        demo_style_select = gr.Dropdown(
                            label="Style", 
                            choices=style_choices, 
                            value="Photographic",
                            allow_custom_value=True
                        )
                        demo_aspect_ratio = gr.Radio(choices=aspect_ratios, value="1:1", label="Image Dimensions")
                        demo_num_images = gr.Slider(label="Number of Images", minimum=1, maximum=4, value=2, step=1)
                        demo_generate_btn = gr.Button("🚀 Generate Scene", variant="primary")

            # --- RIGHT PANEL ---
            with gr.Column(scale=3, elem_classes="main-content-area"):
                output_gallery = gr.Gallery(label="Generated Images", visible=True, columns=2, height="auto")
                i2i_interactive_canvas = gr.Image(type="pil", label="Interactive Canvas", visible=False, height=600, interactive=True)
                with gr.Row(visible=False) as i2i_decision_group:
                    accept_btn = gr.Button("✅ Accept Edit & Continue", variant="primary")
                    retry_btn = gr.Button("❌ Discard & Retry")
                with gr.Row():
                    save_btn = gr.Button("💾 Save")
                    download_output = gr.DownloadButton(label="Download", visible=False)

    ui_components = {
        # Global
        "mode_tabs": mode_tabs, "output_gallery": output_gallery, "i2i_interactive_canvas": i2i_interactive_canvas,
        "save_btn": save_btn, "download_output": download_output,
        "i2i_decision_group": i2i_decision_group, "accept_btn": accept_btn, "retry_btn": retry_btn,
        "provider_select": provider_select, "api_key_input": api_key_input, "save_api_key_btn": save_api_key_btn,
        "clear_api_key_btn": clear_api_key_btn, "pro_api_key_input": pro_api_key_input,
        "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,

        # T2I
        "t2i_prompt": t2i_prompt, "t2i_style_select": t2i_style_select, "t2i_steps": t2i_steps,
        "t2i_guidance": t2i_guidance, "t2i_model_select": t2i_model_select,
        "t2i_num_images": t2i_num_images, "t2i_generate_btn": t2i_generate_btn,
        "t2i_token_counter": t2i_token_counter, "t2i_aspect_ratio": t2i_aspect_ratio,

        # I2I
        "i2i_source_uploader": i2i_source_uploader, "i2i_object_uploader": i2i_object_uploader,
        "i2i_prompt": i2i_prompt, "i2i_tool_select": i2i_tool_select, "i2i_pin_coord_output": i2i_pin_coord_output,
        "i2i_anchor_coord_output": i2i_anchor_coord_output, "i2i_size_slider": i2i_size_slider,
        "i2i_steps": i2i_steps, "i2i_guidance": i2i_guidance, "i2i_model_select": i2i_model_select,
        "i2i_generate_btn": i2i_generate_btn, "i2i_token_counter": i2i_token_counter,
        "i2i_aspect_ratio": i2i_aspect_ratio, "i2i_style_select": i2i_style_select,
        
        # Demo
        "demo_background_gallery": demo_background_gallery, "demo_object_gallery": demo_object_gallery,
        "demo_num_images": demo_num_images, "demo_generate_btn": demo_generate_btn,
        "demo_aspect_ratio": demo_aspect_ratio, "demo_style_select": demo_style_select,

        # State
        "selected_background_path": selected_background_path, "selected_object_path": selected_object_path,
        "current_prompt_templates_state": current_prompt_templates_state, "merged_image_state": merged_image_state,
        "i2i_canvas_image_state": i2i_canvas_image_state, "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state, "i2i_anchor_coords_state": i2i_anchor_coords_state,
    }
    return demo, ui_components, {}