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
            pro_api_key_input = gr.Textbox(label="Flux Pro API Key", type="password", placeholder="Enter key for the Pro image model")
            with gr.Row():
                save_pro_api_key_btn = gr.Button("💾 Save Pro Key")
                clear_pro_api_key_btn = gr.Button("🗑️ Clear Pro Key")

        with gr.Row(equal_height=False):
            # --- LEFT PANEL (CONTROLS) ---
            with gr.Column(scale=3, min_width=450):
                
                gr.Markdown("### 🎨 PhotoGen - Create & Edit Mode")
                
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
                    gr.Markdown("""
                    💡 **Flux Kontext Pro Tip**: For best results in Edit Mode, include phrases like:
                    - `"Place the [object] on the background image on the left"`
                    - `"Add a [object] to the background image on the left"`
                    
                    This helps the AI understand spatial relationships better!
                    """)
                    i2i_prompt = gr.Textbox(
                        label="Describe what you want to create/edit", 
                        lines=8, 
                        max_lines=12,
                        placeholder="Type your creative description here...\n\nFor Edit Mode: Try 'Place the red car on the background image on the left, in the parking lot'",
                        show_copy_button=True,
                        autoscroll=False
                    )
                    
                    # Token counter
                    i2i_token_counter = gr.Markdown("Tokens: 0 / 77", elem_id="token_counter")
                    
                    # Auto Suggestions Section
                    with gr.Row():
                        show_suggestions_btn = gr.Button("🤖 Show Auto Suggestions", variant="secondary", size="sm", visible=False)
                    
                    # Auto Suggestions Collapsible Panel
                    with gr.Accordion("🤖 Auto Suggestions", open=False, visible=False) as auto_suggestions_panel:
                                # Scene Analysis Section
                                with gr.Accordion("🔍 Scene Analysis", open=False) as scene_analysis_section:
                                    scene_summary = gr.Markdown("**Detected:** No scene analyzed yet")
                                    with gr.Row():
                                        scene_details_btn = gr.Button("📋 View Details", size="sm")
                                    scene_analysis_details = gr.JSON(label="Full Scene Analysis", visible=False)
                                
                                # Auto-Generated Prompt Section  
                                with gr.Accordion("🎨 Auto-Generated Prompt", open=False) as auto_prompt_section:
                                    auto_generated_prompt = gr.Textbox(
                                        label="AI Generated Prompt", 
                                        lines=3, 
                                        placeholder="Auto-generated prompt will appear here...",
                                        interactive=False
                                    )
                                    with gr.Row():
                                        copy_auto_prompt_btn = gr.Button("� Copy to Input", variant="primary", size="sm")
                                        copy_auto_icon = gr.Markdown("", visible=False)
                                
                                # Enhanced User Prompt Section
                                with gr.Accordion("✨ Enhanced Prompt", open=False) as enhanced_prompt_section:
                                    enhanced_user_prompt = gr.Textbox(
                                        label="Your Prompt + Scene Context", 
                                        lines=3, 
                                        placeholder="Enhanced version will appear here...",
                                        interactive=False
                                    )
                                    with gr.Row():
                                        copy_enhanced_prompt_btn = gr.Button("📋 Copy to Input", variant="primary", size="sm")
                                        copy_enhanced_icon = gr.Markdown("", visible=False)
                                
                                # Prompt Variations Section
                                with gr.Accordion("🔄 Prompt Variations", open=False) as variations_section:
                                    gr.Markdown("**Creative alternatives based on your scene:**")
                                    variation_1 = gr.Textbox(label="Variation 1", lines=2, interactive=False)
                                    with gr.Row():
                                        copy_var1_btn = gr.Button("📋 Copy", size="sm")
                                        copy_var1_icon = gr.Markdown("", visible=False)
                                    
                                    variation_2 = gr.Textbox(label="Variation 2", lines=2, interactive=False)
                                    with gr.Row():
                                        copy_var2_btn = gr.Button("📋 Copy", size="sm")
                                        copy_var2_icon = gr.Markdown("", visible=False)
                                    
                                    variation_3 = gr.Textbox(label="Variation 3", lines=2, interactive=False)
                                    with gr.Row():
                                        copy_var3_btn = gr.Button("📋 Copy", size="sm")
                                        copy_var3_icon = gr.Markdown("", visible=False)
                    
                    # Progress indicator for Step 2
                    step2_status = gr.Markdown("**Status:** Ready for your prompt ✏️", visible=True)
                
                # Step 3: Area Selection (Edit Mode Only)
                gr.Markdown("### 🎯 Step 3: Select Areas (Edit Mode Only)")
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
                            step3_status = gr.Markdown("**Status:** Ready to select areas 🎯", visible=True)
                
                # Final Step: Generate
                gr.Markdown("### 🚀 Step 4: Generate Your Image")
                final_status = gr.Markdown("**Status:** Ready to generate! 🎉", visible=True)
                            

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
                    download_output = gr.DownloadButton(label="Download Image", visible=False)
                
                i2i_interactive_canvas = gr.Image(type="pil", label="📋 Click to select areas (Edit Mode)", visible=True, height=None, interactive=True, sources=[])

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

    ui_components = {
        "output_gallery": output_gallery, "i2i_interactive_canvas": i2i_interactive_canvas,
        "num_images": num_images, "aspect_ratio": aspect_ratio,

        "provider_select": provider_select, "api_key_input": api_key_input, "save_api_key_btn": save_api_key_btn, "clear_api_key_btn": clear_api_key_btn,
        "pro_api_key_input": pro_api_key_input, "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,

        "i2i_source_uploader": i2i_source_uploader, "i2i_object_uploader": i2i_object_uploader,
        "i2i_prompt": i2i_prompt, "i2i_auto_prompt_btn": i2i_auto_prompt_btn,
        "i2i_reset_selection_btn": i2i_reset_selection_btn, "prompt_separator": prompt_separator,
        "i2i_token_counter": i2i_token_counter,
        "step1_status": step1_status, "step2_status": step2_status, "step3_status": step3_status,
        "final_status": final_status,
        "area_selection_guide": area_selection_guide,
        
        # Save/Download components
        "save_btn": save_btn, "download_output": download_output,
        
        # Auto Suggestions components
        "show_suggestions_btn": show_suggestions_btn, "auto_suggestions_panel": auto_suggestions_panel,
        "scene_analysis_section": scene_analysis_section, "scene_summary": scene_summary, 
        "scene_details_btn": scene_details_btn, "scene_analysis_details": scene_analysis_details,
        "auto_prompt_section": auto_prompt_section, "auto_generated_prompt": auto_generated_prompt,
        "copy_auto_prompt_btn": copy_auto_prompt_btn, "copy_auto_icon": copy_auto_icon,
        "enhanced_prompt_section": enhanced_prompt_section, "enhanced_user_prompt": enhanced_user_prompt,
        "copy_enhanced_prompt_btn": copy_enhanced_prompt_btn, "copy_enhanced_icon": copy_enhanced_icon,
        "variations_section": variations_section, "variation_1": variation_1, "variation_2": variation_2, "variation_3": variation_3,
        "copy_var1_btn": copy_var1_btn, "copy_var1_icon": copy_var1_icon,
        "copy_var2_btn": copy_var2_btn, "copy_var2_icon": copy_var2_icon,
        "copy_var3_btn": copy_var3_btn, "copy_var3_icon": copy_var3_icon,
        
        "i2i_steps": i2i_steps,
        "i2i_guidance": i2i_guidance, "i2i_model_select": i2i_model_select, "i2i_generate_btn": i2i_generate_btn,

        "i2i_canvas_image_state": i2i_canvas_image_state, "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state,
        "i2i_anchor_coords_state": i2i_anchor_coords_state,
        "selected_gallery_image_state": selected_gallery_image_state,
        "last_generated_image_state": last_generated_image_state,
    }
    return demo, ui_components, {}