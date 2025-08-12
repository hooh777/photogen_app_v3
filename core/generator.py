import torch
import gradio as gr
from diffusers import FluxPipeline, FluxKontextPipeline
from transformers import AutoTokenizer
try:
    from nunchaku import NunchakuFluxTransformer2dModel
    from nunchaku.utils import get_precision
    NUNCHAKU_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Nunchaku not available: {e}")
    NUNCHAKU_AVAILABLE = False
    # Placeholder classes
    class NunchakuFluxTransformer2dModel:
        pass
    def get_precision():
        return "fp16"
from PIL import Image
import numpy as np
import requests
import base64
from io import BytesIO
import time
import logging
import math
from core import constants as const
from core import utils
from core.depth_processor import DepthMapProcessor

class Generator:
    def __init__(self, config):
        self.config = config
        self.pipeline = None
        self.kontext_pipeline = None
        self.tokenizer = None
        # Lazy loading - only load when actually needed for better startup time
        
        # Initialize depth processing
        try:
            self.depth_processor = DepthMapProcessor()
            self.depth_enabled = self.depth_processor.depth_estimator is not None
            if self.depth_enabled:
                logging.info("🌊 Depth ControlNet processing enabled")
            else:
                logging.warning("⚠️ Depth processing unavailable - depth models failed to load")
        except Exception as e:
            logging.error(f"❌ Depth processing initialization failed: {e}")
            self.depth_enabled = False
            self.depth_processor = None
            logging.info("📸 Running without depth processing (basic mode)")

    def _initialize_tokenizer(self):
        if self.kontext_pipeline and hasattr(self.kontext_pipeline, 'tokenizer'):
            self.tokenizer = self.kontext_pipeline.tokenizer
            logging.info("✅ Tokenizer accessed from loaded pipeline.")
        else:
            logging.warning("⚠️ Could not access tokenizer from pipeline.")

    def _load_local_t2i_pipeline(self):
        if self.pipeline is None:
            logging.info("Loading FLUX.1 (Text-to-Image) pipeline...")
            DTYPE = torch.bfloat16
            self.pipeline = FluxPipeline.from_pretrained(
                self.config['models']['text_to_image'], torch_dtype=DTYPE
            )
            self.pipeline.enable_model_cpu_offload()
            logging.info("✅ FLUX.1 T2I pipeline configured.")
        return self.pipeline

    def _load_local_i2i_pipeline(self):
        if self.kontext_pipeline is None:
            logging.info("Loading FLUX.1 Kontext (Image-to-Image) pipeline...")
            try:
                if not NUNCHAKU_AVAILABLE:
                    logging.error("🚫 Nunchaku not available - cannot load I2I pipeline")
                    self.kontext_pipeline = None
                    return None
                    
                DTYPE = torch.bfloat16
                torch.set_float32_matmul_precision('high')
                nunchaku_path = self.config['models']['nunchaku_transformer'].format(precision=get_precision())
                
                logging.info("Loading Nunchaku transformer...")
                transformer = NunchakuFluxTransformer2dModel.from_pretrained(nunchaku_path, torch_dtype=DTYPE)
                logging.info("✅ Nunchaku transformer loaded.")
                
                self.kontext_pipeline = FluxKontextPipeline.from_pretrained(
                    self.config['models']['image_to_image'], transformer=transformer, torch_dtype=DTYPE
                )
                self.kontext_pipeline.enable_model_cpu_offload()
                logging.info("✅ FLUX.1 Kontext I2I pipeline configured.")
                self._initialize_tokenizer()
            except Exception:
                logging.error("🔥 FATAL ERROR: Could not load local models.", exc_info=True)
                self.kontext_pipeline = None
                self.tokenizer = None
        return self.kontext_pipeline
        
    def _determine_safe_generation_size(self, background_img, aspect_ratio_setting, model_choice):
        """Smart dimension selection with safety checks for optimal quality and performance"""
        if background_img is None:
            # No background - use aspect ratio setting
            return utils.get_dimensions(aspect_ratio_setting)
        
        bg_size = background_img.size
        bg_pixels = bg_size[0] * bg_size[1]
        bg_ratio = bg_size[0] / bg_size[1]
        
        # Log original dimensions for debugging
        logging.info(f"🔍 Background image original size: {bg_size[0]}×{bg_size[1]} ({bg_pixels:,} pixels, ratio: {bg_ratio:.2f})")
        
        # Safety thresholds based on model choice
        if model_choice == const.PRO_MODEL:
            # Pro API can handle larger images but has cost implications
            MAX_SAFE_PIXELS = 2048 * 2048  # 4MP conservative limit for Pro
            MAX_DIMENSION = 2048
            MIN_QUALITY_PIXELS = 768 * 768  # Minimum for quality preservation
        else:
            # Local model - more conservative for GPU memory
            MAX_SAFE_PIXELS = 1536 * 1536  # 2.3MP for local GPU safety
            MAX_DIMENSION = 1536
            MIN_QUALITY_PIXELS = 512 * 512  # Minimum for quality preservation
            
        MIN_RATIO, MAX_RATIO = 0.3, 3.5  # Reasonable aspect ratio range (3:10 to 10:3)
        
        # Check if background dimensions are safe to use directly
        is_size_safe = bg_pixels <= MAX_SAFE_PIXELS
        is_ratio_safe = MIN_RATIO <= bg_ratio <= MAX_RATIO
        is_dimension_safe = bg_size[0] <= MAX_DIMENSION and bg_size[1] <= MAX_DIMENSION
        is_quality_sufficient = bg_pixels >= MIN_QUALITY_PIXELS
        
        # QUALITY PRESERVATION LOGIC: Prioritize detail retention
        if is_size_safe and is_ratio_safe and is_dimension_safe and is_quality_sufficient:
            # Background is safe and high quality - preserve original
            logging.info(f"✅ Using background dimensions: {bg_size[0]}×{bg_size[1]} (safe & high quality)")
            return bg_size
        elif not is_quality_sufficient and is_ratio_safe:
            # Image is too small - upscale to minimum quality threshold while preserving ratio
            scale_factor = math.sqrt(MIN_QUALITY_PIXELS / bg_pixels)
            new_width = int(bg_size[0] * scale_factor)
            new_height = int(bg_size[1] * scale_factor)
            
            # Ensure dimensions are multiples of 64 for model compatibility
            new_width = ((new_width + 63) // 64) * 64
            new_height = ((new_height + 63) // 64) * 64
            
            logging.info(f"📈 Upscaling for quality: {bg_size[0]}×{bg_size[1]} → {new_width}×{new_height} (quality preservation)")
            return (new_width, new_height)
        elif not is_ratio_safe:
            # Extreme aspect ratio - use aspect ratio setting but ensure minimum quality
            fallback_size = utils.get_dimensions(aspect_ratio_setting)
            if fallback_size[0] * fallback_size[1] < MIN_QUALITY_PIXELS:
                # Even fallback is too small, use minimum quality dimensions
                if bg_ratio > 1:  # Landscape
                    new_height = int(math.sqrt(MIN_QUALITY_PIXELS / bg_ratio))
                    new_width = int(new_height * bg_ratio)
                else:  # Portrait
                    new_width = int(math.sqrt(MIN_QUALITY_PIXELS * bg_ratio))
                    new_height = int(new_width / bg_ratio)
                
                # Ensure multiples of 64
                new_width = max(512, ((new_width + 63) // 64) * 64)
                new_height = max(512, ((new_height + 63) // 64) * 64)
                
                logging.warning(f"⚠️ Extreme aspect ratio with quality protection: {bg_size[0]}×{bg_size[1]} → {new_width}×{new_height}")
                return (new_width, new_height)
            else:
                logging.warning(f"⚠️ Background aspect ratio {bg_ratio:.2f} too extreme, using {fallback_size[0]}×{fallback_size[1]}")
                return fallback_size
        else:
            # Image is too large - scale down but respect minimum quality
            scale_factor = min(
                math.sqrt(MAX_SAFE_PIXELS / bg_pixels),
                MAX_DIMENSION / max(bg_size[0], bg_size[1])
            )
            
            new_width = int(bg_size[0] * scale_factor)
            new_height = int(bg_size[1] * scale_factor)
            
            # Check if scaling down would go below quality threshold
            scaled_pixels = new_width * new_height
            if scaled_pixels < MIN_QUALITY_PIXELS:
                # Prioritize quality over memory safety
                quality_scale_factor = math.sqrt(MIN_QUALITY_PIXELS / bg_pixels)
                new_width = int(bg_size[0] * quality_scale_factor)
                new_height = int(bg_size[1] * quality_scale_factor)
                logging.warning(f"⚠️ Quality protection overriding memory safety: using {new_width}×{new_height} instead of smaller size")
            
            # Ensure dimensions are multiples of 64 for model compatibility
            new_width = max(512, ((new_width + 63) // 64) * 64)
            new_height = max(512, ((new_height + 63) // 64) * 64)
            
            logging.info(f"📐 Scaled background from {bg_size[0]}×{bg_size[1]} to {new_width}×{new_height} (balanced quality/safety)")
            return (new_width, new_height)
    
    def _calculate_smart_object_scale(self, background_size, object_size):
        """Calculate contextually appropriate object scaling with aspect ratio preservation"""
        if not object_size:
            return None
            
        bg_area = background_size[0] * background_size[1]
        obj_area = object_size[0] * object_size[1]
        
        # Base scale: object should be reasonable size relative to background
        # Start with 15% of background area as default
        target_area_ratio = 0.15
        
        # Adjust based on background aspect ratio
        bg_ratio = background_size[0] / background_size[1]
        if bg_ratio > 2.5:  # Very wide background (panorama style)
            target_area_ratio *= 0.7  # Make object relatively smaller
        elif bg_ratio < 0.4:  # Very tall background (portrait style)
            target_area_ratio *= 0.8  # Make object slightly smaller
            
        # Calculate scale factor to achieve target area
        target_area = bg_area * target_area_ratio
        scale_factor = math.sqrt(target_area / obj_area)
        
        # Clamp scale factor to reasonable bounds
        scale_factor = max(0.1, min(scale_factor, 2.0))  # Don't shrink below 10% or grow above 200%
        
        new_width = int(object_size[0] * scale_factor)
        new_height = int(object_size[1] * scale_factor)
        
        # Ensure minimum viable size
        if new_width < 64 or new_height < 64:
            min_scale = max(64 / object_size[0], 64 / object_size[1])
            new_width = int(object_size[0] * min_scale)
            new_height = int(object_size[1] * min_scale)
            
        logging.info(f"🎯 Object scaled from {object_size[0]}×{object_size[1]} to {new_width}×{new_height} (scale: {scale_factor:.2f})")
        return (new_width, new_height)
        
    def _call_pro_api(self, payload, api_config_key, progress):
        """Helper function to call the Pro API, poll for results, and return images."""
        api_config = self.config.get('api_models', {}).get(api_config_key, {})
        api_base = api_config.get('api_base')
        endpoint = api_config.get('endpoint')
        
        if not api_base or not endpoint:
            raise gr.Error(f"Your config.yaml is missing API configuration for '{api_config_key}'.")

        full_endpoint = f"{api_base}{endpoint}"
        api_key = payload.pop("api_key", "")
        
        logging.info(f"🔑 API Call Debug - Config key: {api_config_key}")
        logging.info(f"🔑 API Base: {api_base}")
        logging.info(f"🔑 Endpoint: {endpoint}")
        logging.info(f"🔑 API Key received: {'✅ Found' if api_key else '❌ Empty'}")
        
        # Both providers use the same authentication method (Flux API compatible)
        headers = {"x-key": api_key, "Content-Type": "application/json"}
        logging.info("🔑 Using Flux-compatible authentication (x-key header)")
        
        try:
            progress(0, desc="Sending request to Pro API...")
            logging.info(f"🔑 Request headers: {headers}")
            logging.info(f"🔑 Request payload keys: {list(payload.keys())}")
            post_response = requests.post(full_endpoint, headers=headers, json=payload, timeout=120)
            post_response.raise_for_status()
            
            logging.info(f"🔑 Response status: {post_response.status_code}")
            logging.info(f"🔑 Response content: {post_response.text[:500]}...")  # First 500 chars
            
            polling_url = post_response.json().get('polling_url')
            if not polling_url:
                raise gr.Error(f"API did not return a polling URL. Response: {post_response.text}")
        except requests.exceptions.RequestException as e:
            response_text = e.response.text if e.response else "N/A"
            logging.error("API Request Error", exc_info=True)
            raise gr.Error(f"API Request Error: {e} - Response: {response_text}")
        
        # Polling loop
        for i in range(60):
            progress((i + 1) / 60, desc=f"Waiting for result (Attempt {i+1})...")
            get_response = requests.get(polling_url, headers={"x-key": api_key}, timeout=30)
            get_response.raise_for_status()
            result_data = get_response.json()
            
            if result_data.get('status') == 'Ready':
                progress(0.95, desc="Downloading final image(s)...")
                
                # --- CORRECTED LOGIC START ---
                # The API returns a single URL in 'sample', not a list in 'samples'.
                single_sample_url = result_data.get('result', {}).get('sample')
                
                if not single_sample_url:
                    logging.error(f"API response did not contain an image URL. Full response: {result_data}")
                    raise gr.Error("API job succeeded but the response did not contain a valid image URL.")

                # The rest of the function expects a list, so we put our single URL into a list.
                samples = [single_sample_url]
                # --- CORRECTED LOGIC END ---

                images = []
                for url in samples:
                    image_response = requests.get(url)
                    image_response.raise_for_status()
                    images.append(Image.open(BytesIO(image_response.content)))
                return images

            elif result_data.get('status') == 'failed':
                raise gr.Error(f"API job failed: {result_data.get('error', 'Unknown error')}")
            
            time.sleep(2)

        raise gr.Error("API request timed out after 2 minutes.")

    def _get_pro_provider_info(self, model_choice):
        """Extract provider info from Pro model choice and return config keys and provider name"""
        if model_choice == "Pro (Black Forest Labs)":
            return {
                'provider_name': const.FLUX_PRO_API,
                't2i_config_key': 'bfl_flux_t2i',
                'i2i_config_key': 'bfl_flux_i2i'
            }
        elif model_choice == "Pro (GRS AI)":
            return {
                'provider_name': const.GRS_AI_FLUX_API,
                't2i_config_key': 'grs_flux_t2i', 
                'i2i_config_key': 'grs_flux_i2i'
            }
        else:
            # Fallback for compatibility with old "Pro" choice
            return {
                'provider_name': const.FLUX_PRO_API,
                't2i_config_key': 'bfl_flux_t2i',
                'i2i_config_key': 'bfl_flux_i2i'
            }

    def text_to_image(self, prompt, steps, guidance, model_choice, num_images, width, height, api_key="", progress=gr.Progress(track_tqdm=True)):
        if model_choice == const.LOCAL_MODEL:
            pipeline = self._load_local_t2i_pipeline()
            if pipeline is None:
                raise gr.Error("Local Text-to-Image pipeline could not be loaded.")
            with torch.inference_mode():
                images = pipeline(
                    prompt=prompt, 
                    num_inference_steps=int(steps), 
                    guidance_scale=float(guidance),
                    num_images_per_prompt=int(num_images),
                    width=int(width),
                    height=int(height)
                ).images
                return images
        elif model_choice.startswith("Pro"):
            # Handle provider-specific Pro model selection
            provider_info = self._get_pro_provider_info(model_choice)
            provider_name = provider_info['provider_name']
            config_key = provider_info['t2i_config_key']
            
            if not api_key: 
                raise gr.Error(f"API Key for {provider_name} is missing!")
            
            payload = {
                "model": self.config.get('api_models', {}).get(config_key, {}).get('model_name'),
                "prompt": prompt,
                "num_inference_steps": int(steps),
                "guidance_scale": float(guidance),
                "num_images_per_prompt": int(num_images),
                "width": int(width),
                "height": int(height),
                "api_key": api_key
            }
            return self._call_pro_api(payload, config_key, progress)
        else:
            raise ValueError(f"Invalid model choice: {model_choice}")
            
    def image_to_image(self, source_image_np, prompt, steps, guidance, model_choice, num_images, width, height, api_key="", background_img=None, object_img=None, aspect_ratio_setting="1:1", progress=gr.Progress(), use_depth_control=True, depth_strength=0.6, disable_auto_enhancement=False):
        """Enhanced image-to-image generation with smart dimension handling and depth control"""
        
        # Debug logging for input analysis
        if background_img is not None:
            logging.info(f"🔍 Input analysis - Background: {background_img.size}, Object: {object_img.size if object_img else 'None'}")
            logging.info(f"🔍 Requested dimensions: {width}×{height}, Aspect ratio setting: {aspect_ratio_setting}")
            logging.info(f"🌊 Depth control: {'Enabled' if use_depth_control and self.depth_enabled else 'Disabled'}")
        
        # Generate depth map for enhanced background replacement
        depth_map = None
        if use_depth_control and self.depth_enabled and background_img is not None:
            try:
                logging.info("🌊 Generating depth map for enhanced background replacement...")
                if progress:
                    progress(0.1, "Analyzing image depth...")
                
                depth_map = self.depth_processor.generate_depth_map(background_img)
                if depth_map:
                    # Enhance depth map quality
                    depth_map = self.depth_processor.enhance_depth_map(depth_map)
                    logging.info("✅ Depth map generated successfully")
                    if progress:
                        progress(0.2, "Depth analysis complete")
                else:
                    logging.warning("⚠️ Depth map generation failed, continuing without depth control")
            except Exception as e:
                logging.error(f"❌ Depth processing error: {e}")
                depth_map = None
        
        # Determine optimal generation size using hybrid approach
        if background_img is not None:
            # Use smart dimension calculation based on background
            optimal_size = self._determine_safe_generation_size(background_img, aspect_ratio_setting, model_choice)
            target_width, target_height = optimal_size
            
            # Provide user feedback about dimension choice
            depth_info = " with depth control" if depth_map is not None else ""
            if optimal_size == background_img.size:
                gr.Info(f"✅ Using background dimensions: {target_width}×{target_height}{depth_info}")
            else:
                gr.Info(f"📐 Optimized dimensions: {target_width}×{target_height}{depth_info} (scaled from {background_img.size[0]}×{background_img.size[1]} for performance)")
        else:
            # No background info - use provided dimensions
            target_width, target_height = width, height
            logging.info(f"🔍 No background - using provided dimensions: {target_width}×{target_height}")
        
        # Final dimension validation and logging
        logging.info(f"🎯 Final generation dimensions: {target_width}×{target_height} ({target_width * target_height:,} pixels)")
        
        if model_choice == const.LOCAL_MODEL:
            kontext_pipeline = self._load_local_i2i_pipeline()
            if kontext_pipeline is None:
                raise gr.Error("Local Image-to-Image pipeline could not be loaded.")
            
            # Handle multi-image input for Flux Kontext properly
            if background_img and object_img:
                # Multi-image context: pass background and object as separate images
                # Resize background to target size, but preserve object's original proportions
                if background_img.size != (target_width, target_height):
                    resized_background = background_img.resize((target_width, target_height), Image.LANCZOS)
                    logging.info(f"📐 Resized background: {background_img.size} → {target_width}×{target_height}")
                else:
                    resized_background = background_img
                
                # Keep object at original size to preserve its proportions
                # Flux Kontext will handle the intelligent scaling and placement
                image_inputs = [resized_background, object_img]
                logging.info(f"🎯 Multi-image context: Background {resized_background.size} + Object {object_img.size} (original proportions preserved)")
                logging.info(f"🔍 Object details - Mode: {object_img.mode}, Size: {object_img.size}, Format: {getattr(object_img, 'format', 'Unknown')}")
                gr.Info(f"Using multi-image context: background resized to {target_width}×{target_height}, object preserved at {object_img.size}")
            else:
                # Single image input - resize as before
                current_image_pil = Image.fromarray(source_image_np)
                
                # Resize the input image to match the target dimensions before generation
                if current_image_pil.size != (target_width, target_height):
                    # Quality preservation during resize
                    original_pixels = current_image_pil.size[0] * current_image_pil.size[1]
                    target_pixels = target_width * target_height
                    
                    if target_pixels < original_pixels:
                        # Downscaling - use LANCZOS for quality
                        resize_method = Image.LANCZOS
                        logging.info(f"📉 Downscaling source image: {current_image_pil.size} → {target_width}×{target_height}")
                    else:
                        # Upscaling - use LANCZOS for better quality than default
                        resize_method = Image.LANCZOS
                        logging.info(f"📈 Upscaling source image: {current_image_pil.size} → {target_width}×{target_height}")
                    
                    gr.Info(f"Resizing input image to {target_width}×{target_height} before generation.")
                    current_image_pil = current_image_pil.resize((target_width, target_height), resize_method)
                
                image_inputs = current_image_pil
                logging.info(f"🎯 Single image generation: {current_image_pil.size}")
            
            with torch.inference_mode():
                images = kontext_pipeline(
                    image=image_inputs, 
                    prompt=prompt, 
                    num_inference_steps=int(steps),
                    guidance_scale=float(guidance),
                    num_images_per_prompt=int(num_images)
                ).images
            return images
            
        elif model_choice.startswith("Pro"):
            # Handle provider-specific Pro model selection
            provider_info = self._get_pro_provider_info(model_choice)
            provider_name = provider_info['provider_name'] 
            config_key = provider_info['i2i_config_key']
            
            if not api_key: 
                raise gr.Error(f"API Key for {provider_name} is missing!")
            
            # Pro API doesn't support multi-image input - use merged approach for Pro API
            if background_img and object_img:
                # For Pro API: intelligently merge images with ENHANCED scaling for human placement
                # Use preserve_object_scale=True to maintain better object size for human interaction
                merged_input = utils.merge_images_with_smart_scaling(
                    background_img, object_img, 
                    target_size=(target_width, target_height),
                    preserve_object_scale=True  # Enhanced scaling for human placement scenarios
                )
                pil_img = merged_input
                logging.info(f"🔍 Pro API - Using enhanced merged image: {merged_input.size} (Background: {background_img.size} + Object: {object_img.size}) [preserve_object_scale=True]")
                gr.Info(f"Pro API: Using enhanced merged image approach with preserved object scaling (background + object combined)")
            else:
                # Single image for Pro API
                pil_img = Image.fromarray(source_image_np)
                logging.info(f"🔍 Pro API - Source image size: {pil_img.size}")
                
                if pil_img.size != (target_width, target_height):
                    # Quality preservation during resize for Pro API
                    original_pixels = pil_img.size[0] * pil_img.size[1]
                    target_pixels = target_width * target_height
                    
                    if target_pixels < original_pixels:
                        resize_method = Image.LANCZOS
                        logging.info(f"📉 Pro API downscaling: {pil_img.size} → {target_width}×{target_height}")
                    else:
                        resize_method = Image.LANCZOS
                        logging.info(f"📈 Pro API upscaling: {pil_img.size} → {target_width}×{target_height}")
                    
                    pil_img = pil_img.resize((target_width, target_height), resize_method)

            buffered = BytesIO()
            pil_img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Enhanced prompt handling for Pro API to preserve human figures
            enhanced_prompt = self._enhance_prompt_for_pro_api(prompt, object_img, background_img, depth_map, disable_auto_enhancement)
            
            # Add depth information to payload if available
            if depth_map is not None:
                # Convert depth map to base64 for API transmission
                depth_buffer = BytesIO()
                depth_preview = self.depth_processor.create_depth_preview(background_img, depth_map)
                depth_preview.save(depth_buffer, format="PNG")
                depth_str = base64.b64encode(depth_buffer.getvalue()).decode()
                
                payload = {
                    "model": self.config.get('api_models', {}).get(config_key, {}).get('model_name'),
                    "prompt": enhanced_prompt,
                    "input_image": img_str,
                    "depth_map": depth_str,
                    "depth_strength": depth_strength,
                    "num_inference_steps": int(steps),
                    "guidance_scale": float(guidance),
                    "num_images_per_prompt": int(num_images),
                    "api_key": api_key
                }
                logging.info(f"🌊 Pro API - Including depth map with strength {depth_strength}")
            else:
                payload = {
                    "model": self.config.get('api_models', {}).get(config_key, {}).get('model_name'),
                    "prompt": enhanced_prompt,
                    "input_image": img_str,
                    "num_inference_steps": int(steps),
                    "guidance_scale": float(guidance),
                    "num_images_per_prompt": int(num_images),
                    "api_key": api_key
                }
            return self._call_pro_api(payload, config_key, progress)
        else:
            raise ValueError(f"Invalid model choice: {model_choice}")
    
    def _enhance_prompt_for_pro_api(self, prompt, object_img=None, background_img=None, depth_map=None, disable_auto_enhancement=False):
        """
        Enhance prompt for Pro API to better preserve human figures and object identity.
        
        Args:
            prompt: Original user prompt
            object_img: Object image (PIL Image) 
            background_img: Background image (PIL Image)
            depth_map: Generated depth map
            disable_auto_enhancement: Skip automatic enhancement if True
            
        Returns:
            Enhanced prompt with preservation instructions
        """
        # Skip enhancement if disabled
        if disable_auto_enhancement:
            logging.info("🔧 Pro API auto enhancement disabled - using original prompt")
            return prompt
            
        if not object_img:
            return prompt
            
        # Detect if object contains humans/people using multiple approaches
        contains_human = self._detect_human_in_object(object_img)
        
        # Fallback: Check if prompt mentions human-related terms
        human_keywords = ['girl', 'boy', 'man', 'woman', 'person', 'people', 'child', 'kid', 
                         'lady', 'gentleman', 'figure', 'model', 'pose', 'appearance', 
                         'facial', 'face', 'expression', 'clothing', 'dress', 'outfit']
        
        prompt_mentions_human = any(keyword in prompt.lower() for keyword in human_keywords)
        
        # Use either detection result or prompt analysis
        is_human_content = contains_human or prompt_mentions_human
        
        if is_human_content:
            # Add human preservation instructions for Pro API
            preservation_prefix = "IMPORTANT: Preserve the exact appearance, pose, clothing, and identity of the person visible in the image. "
            focus_instruction = "Only modify the background and environment, keeping the person completely unchanged. "
            identity_preservation = "Do not alter the person's face, expression, pose, or any personal characteristics. "
            
            # Add depth-aware instructions if depth map is available
            depth_instruction = ""
            if depth_map is not None:
                depth_instruction = "Maintain realistic spatial depth and lighting relationships between the person and the new background. "
            
            enhanced_prompt = f"{preservation_prefix}{focus_instruction}{identity_preservation}{depth_instruction}{prompt}"
            
            logging.info(f"🧑 Pro API - Human content detected (detection: {contains_human}, prompt: {prompt_mentions_human})")
            logging.info(f"🧑 Original prompt: {prompt}")
            logging.info(f"🧑 Enhanced prompt: {enhanced_prompt}")
            
            return enhanced_prompt
        else:
            # For non-human objects, add general object preservation
            if background_img is not None:
                object_preservation = "Preserve the main object visible in the image while modifying the background. "
                
                # Add depth-aware instructions for objects too
                depth_instruction = ""
                if depth_map is not None:
                    depth_instruction = "Ensure realistic depth relationships and natural lighting between the object and background. "
                
                enhanced_prompt = f"{object_preservation}{depth_instruction}{prompt}"
                logging.info(f"🎯 Pro API - Object preservation with depth: {enhanced_prompt}")
                return enhanced_prompt
            
        return prompt
    
    def _detect_human_in_object(self, object_img):
        """
        Improved heuristic to detect if object image contains humans/people.
        
        This is a basic implementation that could be enhanced with proper 
        object detection models in the future.
        
        Args:
            object_img: PIL Image object
            
        Returns:
            bool: True if likely contains human, False otherwise
        """
        if not object_img:
            return False
            
        # Convert to numpy for analysis
        import numpy as np
        img_array = np.array(object_img)
        
        # Basic heuristics:
        # 1. Check image dimensions - humans typically need reasonable height
        height, width = img_array.shape[:2]
        aspect_ratio = height / width
        
        # 2. Enhanced skin tone detection
        if len(img_array.shape) == 3:
            # Convert to HSV for better skin detection
            from PIL import Image as PILImage
            hsv_img = object_img.convert('HSV')
            hsv_array = np.array(hsv_img)
            
            h = hsv_array[:,:,0]
            s = hsv_array[:,:,1] 
            v = hsv_array[:,:,2]
            
            # Enhanced skin tone detection in HSV space
            # Skin tones typically have:
            # - Hue: 0-25 and 160-179 (reddish/orange tones)
            # - Saturation: 40-255 (not too gray)
            # - Value: 60-255 (not too dark)
            skin_mask = (
                ((h <= 25) | (h >= 160)) &  # Reddish/orange hues
                (s >= 40) & (s <= 255) &    # Reasonable saturation
                (v >= 60) & (v <= 255)      # Not too dark
            )
            
            skin_percentage = np.sum(skin_mask) / (height * width)
            
            # More stringent requirements for human detection
            human_likelihood_skin = skin_percentage > 0.08  # At least 8% skin tone
            
            # Additional RGB-based check for face-like features
            rgb_array = np.array(object_img.convert('RGB'))
            red = rgb_array[:,:,0]
            green = rgb_array[:,:,1] 
            blue = rgb_array[:,:,2]
            
            # Check for typical human skin RGB ranges
            skin_rgb_mask = (
                (red >= 80) & (red <= 255) &
                (green >= 50) & (green <= 220) &
                (blue >= 30) & (blue <= 200) &
                (red > green) & (green >= blue) &  # Typical skin color relationship
                ((red - green) >= 10) & ((green - blue) >= 5)  # Color separation
            )
            
            skin_rgb_percentage = np.sum(skin_rgb_mask) / (height * width)
            human_likelihood_rgb = skin_rgb_percentage > 0.05  # At least 5% skin-like RGB
            
            # Aspect ratio check - humans can be in various poses
            human_aspect_ratio = 0.2 < aspect_ratio < 5.0  # Broader range for various poses
            
            # Size check: image should be large enough to contain meaningful human figure
            min_size_check = min(height, width) > 80  # At least 80px in smaller dimension
            
            # Edge density check - humans have more complex edges than simple objects
            # Simple edge detection using gradient
            gray_array = np.array(object_img.convert('L'))
            grad_x = np.abs(np.gradient(gray_array, axis=1))
            grad_y = np.abs(np.gradient(gray_array, axis=0))
            edge_density = np.mean(grad_x + grad_y)
            complex_edges = edge_density > 8  # Humans typically have more complex edge patterns
            
            # Combine all checks - require multiple positive indicators
            skin_detected = human_likelihood_skin or human_likelihood_rgb
            basic_requirements = human_aspect_ratio and min_size_check
            
            # Final decision: need skin + basic requirements + reasonable complexity
            final_detection = skin_detected and basic_requirements and complex_edges
            
            logging.info(f"🧑 Enhanced human detection analysis:")
            logging.info(f"   - Image size: {width}×{height}, aspect ratio: {aspect_ratio:.2f}")
            logging.info(f"   - HSV skin percentage: {skin_percentage:.3f} ({skin_percentage*100:.1f}%)")
            logging.info(f"   - RGB skin percentage: {skin_rgb_percentage:.3f} ({skin_rgb_percentage*100:.1f}%)")
            logging.info(f"   - HSV skin detected: {human_likelihood_skin}")
            logging.info(f"   - RGB skin detected: {human_likelihood_rgb}")
            logging.info(f"   - Overall skin detected: {skin_detected}")
            logging.info(f"   - Aspect ratio OK: {human_aspect_ratio}")
            logging.info(f"   - Size check: {min_size_check}")
            logging.info(f"   - Edge density: {edge_density:.2f}, complex: {complex_edges}")
            logging.info(f"   - Final detection: {final_detection}")
            
            return final_detection
            
        return False