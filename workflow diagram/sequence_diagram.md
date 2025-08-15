# PhotoGen App v3 - Current Implementation Workflows

## Overview
This document contains updated sequence diagrams reflecting the current PhotoGen application implementation, including multi-image upload, gallery selection, manual prompt detection, and the "Match Input + post-resize" strategy.

## 1. Multi-Image Upload and Gallery Selection Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio UI
    participant I2IHandler as I2I Handler
    participant CanvasManager as Canvas Manager
    participant Utils as Image Utils

    Note over User, Utils: Current Multi-Image Upload System

    User->>UI: Upload multiple images (background + objects)
    UI->>I2IHandler: handle_multi_image_upload(uploaded_files)
    
    I2IHandler->>I2IHandler: Process uploaded files (max 10 images)
    loop For each uploaded file
        I2IHandler->>I2IHandler: Open and validate image
        I2IHandler->>I2IHandler: Add to processed_images list
    end
    
    I2IHandler->>I2IHandler: Store images in self.uploaded_images
    alt Single Image Uploaded
        I2IHandler->>I2IHandler: Set as background_state, no object_state
        I2IHandler-->>UI: Single image ready for editing
    else Multiple Images Uploaded
        I2IHandler->>I2IHandler: First image = background, second = object (default)
        I2IHandler-->>UI: Gallery preview + default states
    end
    
    I2IHandler-->>UI: Return gallery preview, states, and status
    UI-->>User: Display image gallery for selection
    
    Note over User, Utils: Gallery Selection Process
    
    User->>UI: Click on image in gallery
    UI->>I2IHandler: handle_gallery_click(evt.index)
    
    I2IHandler->>I2IHandler: Get selected image from self.uploaded_images[evt.index]
    alt Multi-image workflow
        I2IHandler->>I2IHandler: Selected = background, others = objects
        I2IHandler->>I2IHandler: Get first other image as object
        I2IHandler-->>UI: Update states (background, object, canvas)
        UI-->>User: Show selected background + object context
    else Single image workflow
        I2IHandler->>I2IHandler: Selected = background, no object
        I2IHandler-->>UI: Update states (background only)
        UI-->>User: Show selected image for editing
    end
```

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio UI
    participant GenManager as Generation Manager
    participant StyleTransfer as Style Transfer
    participant Vision as Vision Model

    Note over User, Vision: Prompt Analysis and Enhancement System

    User->>UI: Enter prompt text
    UI->>GenManager: _process_prompt_for_pro_model(prompt)
    
    GenManager->>GenManager: Check for auto-prompt indicators
    Note right of GenManager: Search for: "based on", "analyzing", "I can see"<br/>"looking at", "appears to", "seems to be"
    
    alt Manual Prompt Detected (no indicators)
        GenManager->>GenManager: is_manual_prompt = True
        GenManager->>GenManager: Log: "Manual prompt detected, skipping enhancement"
        GenManager-->>UI: Return original prompt unchanged
        
    else Auto-Generated Prompt (indicators found)
        GenManager->>GenManager: is_manual_prompt = False
        GenManager->>GenManager: Check style_mode setting
        
        alt Style Enhancement Enabled
            GenManager->>StyleTransfer: enhance_prompt(prompt, style_mode)
            
            StyleTransfer->>StyleTransfer: Load style keywords from config
            StyleTransfer->>StyleTransfer: Apply style-specific enhancements
            alt style_mode == "style-only"
                StyleTransfer->>StyleTransfer: Focus on artistic elements
                StyleTransfer-->>GenManager: Enhanced style prompt
            else style_mode == "selective"  
                StyleTransfer->>StyleTransfer: Balance content + style
                StyleTransfer-->>GenManager: Balanced enhanced prompt
            else style_mode == "enhance"
                StyleTransfer->>StyleTransfer: Full content enhancement
                StyleTransfer-->>GenManager: Fully enhanced prompt
            end
            
            GenManager->>GenManager: Log enhanced prompt details
            GenManager-->>UI: Return style-enhanced prompt
            
        else Style Enhancement Disabled
            GenManager->>GenManager: Log: "Auto-prompt without style enhancement"
            GenManager-->>UI: Return original auto-prompt
        end
    end

    Note over User, Vision: Vision Analysis Integration
    
    alt Vision Analysis Required
        User->>UI: Click "Auto-Generate Prompt" 
        UI->>Vision: analyze_image_region(background, object, provider)
        
        Vision->>Vision: Convert images to base64
        Vision->>Qwen-VL-Max: Send analysis request with context
        Qwen-VL-Max-->>Vision: Return analysis ("bottle on wooden surface")
        Vision-->>GenManager: Auto-generated prompt with indicators
        
        GenManager->>GenManager: Detect auto-prompt indicators
        GenManager->>GenManager: Process through style enhancement if enabled
        GenManager-->>UI: Final processed prompt
    end
```

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio UI
    participant GenManager as Generation Manager
    participant Generator as FLUX Generator
    participant Utils as Image Utils
    participant Storage as Secure Storage

    Note over User, Storage: Pro API Multi-Image Generation Strategy

    User->>UI: Select images from gallery
    User->>UI: Enter prompt (manual or auto-generated)
    User->>UI: Set generation parameters
    User->>UI: Click "Generate"
    
    UI->>GenManager: run_main_generation(images, prompt, settings)
    GenManager->>GenManager: Validate inputs and settings
    GenManager->>Storage: load_api_key(FLUX_PRO_API)
    Storage-->>GenManager: API key
    
    GenManager->>Utils: merge_images_with_smart_scaling(images)
    Note right of Utils: Reduced gap layout: 2px spacing<br/>Better integration for FLUX Kontext
    Utils->>Utils: Calculate optimal scaling for merged dimensions
    Utils->>Utils: Create side-by-side layout with 2px gaps
    Utils-->>GenManager: Merged input image
    
    GenManager->>GenManager: Apply "Match Input + post-resize" strategy
    GenManager->>GenManager: Override target dimensions to match merged input
    Note right of GenManager: Force dimensions = merged_image.size<br/>Prevents duplicate object issues
    
    GenManager->>Generator: generate_with_pro_api(merged_image, prompt, "Match Input")
    Generator->>Generator: Build Pro API request
    Generator->>FLUX_API: POST /v1/flux-kontext-pro
    Note right of FLUX_API: Request includes:<br/>• input_image (merged)<br/>• prompt (processed)<br/>• width/height (match input)<br/>• steps, guidance, num_images
    
    FLUX_API-->>Generator: Generated image URL(s)
    Generator->>Generator: Download images from URLs
    Generator->>Generator: Validate image quality
    
    alt Post-Generation Resize Required
        Generator->>Generator: Check if resize needed for target output
        Generator->>Utils: resize_image(generated, target_size)
        Utils-->>Generator: Resized final image
    end
    
    Generator-->>GenManager: Final generated images
    GenManager->>Utils: save_image(result, GENERATION_TYPE)
    Utils-->>GenManager: Saved file path with timestamp
    GenManager-->>UI: Display final results
    UI-->>User: Show generated images in gallery

    Note over User, Storage: Debug Logging Throughout
    GenManager->>GenManager: Log input dimensions
    GenManager->>GenManager: Log merged image properties  
    GenManager->>GenManager: Log Pro API request details
    GenManager->>GenManager: Log generation success/failure
