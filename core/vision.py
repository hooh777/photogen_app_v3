from openai import OpenAI
from PIL import Image
import base64
from io import BytesIO
import logging
import numpy as np
import requests
import json

def analyze_image_region(background_image: Image.Image, object_image: Image.Image, provider_name: str, api_key: str, selection_coords=None):
    """
    Analyzes where an object will be placed in a background scene using contextual spatial analysis.
    Supports Qwen-VL-Max (Alibaba Cloud) and Grok models.
    
    Args:
        background_image: The background scene with selection box overlay
        object_image: The object to be placed (can be None for surface analysis only)
        provider_name: Vision model provider
        api_key: API key for the provider
        selection_coords: Optional coordinates for additional context
    """
    if "Qwen-VL-Max" in provider_name:
        return _analyze_with_qwen_vl_max(background_image, object_image, api_key, selection_coords)
    elif "Grok" in provider_name:
        return _analyze_with_grok(background_image, object_image, provider_name, api_key, selection_coords)
    else:
        raise ValueError(f"{provider_name} is not supported for this vision task. Please use Qwen-VL-Max or a Grok model.")

def _analyze_with_qwen_vl_max(background_image: Image.Image, object_image: Image.Image, api_key: str, selection_coords=None):
    """
    Analyzes where an object will be placed in a background scene using contextual spatial analysis.
    Uses OpenAI-compatible format for international Alibaba Cloud accounts.
    """
    if not api_key:
        raise ValueError("API key is required for Qwen-VL-Max analysis.")

    # Convert background image to base64
    buffered = BytesIO()
    background_image.save(buffered, format="PNG")
    bg_img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Prepare content array with background image
    content = [
        {
            "type": "text",
            "text": """Analyze the background scene and describe where the object will be positioned. 

Look at the background image which shows a scene with a blue selection box indicating the placement location."""
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{bg_img_base64}"
            }
        }
    ]
    
    # Add object image if provided
    if object_image is not None:
        obj_buffered = BytesIO()
        object_image.save(obj_buffered, format="PNG")
        obj_img_base64 = base64.b64encode(obj_buffered.getvalue()).decode('utf-8')
        
        content.insert(1, {
            "type": "text", 
            "text": "Here is the object that will be placed:"
        })
        content.insert(2, {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{obj_img_base64}"
            }
        })
        
        # Enhanced prompt for object placement
        content[0]["text"] = """You will see two images:
1. A background scene with a blue selection box showing the placement location
2. The object that will be placed there

Describe the SURFACE TYPE only for object placement in around 10 words or less.

Format: "on the [surface type]" or "in the [immediate area]"

Examples:
- "on the existing surface"
- "on the wooden surface"
- "on the fabric surface"
- "in the grass area"
- "on the stone surface"
- "on the metal surface"

Focus ONLY on:
- Surface material type (wood, fabric, grass, stone, metal, glass, etc.)
- Use "existing surface" if surface type is unclear

DO NOT mention rooms, furniture names, or scene descriptions.
Keep it extremely concise - surface type only."""

    else:
        # Fallback for surface analysis only
        content[0]["text"] = """Analyze the background scene and describe only the SURFACE TYPE in the selected area (marked with blue box) in around 10 words or less.

Be SPECIFIC about SURFACE MATERIAL only:
- Surface material (wooden, marble, fabric, stone, glass, metal, grass, etc.)

Format: "on the [surface type]" or "in the [immediate area type]"

Examples:
- "on the wooden surface"
- "on the marble surface" 
- "on the fabric surface"
- "in the grass area"
- "on the stone surface"
- "on the existing surface"

DO NOT mention:
- Room names (kitchen, living room, etc.)
- Furniture names (table, sofa, etc.)
- Scene descriptions or context

Keep it focused - surface material type only."""

    try:
        logging.info("Sending contextual scene analysis to Qwen-VL-Max...")
        
        # Use OpenAI client with Alibaba Cloud International endpoint
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
        
        completion = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=300,
            temperature=0.5
        )
        
        if completion.choices and len(completion.choices) > 0:
            description = completion.choices[0].message.content.strip()
            
            # Extract placement description from the response
            if object_image is not None:
                # For object placement analysis - look for multiple patterns
                if "will be" in description:
                    # Extract everything after "will be"
                    placement_parts = description.split("will be", 1)
                    if len(placement_parts) > 1:
                        placement_desc = placement_parts[1].strip().rstrip('.')
                    else:
                        placement_desc = "in the selected location"
                elif "placed" in description:
                    # Alternative pattern: "object placed [location]"
                    placement_parts = description.split("placed", 1)
                    if len(placement_parts) > 1:
                        placement_desc = placement_parts[1].strip().rstrip('.')
                    else:
                        placement_desc = "in the selected location"
                else:
                    # Use the full description but try to extract spatial context
                    # Remove common prefixes to get to the spatial description
                    cleaned = description.replace("The selected area is", "").replace("The area is", "").strip()
                    if cleaned:
                        placement_desc = cleaned.rstrip('.')
                    else:
                        placement_desc = "in the selected area"
            else:
                # For surface analysis only
                if "selected area is" in description:
                    placement_parts = description.split("selected area is", 1)
                    if len(placement_parts) > 1:
                        placement_desc = placement_parts[1].strip().rstrip('.')
                    else:
                        placement_desc = "in the selected location"
                elif "area is" in description:
                    placement_parts = description.split("area is", 1)
                    if len(placement_parts) > 1:
                        placement_desc = placement_parts[1].strip().rstrip('.')
                    else:
                        placement_desc = "in the selected location"
                else:
                    # Use the full description but clean it up
                    placement_desc = description.strip().rstrip('.')
            
            # Clean up the placement description
            if placement_desc.startswith("on ") or placement_desc.startswith("in ") or placement_desc.startswith("near ") or placement_desc.startswith("at "):
                final_placement = placement_desc
            else:
                final_placement = f"on {placement_desc}"
            
            # Keep the full detailed analysis - no truncation
            logging.info(f"Qwen-VL-Max contextual analysis: '{description}'")
            logging.info(f"Extracted placement: '{final_placement}'")
            return final_placement
        else:
            logging.warning("No response from Qwen-VL-Max")
            return "in the selected area"

    except Exception as e:
        logging.error(f"Qwen-VL-Max contextual analysis failed: {e}", exc_info=True)
        return "in the selected area"

