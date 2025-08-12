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
                **Multi-Image Upload:**
                - Support up to 10 images for complex scenes
                """)
                
                with gr.Column():
                    # Single multi-image uploader (like Flux Kontext)
                    multi_image_uploader = gr.File(
                        label="📁 Images (drag & drop or browse)",
                        file_count="multiple",
                        file_types=["image"],
                        height=150,
                        interactive=True
                    )
                    
                    # Display uploaded images in a gallery for preview
                    uploaded_images_preview = gr.Gallery(
                        label="📋 Uploaded Images (max 10)",
                        visible=True,
                        columns=3,
                        height=200,
                        allow_preview=True,
                        show_label=True,
                        container=True,
                        object_fit="cover",
                        interactive=False
                    )
                    
                    # Progress indicator for Step 1
                    step1_status = gr.Markdown("**Status:** Ready to upload images 📁", visible=True)
                
                # Step 2: Smart Prompt Creation
                gr.Markdown("### ✍️ Step 2: Compose Your Scene")
                gr.Markdown("""
                **Intelligent Scene Composition:**
                - Single image: Direct editing/enhancement
                - Multiple images: AI-powered composition with context understanding
                - Click canvas to select areas for targeted editing (if needed)
                """)
                
                with gr.Column():
                    # Human interaction toggle with help text
                    with gr.Row():
                        allow_human_surfaces = gr.Checkbox(
                            label="🤝 Allow objects on people (hands, clothing, etc.)", 
                            value=False, 
                            visible=True,
                            info="Enable placement directly on people for realistic interactions."
                        )
                    


                    prompt_separator = gr.Markdown("## Adjust Your Prompt", visible=True, elem_id="prompt_separator")

                    # Manual prompt writing
                    i2i_prompt = gr.Textbox(
                        label="Describe your desired composition", 
                        lines=8, 
                        max_lines=12,
                        placeholder="Describe how to combine your images...\n\nSingle Image: 'Enhance the lighting and add dramatic shadows'\nMulti-Image: 'Place the person in the room, sitting on the chair by the window'\nComposition: 'Combine these elements into a cohesive restaurant scene'",
                        show_copy_button=True,
                        autoscroll=False
                    )
                    
                    # Token counter
                    i2i_token_counter = gr.Markdown("Tokens: 0 / 77", elem_id="token_counter")
                    
                    # Progress indicator for Step 2
                    step2_status = gr.Markdown("**Status:** Ready for composition prompt ✏️", visible=True)
                            

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
                
                # Canvas controls and workspace
                
                # Preview Mode: Show selected image with edit button
                preview_mode_container = gr.Column(visible=False)
                with preview_mode_container:
                    preview_instructions = gr.Markdown("**✨ Ready to edit this image?** Click the button below to start area selection:", visible=True)
                    with gr.Row(variant="panel"):
                        edit_selected_btn = gr.Button("🖼️ Edit Selected Image", variant="primary", size="lg", visible=True, elem_classes="pulse-button")
                
                # Editing Mode: Interactive canvas with controls
                editing_mode_container = gr.Column(visible=False)
                with editing_mode_container:
                    canvas_instructions = gr.Markdown("**🎯 Click and drag on the image** to select areas for targeted editing:", visible=True)
                    
                    i2i_interactive_canvas = gr.Image(
                        type="pil", 
                        label="🎨 Interactive Canvas", 
                        visible=True, 
                        height=400, 
                        interactive=True, 
                        sources=[]
                    )
                    
                    with gr.Row():
                        back_to_compose_btn = gr.Button("🔙 Back to Composition", variant="stop", size="lg")
                        i2i_auto_prompt_btn = gr.Button("🤖 Generate Smart Prompt", variant="primary", size="lg", visible=False)
                        canvas_mode_info = gr.Markdown("**Select an area first to unlock prompt generation**", visible=True)
                
                # Legacy canvas (hidden by default, kept for compatibility)
                i2i_interactive_canvas_legacy = gr.Image(
                    type="pil", 
                    label="🎨 Image Editor: Click areas for targeted editing", 
                    visible=False, 
                    height=400, 
                    interactive=True, 
                    sources=[]
                )

            # --- RIGHT PANEL (GENERATION & OUTPUT SETTINGS) ---
            with gr.Column(scale=2, min_width=280):
                # Canvas Controls (only visible in editing mode)
                canvas_controls_container = gr.Column(visible=False)
                with canvas_controls_container:
                    gr.Markdown("### 🎯 Canvas Controls")
                    canvas_help_text = gr.Markdown("💡 **Select an area first**, then use the tools below:", visible=True)
                    
                    with gr.Column():
                        i2i_reset_selection_btn = gr.Button("🔄 Reset Selection", variant="secondary", visible=False)
                    
                    gr.Markdown("---")  # Separator
                
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
                    
                    # Depth Control Settings
                    gr.Markdown("#### 🌊 Depth Enhancement")
                    with gr.Row():
                        use_depth_control = gr.Checkbox(
                            label="Enable Depth Control", 
                            value=True,
                            interactive=True,
                            info="Analyze image depth for better background replacement"
                        )
                    with gr.Row():
                        depth_strength = gr.Slider(
                            label="Depth Strength", 
                            minimum=0.1, 
                            maximum=1.0, 
                            value=0.6, 
                            step=0.1,
                            interactive=True,
                            info="Control how much depth information influences generation"
                        )
                    
                    # Prompt Enhancement Control
                    gr.Markdown("#### 🔧 Prompt Control")
                    with gr.Row():
                        disable_auto_enhancement = gr.Checkbox(
                            label="Disable Auto Prompt Enhancement", 
                            value=True,
                            interactive=True,
                            info="Turn off automatic preservation instructions (for manual testing)"
                        )

                i2i_generate_btn = gr.Button("🚀 Generate", variant="primary", visible=True, size="lg")


    ui_components = {
        "output_gallery": output_gallery, "i2i_interactive_canvas": i2i_interactive_canvas,
        "num_images": num_images, "aspect_ratio": aspect_ratio,

        "provider_select": provider_select, "api_key_input": api_key_input, "save_api_key_btn": save_api_key_btn, "clear_api_key_btn": clear_api_key_btn,
        "pro_api_provider_select": pro_api_provider_select, "pro_api_key_input": pro_api_key_input, "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,

        "i2i_source_uploader": multi_image_uploader, "i2i_object_uploader": uploaded_images_preview,
        "uploaded_images_preview": uploaded_images_preview,
        
        # Mode containers and controls
        "preview_mode_container": preview_mode_container,
        "editing_mode_container": editing_mode_container, 
        "canvas_controls_container": canvas_controls_container,
        "canvas_mode_info": canvas_mode_info, "edit_selected_btn": edit_selected_btn, "back_to_compose_btn": back_to_compose_btn,
        "i2i_prompt": i2i_prompt, "i2i_auto_prompt_btn": i2i_auto_prompt_btn,
        "i2i_reset_selection_btn": i2i_reset_selection_btn, "allow_human_surfaces": allow_human_surfaces,
        "prompt_separator": prompt_separator,
        "i2i_token_counter": i2i_token_counter,
        "step1_status": step1_status, "step2_status": step2_status,
        "final_status": final_status,
        
        # Save/Download components
        "save_btn": save_btn, "clear_all_btn": clear_all_btn, "download_output": download_output,
        
        "i2i_steps": i2i_steps,
        "i2i_guidance": i2i_guidance, 
        "i2i_model_select": i2i_model_select, 
        "use_depth_control": use_depth_control,
        "depth_strength": depth_strength,
        "disable_auto_enhancement": disable_auto_enhancement,
        "i2i_generate_btn": i2i_generate_btn,

        "i2i_canvas_image_state": i2i_canvas_image_state, "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state,
        "i2i_anchor_coords_state": i2i_anchor_coords_state,
        "selected_gallery_image_state": selected_gallery_image_state,
        "last_generated_image_state": last_generated_image_state,
    }
    return demo, ui_components, {}