```

```mermaid
sequenceDiagram
    participant User
    participant Utils as Image Utils
    participant PIL as PIL Image
    participant Logging as Debug Logger

    Note over User, Logging: Smart Scaling and Reduced Gap Layout

    Utils->>Utils: merge_images_with_smart_scaling(image_list)
    Utils->>Logging: Log input image count and dimensions
    
    Utils->>Utils: Calculate individual image dimensions
    loop For each image in image_list
        Utils->>PIL: Open and get image.size
        Utils->>Utils: Track max_width, total_height
    end
    
    Utils->>Utils: Calculate scaling factor
    Note right of Utils: Scale to fit within reasonable bounds<br/>while preserving aspect ratios
    Utils->>Utils: target_width = min(max_width * scale, MAX_WIDTH)
    
    Utils->>Utils: Create merged canvas
    Utils->>PIL: new_image = Image.new('RGB', canvas_size, 'white')
    
    Utils->>Utils: Apply reduced gap layout (2px spacing)
    Note right of Utils: Previous: 10px gaps caused integration issues<br/>Current: 2px gaps for better FLUX Kontext results
    
    loop For each image
        Utils->>PIL: Resize image to calculated dimensions
        Utils->>PIL: Paste at position with 2px vertical gap
        Utils->>Utils: Update y_offset += scaled_height + 2
    end
    
    Utils->>Logging: Log final merged dimensions
    Utils->>Logging: Log scaling factor applied
    Utils-->>Utils: Return optimized merged image

    Note over User, Logging: Quality Validation
    Utils->>Utils: Validate merged image quality
    Utils->>Utils: Check for reasonable dimensions (not too large/small)
    Utils->>Utils: Verify all images successfully merged
```

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio UI
    participant GenManager as Generation Manager
    participant Generator as FLUX Generator
    participant Utils as Image Utils
    participant Storage as Secure Storage
    participant ErrorHandler as Error Handler

    Note over User, ErrorHandler: End-to-End Generation with Comprehensive Error Handling

    User->>UI: Complete generation request
    UI->>GenManager: run_main_generation(params)
    
    GenManager->>GenManager: Validate all inputs
    alt Validation Failed
        GenManager->>ErrorHandler: Log validation error
        GenManager-->>UI: Return error message
        UI-->>User: Display validation error
    end
    
    GenManager->>GenManager: Process prompt (manual vs auto detection)
    GenManager->>Storage: load_api_key(selected_model)
    alt API Key Missing
        GenManager->>ErrorHandler: Log missing API key
        GenManager-->>UI: Return "API key not configured" error
        UI-->>User: Display configuration error
    end
    
    GenManager->>Utils: merge_images_with_smart_scaling(images)
    alt Image Merge Failed
        Utils->>ErrorHandler: Log merge failure details
        Utils-->>GenManager: Return None
        GenManager-->>UI: Return merge error
        UI-->>User: Display image processing error
    end
    
    GenManager->>Generator: generate_images(merged_input, processed_prompt, settings)
    
    alt Local Model Generation
        Generator->>Generator: Load local FLUX model
        alt Model Load Failed
            Generator->>ErrorHandler: Log model load error
            Generator-->>GenManager: Return error result
        else Model Load Success
            Generator->>FLUX_Local: Generate with pipeline
            alt Generation Failed
                FLUX_Local->>ErrorHandler: Log generation error
                FLUX_Local-->>Generator: Return None
            else Generation Success
                FLUX_Local-->>Generator: Return generated images
            end
        end
        
    else Pro API Generation  
        Generator->>Generator: Build API request with "Match Input" dimensions
        Generator->>FLUX_API: POST /v1/flux-kontext-pro
        alt API Request Failed
            FLUX_API->>ErrorHandler: Log HTTP error (timeout, 429, 500, etc.)
            FLUX_API-->>Generator: Return error response
            Generator->>Generator: Parse error details
            Generator-->>GenManager: Return API error
        else API Request Success
            FLUX_API-->>Generator: Return image URLs
            Generator->>Generator: Download images with retry logic
            alt Download Failed
                Generator->>ErrorHandler: Log download failure
                Generator-->>GenManager: Return download error
            else Download Success
                Generator-->>GenManager: Return final images
            end
        end
    end
    
    alt Generation Success
        GenManager->>Utils: save_image(results, timestamp)
        Utils->>Utils: Create outputs directory if needed
        Utils->>Utils: Save with unique filename
        Utils-->>GenManager: Return saved file paths
        
        GenManager->>GenManager: Log generation success
        GenManager-->>UI: Return results with file paths
        UI-->>User: Display generated images
        
    else Generation Failed
        GenManager->>ErrorHandler: Log complete failure context
        GenManager-->>UI: Return user-friendly error message
        UI-->>User: Display error with suggested actions
    end

    Note over User, ErrorHandler: Comprehensive Debugging Context
    ErrorHandler->>ErrorHandler: Track all error types and frequencies
    ErrorHandler->>ErrorHandler: Provide detailed logs for troubleshooting
    ErrorHandler->>ErrorHandler: Suggest user actions for common errors
```

