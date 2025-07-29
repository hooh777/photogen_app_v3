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
from core import constants as const

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

    def text_to_image(self, prompt, steps, guidance, model_choice, num_images, api_key="", progress=gr.Progress(track_tqdm=True)):
        if model_choice == const.LOCAL_MODEL:
            pipeline = self._load_local_t2i_pipeline()
            if pipeline is None:
                raise gr.Error("Local Text-to-Image pipeline could not be loaded.")
            with torch.inference_mode():
                images = pipeline(
                    prompt=prompt, 
                    num_inference_steps=int(steps), 
                    guidance_scale=float(guidance),
                    num_images_per_prompt=int(num_images)
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
                "api_key": api_key
            }
            return self._call_pro_api(payload, 'pro_t2i', progress)
        else:
            raise ValueError(f"Invalid model choice: {model_choice}")
            
    def image_to_image(self, source_image_np, prompt, steps, guidance, model_choice, num_images, width, height, api_key="", progress=gr.Progress()):
        if model_choice == const.LOCAL_MODEL:
            kontext_pipeline = self._load_local_i2i_pipeline()
            if kontext_pipeline is None:
                raise gr.Error("Local Image-to-Image pipeline could not be loaded.")
            
            current_image_pil = Image.fromarray(source_image_np)
            
            # Resize the input image to match the target dimensions before generation
            if current_image_pil.size != (width, height):
                gr.Info(f"Resizing input image to {width}x{height} before generation.")
                current_image_pil = current_image_pil.resize((width, height), Image.LANCZOS)
            
            with torch.inference_mode():
                images = kontext_pipeline(
                    image=current_image_pil, 
                    prompt=prompt, 
                    num_inference_steps=int(steps),
                    guidance_scale=float(guidance),
                    num_images_per_prompt=int(num_images)
                ).images
            return images
            
        elif model_choice == const.PRO_MODEL:
            if not api_key: raise gr.Error(f"API Key for {const.FLUX_PRO_API} is missing!")
            
            pil_img = Image.fromarray(source_image_np)
            if pil_img.size != (width, height):
                pil_img = pil_img.resize((width, height), Image.LANCZOS)

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