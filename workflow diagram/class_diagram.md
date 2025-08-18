# PhotoGen App v3 - Comprehensive Class Diagrams

## 📋 Table of Contents
1. [Core Architecture Classes](#core-architecture-classes)
2. [Handler and Manager Classes](#handler-and-manager-classes)
3. [Vision and Enhancement Classes](#vision-and-enhancement-classes)
4. [Utility and Support Classes](#utility-and-support-classes)
5. [Complete Relationship Map](#complete-relationship-map)

---

## Core Architecture Classes

### Main Application Structure

```mermaid
classDiagram
    class PhotoGenApp {
        -config: dict
        -secure_storage: SecureStorage
        -generator: Generator
        -demo: gr.Blocks
        -ui: dict
        -states: dict
        -i2i_handler: I2IHandler
        +__init__()
        +_register_event_handlers()
        +_register_api_key_handlers()
        +_register_additional_handlers()
        +load_app_state()
        +load_saved_key(provider)
        +save_enhancer_api_key(provider, key)
        +save_pro_api_key(provider, key)
        +update_pro_api_label_and_load_key(provider)
        +clear_pro_api_key(provider)
        +clear_all()
        +save_and_download_image(img, prefix)
        +launch()
    }

    class I2IHandler {
        -ui: dict
        -generator: Generator
        -secure_storage: SecureStorage
        -canvas_manager: CanvasManager
        -auto_prompt_manager: AutoPromptManager
        -state_manager: StateManager
        -generation_manager: GenerationManager
        -uploaded_images: list
        +__init__(ui, generator, secure_storage)
        +reset_handler_state()
        +register_event_handlers()
        +handle_multi_image_upload(files)
        +handle_gallery_click(evt)
        +run_i2i_generation_unified(params)
        +handle_click_with_prompt_button(base_img, obj_img, coords, evt)

    }

    class Generator {
        -config: dict
        -pipeline: FluxPipeline
        -kontext_pipeline: FluxKontextPipeline
        -depth_enabled: bool
        -depth_processor: None
        -tokenizer: Any
        +__init__(config)
        +_load_local_t2i_pipeline()
        +_load_local_i2i_pipeline()
        +_determine_safe_generation_size(bg_img, aspect, model, force)
        +_calculate_smart_object_scale(bg_size, obj_size)
        +_call_pro_api(payload, api_config_key, progress)
        +_get_pro_provider_info(model_choice)
        +text_to_image(prompt, steps, guidance, model, num_images, width, height, api_key, progress)
        +image_to_image(source_img_np, prompt, steps, guidance, model, num_images, width, height, api_key, bg_img, obj_img, aspect, progress)
    }

    class SecureStorage {
        -key_path: str
        -data_path: str
        -key: bytes
        -cipher: Fernet
        +__init__(key_path, data_path)
        +_load_or_generate_key()
        +_load_decrypted_data()
        +_save_encrypted_data(data)
        +save_api_key(provider_name, api_key)
        +load_api_key(provider_name)
        +clear_api_key(provider_name)
        +list_saved_providers()
    }

    PhotoGenApp --> Generator : uses
    PhotoGenApp --> SecureStorage : uses
    PhotoGenApp --> I2IHandler : contains
    I2IHandler --> Generator : delegates to
    I2IHandler --> SecureStorage : accesses
    Generator --> SecureStorage : accesses keys
```

---

## Handler and Manager Classes

### Complete Handler System Architecture

```mermaid
classDiagram
    class I2IHandler {
        -ui: dict
        -generator: Generator
        -secure_storage: SecureStorage
        -canvas_manager: CanvasManager
        -auto_prompt_manager: AutoPromptManager
        -state_manager: StateManager
        -generation_manager: GenerationManager
        -uploaded_images: list
        +__init__(ui, generator, secure_storage)
        +reset_handler_state()
        +register_event_handlers()
        +handle_multi_image_upload(files)
        +handle_gallery_click(evt)
        +run_i2i_generation_unified(params)
        +handle_click_with_prompt_button(base_img, obj_img, coords, evt)
    }

    class GenerationManager {
        -generator: Generator
        -secure_storage: SecureStorage
        -_executor: ThreadPoolExecutor
        +__init__(generator, secure_storage)
        +run_generation(source_img, obj_img, prompt, aspect, steps, guidance, model, coords, progress)
        +_process_prompt_for_pro_model(prompt, obj_img, src_img, model)
        +_determine_dimensions(aspect_ratio, source_img, is_create_mode)
        +_get_api_key_for_model(model_choice)
        +_handle_create_mode(obj_img, prompt, steps, guidance, model, w, h, key, progress)
        +_handle_edit_mode(src_img, obj_img, prompt, aspect, steps, guidance, model, w, h, key, progress)
        +_execute_pro_generation(params, progress)
        +_execute_local_generation(params, progress)
        +_truncate_prompt_if_needed(prompt)
        +_prepare_result(images)
    }

    class AutoPromptManager {
        -secure_storage: SecureStorage
        -vision_analyzer: VisionAnalyzer
        +__init__(secure_storage)
        +generate_auto_prompt(base_img, obj_img, coords, existing_prompt, provider)
        +_validate_inputs(base_img, obj_img, coords, provider)
        +_process_selection_coordinates(base_img, top_left, bottom_right)
        +_create_selection_overlay(base_img, coords)
        +_optimize_for_pro_model(prompt)
    }

    class CanvasManager {
        +__init__()
        +update_canvas_with_merge(base_img, obj_img, coords)
        +handle_click(base_img, obj_img, coords, evt)
        +_redraw_canvas(base_img, obj_img, coords)
        +_draw_selection_box(image, coords, color, thickness)
        +_calculate_click_coordinates(evt, img_size)
        +_snap_to_edges(x, y, img_size, tolerance)
        +_create_auto_selection_area(click_x, click_y, img_size)
    }

    class StateManager {
        +__init__()
        +store_background(img, existing_object)
        +store_object(img)
        +update_prompt_status(prompt_text)
        +_create_placeholder_canvas(existing_object)
        +_validate_state_transition(from_state, to_state)
        +reset_all_states()
    }

    class Generator {
        -config: dict
        -pipeline: FluxPipeline
        -kontext_pipeline: FluxKontextPipeline
        -depth_enabled: bool
        -depth_processor: None
        -tokenizer: Any
        +__init__(config)
        +_load_local_t2i_pipeline()
        +_load_local_i2i_pipeline()
        +_determine_safe_generation_size(bg_img, aspect, model, force)
        +_calculate_smart_object_scale(bg_size, obj_size)
        +_call_pro_api(payload, api_config_key, progress)
        +_get_pro_provider_info(model_choice)
        +text_to_image(prompt, steps, guidance, model, num_images, width, height, api_key, progress)
        +image_to_image(source_img_np, prompt, steps, guidance, model, num_images, width, height, api_key, bg_img, obj_img, aspect, progress)
    }

    class SecureStorage {
        -key_path: str
        -data_path: str
        -key: bytes
        -cipher: Fernet
        +__init__(key_path, data_path)
        +_load_or_generate_key()
        +_load_decrypted_data()
        +_save_encrypted_data(data)
        +save_api_key(provider_name, api_key)
        +load_api_key(provider_name)
        +clear_api_key(provider_name)
        +list_saved_providers()
    }

    class VisionAnalyzer {
        -api_base: str
        -model: str
        +__init__()
        +generate_comprehensive_auto_prompt(bg_img, obj_img, coords, provider, api_key)
        +_image_to_base64(image)
        +_calculate_position_description(coords, img_size)
        +_create_analysis_prompt(position_desc, has_object)
        +_clean_prompt_response(prompt)
        +_basic_clean_prompt_response(prompt)
        +_log_human_surface_detection(prompt)
    }

    class Utils {
        +get_dimensions(aspect_ratio)
        +create_side_by_side_display(bg_img, obj_img)
        +merge_images_with_smart_scaling(bg_img, obj_img, target_size, preserve_scale)
        +merge_images_intelligently(bg_img, obj_img, coords, target_size)
        +save_image(image, filename, output_dir)
        +load_image_safely(file_path)
        +validate_image_format(image)
        +calculate_aspect_ratio(width, height)
        +resize_if_too_large(image, max_pixels)
        +create_thumbnail(image, size)
        +_calculate_human_scaling(obj_img, target_height)
        +_apply_area_based_scaling(obj_img, bg_area, ratios)
    }

    I2IHandler --> GenerationManager : delegates generation
    I2IHandler --> AutoPromptManager : handles prompts
    I2IHandler --> CanvasManager : manages canvas
    I2IHandler --> StateManager : manages state
    GenerationManager --> Generator : executes generation
    GenerationManager --> SecureStorage : accesses keys
    AutoPromptManager --> VisionAnalyzer : analyzes images
    AutoPromptManager --> SecureStorage : gets API keys
    CanvasManager --> Utils : uses utilities
    StateManager --> Utils : uses utilities
    
    %% Note: I2IHandler receives Generator and SecureStorage via dependency injection from PhotoGenApp
```

---

## Vision and Enhancement Classes

### AI-Powered Analysis and Enhancement

```mermaid
classDiagram
    class AutoPromptManager {
        -secure_storage: SecureStorage
        -vision_analyzer: VisionAnalyzer
        +__init__(secure_storage)
        +generate_auto_prompt(base_img, obj_img, coords, existing_prompt, provider)
        +_validate_inputs(base_img, obj_img, coords, provider)
        +_process_selection_coordinates(base_img, top_left, bottom_right)
        +_create_selection_overlay(base_img, coords)
        +_optimize_for_pro_model(prompt)
    }

    class VisionAnalyzer {
        -api_base: str
        -model: str
        +__init__()
        +generate_comprehensive_auto_prompt(bg_img, obj_img, coords, provider, api_key)
        +_image_to_base64(image)
        +_calculate_position_description(coords, img_size)
        +_create_analysis_prompt(position_desc, has_object)
        +_clean_prompt_response(prompt)
        +_basic_clean_prompt_response(prompt)
        +_log_human_surface_detection(prompt)
    }

    class Enhancer {
        <<abstract>>
        -api_key: str
        +__init__(api_key)
        +setup_client()
        +enhance(base_prompt, image)
        +get_instruction(base_prompt, has_image)
        +parse_response(text)
        +_validate_api_key()
    }

    class QwenVLMaxEnhancer {
        -api_key: str
        +setup_client()
        +enhance(base_prompt, image)
        +_enhance_text_only(base_prompt)
        +_enhance_with_vision(base_prompt, image)
        +_prepare_messages(instruction, image)
        +_call_api(messages)
        +_parse_structured_response(response)
    }

    class get_enhancer {
        <<static function>>
        +get_enhancer(provider_name, api_key)
        +_create_qwen_enhancer(api_key)
        +_validate_provider(provider_name)
    }

    class SecureStorage {
        -key_path: str
        -data_path: str
        -key: bytes
        -cipher: Fernet
        +__init__(key_path, data_path)
        +_load_or_generate_key()
        +_load_decrypted_data()
        +_save_encrypted_data(data)
        +save_api_key(provider_name, api_key)
        +load_api_key(provider_name)
        +clear_api_key(provider_name)
        +list_saved_providers()
    }

    %% Relationships
    AutoPromptManager --> VisionAnalyzer : uses
    AutoPromptManager --> get_enhancer : gets enhancer via
    Enhancer <|-- QwenVLMaxEnhancer : implements
    get_enhancer --> QwenVLMaxEnhancer : creates via ENHANCER_MAP
    
    %% External connections
    AutoPromptManager --> SecureStorage : accesses keys
    VisionAnalyzer --> SecureStorage : gets API keys
```

---

## Utility and Support Classes

### Core Utilities and Configuration

```mermaid
classDiagram
    class Utils {
        <<static>>
        +get_dimensions(aspect_ratio)
        +create_side_by_side_display(bg_img, obj_img)
        +merge_images_with_smart_scaling(bg_img, obj_img, target_size, preserve_scale)
        +merge_images_intelligently(bg_img, obj_img, coords, target_size)
        +save_image(image, filename, output_dir)
        +load_image_safely(file_path)
        +validate_image_format(image)
        +calculate_aspect_ratio(width, height)
        +resize_if_too_large(image, max_pixels)
        +create_thumbnail(image, size)
        +_calculate_human_scaling(obj_img, target_height)
        +_apply_area_based_scaling(obj_img, bg_area, ratios)
    }

    class Constants {
        <<static>>
        +I2I_MODE: str
        +T2I_MODE: str
        +LOCAL_MODEL: str
        +PRO_MODEL: str
        +FLUX_PRO_API: str
        +GRS_AI_FLUX_API: str
        +QWEN_VL_MAX: str
        +BOX_START_TOOL: str
        +BOX_END_TOOL: str
        +OUTPUTS_DIR: str
        +T2I_TYPE: str
        +I2I_TYPE: str
    }

    class UI {
        <<static>>
        +create_ui()
        +_create_custom_css()
        +_create_state_holders()
        +_create_control_panel()
        +_create_canvas_panel()
        +_create_output_panel()
        +_create_api_settings()
        +_setup_event_handlers()
    }

    class PhotoGenApp {
        +Main Application Controller
    }

    class config.yaml {
        <<external file>>
        +Application configuration
    }

        class Generator {
        -config: dict
        -pipeline: FluxPipeline
        -kontext_pipeline: FluxKontextPipeline
        -depth_enabled: bool
        -depth_processor: None
        -tokenizer: Any
        +__init__(config)
        +_load_local_t2i_pipeline()
        +_load_local_i2i_pipeline()
        +_determine_safe_generation_size(bg_img, aspect, model, force)
        +_calculate_smart_object_scale(bg_size, obj_size)
        +_call_pro_api(payload, api_config_key, progress)
        +_get_pro_provider_info(model_choice)
        +text_to_image(prompt, steps, guidance, model, num_images, width, height, api_key, progress)
        +image_to_image(source_img_np, prompt, steps, guidance, model, num_images, width, height, api_key, bg_img, obj_img, aspect, progress)
    }


    class CanvasManager {
        +__init__()
        +update_canvas_with_merge(base_img, obj_img, coords)
        +handle_click(base_img, obj_img, coords, evt)
        +_redraw_canvas(base_img, obj_img, coords)
        +_draw_selection_box(image, coords, color, thickness)
        +_calculate_click_coordinates(evt, img_size)
        +_snap_to_edges(x, y, img_size, tolerance)
        +_create_auto_selection_area(click_x, click_y, img_size)
    }

    class StateManager {
        +__init__()
        +store_background(img, existing_object)
        +store_object(img)
        +update_prompt_status(prompt_text)
        +_create_placeholder_canvas(existing_object)
        +_validate_state_transition(from_state, to_state)
        +reset_all_states()
    }

    %% Relationships
    Utils --> Constants : references
    UI --> Constants : uses
    PhotoGenApp --> UI : creates interface via
    PhotoGenApp --> config.yaml : loads directly (no ConfigManager class)
    
    %% Usage by other components
    Generator --> Utils : uses for image processing
    CanvasManager --> Utils : uses for canvas operations
    StateManager --> Utils : uses for state management
```

---

## Complete Relationship Map

### Full System Architecture with All Dependencies

```mermaid
classDiagram
    %% Core Application Layer
    class PhotoGenApp {
        +Main Application Controller
    }
    
    %% Core Services Layer
    class Generator {
        +Image Generation Engine
    }
    class SecureStorage {
        +Encrypted Key Management
    }
    class UI {
        +User Interface Factory
    }
    
    %% Handler Management Layer
    class I2IHandler {
        +Main Request Handler
    }
    class GenerationManager {
        +Generation Workflow Manager
    }
    class AutoPromptManager {
        +AI Prompt Enhancement Manager
    }
    class CanvasManager {
        +Canvas Interaction Manager
    }
    class StateManager {
        +Application State Manager
    }
    
    %% AI/Vision Layer
    class VisionAnalyzer {
        +Computer Vision Analysis
    }
    class Enhancer {
        +Prompt Enhancement Engine
    }
    class QwenVLMaxEnhancer {
        +Qwen-Specific Implementation
    }
    
    %% Utility Layer
    class Utils {
        +Image Processing Utilities
    }
    class Constants {
        +Application Constants
    }

    %% Relationships
    PhotoGenApp --> Generator
    PhotoGenApp --> SecureStorage
    PhotoGenApp --> UI
    PhotoGenApp --> I2IHandler

    I2IHandler --> GenerationManager
    I2IHandler --> AutoPromptManager
    I2IHandler --> CanvasManager
    I2IHandler --> StateManager

    GenerationManager --> Generator
    GenerationManager --> SecureStorage
    AutoPromptManager --> VisionAnalyzer
    AutoPromptManager --> SecureStorage
    VisionAnalyzer --> SecureStorage

    Generator --> Utils
    Generator --> Constants
    CanvasManager --> Utils
    StateManager --> Utils
    UI --> Constants

    AutoPromptManager --> Enhancer
    Enhancer <|-- QwenVLMaxEnhancer

    %% External Dependencies
    Generator --> FluxPipeline : uses
    Generator --> FluxKontextPipeline : uses
    Generator --> NunchakuFluxTransformer2dModel : optionally uses
    VisionAnalyzer --> OpenAI : API client
    QwenVLMaxEnhancer --> OpenAI : API client
    SecureStorage --> Fernet : encryption

    %% Style classes by layer
    classDef coreLayer fill:#e1f5fe
    classDef managerLayer fill:#f3e5f5
    classDef visionLayer fill:#e8f5e8
    classDef utilityLayer fill:#fff3e0
    
    class PhotoGenApp:::coreLayer
    class Generator:::coreLayer
    class SecureStorage:::coreLayer
    class UI:::coreLayer
    class I2IHandler:::managerLayer
    class GenerationManager:::managerLayer
    class AutoPromptManager:::managerLayer
    class CanvasManager:::managerLayer
    class StateManager:::managerLayer
    class VisionAnalyzer:::visionLayer
    class Enhancer:::visionLayer
    class QwenVLMaxEnhancer:::visionLayer
    class Utils:::utilityLayer
    class Constants:::utilityLayer
```

---

## Detailed Method Signatures

### Key Method Details by Class

#### GenerationManager Methods
```python
run_generation(source_image: Image, object_image: Image, prompt: str, 
               aspect_ratio: str, steps: int, guidance: float, 
               model_choice: str, top_left: tuple, bottom_right: tuple, 
               progress: gr.Progress) -> list

_process_prompt_for_pro_model(prompt: str, object_image: Image, 
                             source_image: Image, model_choice: str) -> str

_execute_pro_generation(source_img: Image, object_img: Image, prompt: str,
                       width: int, height: int, steps: int, guidance: float,
                       model_choice: str, api_key: str, progress: gr.Progress) -> list
```

#### VisionAnalyzer Methods
```python
generate_comprehensive_auto_prompt(background_image: Image, object_image: Image,
                                  selection_coords: tuple, provider_name: str,
                                  api_key: str) -> str

_create_analysis_prompt(position_desc: str, has_object_image: bool) -> str

_post_process_prompt(raw_response: str) -> str
```

#### CanvasManager Methods
```python
handle_click(base_img: Image, obj_img: Image, top_left: tuple,
            bottom_right: tuple, evt: gr.SelectData) -> tuple

update_canvas_with_merge(base_img: Image, obj_img: Image,
                        top_left: tuple, bottom_right: tuple) -> Image

create_side_by_side_display(bg_img: Image, obj_img: Image) -> Image
```

---

## Design Patterns and Architectural Decisions

### Patterns Implemented
- **Manager Pattern**: Separate managers for distinct responsibilities (Generation, Canvas, State, AutoPrompt)
- **Strategy Pattern**: Multiple API providers with unified interface
- **Factory Pattern**: get_enhancer() function creates appropriate enhancer instances
- **Facade Pattern**: I2IHandler provides simplified interface to complex subsystem
- **Observer Pattern**: State changes trigger UI updates through Gradio
- **Template Method Pattern**: Enhancer base class defines enhancement workflow

### Key Architectural Benefits
- **Separation of Concerns**: Each manager handles specific domain logic
- **Extensibility**: Easy to add new API providers, enhancers, or generation methods
- **Testability**: Modular design enables unit testing of individual components
- **Security**: Centralized encrypted storage for sensitive API keys
- **Performance**: Lazy loading, async operations, and resource management
- **Maintainability**: Clear responsibilities and minimal coupling between components