```mermaid
sequenceDiagram
    participant UI as Gradio UI
    participant I2IHandler as I2I Handler
    participant GenManager as Generation Manager
    participant CanvasManager as Canvas Manager
    participant StyleTransfer as Style Transfer
    participant Storage as Secure Storage

    Note over UI, Storage: Streamlined Handler Architecture

    UI->>I2IHandler: User interactions (uploads, clicks, generation)
    I2IHandler->>I2IHandler: Maintain session state
    Note right of I2IHandler: Tracks: uploaded_images, background_state<br/>object_state, canvas_state, selection_coords
    
    alt Multi-Image Upload Operations
        I2IHandler->>I2IHandler: handle_multi_image_upload(files)
        I2IHandler->>I2IHandler: handle_gallery_click(selection)
        I2IHandler->>CanvasManager: update_canvas_states(background, object)
        CanvasManager-->>I2IHandler: Updated canvas preview
    end
    
    alt Generation Operations
        I2IHandler->>GenManager: run_main_generation(params)
        GenManager->>GenManager: _process_prompt_for_pro_model(prompt)
        
        alt Style Enhancement Required
            GenManager->>StyleTransfer: enhance_prompt(prompt, style_mode)
            StyleTransfer-->>GenManager: Enhanced prompt
        end
        
        GenManager->>GenManager: Execute generation workflow
        GenManager-->>I2IHandler: Generation results
    end
    
    alt Configuration Management
        I2IHandler->>Storage: load_api_key(model_type)
        Storage-->>I2IHandler: Decrypted API key
        I2IHandler->>Storage: save_api_key(key, model_type)
        Storage->>Storage: Encrypt and store securely
    end
    
    Note over UI, Storage: State Persistence and Memory Management
    I2IHandler->>I2IHandler: Clean up temporary images
    I2IHandler->>I2IHandler: Manage memory usage for large image sets
    I2IHandler->>I2IHandler: Preserve user selections across operations
    
    alt Session Reset
        I2IHandler->>I2IHandler: clear_session_state()
        I2IHandler->>CanvasManager: reset_canvas_states()
        I2IHandler->>I2IHandler: Clear uploaded_images cache
    end
```

## Technical Implementation Notes

### Current System Capabilities
- **Multi-Image Upload**: Supports up to 10 images with gallery selection interface
- **Manual Prompt Detection**: Automatically detects user-written vs AI-generated prompts
- **Style Transfer Integration**: Optional prompt enhancement with multiple style modes
- **Pro API Optimization**: "Match Input + post-resize" strategy for reliable multi-image generation
- **Reduced Gap Layout**: 2px spacing for better FLUX Kontext integration
- **Comprehensive Error Handling**: Detailed logging and user-friendly error messages
- **Secure API Management**: Encrypted storage for API keys with automatic loading

### Key Technical Decisions
1. **Manual vs Auto-Prompt Detection**: Prevents accidental enhancement of user-written prompts
2. **"Match Input" Dimensions**: Eliminates duplicate object issues in Pro API generation  
3. **Reduced Gap Merging**: 2px spacing improves AI model integration vs previous 10px gaps
4. **Handler Separation**: Focused responsibilities - I2I for UI state, GenManager for processing
5. **Comprehensive Debugging**: Extensive logging throughout pipeline for troubleshooting

### Performance Optimizations
- Smart image scaling to prevent oversized merged images
- Memory management for large image sets
- Retry logic for API requests and downloads
- Efficient state management across multi-image workflows
- Cached processed images to avoid redundant operations

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio UI
    participant I2IHandler as I2I Handler
    participant Generator as FLUX Generator
    participant Utils as Image Utils
    participant Storage as Secure Storage

    Note over User, Storage: Create Mode - Object to Scene Generation

    User->>UI: Skip background upload (Create Mode)
    User->>UI: Upload object image(s)
    UI->>I2IHandler: store_object(object_image)
    I2IHandler->>I2IHandler: Show CREATE MODE placeholder canvas
    I2IHandler-->>UI: Object preview in placeholder
    
    User->>UI: Enter prompt describing desired scene
    Note right of User: "Place this object on a wooden table in a kitchen"
    User->>UI: Adjust settings (steps, guidance, etc.)
    User->>UI: Click "Generate"
    
    UI->>I2IHandler: run_i2i(source=None, object, prompt, settings)
    I2IHandler->>I2IHandler: Detect Create Mode (source_image is None)
    I2IHandler->>Storage: load_api_key(FLUX_PRO_API)
    Storage-->>I2IHandler: API key
    
    alt Object Image Provided
        Note over I2IHandler: Future enhancement: Object composition
        I2IHandler->>Generator: text_to_image(prompt, settings)
        
        alt Local Model Selected
            Generator->>FLUX_Local: pipeline(prompt, steps=28, guidance=4.0, num_images)
            Note right of FLUX_Local: Model: black-forest-labs/FLUX.1-Kontext-dev
            FLUX_Local-->>Generator: Generated scene with object
        else Pro Model Selected
            Generator->>FLUX_API: POST /v1/flux-kontext-pro
            Note right of FLUX_API: Model: flux-1-kontext-pro<br/>Include: prompt, steps, guidance, num_images
            FLUX_API-->>Generator: Generated image URLs
            Generator->>Generator: Download images from URLs
        end
        
        Generator-->>I2IHandler: Result images
    else Text Only
        I2IHandler->>Generator: text_to_image(prompt, settings)
        
        alt Local Model Selected
            Generator->>FLUX_Local: pipeline(prompt, steps=28, guidance=4.0, num_images)
            FLUX_Local-->>Generator: Generated images
        else Pro Model Selected
            Generator->>FLUX_API: POST /v1/flux-kontext-pro
            FLUX_API-->>Generator: Generated image URLs
            Generator->>Generator: Download images from URLs
        end
        
        Generator-->>I2IHandler: Result images
    end
    
    I2IHandler->>Utils: save_image(result, T2I_TYPE)
    Utils-->>I2IHandler: Saved file path
    I2IHandler-->>UI: Display generated images
    UI-->>User: Show results
