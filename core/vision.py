from openai import OpenAI
from PIL import Image
import base64
from io import BytesIO
import logging

def analyze_image_region(image: Image.Image, provider_name: str, api_key: str):
    """
    Analyzes an image region using a specified vision model provider.
    Currently supports Grok (x.ai).
    """
    if "Grok" not in provider_name:
        raise ValueError(f"{provider_name} is not supported for this vision task. Please use a Grok model.")

    if not api_key:
        raise ValueError("API key is required for vision analysis.")

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    
    # Convert PIL Image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    try:
        logging.info("Sending image region to Grok for analysis...")
        response = client.chat.completions.create(
            model="grok-1.5-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe the main object or surface in this image in a very short, simple phrase suitable for an image generation prompt (e.g., 'on a wooden table', 'in a grassy field', 'on a sandy beach')."
                        },
                        {
                            "type": "image_url",
                            "image_url": { "url": f"data:image/png;base64,{img_base64}" }
                        }
                    ]
                }
            ],
            max_tokens=20
        )
        description = response.choices[0].message.content.strip()
        logging.info(f"Grok analysis received: {description}")
        return description

    except Exception as e:
        logging.error(f"Grok vision API call failed: {e}", exc_info=True)
        return "at the selected location"