def _analyze_with_grok(image: Image.Image, provider_name: str, api_key: str):
    """
    Analyzes an image using Grok vision models (fallback option).
    """
    if not api_key:
        raise ValueError("API key is required for Grok analysis.")

    # Convert PIL Image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    try:
        logging.info(f"Sending image region to {provider_name} for analysis...")
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        
        response = client.chat.completions.create(
            model="grok-vision-beta",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image and describe what you see, focusing on:
1. Overall scene and environment
2. Surface types and materials
3. Suitable placement areas for objects

Respond with a brief description suitable for image editing placement."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        if response.choices and len(response.choices) > 0:
            description = response.choices[0].message.content.strip()
            
            # Convert to simple placement format
            if any(word in description.lower() for word in ['grass', 'field', 'lawn']):
                placement_desc = "in the grass area"
            elif any(word in description.lower() for word in ['stone', 'rock', 'granite']):
                placement_desc = "on the stone surface"
            elif any(word in description.lower() for word in ['wood', 'wooden', 'table']):
                placement_desc = "on the wooden surface"
            elif any(word in description.lower() for word in ['water', 'lake', 'river']):
                placement_desc = "near the water"
            else:
                placement_desc = "on the selected surface"
            
            logging.info(f"Grok analysis: '{description}' -> '{placement_desc}'")
            return placement_desc
        else:
            logging.warning(f"No response from {provider_name}")
            return "on the selected surface"

    except Exception as e:
        logging.error(f"Grok API call failed: {e}", exc_info=True)
        return "on the selected surface"