```

## 1b. Multi-Object Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio UI
    participant I2IHandler as I2I Handler
    participant Utils as Image Utils
    participant Generator as FLUX Generator
    participant FLUX_Local as Local FLUX Pipeline
    participant FLUX_API as FLUX Kontext Pro API
    participant Vision as Vision Model
    participant Storage as Secure Storage

    Note over User, Storage: Multiple Object Handling

    User->>UI: Upload background image
    User->>UI: Upload first object image
    UI->>I2IHandler: store_object(object1)
    I2IHandler->>Utils: merge_multiple_images_high_quality([background, object1])
    Utils-->>I2IHandler: Merged canvas (2 images side-by-side)
    I2IHandler-->>UI: Display merged canvas
    
    User->>UI: Upload additional object image
    UI->>I2IHandler: store_object(object2) 
    Note right of I2IHandler: Current implementation replaces object1 with object2<br/>Future: Support multiple objects simultaneously
    I2IHandler->>Utils: merge_multiple_images_high_quality([background, object2])
    Utils-->>I2IHandler: Updated merged canvas (background + object2)
    I2IHandler-->>UI: Display updated canvas
    
    User->>UI: Click twice to select area
    UI->>I2IHandler: Selection coordinates (top_left, bottom_right)
    
    alt Auto-Generate Prompt (Optional)
        User->>UI: Click "Auto-Generate Prompt"
        UI->>I2IHandler: auto_generate_prompt()
        I2IHandler->>Vision: analyze_image_region(background, final_object, provider)
        Vision-->>I2IHandler: Surface description
        I2IHandler-->>UI: Generated prompt with surface info
    end
    
    User->>UI: Enter/edit prompt text
    Note right of User: User must provide prompt describing<br/>what to do with the object
    User->>UI: Adjust settings (steps, guidance, etc.)
    User->>UI: Click "Generate"
    
    UI->>I2IHandler: run_i2i(background, final_object, prompt, settings)
    I2IHandler->>I2IHandler: Validate inputs and truncate prompt
    I2IHandler->>Storage: load_api_key(FLUX_PRO_API)
    Storage-->>I2IHandler: API key
    
    I2IHandler->>Utils: merge_multiple_images_high_quality([background, final_object])
    Utils-->>I2IHandler: Merged canvas image
    I2IHandler->>UI: update_canvas_with_merge(merged_image)
    
    alt Local Model Selected
        I2IHandler->>Generator: image_to_image(merged_canvas, prompt, settings)
        Generator->>FLUX_Local: kontext_pipeline(image, prompt, steps=28, guidance=3.0)
        Note right of FLUX_Local: Model: FLUX.1-Kontext-dev + Nunchaku
        FLUX_Local-->>Generator: Edited images
    else Pro Model Selected
        I2IHandler->>Generator: image_to_image(merged_canvas, prompt, settings)
        Generator->>FLUX_API: POST /v1/flux-kontext-pro
        Note right of FLUX_API: Model: flux-1-kontext-pro<br/>Include: prompt, input_image, steps, guidance
        FLUX_API-->>Generator: Edited image URLs
        Generator->>Generator: Download images from URLs
    end
    
    Generator-->>I2IHandler: Generated result
    I2IHandler->>Utils: save_image(result, I2I_TYPE)
    Utils-->>I2IHandler: Saved file path
    I2IHandler-->>UI: Display result
    UI-->>User: Show final image with object modifications
```

## 2. Vision Analysis Workflow (Detailed)

```mermaid
sequenceDiagram
    participant I2IHandler as I2I Handler
    participant Vision as Vision Module
    participant QwenVL as Qwen-VL-Max API
    participant Utils as Image Utils

    Note over I2IHandler, Utils: Vision-Based Surface Analysis

    I2IHandler->>Vision: analyze_image_region(bg_image, obj_image, provider, api_key)
    Vision->>Vision: Convert background image to base64
    
    alt Object Image Provided
        Vision->>Vision: Convert object image to base64
        Vision->>Vision: Build dual-image prompt (background + object)
        Note right of Vision: Prompt: "Describe SURFACE TYPE only<br/>Format: 'on the [surface type]'<br/>Examples: 'on the wooden surface'"
    else Surface Analysis Only
        Vision->>Vision: Build single-image prompt (background only)
        Note right of Vision: Prompt: "Describe SURFACE MATERIAL only<br/>DO NOT mention rooms or furniture"
    end
    
    Vision->>QwenVL: POST /compatible-mode/v1/chat/completions
    Note right of QwenVL: OpenAI-compatible endpoint<br/>Model: qwen-vl-max<br/>Max tokens: 300
    
    QwenVL-->>Vision: Response with surface description
    Vision->>Vision: Extract placement description from response
    Vision->>Vision: Clean up and format ("on wooden surface")
    Vision-->>I2IHandler: Final surface description
```

## 3. Image Generation Workflow (FLUX Models)

