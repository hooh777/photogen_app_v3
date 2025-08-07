# core/enhancer.py
import os
import abc
from openai import OpenAI
from PIL import Image
import numpy as np
import logging

from core import constants as const
import requests
import json

class Enhancer(abc.ABC):
    """Abstract base class for all prompt enhancers."""
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.setup_client()

    @abc.abstractmethod
    def setup_client(self):
        """Sets up the specific API client."""
        pass

    @abc.abstractmethod
    def enhance(self, base_prompt, image=None):
        """The main method to enhance a prompt, now accepting an optional image."""
        pass

    def get_instruction(self, base_prompt, has_image=False):
        """Generates a universal instruction for any LLM by reading from prompt_guide.md."""
        image_context_instruction = (
            "You have been provided with an image. First, briefly analyze the key subjects, style, and composition of the image. "
            "Then, use that analysis to inform your three prompt variations. The prompts should be relevant to modifying or building upon the provided image."
            if has_image
            else ""
        )

        try:
            with open('prompt_guide.md', 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logging.error("prompt_guide.md not found. Please ensure the file exists in the main project directory.")
            # Fallback to a basic instruction if the file is missing
            prompt_template = """
            Please enhance this image generation prompt: "{base_prompt}"
            
            Provide three enhanced versions:
            1. **Detailed Version**: Add specific details about lighting, composition, and technical aspects
            2. **Stylized Version**: Apply artistic style and mood enhancements 
            3. **Rephrased Version**: Rewrite with better structure and flow
            
            Format your response exactly as:
            **Detailed:** [enhanced prompt]
            **Stylized:** [enhanced prompt]  
            **Rephrased:** [enhanced prompt]
            """

        return prompt_template.format(
            image_context_instruction=image_context_instruction,
            base_prompt=base_prompt
        )

    def parse_response(self, text):
        """Parses the LLM's response text into three prompt variations."""
        try:
            # Look for the formatted response pattern
            lines = text.split('\n')
            detailed = ""
            stylized = ""
            rephrased = ""
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('**Detailed:**'):
                    detailed = line.replace('**Detailed:**', '').strip()
                    current_section = 'detailed'
                elif line.startswith('**Stylized:**'):
                    stylized = line.replace('**Stylized:**', '').strip()
                    current_section = 'stylized'
                elif line.startswith('**Rephrased:**'):
                    rephrased = line.replace('**Rephrased:**', '').strip()
                    current_section = 'rephrased'
                elif line and current_section:
                    # Continue previous section if no new marker found
                    if current_section == 'detailed' and not detailed:
                        detailed = line
                    elif current_section == 'stylized' and not stylized:
                        stylized = line
                    elif current_section == 'rephrased' and not rephrased:
                        rephrased = line
            
            # Fallback to simple split if structured parsing fails
            if not detailed or not stylized or not rephrased:
                parts = text.split('---')
                detailed = detailed or (parts[0].strip() if len(parts) > 0 else "Enhanced version of the prompt")
                stylized = stylized or (parts[1].strip() if len(parts) > 1 else "Stylized version of the prompt")
                rephrased = rephrased or (parts[2].strip() if len(parts) > 2 else "Rephrased version of the prompt")
            
            return detailed, stylized, rephrased
            
        except Exception as e:
            logging.error(f"Error parsing response: {e}")
            return "Could not generate detailed version.", "Could not generate stylized version.", "Could not generate rephrased version."

class QwenVLMaxEnhancer(Enhancer):
    def setup_client(self):
        # No client setup needed for DashScope API - we use requests directly
        pass
    
    def enhance(self, base_prompt, image=None):
        if image is not None:
            return self._enhance_with_vision(base_prompt, image)
        else:
            return self._enhance_text_only(base_prompt)
    
    def _enhance_text_only(self, base_prompt):
        """Text-only prompt enhancement using Qwen-VL-Max."""
        instruction = self.get_instruction(base_prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-max",  # Use text-only model for text enhancement
            "input": {
                "messages": [
                    {"role": "user", "content": instruction}
                ]
            },
            "parameters": {
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'output' in result and 'choices' in result['output']:
                    content = result['output']['choices'][0]['message']['content']
                    return self.parse_response(content)
                else:
                    logging.error("Unexpected response format from Qwen-Max")
                    return f"API Error: Unexpected response format", f"API Error: Unexpected response format", f"API Error: Unexpected response format"
            else:
                logging.error(f"Qwen-Max API error: {response.status_code} - {response.text}")
                return f"API Error: {response.status_code}", f"API Error: {response.status_code}", f"API Error: {response.status_code}"
                
        except Exception as e:
            logging.error("Qwen-Max API Error", exc_info=True)
            return f"API Error: {e}", f"API Error: {e}", f"API Error: {e}"
    
    def _enhance_with_vision(self, base_prompt, image):
        """Vision-enhanced prompt generation using Qwen-VL-Max."""
        import base64
        from io import BytesIO
        from PIL import Image as PILImage
        
        # Convert numpy array to PIL Image if needed
        if isinstance(image, np.ndarray):
            pil_image = PILImage.fromarray(image)
        else:
            pil_image = image
            
        # Convert to base64
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        vision_instruction = f"""
        I want to improve this image generation prompt: "{base_prompt}"
        
        Please analyze the provided image and provide three enhanced versions:
        1. **Detailed Version**: Add specific details about lighting, composition, and technical aspects based on what you see
        2. **Stylized Version**: Apply artistic style and mood enhancements that complement the image
        3. **Rephrased Version**: Rewrite with better structure and flow while maintaining visual consistency
        
        Format your response exactly as:
        **Detailed:** [enhanced prompt]
        **Stylized:** [enhanced prompt]  
        **Rephrased:** [enhanced prompt]
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-vl-max",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": vision_instruction},
                            {"image": f"data:image/png;base64,{img_base64}"}
                        ]
                    }
                ]
            },
            "parameters": {
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'output' in result and 'choices' in result['output']:
                    content = result['output']['choices'][0]['message']['content']
                    return self.parse_response(content)
                else:
                    logging.error("Unexpected response format from Qwen-VL-Max")
                    # Fallback to text-only enhancement
                    logging.info("Falling back to text-only enhancement...")
                    return self._enhance_text_only(base_prompt)
            else:
                logging.error(f"Qwen-VL-Max API error: {response.status_code} - {response.text}")
                # Fallback to text-only enhancement
                logging.info("Falling back to text-only enhancement...")
                return self._enhance_text_only(base_prompt)
                
        except Exception as e:
            logging.error("Qwen-VL-Max Vision API Error", exc_info=True)
            # Fallback to text-only enhancement
            logging.info("Falling back to text-only enhancement...")
            return self._enhance_text_only(base_prompt)

ENHANCER_MAP = {
    const.QWEN_VL_MAX: QwenVLMaxEnhancer,
}

def get_enhancer(provider_name, api_key):
    enhancer_class = ENHANCER_MAP.get(provider_name)
    if not enhancer_class:
        raise ValueError(f"Invalid provider selected: {provider_name}. Available providers: {list(ENHANCER_MAP.keys())}")
    return enhancer_class(api_key=api_key)