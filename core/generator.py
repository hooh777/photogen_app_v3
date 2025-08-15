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

class Generator:
    def __init__(self, config):
        self.config = config
        self.pipeline = None
        self.kontext_pipeline = None
        self.tokenizer = None
        # Lazy loading - only load when actually needed for better startup time
        
        # Depth processing disabled (module removed)
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
        """Simplified dimension selection with safety checks"""
        if background_img is None:
            return utils.get_dimensions(aspect_ratio_setting)
        
        bg_size = background_img.size
        bg_pixels = bg_size[0] * bg_size[1]
        bg_ratio = bg_size[0] / bg_size[1]
        
        logging.info(f"🔍 Background: {bg_size[0]}×{bg_size[1]} ({bg_pixels:,} pixels, ratio: {bg_ratio:.2f})")
        
        # Set limits based on model choice
        if model_choice == const.PRO_MODEL:
            MAX_PIXELS = 2048 * 2048
            MAX_DIM = 2048
        else:
            MAX_PIXELS = 1536 * 1536
            MAX_DIM = 1536
            
        MIN_PIXELS = 512 * 512
        MIN_RATIO, MAX_RATIO = 0.3, 3.5
        
        # Check if we can use original size
        if (bg_pixels <= MAX_PIXELS and 
            bg_size[0] <= MAX_DIM and bg_size[1] <= MAX_DIM and
            MIN_RATIO <= bg_ratio <= MAX_RATIO and
            bg_pixels >= MIN_PIXELS):
            logging.info(f"✅ Using original size: {bg_size[0]}×{bg_size[1]}")
            return bg_size
        
        # Handle extreme aspect ratios
        if not (MIN_RATIO <= bg_ratio <= MAX_RATIO):
            logging.warning(f"⚠️ Extreme aspect ratio {bg_ratio:.2f}, using fallback dimensions")
            return utils.get_dimensions(aspect_ratio_setting)
        
        # Scale down if too large, scale up if too small
        if bg_pixels > MAX_PIXELS or max(bg_size) > MAX_DIM:
            scale_factor = min(math.sqrt(MAX_PIXELS / bg_pixels), MAX_DIM / max(bg_size))
        elif bg_pixels < MIN_PIXELS:
            scale_factor = math.sqrt(MIN_PIXELS / bg_pixels)
        else:
            return bg_size
            
        # Apply scaling and ensure multiple of 64
        new_width = max(512, ((int(bg_size[0] * scale_factor) + 63) // 64) * 64)
        new_height = max(512, ((int(bg_size[1] * scale_factor) + 63) // 64) * 64)
        
        logging.info(f"📐 Scaled: {bg_size[0]}×{bg_size[1]} → {new_width}×{new_height}")
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
            logging.info(f"🌐 === API REQUEST DEBUG ===")
            logging.info(f"🌐 Full Endpoint: {full_endpoint}")
            logging.info(f"🌐 Request Headers: {headers}")
            logging.info(f"🌐 Payload Keys: {list(payload.keys())}")
            logging.info(f"🌐 Payload Model: {payload.get('model', 'Unknown')}")
            logging.info(f"🌐 Payload Steps: {payload.get('num_inference_steps', 'Unknown')}")
            logging.info(f"🌐 Payload Guidance: {payload.get('guidance_scale', 'Unknown')}")
            
            post_response = requests.post(full_endpoint, headers=headers, json=payload, timeout=120)
            post_response.raise_for_status()
            
            logging.info(f"🌐 Response Status: {post_response.status_code}")
            logging.info(f"🌐 Response Content Preview: {post_response.text[:500]}...")
            logging.info(f"🌐 === END API REQUEST DEBUG ===")
            
            polling_url = post_response.json().get('polling_url')
            if not polling_url:
                raise gr.Error(f"API did not return a polling URL. Response: {post_response.text}")
        except requests.exceptions.Timeout:
            logging.error("⏰ API Request Timeout - Server took too long to respond")
            raise gr.Error("⏰ API Timeout: The server is taking too long to respond. Please try again in a moment, or consider switching to a different model provider.")
        except requests.exceptions.HTTPError as e:
            response_text = e.response.text if e.response else "N/A"
            status_code = e.response.status_code if e.response else "Unknown"
            
            if status_code == 504:
                logging.error("🚪 Gateway Timeout (504) - API server is overloaded or unavailable")
                raise gr.Error("🚪 Server Timeout (504): The API server is currently overloaded or temporarily unavailable. Please try again in a few minutes, or switch to 'Pro (Black Forest Labs)' model.")
            elif status_code == 503:
                logging.error("🔧 Service Unavailable (503) - API server is down for maintenance")  
                raise gr.Error("🔧 Service Unavailable (503): The API server is temporarily down for maintenance. Please try again later or use a different model.")
            elif status_code == 429:
                logging.error("⚡ Rate Limited (429) - Too many requests")
                raise gr.Error("⚡ Rate Limited (429): Too many requests. Please wait a moment before trying again.")
            else:
                logging.error(f"❌ HTTP Error {status_code}: {e}")
                raise gr.Error(f"❌ API Error ({status_code}): {e}\n\nTry switching to 'Pro (Black Forest Labs)' model or try again later.")
        except requests.exceptions.ConnectionError:
            logging.error("🌐 Connection Error - Cannot reach API server")
            raise gr.Error("🌐 Connection Error: Cannot reach the API server. Please check your internet connection and try again.")
        except requests.exceptions.RequestException as e:
            response_text = e.response.text if e.response else "N/A"
            logging.error("❌ API Request Error", exc_info=True)
            raise gr.Error(f"❌ API Request Error: {e}\n\nResponse: {response_text}\n\nTry switching to a different model provider.")
        
        # Polling loop with improved error handling
        for i in range(60):
            try:
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
                
            except requests.exceptions.Timeout:
                logging.warning(f"⏰ Polling timeout on attempt {i+1}/60")
                if i >= 55:  # Last few attempts
                    raise gr.Error("⏰ Polling Timeout: Server is taking too long to process your request. Please try again.")
            except requests.exceptions.RequestException as e:
                logging.warning(f"🌐 Polling error on attempt {i+1}/60: {e}")
                if i >= 55:  # Last few attempts  
                    raise gr.Error(f"🌐 Polling Error: {e}")
            
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
            
    def image_to_image(self, source_image_np, prompt, steps, guidance, model_choice, num_images, width, height, api_key="", background_img=None, object_img=None, aspect_ratio_setting="1:1", progress=gr.Progress()):
        """Enhanced image-to-image generation with smart dimension handling and depth control"""
        
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
                
                # DETAILED LOGGING for debugging
                logging.info(f"🔍 === PRO API MULTI-IMAGE DEBUG ===")
                logging.info(f"🔍 Background Image: {background_img.size} {background_img.mode}")
                logging.info(f"🔍 Object Image: {object_img.size} {object_img.mode}")
                logging.info(f"🔍 Merged Result: {merged_input.size} {merged_input.mode}")
                logging.info(f"🔍 Target Dimensions: {target_width}×{target_height}")
                logging.info(f"🔍 === END DEBUG ===")
                
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
            
            # DETAILED API PAYLOAD LOGGING
            logging.info(f"🚀 === PRO API PAYLOAD DEBUG ===")
            logging.info(f"🚀 Model: {self.config.get('api_models', {}).get(config_key, {}).get('model_name')}")
            logging.info(f"🚀 Prompt: '{prompt}'")
            logging.info(f"🚀 Prompt Length: {len(prompt)} characters")
            logging.info(f"🚀 Steps: {int(steps)}")
            logging.info(f"🚀 Guidance: {float(guidance)}")
            logging.info(f"🚀 Num Images: {int(num_images)}")
            logging.info(f"🚀 Image Size Being Sent: {pil_img.size}")
            logging.info(f"🚀 Image Mode: {pil_img.mode}")
            logging.info(f"🚀 Base64 Image Length: {len(img_str)} characters")
            logging.info(f"🚀 Config Key: {config_key}")
            logging.info(f"🚀 === END API PAYLOAD DEBUG ===")
            
            payload = {
                "model": self.config.get('api_models', {}).get(config_key, {}).get('model_name'),
                "prompt": prompt,
                "input_image": img_str,
                "num_inference_steps": int(steps),
                "guidance_scale": float(guidance),
                "num_images_per_prompt": int(num_images),
                "api_key": api_key
            }
            
            return self._call_pro_api(payload, config_key, progress)
        else:
            raise ValueError(f"Invalid model choice: {model_choice}")