```mermaid
sequenceDiagram
    participant I2IHandler as I2I Handler
    participant Generator as Generator
    participant FLUX_Local as Local FLUX Pipeline
    participant FLUX_API as FLUX Kontext Pro API
    participant Storage as File Storage

    Note over I2IHandler, Storage: Image Generation Process

    I2IHandler->>Generator: text_to_image() OR image_to_image()
    
    alt Local Model Selected
        Generator->>Generator: _load_local_pipeline()
        Note right of Generator: T2I: FLUX.1-Kontext-dev<br/>I2I: FLUX.1-Kontext-dev + Nunchaku
        Generator->>FLUX_Local: Initialize FluxPipeline/FluxKontextPipeline
        FLUX_Local-->>Generator: Pipeline ready
        
        alt Text-to-Image
            Generator->>FLUX_Local: pipeline(prompt, steps=28, guidance=4.0, num_images)
            Note right of FLUX_Local: Model: black-forest-labs/FLUX.1-Kontext-dev
            FLUX_Local-->>Generator: Generated images
        else Image-to-Image
            Generator->>FLUX_Local: kontext_pipeline(image, prompt, steps=28, guidance=3.0)
            Note right of FLUX_Local: Model: FLUX.1-Kontext-dev + Nunchaku transformer<br/>mit-han-lab/nunchaku-flux.1-kontext-dev
            FLUX_Local-->>Generator: Edited images
        end
        
    else Pro Model Selected
        Generator->>Generator: Prepare API payload with base64 image
        
        alt Text-to-Image (Pro)
            Generator->>FLUX_API: POST /v1/flux-kontext-pro
            Note right of FLUX_API: Model: flux-1-kontext-pro<br/>Include: prompt, steps, guidance, num_images
            FLUX_API-->>Generator: Generated image URLs
        else Image-to-Image (Pro)
            Generator->>FLUX_API: POST /v1/flux-kontext-pro
            Note right of FLUX_API: Model: flux-1-kontext-pro<br/>Include: prompt, input_image, steps, guidance
            FLUX_API-->>Generator: Edited image URLs
        end
        
        Generator->>Generator: Download images from URLs
    end
    
    Generator-->>I2IHandler: PIL Image objects
    I2IHandler->>Storage: save_image(images, type, timestamp)
    Storage-->>I2IHandler: Saved file paths
```

## 4. UI Canvas Update Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio Interface
    participant I2IHandler as I2I Handler
    participant Utils as Image Utils

    Note over User, Utils: Complete Canvas Management Workflow

    %% Initial Canvas Setup
    alt Create Mode (No Background)
        User->>UI: Skip background upload
        UI->>I2IHandler: store_background(img=None)
        I2IHandler->>I2IHandler: _redraw_canvas(None, None, None, None)
        I2IHandler->>I2IHandler: Create CREATE MODE placeholder (512x512)
        I2IHandler->>I2IHandler: Draw dashed borders and instructions
        I2IHandler-->>UI: Placeholder canvas with "CREATE MODE" text
        UI-->>User: Show placeholder canvas
    else Edit Mode (Background Uploaded)
        User->>UI: Upload background image
        UI->>I2IHandler: store_background(background_img)
        I2IHandler->>I2IHandler: Detect Edit Mode
        I2IHandler-->>UI: Background canvas + enable area selection
        UI-->>User: Show background image ready for editing
    end

    %% Object Upload and Canvas Merge
    alt Object Image Added
        User->>UI: Upload object image
        UI->>I2IHandler: store_object(object_img)
        
        alt Edit Mode with Background
            I2IHandler->>Utils: merge_multiple_images_high_quality([background, object])
            Utils->>Utils: Resize to same height using LANCZOS
            Utils->>Utils: Create side-by-side horizontal layout
            Utils-->>I2IHandler: Merged canvas image
            I2IHandler-->>UI: update_canvas_with_merge(merged_canvas)
            UI-->>User: Show merged view (background | object)
        else Create Mode
            I2IHandler->>I2IHandler: _redraw_canvas(None, object, None, None)
            I2IHandler->>I2IHandler: Show object preview in placeholder
            I2IHandler->>I2IHandler: Add object preview with white border
            I2IHandler-->>UI: Placeholder with object preview
            UI-->>User: Show CREATE MODE canvas with object
        end
    end

    %% Area Selection Process
    User->>UI: Click on canvas (first click)
    UI->>I2IHandler: handle_canvas_click(click_coords, current_state)
    I2IHandler->>I2IHandler: Validate click coordinates
    I2IHandler->>I2IHandler: Apply edge tolerance and snapping
    I2IHandler->>I2IHandler: Store top_left coordinates
    I2IHandler-->>UI: Status: "Selection started at (x, y)"
    
    User->>UI: Click on canvas (second click)
    UI->>I2IHandler: handle_canvas_click(click_coords, current_state)
    I2IHandler->>I2IHandler: Store bottom_right coordinates
    I2IHandler->>I2IHandler: Calculate selection area dimensions
    I2IHandler->>I2IHandler: Ensure minimum box size (10x10 pixels)
    I2IHandler-->>UI: Status: "Selection completed! Area: WxH pixels"
    
    %% Canvas Redraw with Selection Box
    I2IHandler->>I2IHandler: _redraw_canvas(base_img, obj_img, top_left, bottom_right)
    
    alt Background + Object Available
        I2IHandler->>Utils: merge_multiple_images_high_quality([bg, obj])
        Utils-->>I2IHandler: Merged canvas
        I2IHandler->>Utils: draw_selection_box(canvas, coords, alpha=20)
        Note right of Utils: Transparent blue rectangle<br/>Color: (0, 100, 255, 20)
        Utils-->>I2IHandler: Canvas with transparent selection overlay
        I2IHandler-->>UI: update_canvas_with_merge(canvas_with_selection)
    else Background Only
        I2IHandler->>Utils: draw_selection_box(bg_image, coords, alpha=20)
        Utils-->>I2IHandler: Background with selection box
        I2IHandler-->>UI: Updated canvas
    else Create Mode
        I2IHandler->>I2IHandler: Show placeholder with selection indicators
        I2IHandler-->>UI: CREATE MODE canvas (no selection box)
    end
    
    %% Reset Selection
    alt User Resets Selection
        User->>UI: Click "Reset Selection" button
        UI->>I2IHandler: reset_selection()
        I2IHandler->>I2IHandler: Clear top_left and bottom_right
        I2IHandler->>I2IHandler: _redraw_canvas(base_img, obj_img, None, None)
        I2IHandler-->>UI: Canvas without selection box
        I2IHandler-->>UI: Status: "Ready to select areas 🎯"
        UI-->>User: Clean canvas ready for new selection
    end
    
    UI-->>User: Display final updated canvas
