import torch
import gradio as gr
from diffusers import FluxPipeline, FluxKontextPipeline
from transformers import AutoTokenizer
from nunchaku import NunchakuFluxTransformer2dModel
from nunchaku.utils import get_precision
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

class Generator:
    def __init__(self, config):
        self.config = config
        self.pipeline = None
        self.kontext_pipeline = None
        self.tokenizer = None
        self._load_local_i2i_pipeline()

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
        headers = {"x-key": api_key, "Content-Type": "application/json"}
        
        try:
            progress(0, desc="Sending request to Pro API...")
            post_response = requests.post(full_endpoint, headers=headers, json=payload, timeout=120)
            post_response.raise_for_status()
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
        elif model_choice == const.PRO_MODEL:
            if not api_key: raise gr.Error(f"API Key for {const.FLUX_PRO_API} is missing!")
            payload = {
                "model": self.config.get('api_models', {}).get('pro_t2i', {}).get('model_name'),
                "prompt": prompt,
                "num_inference_steps": int(steps),
                "guidance_scale": float(guidance),
                "num_images_per_prompt": int(num_images),
                "width": int(width),
                "height": int(height),
                "api_key": api_key
            }
            return self._call_pro_api(payload, 'pro_t2i', progress)
        else:
            raise ValueError(f"Invalid model choice: {model_choice}")
            
    def image_to_image(self, source_image_np, prompt, steps, guidance, model_choice, num_images, width, height, api_key="", background_img=None, object_img=None, aspect_ratio_setting="1:1", progress=gr.Progress()):
        """Enhanced image-to-image generation with smart dimension handling"""
        
        # Debug logging for input analysis
        if background_img is not None:
            logging.info(f"🔍 Input analysis - Background: {background_img.size}, Object: {object_img.size if object_img else 'None'}")
            logging.info(f"🔍 Requested dimensions: {width}×{height}, Aspect ratio setting: {aspect_ratio_setting}")
        
        # Determine optimal generation size using hybrid approach
        if background_img is not None:
            # Use smart dimension calculation based on background
            optimal_size = self._determine_safe_generation_size(background_img, aspect_ratio_setting, model_choice)
            target_width, target_height = optimal_size
            
            # Provide user feedback about dimension choice
            if optimal_size == background_img.size:
                gr.Info(f"✅ Using background dimensions: {target_width}×{target_height}")
            else:
                gr.Info(f"📐 Optimized dimensions: {target_width}×{target_height} (scaled from {background_img.size[0]}×{background_img.size[1]} for performance)")
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
            
        elif model_choice == const.PRO_MODEL:
            if not api_key: raise gr.Error(f"API Key for {const.FLUX_PRO_API} is missing!")
            
            # Pro API doesn't support multi-image input - use merged approach for Pro API
            if background_img and object_img:
                # For Pro API: intelligently merge images with proper scaling
                # Use target dimensions for merging to avoid distortion
                merged_input = utils.merge_images_with_smart_scaling(background_img, object_img, target_size=(target_width, target_height))
                pil_img = merged_input
                logging.info(f"🔍 Pro API - Using merged image: {merged_input.size} (Background: {background_img.size} + Object: {object_img.size})")
                gr.Info(f"Pro API: Using merged image approach (background + object combined)")
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
            
            payload = {
                "model": self.config.get('api_models', {}).get('pro_i2i', {}).get('model_name'),
                "prompt": prompt,
                "input_image": img_str,
                "num_inference_steps": int(steps),
                "guidance_scale": float(guidance),
                "num_images_per_prompt": int(num_images),
                "api_key": api_key
            }
            return self._call_pro_api(payload, 'pro_i2i', progress)
        else:
            raise ValueError(f"Invalid model choice: {model_choice}")