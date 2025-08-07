import gradio as gr
from core import constants as const

def create_ui():
    """Creates the final three-panel Gradio UI."""
    
    custom_css = """
    .gradio-container { max-width: none !important; }
    .main-content-area { min-height: 80vh; }
    
    /* Progress status styling */
    [data-testid="markdown"] p strong {
        color: #10b981 !important;
    }
    
    /* Step headers styling */
    h3 {
        color: #1f2937 !important;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
    
    /* Auto-generate button prominence */
    .auto-generate-primary {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6) !important;
        border: none !important;
        font-weight: 600 !important;
    }
    """

    with gr.Blocks(theme=gr.themes.Soft(), title="PhotoGen", css=custom_css) as demo:
        # --- State Holders ---
        i2i_canvas_image_state = gr.State()
        i2i_object_image_state = gr.State()
        i2i_pin_coords_state = gr.State()
        i2i_anchor_coords_state = gr.State()
        selected_gallery_image_state = gr.State()
        last_generated_image_state = gr.State()  # Track last generated image for direct saving
        
        gr.Markdown("# 📸 PhotoGen")
        
        with gr.Accordion("⚙️ AI Vision / Enhancer Settings", open=False):
            provider_select = gr.Dropdown(choices=[], value=None, label="Vision/Enhancer Provider")
            api_key_input = gr.Textbox(label="API Key", type="password", placeholder="Enter key and click Save")
            with gr.Row():
                save_api_key_btn = gr.Button("💾 Save Key")
                clear_api_key_btn = gr.Button("🗑️ Clear Key")

        with gr.Accordion("⚙️ Pro Model Settings", open=False):
            # API Provider Selection
            pro_api_provider_select = gr.Dropdown(
                choices=["Black Forest Labs API", "GRS AI Flux API"], 
                value="Black Forest Labs API", 
                label="🚀 Pro API Provider",
                info="Choose your preferred Pro API provider"
            )
            # Dynamic API Key Input
            pro_api_key_input = gr.Textbox(
                label="Black Forest Labs API Key", 
                type="password", 
                placeholder="Enter your API key and click Save"
            )
            with gr.Row():
                save_pro_api_key_btn = gr.Button("💾 Save API Key")
                clear_pro_api_key_btn = gr.Button("🗑️ Clear API Key")

        with gr.Row(equal_height=False):
            # --- LEFT PANEL (CONTROLS) ---
            with gr.Column(scale=3, min_width=450):
                
                gr.Markdown("### 🎨 PhotoGen - Create & Edit Mode")
                
                # Step 1: Upload Images
                gr.Markdown("### 📸 Step 1: Upload Your Images")
                gr.Markdown("""
                **You can do the following:**
                - Leave background empty to generate new images
                - Upload background to edit existing photos
                """)
                
                with gr.Column():
                    i2i_source_uploader = gr.Image(type="pil", label="Background Image (Optional - leave empty for Create Mode)")
                    i2i_object_uploader = gr.Image(type="pil", label="Object Image (Optional)")
                    
                    # Progress indicator for Step 1
                    step1_status = gr.Markdown("**Status:** Ready to upload images 📁", visible=True)
                
                # Step 2: Smart Prompt Creation with Area Selection
                gr.Markdown("### ✍️ Step 2: Select Area to Auto-generate Prompt")
                gr.Markdown("""
                If you have a background image, click on it to select where to place the object.
                The AI will then generate a prompt based on your selection.
                """)
                
                with gr.Column():
                    # Area selection controls for Edit Mode
                    with gr.Row():
                        i2i_auto_prompt_btn = gr.Button("🤖 Generate Auto-Prompt", variant="primary", visible=False, elem_classes="auto-generate-primary")
                        i2i_reset_selection_btn = gr.Button("🔄 Reset Selection", variant="secondary", visible=False)
                    
                    # Human interaction toggle with help text
                    with gr.Row():
                        allow_human_surfaces = gr.Checkbox(
                            label="🤝 Allow objects on people (hands, clothing, etc.)", 
                            value=False, 
                            visible=False,
                            info="By default, objects are placed on environmental surfaces (tables, counters, etc.). Enable this to allow placement directly on people."
                        )
                    


                    prompt_separator = gr.Markdown("## Adjust Your Prompt", visible=True, elem_id="prompt_separator")

                    # Manual prompt writing
                    i2i_prompt = gr.Textbox(
                        label="Describe what you want to create/edit", 
                        lines=8, 
                        max_lines=12,
                        placeholder="Type your creative description here...\n\nCreate Mode: 'A beautiful red wine glass on an elegant table'\nEdit Mode: 'Place the red car in the parking area on the concrete surface'",
                        show_copy_button=True,
                        autoscroll=False
                    )
                    
                    # Token counter
                    i2i_token_counter = gr.Markdown("Tokens: 0 / 77", elem_id="token_counter")
                    
                    # Progress indicator for Step 2
                    step2_status = gr.Markdown("**Status:** Ready for your prompt ✏️", visible=True)
                            

            # --- CENTER PANEL (CANVAS / GALLERY) ---
            with gr.Column(scale=5, elem_classes="main-content-area"):
                gr.Markdown("### 🖼️ Workspace")
                
                output_gallery = gr.Gallery(
                    label="Generated Images", 
                    visible=True, 
                    columns=2, 
                    height="auto",
                    allow_preview=True,
                    selected_index=None,
                    interactive=True
                )
                
                # Add save button for gallery images
                with gr.Row():
                    save_btn = gr.Button("💾 Save Selected Image", variant="secondary")
                    clear_all_btn = gr.Button("🗑️ Clear All", variant="stop")
                    download_output = gr.DownloadButton(label="Download Image", visible=False)
                
                i2i_interactive_canvas = gr.Image(type="pil", label="📋 Canvas: View generated images & select areas (Edit Mode)", visible=True, height=None, interactive=True, sources=[])

            # --- RIGHT PANEL (GENERATION & OUTPUT SETTINGS) ---
            with gr.Column(scale=2, min_width=280):
                # Step 3: Generate Your Image (moved from left panel)
                gr.Markdown("### 🚀 Step 3: Generate Your Image")
                final_status = gr.Markdown("**Status:** Ready to generate! 🎉", visible=True)
                
                gr.Markdown("---")  # Separator
                
                gr.Markdown("### ⚙️ Output Settings")
                num_images = gr.Slider(label="Number of Images", minimum=1, maximum=4, value=1, step=1)
                aspect_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
                aspect_ratio = gr.Radio(choices=["Match Input"] + aspect_ratios, value="1:1", label="Image Dimensions")

                with gr.Accordion("Advanced Settings", open=True):
                    i2i_steps = gr.Slider(label="Inference Steps", minimum=1, maximum=50, value=25, step=1)
                    i2i_guidance = gr.Slider(label="Guidance Scale", minimum=0, maximum=10, value=2.5, step=0.1)
                    i2i_model_select = gr.Dropdown(
                        choices=[const.LOCAL_MODEL, "Pro (Black Forest Labs)", "Pro (GRS AI)"], 
                        label="🤖 Model Selection", 
                        value=const.LOCAL_MODEL,
                        info="Choose between local processing or Pro API providers"
                    )

                i2i_generate_btn = gr.Button("🚀 Generate", variant="primary", visible=True, size="lg")


    ui_components = {
        "output_gallery": output_gallery, "i2i_interactive_canvas": i2i_interactive_canvas,
        "num_images": num_images, "aspect_ratio": aspect_ratio,

        "provider_select": provider_select, "api_key_input": api_key_input, "save_api_key_btn": save_api_key_btn, "clear_api_key_btn": clear_api_key_btn,
        "pro_api_provider_select": pro_api_provider_select, "pro_api_key_input": pro_api_key_input, "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,

        "i2i_source_uploader": i2i_source_uploader, "i2i_object_uploader": i2i_object_uploader,
        "i2i_prompt": i2i_prompt, "i2i_auto_prompt_btn": i2i_auto_prompt_btn,
        "i2i_reset_selection_btn": i2i_reset_selection_btn, "allow_human_surfaces": allow_human_surfaces,
        "prompt_separator": prompt_separator,
        "i2i_token_counter": i2i_token_counter,
        "step1_status": step1_status, "step2_status": step2_status,
        "final_status": final_status,
        
        # Save/Download components
        "save_btn": save_btn, "clear_all_btn": clear_all_btn, "download_output": download_output,
        
        "i2i_steps": i2i_steps,
        "i2i_guidance": i2i_guidance, "i2i_model_select": i2i_model_select, "i2i_generate_btn": i2i_generate_btn,

        "i2i_canvas_image_state": i2i_canvas_image_state, "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state,
        "i2i_anchor_coords_state": i2i_anchor_coords_state,
        "selected_gallery_image_state": selected_gallery_image_state,
        "last_generated_image_state": last_generated_image_state,
    }
    return demo, ui_components, {}