```

## 4a. Canvas State Management

```mermaid
sequenceDiagram
    participant UI as Gradio Interface
    participant I2IHandler as I2I Handler
    participant Utils as Image Utils

    Note over UI, Utils: Canvas State Transitions

    %% State: Empty
    UI->>I2IHandler: Initial state (no uploads)
    I2IHandler-->>UI: Empty canvas placeholder
    
    %% State: Background Only
    UI->>I2IHandler: store_background(background_img)
    I2IHandler->>I2IHandler: Enable Edit Mode features
    I2IHandler-->>UI: Background canvas + selection tools
    
    %% State: Object Only (Create Mode)
    UI->>I2IHandler: store_object(object_img) [no background]
    I2IHandler->>I2IHandler: _redraw_canvas(None, object, None, None)
    I2IHandler-->>UI: CREATE MODE placeholder with object preview
    
    %% State: Background + Object (Edit Mode)
    UI->>I2IHandler: store_object(object_img) [with background]
    I2IHandler->>Utils: merge_multiple_images_high_quality([bg, obj])
    Utils-->>I2IHandler: Side-by-side merged canvas
    I2IHandler-->>UI: Merged view for AI processing
    
    %% State: With Selection
    UI->>I2IHandler: handle_canvas_click() [second click]
    I2IHandler->>Utils: draw_selection_box(canvas, coords, alpha=20)
    Utils-->>I2IHandler: Canvas with transparent selection overlay
    I2IHandler-->>UI: Final canvas with selection visualization
```

## 5. API Key Management Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Settings UI
    participant SecureStorage as Secure Storage
    participant Filesystem as File System

    Note over User, Filesystem: Encrypted API Key Storage

    User->>UI: Enter API key in settings
    UI->>SecureStorage: save_api_key(provider_name, api_key)
    SecureStorage->>SecureStorage: load_or_generate_key()
    
    alt Key file exists
        SecureStorage->>Filesystem: Read secret.key
        Filesystem-->>SecureStorage: Encryption key
    else First time setup
        SecureStorage->>SecureStorage: Generate new Fernet key
        SecureStorage->>Filesystem: Write secret.key
        Filesystem-->>SecureStorage: Key saved
    end
    
    SecureStorage->>SecureStorage: Encrypt API key with Fernet
    SecureStorage->>Filesystem: Update api_keys.json.enc
    Filesystem-->>SecureStorage: Encrypted data saved
    SecureStorage-->>UI: Success confirmation
    
    Note over User, Filesystem: API Key Retrieval
    
    I2IHandler->>SecureStorage: load_api_key(provider_name)
    SecureStorage->>Filesystem: Read api_keys.json.enc
    Filesystem-->>SecureStorage: Encrypted data
    SecureStorage->>SecureStorage: Decrypt with stored key
    SecureStorage-->>I2IHandler: Decrypted API key
```

## 6. Complete PhotoGen Application Workflow

```mermaid
graph TB
    %% User Interface Layer
    subgraph UI_LAYER ["User Interface Layer"]
        direction TB
        subgraph UI_COMPONENTS ["Gradio Web Interface"]
            UI[Main Interface]
            BG_UP[Background Upload]
            OBJ_UP[Object Upload]
            CANVAS[Interactive Canvas]
            PROMPT[Prompt Input]
            SETTINGS[Model Settings]
            GENERATE[Generate Button]
            RESULTS[Results Display]
        end
        
        subgraph OUTPUT_CONTROLS ["Output Parameter Controls"]
            NUM_IMAGES[Number of Images<br/>Slider: 1-4]
            ASPECT_RATIO[Image Dimensions<br/>Match Input, 1:1, 16:9, etc.]
            STEPS[Inference Steps<br/>Slider: 1-50, Default: 20]
            GUIDANCE[Guidance Scale<br/>Slider: 0-10, Default: 3.0]
            MODEL_SELECT[Model Selection<br/>Local vs Pro API]
        end
    end
    
    %% Core Application Layer
    subgraph CORE_LAYER ["Core Application Layer"]
        direction TB
        subgraph HANDLERS ["Request Handlers"]
            I2I_H[I2I Handler<br/>Main Orchestrator]
            DEMO_H[Demo Handler<br/>Showcase Features]
            T2I_H[T2I Handler<br/>Text Generation]
        end
        
        subgraph CORE_MODULES ["Core Processing Modules"]
            VISION[Vision Module<br/>Surface Analysis]
            GEN[Generator Module<br/>FLUX Interface]
            UTILS[Image Utils<br/>Merge & Processing]
            STORAGE[Secure Storage<br/>API Key Management]
            UI_CORE[UI Core<br/>Interface Builder]
        end
        
        subgraph CONFIG_LAYER ["Configuration Management"]
            CONFIG[config.yaml<br/>Model Settings]
            CONST[Constants<br/>API Endpoints]
        end
    end
    
    %% External Services Layer
    subgraph EXTERNAL_LAYER ["External AI Services"]
        direction LR
        QWEN[Qwen-VL-Max API<br/>Vision Analysis<br/>Alibaba Cloud]
        FLUX_API[FLUX Kontext Pro API<br/>Cloud Generation<br/>Professional Models]
    end
    
    %% Local AI Layer
    subgraph LOCAL_LAYER ["Local AI Models"]
        direction LR
        FLUX_LOCAL[FLUX.1-Kontext-dev<br/>Local Generation<br/>Hugging Face]
        NUNCHAKU[Nunchaku Optimizer<br/>I2I Enhancement<br/>MIT Han Lab]
    end
    
    %% File System Layer
    subgraph STORAGE_LAYER ["Persistent Storage"]
        direction LR
        API_KEYS[api_keys.json.enc<br/>Encrypted API Keys]
        SECRET[secret.key<br/>Encryption Master Key]
        OUTPUTS[outputs Directory<br/>Generated Images]
    end
    
    %% Primary User Flow - Main path only
    UI --> I2I_H
    GENERATE --> I2I_H
    
    %% Output Parameter Flow - User controls
    STEPS --> I2I_H
    GUIDANCE --> I2I_H
    NUM_IMAGES --> I2I_H
    ASPECT_RATIO --> I2I_H
    MODEL_SELECT --> I2I_H
    
    %% Core Processing Flow - Essential connections only
    I2I_H --> VISION
    I2I_H --> GEN
    I2I_H --> UTILS
    
    %% External Service Connections - Key integrations
    VISION ==> QWEN
    GEN ==> FLUX_API
    GEN ==> FLUX_LOCAL
    
    %% Storage Operations - Essential data persistence
    I2I_H -.-> STORAGE
    STORAGE -.-> API_KEYS
    UTILS -.-> OUTPUTS
    
    %% Results Flow - Final output path
    GEN --> I2I_H
    I2I_H --> RESULTS
    
    %% Configuration Access - Minimal config connections
    GEN -.-> CONFIG
    
    %% Advanced Styling with Better Color Palette
    classDef uiStyle fill:#E3F2FD,stroke:#1565C0,stroke-width:3px,color:#0D47A1
    classDef handlerStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px,color:#4A148C
    classDef coreStyle fill:#E8F5E8,stroke:#2E7D32,stroke-width:3px,color:#1B5E20
    classDef configStyle fill:#FFF3E0,stroke:#F57C00,stroke-width:2px,color:#E65100
    classDef externalStyle fill:#FFEBEE,stroke:#C62828,stroke-width:3px,color:#B71C1C
    classDef localStyle fill:#E0F2F1,stroke:#00695C,stroke-width:3px,color:#004D40
    classDef storageStyle fill:#FCE4EC,stroke:#AD1457,stroke-width:2px,color:#880E4F
    classDef layerStyle fill:#F5F5F5,stroke:#616161,stroke-width:2px,color:#424242
    
    %% Apply Styles to Components
    class UI,BG_UP,OBJ_UP,CANVAS,PROMPT,SETTINGS,GENERATE,RESULTS uiStyle
    class NUM_IMAGES,ASPECT_RATIO,STEPS,GUIDANCE,MODEL_SELECT configStyle
    class I2I_H,DEMO_H,T2I_H handlerStyle
    class VISION,GEN,UTILS,UI_CORE coreStyle
    class STORAGE storageStyle
    class CONFIG,CONST configStyle
    class QWEN,FLUX_API externalStyle
    class FLUX_LOCAL,NUNCHAKU localStyle
    class API_KEYS,SECRET,OUTPUTS storageStyle
    class UI_LAYER,CORE_LAYER,EXTERNAL_LAYER,LOCAL_LAYER,STORAGE_LAYER layerStyle
```

