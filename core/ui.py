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

                    with gr.Tab("Demo", id=0):
                        gr.Markdown("### Step 1: Choose Background & Object")
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("**Select Background:**")
                                demo_background_gallery = gr.Gallery(label="Backgrounds", columns=3, height=200)
                                selected_background_path = gr.State()
                            with gr.Column():
                                gr.Markdown("**Select Object:**")
                                demo_object_gallery = gr.Gallery(label="Objects", columns=3, height=200)
                                selected_object_path = gr.State()
                        
                        gr.Markdown("### Step 2: Customize Prompt")
                        current_prompt_templates_state = gr.State()
                        
                        with gr.Column():
                            with gr.Row():
                                p1_prefix = gr.State()
                                p1_suffix = gr.State()
                                p1_editable = gr.Textbox(label="Base Description", placeholder="Enter object description...")
                            
                            with gr.Row():
                                p2_checkbox = gr.Checkbox(label="Include Position & Lighting", value=False)
                                p2_prefix = gr.State()
                                p2_suffix = gr.State()
                                p2_editable = gr.Textbox(label="Position & Lighting", placeholder="Position details...", visible=False)
                            
                            with gr.Row():
                                p3_checkbox = gr.Checkbox(label="Include Style & Tone", value=False)
                                p3_prefix = gr.State()
                                p3_suffix = gr.State()
                                p3_editable = gr.Textbox(label="Style & Tone", placeholder="Style details...", visible=False)
                        
                        demo_num_images = gr.Slider(label="Number of Images", minimum=1, maximum=4, value=1, step=1)
                        demo_generate_btn = gr.Button("🚀 Generate Demo", variant="primary")
                        
                        # Event handlers for demo checkboxes
                        p2_checkbox.change(lambda x: gr.update(visible=x), inputs=p2_checkbox, outputs=p2_editable)
                        p3_checkbox.change(lambda x: gr.update(visible=x), inputs=p3_checkbox, outputs=p3_editable)

                    with gr.Tab("Create / Edit", id=1):
                        gr.Markdown("### 🎨 Create & Edit Mode")
                        
                        # Step 1: Upload Images
                        gr.Markdown("### 📸 Step 1: Upload Your Images")
                        gr.Markdown("""
                        **Choose your mode by uploading images:**
                        - **🎨 Create Mode**: Leave background empty to generate new images
                        - **✏️ Edit Mode**: Upload background to edit existing photos
                        """)
                        
                        with gr.Column():
                            i2i_source_uploader = gr.Image(type="pil", label="Background Image (Optional - leave empty for Create Mode)")
                            i2i_object_uploader = gr.Image(type="pil", label="Object Image (Optional)")
                            
                            # Progress indicator for Step 1
                            step1_status = gr.Markdown("**Status:** Ready to upload images 📁", visible=True)
                        
                        # Step 2: Generate/Write Prompt  
                        gr.Markdown("### ✍️ Step 2: Create Your Prompt")
                        gr.Markdown("""
                        **Two ways to create your prompt:**
                        - **🤖 Auto-Generate** (Edit Mode): Let AI analyze your images and suggest prompts
                        - **✏️ Manual Writing**: Write your own creative description
                        """)
                        
                        with gr.Column():
                            # Auto-generate button (will be hidden in Create Mode)
                            i2i_auto_prompt_btn = gr.Button("🤖 Step 2A: Auto-Generate Smart Prompt", variant="primary", visible=False, elem_classes="auto-generate-primary")
                            prompt_separator = gr.Markdown("---\n**OR**\n---", visible=False, elem_id="prompt_separator")
                            
                            # Manual prompt writing
                            gr.Markdown("**✏️ Step 2B: Write Your Own Prompt**")
                            i2i_prompt = gr.Textbox(
                                label="Describe what you want to create/edit", 
                                lines=8, 
                                max_lines=12,
                                placeholder="Type your creative description here...",
                                show_copy_button=True,
                                autoscroll=False
                            )
                            
                            # Token counter
                            i2i_token_counter = gr.Markdown("Tokens: 0 / 77", elem_id="token_counter")
                            
                            # Enhancement launcher
                            with gr.Row():
                                launch_enhancer_btn = gr.Button("🚀 AI Prompt Enhancement", variant="secondary", size="sm")
                            
                            # Progress indicator for Step 2
                            step2_status = gr.Markdown("**Status:** Ready for your prompt ✏️", visible=True)
                        
                        # Step 3: Style Selection
                        gr.Markdown("### 🎨 Step 3: Choose Style (Optional)")
                        i2i_style_select = gr.Dropdown(label="Style", choices=style_choices, value=None, allow_custom_value=True)
                        step3_status = gr.Markdown("**Status:** Style ready ✨", visible=True)
                        # Step 4: Area Selection (Edit Mode Only)
                        gr.Markdown("### 🎯 Step 4: Select Areas (Edit Mode Only)")
                        gr.Markdown("💡 **Look at the center workspace** → Click twice on your image to select where to place objects")
                        with gr.Accordion("How to Select Areas", open=False, visible=False, elem_id="area_selection_guide") as area_selection_guide:
                            gr.Markdown("""
                            **� Quick Guide:**
                            • **Click twice** on your photo to select where to place objects
                            • First click = top-left corner 🔵
                            • Second click = bottom-right corner 🔵
                            • You'll see a blue box showing your selection ✨
                            
                            **💡 Tips:**
                            • Click near edges - we'll help you select them perfectly!
                            • Use the Auto-Generate button for smart suggestions
                            
                            <details>
                            <summary><strong>🔧 Need Help? (Click to expand)</strong></summary>
                            
                            **Having trouble selecting?**
                            • Make sure you upload a background image first
                            • Try clicking in different spots if selection isn't working
                            • The gray corners show you can click there easily
                            • Small selections will be made bigger automatically
                            
                            **Reset anytime:** Use the Reset Selection button to start over
                            </details>
                            """)
                            
                            i2i_reset_selection_btn = gr.Button("🔄 Reset Selection", variant="secondary")
                            step4_status = gr.Markdown("**Status:** Ready to select areas 🎯", visible=True)
                        
                        # Final Step: Generate
                        gr.Markdown("### 🚀 Step 5: Generate Your Image")
                        final_status = gr.Markdown("**Status:** Ready to generate! 🎉", visible=True)
                            

            # --- CENTER PANEL (CANVAS / GALLERY) ---
            with gr.Column(scale=5, elem_classes="main-content-area"):
                gr.Markdown("### 🖼️ Workspace")
                gr.Markdown("Upload a background image to start editing, or leave empty for create mode")
                
                output_gallery = gr.Gallery(label="Generated Images", visible=True, columns=2, height="auto")
                
                # Add save button for gallery images
                with gr.Row():
                    save_btn = gr.Button("💾 Save Selected Image", variant="secondary")
                    download_output = gr.DownloadButton(label="Download Image", visible=False)
                
                i2i_interactive_canvas = gr.Image(type="pil", label="📋 Click and drag to select areas (Edit Mode)", visible=True, height=None, interactive=True)
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
                
                i2i_generate_btn = gr.Button("🚀 Generate", variant="primary", visible=True)
        
        # Enhancement Modal (hidden by default)
        with gr.Column(visible=False) as enhancer_modal:
            gr.Markdown("## 🚀 AI Prompt Enhancement")
            with gr.Row():
                with gr.Column():
                    base_prompt_input = gr.Textbox(label="Basic Prompt Idea", placeholder="Enter your basic idea...")
                    close_enhancer_btn = gr.Button("❌ Close", variant="secondary")
                
                with gr.Column():
                    enhance_btn = gr.Button("✨ Generate Enhancements", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    detailed_output = gr.Textbox(label="Detailed Version", lines=3)
                    use_detailed_btn = gr.Button("Use Detailed", variant="secondary")
                with gr.Column():
                    stylized_output = gr.Textbox(label="Stylized Version", lines=3)
                    use_stylized_btn = gr.Button("Use Stylized", variant="secondary")
                with gr.Column():
                    rephrased_output = gr.Textbox(label="Rephrased Version", lines=3)
                    use_rephrased_btn = gr.Button("Use Rephrased", variant="secondary")

    ui_components = {
        "mode_tabs": mode_tabs,
        "output_gallery": output_gallery, "i2i_interactive_canvas": i2i_interactive_canvas,
        "i2i_actions_group": i2i_actions_group,
        "i2i_decision_group": i2i_decision_group, "accept_btn": accept_btn, "retry_btn": retry_btn,
        "i2i_save_btn": i2i_save_btn, "i2i_download_output": i2i_download_output,
        "num_images": num_images, "aspect_ratio": aspect_ratio,

        "provider_select": provider_select, "api_key_input": api_key_input, "save_api_key_btn": save_api_key_btn, "clear_api_key_btn": clear_api_key_btn,
        "pro_api_key_input": pro_api_key_input, "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,

        # Demo components
        "demo_background_gallery": demo_background_gallery, "demo_object_gallery": demo_object_gallery,
        "selected_background_path": selected_background_path, "selected_object_path": selected_object_path,
        "current_prompt_templates_state": current_prompt_templates_state,
        "p1_editable": p1_editable, "p1_prefix": p1_prefix, "p1_suffix": p1_suffix,
        "p2_editable": p2_editable, "p2_prefix": p2_prefix, "p2_suffix": p2_suffix, "p2_checkbox": p2_checkbox,
        "p3_editable": p3_editable, "p3_prefix": p3_prefix, "p3_suffix": p3_suffix, "p3_checkbox": p3_checkbox,
        "demo_num_images": demo_num_images, "demo_generate_btn": demo_generate_btn,

        "i2i_source_uploader": i2i_source_uploader, "i2i_object_uploader": i2i_object_uploader,
        "i2i_prompt": i2i_prompt, "i2i_style_select": i2i_style_select, "i2i_auto_prompt_btn": i2i_auto_prompt_btn,
        "i2i_reset_selection_btn": i2i_reset_selection_btn, "prompt_separator": prompt_separator,
        "i2i_token_counter": i2i_token_counter,
        "step1_status": step1_status, "step2_status": step2_status, "step3_status": step3_status,
        "step4_status": step4_status, "final_status": final_status,
        "area_selection_guide": area_selection_guide,
        
        # Save/Download components
        "save_btn": save_btn, "download_output": download_output,
        
        # Enhancement modal components
        "enhancer_modal": enhancer_modal, "base_prompt_input": base_prompt_input,
        "launch_enhancer_btn": launch_enhancer_btn, "close_enhancer_btn": close_enhancer_btn,
        "enhance_btn": enhance_btn, "detailed_output": detailed_output, "stylized_output": stylized_output,
        "rephrased_output": rephrased_output, "use_detailed_btn": use_detailed_btn,
        "use_stylized_btn": use_stylized_btn, "use_rephrased_btn": use_rephrased_btn,
        
        "i2i_steps": i2i_steps,
        "i2i_guidance": i2i_guidance, "i2i_model_select": i2i_model_select, "i2i_generate_btn": i2i_generate_btn,

        "i2i_canvas_image_state": i2i_canvas_image_state, "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state,
        "i2i_anchor_coords_state": i2i_anchor_coords_state,
    }
    return demo, ui_components, {}