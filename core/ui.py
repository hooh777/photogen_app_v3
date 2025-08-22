import gradio as gr
from PIL import Image, ImageDraw
from core import constants as const

def create_default_canvas_image():
    """Create a default plain white image for the interactive canvas."""
    # Create a completely plain white image
    img = Image.new('RGB', (600, 400), 'white')
    return img

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
    
    /* Interactive Canvas Styling - Make image bigger */
    .interactive-canvas {
        min-height: 600px !important;
    }
    
    .interactive-canvas img {
        max-height: 580px !important;
        min-height: 500px !important;
        object-fit: contain !important;
        width: 100% !important;
        height: auto !important;
    }
    
    /* Hide ONLY upload prompts, keep image display functionality */
    .canvas-no-upload .upload-button,
    .canvas-no-upload .drag-drop-text,
    .canvas-no-upload .file-upload-text {
        display: none !important;
    }
    
    /* Hide cross/clear buttons from interactive canvas */
    .interactive-canvas .clear-button,
    .interactive-canvas button[aria-label="Clear"],
    .interactive-canvas button[title="Clear"],
    .interactive-canvas [data-testid="clear-button"],
    .canvas-no-upload .clear-button,
    .canvas-no-upload button[aria-label="Clear"],
    .canvas-no-upload button[title="Clear"],
    .canvas-no-upload [data-testid="clear-button"],
    .interactive-canvas .image-button,
    .canvas-no-upload .image-button {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide any buttons inside the image container */
    .interactive-canvas [data-testid="image"] button,
    .canvas-no-upload [data-testid="image"] button {
        display: none !important;
    }
    
    </style>
    
    <style>
    
    /* More specific targeting for canvas images */
    .interactive-canvas [data-testid="image"] img {
        max-height: 580px !important;
        min-height: 500px !important;
        object-fit: contain !important;
    }
    
    /* General image component enhancement */
    .gradio-image {
        min-height: 600px !important;
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
                gr.Markdown("### 📸 Step 1: Upload Your Images (Skip it if doing text2img)")
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
                - Click canvas to select areas for targeted editing (if needed)
                """)
                
                with gr.Column():
                    # Add Selfie Background Presets Section
                    gr.Markdown("#### 🎯 Selfie Background Presets")
                    selfie_preset_dropdown = gr.Dropdown(
                        choices=[
                            "None (Custom Prompt)",
                            # Elevator variations
                            "Elevator - Modern",
                            "Elevator - Vintage",
                            "Elevator - Glass/Panoramic",
                            "Elevator - Industrial",
                            # Train variations
                            "Train - Subway Car",
                            "Train - Luxury Train",
                            "Train - Vintage Train Car",
                            "Train - Bullet Train Interior",
                            # Cafe variations
                            "Cafe - Cozy Coffee Shop",
                            "Cafe - Modern Minimalist",
                            "Cafe - Outdoor Patio",
                            "Cafe - Bookstore Cafe",
                            # Restaurant variations
                            "Restaurant - Fine Dining",
                            "Restaurant - Casual Bistro",
                            "Restaurant - Rooftop Bar",
                            "Restaurant - Kitchen Counter"
                        ],
                        value="None (Custom Prompt)",
                        label="🏢 Choose Background Setting",
                        info="Select a preset to auto-fill the prompt, then customize as needed"
                    )


                    prompt_separator = gr.Markdown("## Write or Adjust Your Prompt", visible=True, elem_id="prompt_separator")

                    # Manual prompt writing
                    i2i_prompt = gr.Textbox(
                        label="Describe your desired composition", 
                        lines=8, 
                        max_lines=12,
                        placeholder="Describe how to combine your images...\n\nSingle Image: 'Enhance the lighting and add dramatic shadows'\nMulti-Image: 'Place the person in the room, sitting on the chair by the window'\nComposition: 'Combine these elements into a cohesive restaurant scene'",
                        show_copy_button=True,
                        autoscroll=False
                    )
                    
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
                    interactive=False  # Make display-only, not clickable
                )
                
                # Add download and clear buttons
                with gr.Row():
                    download_result_btn = gr.Button("⬇️ Download Result", variant="primary")
                    clear_all_btn = gr.Button("🗑️ Clear All", variant="stop")
                    download_output = gr.DownloadButton(label="Download Image", visible=False)
                
                # Always visible interactive canvas - no mode switching
                gr.Markdown("### 🎨 Interactive Canvas")
                canvas_instructions = gr.Markdown("**🎯 Click on the image** to select areas for targeted editing:", visible=True)
                
                i2i_interactive_canvas = gr.Image(
                    value=create_default_canvas_image(),  # Start with default white image
                    type="pil", 
                    label="🎨 Interactive Canvas", 
                    visible=True, 
                    height=600, 
                    interactive=True, 
                    sources=[],  # Empty list instead of None - this should actually disable uploads
                    elem_classes="interactive-canvas canvas-no-upload",
                    container=True,
                    show_label=True
                )
                
                # Both buttons in the same row under the canvas
                with gr.Row():
                    i2i_reset_selection_btn = gr.Button("🔄 Reset Selection", variant="secondary", visible=True)
                    i2i_auto_prompt_btn = gr.Button("🤖 Generate Smart Prompt", variant="primary", visible=False)
                
                # Canvas info (for upload instructions when no image)
                canvas_mode_info = gr.Markdown("**Upload images first to start selecting area**", visible=True)
                
                # Add JavaScript for canvas monitoring
                gr.HTML("""
                <script>
                console.log('🚀 PhotoGen Debug Script Loading...');
                
                // Monitor canvas and restore white image when cleared
                let canvasCheckInterval;
                let defaultImageDataUrl = null;
                let debugCounter = 0;
                let lastCanvasState = {};
                
                // Create default white image data URL
                function createDefaultImageDataUrl() {
                    if (!defaultImageDataUrl) {
                        console.log('🎨 Creating default white image data URL...');
                        const canvas = document.createElement('canvas');
                        canvas.width = 600;
                        canvas.height = 400;
                        const ctx = canvas.getContext('2d');
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, 600, 400);
                        defaultImageDataUrl = canvas.toDataURL();
                        console.log('🎨 Default white image created:', defaultImageDataUrl.substring(0, 50) + '...');
                    }
                    return defaultImageDataUrl;
                }
                
                // Check if canvas is empty and restore white image
                function checkAndRestoreCanvas(triggerReason = 'interval') {
                    debugCounter++;
                    const timestamp = new Date().toLocaleTimeString();
                    const canvasElements = document.querySelectorAll('.canvas-no-upload img, .interactive-canvas img, [data-testid="image"] img');
                    
                    console.log(`🔍 Check #${debugCounter} (${triggerReason}) at ${timestamp}: Found ${canvasElements.length} canvas image elements`);
                    
                    let restoredCount = 0;
                    canvasElements.forEach((img, index) => {
                        const currentState = {
                            src: img.src ? img.src.substring(0, 50) + '...' : 'EMPTY',
                            display: img.style.display,
                            visibility: img.style.visibility,
                            offsetHeight: img.offsetHeight,
                            offsetWidth: img.offsetWidth
                        };
                        
                        // Only log if state changed
                        const stateKey = `canvas_${index}`;
                        if (JSON.stringify(currentState) !== JSON.stringify(lastCanvasState[stateKey])) {
                            console.log(`🔄 Canvas ${index} state changed:`, currentState);
                            lastCanvasState[stateKey] = currentState;
                        }
                        
                        // Check if image is missing or shows upload placeholder
                        const isEmpty = !img.src || img.src === '' || img.src === 'data:,' || 
                                       img.style.display === 'none' || img.offsetHeight === 0 ||
                                       img.src.includes('data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP') ||
                                       img.naturalWidth === 0;
                                       
                        if (isEmpty) {
                            console.log(`❌ Canvas ${index} is empty, restoring white image... (trigger: ${triggerReason})`);
                            const whiteImageSrc = createDefaultImageDataUrl();
                            img.src = whiteImageSrc;
                            img.style.display = 'block';
                            img.style.visibility = 'visible';
                            restoredCount++;
                            console.log(`✅ White image restored to canvas ${index}`);
                        } else {
                            console.log(`✅ Canvas ${index} has image, no action needed`);
                        }
                    });
                    
                    if (restoredCount > 0) {
                        console.log(`🎉 Restored ${restoredCount} canvas(es) to white image`);
                    }
                    
                    // Also check for upload text and hide it
                    const uploadTexts = document.querySelectorAll('.canvas-no-upload .upload-message, .canvas-no-upload .drop-message, .interactive-canvas .upload-message');
                    if (uploadTexts.length > 0) {
                        console.log(`🚫 Found ${uploadTexts.length} upload text elements, hiding them`);
                        uploadTexts.forEach(text => {
                            text.style.display = 'none';
                        });
                    }
                    
                    // Log canvas container info
                    const canvasContainers = document.querySelectorAll('.canvas-no-upload, .interactive-canvas');
                    console.log(`📦 Found ${canvasContainers.length} canvas containers`);
                }
                
                // Add event listeners for immediate canvas checks
                function addButtonEventListeners() {
                    console.log('🎯 Setting up button event listeners...');
                    
                    // Check every 200ms for new buttons (they might be dynamically created)
                    setInterval(() => {
                        // Clear All button
                        const clearAllBtns = document.querySelectorAll('button[data-testid="Clear All"], button:contains("Clear All"), button:contains("🗑️")');
                        clearAllBtns.forEach(btn => {
                            if (!btn.hasAttribute('canvas-listener')) {
                                btn.setAttribute('canvas-listener', 'true');
                                console.log('🔗 Added Clear All button listener');
                                btn.addEventListener('click', () => {
                                    console.log('🗑️ Clear All button clicked!');
                                    // Check immediately and then a few more times
                                    setTimeout(() => checkAndRestoreCanvas('clear-all-100ms'), 100);
                                    setTimeout(() => checkAndRestoreCanvas('clear-all-300ms'), 300);
                                    setTimeout(() => checkAndRestoreCanvas('clear-all-500ms'), 500);
                                    setTimeout(() => checkAndRestoreCanvas('clear-all-1000ms'), 1000);
                                });
                            }
                        });
                        
                        // Note: Cross buttons removed from interactive canvas, no need to monitor them
                    }, 200);
                }
                
                // Start monitoring when page loads
                function startCanvasMonitoring() {
                    console.log('🚀 Starting canvas monitoring...');
                    if (canvasCheckInterval) {
                        console.log('🛑 Clearing existing interval');
                        clearInterval(canvasCheckInterval);
                    }
                    
                    // Check every 300ms for cleared canvas (faster response)
                    canvasCheckInterval = setInterval(() => {
                        checkAndRestoreCanvas('interval');
                    }, 300);
                    
                    // Also check immediately
                    console.log('🔄 Running initial canvas check...');
                    setTimeout(() => checkAndRestoreCanvas('initial'), 500);
                    
                    // Set up button listeners
                    addButtonEventListeners();
                }
                
                // Initialize monitoring with delay to ensure DOM is ready
                setTimeout(() => {
                    console.log('⏱️ Delayed start - initializing canvas monitoring');
                    startCanvasMonitoring();
                }, 2000);
                
                // Also try on DOMContentLoaded
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', () => {
                        console.log('📄 DOM Content Loaded - starting canvas monitoring');
                        setTimeout(startCanvasMonitoring, 1000);
                    });
                } else {
                    console.log('📄 DOM already ready - starting canvas monitoring immediately');
                    setTimeout(startCanvasMonitoring, 1000);
                }
                </script>
                """)

            # --- RIGHT PANEL (GENERATION & OUTPUT SETTINGS) ---
            with gr.Column(scale=2, min_width=280):
                
                # Step 3: Generate Your Image (moved from left panel)
                gr.Markdown("### 🚀 Step 3: Generate Your Image")
                final_status = gr.Markdown("**Status:** Ready to generate! 🎉", visible=True)
                
                gr.Markdown("---")  # Separator
                
                gr.Markdown("### ⚙️ Output Settings")
                
                # Combined dimension options with both standard and product mood shot sizes
                dimension_options = [
                    "Match Input",
                    # Standard Aspect Ratios
                    "1:1 (Square)",
                    "16:9 (Landscape)",
                    "9:16 (Portrait)", 
                    "4:3 (Standard)",
                    "3:4 (Portrait)"
                ]
                
                aspect_ratio = gr.Dropdown(
                    choices=dimension_options,
                    value="Match Input", 
                    label="📐 Image Dimensions",
                    info="Temporarily disabled - dimension selection not working properly",
                    interactive=False
                )

                with gr.Accordion("Advanced Settings", open=False):
                    i2i_steps = gr.Slider(label="Inference Steps", minimum=1, maximum=50, value=25, step=1)
                    i2i_guidance = gr.Slider(label="Guidance Scale", minimum=0, maximum=10, value=2.5, step=0.1)
                    i2i_model_select = gr.Dropdown(
                        choices=[const.LOCAL_MODEL, "Pro (Black Forest Labs)", "Pro (GRS AI)"], 
                        label="🤖 Model Selection", 
                        value="Pro (GRS AI)",
                        info="Choose between local processing or Pro API providers"
                    )

                i2i_generate_btn = gr.Button("🚀 Generate", variant="primary", visible=True, size="lg")


    ui_components = {
        "output_gallery": output_gallery, "i2i_interactive_canvas": i2i_interactive_canvas,
        "aspect_ratio": aspect_ratio,

        "provider_select": provider_select, "api_key_input": api_key_input, "save_api_key_btn": save_api_key_btn, "clear_api_key_btn": clear_api_key_btn,
        "pro_api_provider_select": pro_api_provider_select, "pro_api_key_input": pro_api_key_input, "save_pro_api_key_btn": save_pro_api_key_btn, "clear_pro_api_key_btn": clear_pro_api_key_btn,

        "i2i_source_uploader": multi_image_uploader, "i2i_object_uploader": uploaded_images_preview,
        "uploaded_images_preview": uploaded_images_preview,
        
        # Mode containers and controls
        "canvas_mode_info": canvas_mode_info, 
        "i2i_prompt": i2i_prompt, "i2i_auto_prompt_btn": i2i_auto_prompt_btn,
        "i2i_reset_selection_btn": i2i_reset_selection_btn,
        "prompt_separator": prompt_separator,
        "step1_status": step1_status, "step2_status": step2_status,
        "final_status": final_status,
        
        # Add selfie preset to components
        "selfie_preset_dropdown": selfie_preset_dropdown,
        
        # Download/Clear components
        "download_result_btn": download_result_btn, "clear_all_btn": clear_all_btn, "download_output": download_output,
        
        "i2i_steps": i2i_steps,
        "i2i_guidance": i2i_guidance, 
        "i2i_model_select": i2i_model_select, 
        "i2i_generate_btn": i2i_generate_btn,

        "i2i_canvas_image_state": i2i_canvas_image_state, "i2i_object_image_state": i2i_object_image_state,
        "i2i_pin_coords_state": i2i_pin_coords_state,
        "i2i_anchor_coords_state": i2i_anchor_coords_state,
        "selected_gallery_image_state": selected_gallery_image_state,
        "last_generated_image_state": last_generated_image_state,
    }
    return demo, ui_components, {}