## 6a. Mode-Based Workflow Decision Tree

```mermaid
flowchart TD
    START([User Starts PhotoGen]) --> UPLOAD_BG{Upload Background?}
    
    UPLOAD_BG -->|Yes| EDIT_MODE[Edit Mode Activated]
    UPLOAD_BG -->|No| CREATE_MODE[Create Mode Activated]
    
    %% Edit Mode Path
    EDIT_MODE --> UPLOAD_OBJ{Upload Object?}
    UPLOAD_OBJ -->|Yes| MERGE_CANVAS[Merge Canvas<br/>Background | Object]
    UPLOAD_OBJ -->|No| BG_ONLY[Background Only Canvas]
    
    MERGE_CANVAS --> SELECT_AREA[Select Area on Canvas]
    BG_ONLY --> SELECT_AREA
    
    SELECT_AREA --> AUTO_PROMPT{Use Auto-Prompt?}
    AUTO_PROMPT -->|Yes| VISION_ANALYSIS[Vision Surface Analysis]
    AUTO_PROMPT -->|No| MANUAL_PROMPT[Manual Prompt Entry]
    
    VISION_ANALYSIS --> ENHANCED_PROMPT[Enhanced Prompt with Surface Info]
    MANUAL_PROMPT --> USER_PROMPT[User-Written Prompt]
    ENHANCED_PROMPT --> EDIT_GENERATE[I2I Generation]
    USER_PROMPT --> EDIT_GENERATE
    
    EDIT_GENERATE --> MODEL_CHOICE{Model Choice?}
    MODEL_CHOICE -->|Local| LOCAL_I2I[Local FLUX + Nunchaku]
    MODEL_CHOICE -->|Pro API| API_I2I[FLUX Kontext Pro API]
    
    %% Create Mode Path
    CREATE_MODE --> CREATE_OBJ{Upload Object?}
    CREATE_OBJ -->|Yes| OBJ_PREVIEW[Object Preview in Placeholder]
    CREATE_OBJ -->|No| TEXT_ONLY[Text-Only Generation]
    
    OBJ_PREVIEW --> CREATE_AUTO_PROMPT{Use Auto-Prompt?}
    TEXT_ONLY --> CREATE_AUTO_PROMPT
    
    CREATE_AUTO_PROMPT -->|Yes| CREATE_VISION[Vision Analysis for Context]
    CREATE_AUTO_PROMPT -->|No| SCENE_PROMPT[Manual Scene Description]
    
    CREATE_VISION --> ENHANCED_SCENE[Enhanced Scene Prompt]
    SCENE_PROMPT --> USER_SCENE[User Scene Prompt]
    ENHANCED_SCENE --> CREATE_GENERATE[T2I Generation]
    USER_SCENE --> CREATE_GENERATE
    
    CREATE_GENERATE --> CREATE_MODEL{Model Choice?}
    CREATE_MODEL -->|Local| LOCAL_T2I[Local FLUX.1-Kontext-dev]
    CREATE_MODEL -->|Pro API| API_T2I[FLUX Kontext Pro API]
    
    %% Results
    LOCAL_I2I --> SAVE_RESULT[Save to outputs/]
    API_I2I --> SAVE_RESULT
    LOCAL_T2I --> SAVE_RESULT
    API_T2I --> SAVE_RESULT
    
    SAVE_RESULT --> DISPLAY[Display Results to User]
    DISPLAY --> CONTINUE{Continue?}
    CONTINUE -->|Yes| UPLOAD_BG
    CONTINUE -->|No| END([Session End])
    
    %% Styling
    classDef mode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef process fill:#f1f8e9,stroke:#388e3c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef generation fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef endpoint fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class EDIT_MODE,CREATE_MODE mode
    class MERGE_CANVAS,BG_ONLY,SELECT_AREA,VISION_ANALYSIS,MANUAL_PROMPT,ENHANCED_PROMPT,USER_PROMPT,OBJ_PREVIEW,TEXT_ONLY,SCENE_PROMPT,USER_SCENE,CREATE_VISION,ENHANCED_SCENE,SAVE_RESULT,DISPLAY process
    class UPLOAD_BG,UPLOAD_OBJ,AUTO_PROMPT,CREATE_OBJ,CREATE_AUTO_PROMPT,MODEL_CHOICE,CREATE_MODEL,CONTINUE decision
    class EDIT_GENERATE,CREATE_GENERATE generation
    class LOCAL_I2I,API_I2I,LOCAL_T2I,API_T2I endpoint
```

## 6b. System Architecture Overview

```mermaid
graph LR
    subgraph "Frontend Layer"
        WEB[Web Browser]
        GRADIO[Gradio Interface]
    end
    
    subgraph "Application Layer"
        APP[app.py<br/>Main Entry Point]
        
        subgraph "Core Components"
            UI_MOD[UI Module<br/>Interface Builder]
            HANDLERS[Handler Classes<br/>Business Logic]
            CORE_UTILS[Core Utilities<br/>Image Processing]
        end
        
        subgraph "AI Integration"
            VISION_MOD[Vision Module<br/>Qwen-VL Integration]
            GEN_MOD[Generator Module<br/>FLUX Integration]
        end
        
        subgraph "Security & Config"
            SEC_STORE[Secure Storage<br/>Encrypted API Keys]
            CONFIG_MGR[Configuration<br/>Model Settings]
        end
    end
    
    subgraph "External Services"
        ALIBABA[Alibaba Cloud<br/>Qwen-VL-Max API]
        FLUX_CLOUD[FLUX API<br/>Kontext Pro Service]
    end
    
    subgraph "Local Resources"
        HF_MODELS[Hugging Face Models<br/>Local FLUX Pipeline]
        FILE_SYS[File System<br/>Images & Config]
    end
    
    %% User Flow
    WEB --> GRADIO
    GRADIO --> APP
    
    %% App Internal Flow
    APP --> UI_MOD
    APP --> HANDLERS
    HANDLERS --> CORE_UTILS
    HANDLERS --> VISION_MOD
    HANDLERS --> GEN_MOD
    HANDLERS --> SEC_STORE
    GEN_MOD --> CONFIG_MGR
    
    %% External Connections
    VISION_MOD --> ALIBABA
    GEN_MOD --> FLUX_CLOUD
    GEN_MOD --> HF_MODELS
    SEC_STORE --> FILE_SYS
    CORE_UTILS --> FILE_SYS
    
    %% Response Flow
    ALIBABA --> VISION_MOD
    FLUX_CLOUD --> GEN_MOD
    HF_MODELS --> GEN_MOD
    FILE_SYS --> CORE_UTILS
    
    %% Styling
    classDef frontend fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    classDef app fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef external fill:#fff8e1,stroke:#ff8f00,stroke-width:2px
    classDef local fill:#fce4ec,stroke:#ad1457,stroke-width:2px
    
    class WEB,GRADIO frontend
    class APP,UI_MOD,HANDLERS,CORE_UTILS,VISION_MOD,GEN_MOD,SEC_STORE,CONFIG_MGR app
    class ALIBABA,FLUX_CLOUD external
    class HF_MODELS,FILE_SYS local
```

## Key Components Summary

### Core Modules:
- **UI (core/ui.py)**: Gradio interface handling user interactions
- **I2I Handler (core/handlers/i2i_handler.py)**: Main workflow orchestration
- **Vision (core/vision.py)**: AI-powered image analysis
- **Generator (core/generator.py)**: FLUX model interface (local & API)
- **Utils (core/utils.py)**: Image processing utilities
- **Secure Storage (core/secure_storage.py)**: Encrypted API key management

### External Services:
- **Qwen-VL-Max**: Vision analysis API (Alibaba Cloud)
- **FLUX Kontext Pro API**: Cloud-based image generation using flux-1-kontext-pro
- **Local FLUX Models**: On-device generation using FLUX.1-Kontext-dev + Nunchaku optimization

### Model Configuration:
#### Local Models:
- **T2I**: `black-forest-labs/FLUX.1-Kontext-dev`
- **I2I**: `black-forest-labs/FLUX.1-Kontext-dev` + Nunchaku transformer
- **Nunchaku**: `mit-han-lab/nunchaku-flux.1-kontext-dev/svdq-int4_r32-flux.1-kontext-dev.safetensors`

#### API Models (Pro):
- **T2I**: `flux-1-kontext-pro` via `/v1/flux-kontext-pro`
- **I2I**: `flux-1-kontext-pro` via `/v1/flux-kontext-pro`

### Default Parameters:
- **T2I**: 28 steps, guidance 4.0
- **I2I**: 28 steps, guidance 3.0

### Data Flow:
1. **Standard Edit Mode**: User uploads background + object → selects area → vision analysis → generates with background preservation
2. **Create Mode**: User uploads object only → describes desired scene → generates new background with object context  
3. **Object-Only Mode**: User uploads multiple objects → system handles object replacement/swapping → generates edited scene
4. **Multi-Object Support**: Framework ready for multiple object composition (future enhancement)
5. Vision model analyzes surface types for contextual placement
6. Prompts are enhanced with surface-specific information while preserving backgrounds
7. FLUX models generate/edit images based on merged canvas approach
8. Results are saved and displayed to user

## Usage Scenarios Covered:

### ✅ **Edit Mode (Background + Object)**
- Upload background image → Upload object → Select area → Generate
- Supports vision analysis and surface detection
- Uses side-by-side merge approach for background preservation

### ✅ **Create Mode (Object Only)**  
- Skip background → Upload object → Describe scene → Generate
- Pure T2I generation with object context
- Future: Advanced object composition capabilities

### ✅ **Create Mode (Text Only)**
- Skip background → Skip object → Write prompt → Generate  
- Standard text-to-image generation

### ✅ **Multi-Object Handling**
- Framework supports multiple objects via merge_multiple_images_high_quality()
- Current UI: Single object replacement workflow
- Future: Multiple object placement and composition

This architecture ensures background preservation while enabling intelligent object placement based on surface analysis, and provides flexibility for various creative workflows.
