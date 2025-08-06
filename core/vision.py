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

Please provide a detailed analysis of the scene and placement area. Describe:

1. **Overall Scene**: What type of environment/setting this is
2. **Background Context**: The broader scene and surroundings  
3. **Selection Area Details**: What's specifically in the blue selection box area
4. **Surface Analysis**: The material, texture, and characteristics of the surface where the object will be placed
5. **Spatial Context**: How this area relates to the overall scene
6. **Placement Suitability**: Any relevant details about placing objects in this location

Be thorough and detailed in your description. Include all observations about the scene, surfaces, lighting, materials, and spatial relationships. Don't limit your response - provide complete context and analysis."""

    else:
        # Fallback for surface analysis only
        content[0]["text"] = """Analyze the background scene and provide a detailed description focusing on the selected area (marked with blue box).

Please describe:

1. **Overall Scene**: What type of environment/setting this is (indoor/outdoor, specific location type)
2. **Scene Context**: The broader background and surroundings
3. **Selection Area Analysis**: Detailed description of what's in the blue selection box
4. **Surface Details**: Material type, texture, color, condition of the surface in the selection area
5. **Spatial Relationships**: How the selected area relates to surrounding elements
6. **Environmental Factors**: Lighting, shadows, any other relevant visual details
7. **Material Classification**: Specific material identification (wood, marble, fabric, grass, stone, concrete, metal, etc.)

Be comprehensive and detailed. Provide complete context about the scene and the specific area marked for analysis. Include all relevant observations about materials, textures, spatial context, and environmental factors."""

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


# ============================================================================
# AUTO PROMPT GENERATION SYSTEM
# ============================================================================

def analyze_scene_for_prompting(background_image: Image.Image, provider_name: str, api_key: str, selection_coords=None):
    """
    Enhanced scene analysis specifically for auto prompt generation.
    Identifies people, objects, materials, lighting, style, and context.
    
    Returns a detailed scene analysis dictionary with all context needed for prompt generation.
    """
    if not api_key:
        raise ValueError("API key is required for scene analysis.")

    # Convert background image to base64
    buffered = BytesIO()
    background_image.save(buffered, format="PNG")
    bg_img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    try:
        logging.info("Analyzing scene for auto prompt generation...")
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
        
        completion = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image for auto prompt generation. Focus on the selected area (blue box) and provide detailed analysis in this exact JSON format:

{
  "environment": {
    "type": "indoor/outdoor",
    "location": "specific location description",
    "time_of_day": "morning/afternoon/evening/night",
    "weather": "sunny/cloudy/rainy/etc or N/A for indoor"
  },
  "people": {
    "present": true/false,
    "count": 0,
    "descriptions": ["person 1 description", "person 2 description"],
    "activities": ["what they're doing"],
    "clothing_style": "casual/formal/sporty/etc"
  },
  "selection_area": {
    "surface_material": "wood/stone/fabric/metal/grass/concrete/etc",
    "texture": "smooth/rough/soft/hard/weathered/polished/etc",
    "color": "dominant color description",
    "condition": "new/worn/vintage/damaged/pristine/etc",
    "size": "small/medium/large surface area"
  },
  "lighting": {
    "type": "natural/artificial/mixed",
    "direction": "front/back/side/overhead/ambient",
    "quality": "bright/dim/dramatic/soft/harsh",
    "shadows": "strong/soft/minimal/none"
  },
  "style_mood": {
    "overall_style": "modern/rustic/elegant/casual/industrial/vintage/etc",
    "atmosphere": "cozy/formal/relaxed/energetic/serene/busy/etc",
    "color_palette": "warm/cool/neutral/vibrant/muted"
  },
  "context_details": {
    "surrounding_objects": ["visible objects near selection"],
    "spatial_relationship": "how selection area relates to scene",
    "purpose": "dining/working/relaxing/cooking/etc",
    "formality_level": "very casual/casual/semi-formal/formal/very formal"
  }
}

Provide only the JSON response, no additional text."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{bg_img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        if completion.choices and len(completion.choices) > 0:
            response_text = completion.choices[0].message.content.strip()
            
            try:
                # Try to extract JSON from response - look for JSON block
                import json
                import re
                
                # Log the raw response for debugging
                logging.info(f"Raw scene analysis response: {response_text}")
                
                # Try to find JSON within the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    scene_analysis = json.loads(json_text)
                    logging.info(f"Successfully parsed JSON scene analysis")
                    return scene_analysis
                else:
                    # If no JSON found, try parsing the whole response
                    scene_analysis = json.loads(response_text)
                    logging.info(f"Successfully parsed full response as JSON")
                    return scene_analysis
                    
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse JSON response: {e}")
                logging.info("Converting text response to structured analysis...")
                return _parse_text_to_scene_analysis(response_text)
        else:
            logging.warning("No response from vision model")
            return _create_fallback_scene_analysis()

    except Exception as e:
        logging.error(f"Scene analysis failed: {e}")
        return _create_fallback_scene_analysis()


def generate_auto_prompt(scene_analysis: dict, object_description: str, style_preferences: dict = None):
    """
    Generates contextual prompts based on scene analysis.
    
    Args:
        scene_analysis: Dict from analyze_scene_for_prompting()
        object_description: Basic description of object to place (e.g., "coffee cup")
        style_preferences: Optional style preferences {"realism": "high", "artistic_style": "photorealistic"}
    
    Returns:
        Enhanced prompt string ready for image generation
    """
    if not scene_analysis or not object_description:
        return object_description
    
    # Extract key scene elements
    environment = scene_analysis.get('environment', {})
    people = scene_analysis.get('people', {})
    selection_area = scene_analysis.get('selection_area', {})
    lighting = scene_analysis.get('lighting', {})
    style_mood = scene_analysis.get('style_mood', {})
    context = scene_analysis.get('context_details', {})
    
    # Build enhanced prompt components
    prompt_parts = []
    
    # 1. Core object with material matching
    material = selection_area.get('surface_material', '')
    
    # Smart material integration
    if material and material != 'unknown' and material != 'general surface':
        if material in ['wood', 'wooden']:
            if "cup" in object_description.lower() or "mug" in object_description.lower():
                enhanced_object = f"wooden {object_description}"
            else:
                enhanced_object = f"{object_description} with warm wood tones"
        elif material in ['stone', 'marble', 'granite']:
            enhanced_object = f"elegant {object_description}"
        elif material in ['metal', 'metallic']:
            enhanced_object = f"sleek {object_description}"
        elif material in ['glass']:
            enhanced_object = f"crystal-clear {object_description}"
        else:
            enhanced_object = object_description
    else:
        enhanced_object = object_description
    
    prompt_parts.append(enhanced_object)
    
    # 2. Add positioning context with smart surface handling
    surface_desc = selection_area.get('surface_material', '')
    texture_desc = selection_area.get('texture', '')
    
    if surface_desc and surface_desc not in ['unknown', 'general surface']:
        if texture_desc and texture_desc != 'unknown':
            prompt_parts.append(f"positioned on {texture_desc} {surface_desc}")
        else:
            prompt_parts.append(f"placed on {surface_desc}")
    
    # 3. Add lighting context
    lighting_type = lighting.get('type', '')
    lighting_quality = lighting.get('quality', '')
    
    if lighting_type and lighting_quality and lighting_quality != 'unknown':
        if lighting_type == 'natural':
            prompt_parts.append(f"in {lighting_quality} natural lighting")
        elif lighting_type == 'artificial':
            prompt_parts.append(f"under {lighting_quality} lighting")
    
    # 4. Add environmental context
    env_type = environment.get('type', '')
    location = environment.get('location', '')
    
    if location and location != 'general indoor/outdoor space':
        if env_type == 'outdoor':
            prompt_parts.append(f"in {location} outdoor setting")
        elif env_type == 'indoor':
            prompt_parts.append(f"in {location}")
        else:
            prompt_parts.append(f"in {location}")
    
    # 5. Add style and mood
    overall_style = style_mood.get('overall_style', '')
    atmosphere = style_mood.get('atmosphere', '')
    
    if overall_style and overall_style != 'neutral':
        prompt_parts.append(f"{overall_style} style")
    
    if atmosphere and atmosphere not in ['casual', 'neutral'] and atmosphere != overall_style:
        prompt_parts.append(f"{atmosphere} atmosphere")
    
    # 6. Add quality enhancement
    if style_preferences:
        realism = style_preferences.get('realism', 'high')
        artistic_style = style_preferences.get('artistic_style', 'photorealistic')
        
        if realism == 'high':
            prompt_parts.append("highly detailed")
        
        if artistic_style and artistic_style != 'photorealistic':
            prompt_parts.append(artistic_style)
    else:
        prompt_parts.append("photorealistic, highly detailed")
    
    # Join all parts into final prompt
    final_prompt = ", ".join(prompt_parts)
    
    logging.info(f"Generated auto prompt: '{final_prompt}'")
    return final_prompt


def enhance_user_prompt(user_prompt: str, scene_analysis: dict):
    """
    Enhances a user's manual prompt with scene context.
    
    Args:
        user_prompt: User's original prompt
        scene_analysis: Scene analysis from analyze_scene_for_prompting()
    
    Returns:
        Enhanced prompt with added context
    """
    if not scene_analysis or not user_prompt:
        return user_prompt
    
    # Extract scene context
    lighting = scene_analysis.get('lighting', {})
    style_mood = scene_analysis.get('style_mood', {})
    environment = scene_analysis.get('environment', {})
    selection_area = scene_analysis.get('selection_area', {})
    
    enhancements = []
    
    # Add lighting if not mentioned
    if not any(word in user_prompt.lower() for word in ['light', 'bright', 'dim', 'shadow']):
        lighting_quality = lighting.get('quality', '')
        lighting_type = lighting.get('type', '')
        if lighting_quality and lighting_type:
            enhancements.append(f"{lighting_quality} {lighting_type} lighting")
    
    # Add surface context if not mentioned
    if not any(word in user_prompt.lower() for word in ['on', 'surface', 'table', 'ground']):
        surface = selection_area.get('surface_material', '')
        if surface:
            enhancements.append(f"on {surface} surface")
    
    # Add style context if not mentioned
    if not any(word in user_prompt.lower() for word in ['style', 'modern', 'rustic', 'elegant']):
        style = style_mood.get('overall_style', '')
        if style:
            enhancements.append(f"{style} style")
    
    # Add environment context if not mentioned
    if not any(word in user_prompt.lower() for word in ['indoor', 'outdoor', 'kitchen', 'park']):
        env_type = environment.get('type', '')
        location = environment.get('location', '')
        if location:
            enhancements.append(f"in {location}")
    
    # Combine user prompt with enhancements
    if enhancements:
        enhanced_prompt = f"{user_prompt}, {', '.join(enhancements)}"
    else:
        enhanced_prompt = user_prompt
    
    logging.info(f"Enhanced user prompt: '{user_prompt}' -> '{enhanced_prompt}'")
    return enhanced_prompt


def suggest_prompt_variations(base_prompt: str, scene_analysis: dict, num_variations: int = 3):
    """
    Suggests alternative prompt variations based on scene analysis.
    
    Args:
        base_prompt: Base prompt to create variations from
        scene_analysis: Scene analysis context
        num_variations: Number of variations to generate
    
    Returns:
        List of prompt variations
    """
    if not scene_analysis:
        return [base_prompt]
    
    variations = []
    style_mood = scene_analysis.get('style_mood', {})
    lighting = scene_analysis.get('lighting', {})
    selection_area = scene_analysis.get('selection_area', {})
    
    # Variation 1: Emphasis on material and texture
    material = selection_area.get('surface_material', '')
    texture = selection_area.get('texture', '')
    if material and texture:
        var1 = f"{base_prompt}, emphasizing {texture} {material} texture, tactile details"
        variations.append(var1)
    
    # Variation 2: Emphasis on lighting and mood
    lighting_quality = lighting.get('quality', '')
    atmosphere = style_mood.get('atmosphere', '')
    if lighting_quality and atmosphere:
        var2 = f"{base_prompt}, dramatic {lighting_quality} lighting, {atmosphere} mood"
        variations.append(var2)
    
    # Variation 3: Emphasis on style and artistic approach
    overall_style = style_mood.get('overall_style', '')
    if overall_style:
        var3 = f"{base_prompt}, {overall_style} aesthetic, artistic composition"
        variations.append(var3)
    
    # Ensure we always return the requested number of variations
    while len(variations) < num_variations:
        variations.append(base_prompt)
    
    return variations[:num_variations]


def _parse_text_to_scene_analysis(text_response: str):
    """
    Converts a text response into structured scene analysis when JSON parsing fails.
    Uses keyword detection to extract scene information.
    """
    import re
    
    # Initialize with fallback data
    analysis = _create_fallback_scene_analysis()
    
    text_lower = text_response.lower()
    
    try:
        # Environment type detection
        if any(word in text_lower for word in ['outdoor', 'outside', 'park', 'garden', 'street', 'beach', 'nature']):
            analysis['environment']['type'] = 'outdoor'
        elif any(word in text_lower for word in ['indoor', 'inside', 'room', 'kitchen', 'bedroom', 'office', 'house']):
            analysis['environment']['type'] = 'indoor'
        
        # Location detection
        locations = ['kitchen', 'bedroom', 'living room', 'office', 'bathroom', 'park', 'garden', 'beach', 'restaurant', 'cafe']
        for location in locations:
            if location in text_lower:
                analysis['environment']['location'] = location
                break
        
        # People detection
        people_indicators = ['person', 'people', 'man', 'woman', 'child', 'human', 'individual', 'someone']
        if any(indicator in text_lower for indicator in people_indicators):
            analysis['people']['present'] = True
            # Try to extract count
            count_match = re.search(r'(\d+)\s*(?:person|people|individual)', text_lower)
            if count_match:
                analysis['people']['count'] = int(count_match.group(1))
            else:
                analysis['people']['count'] = 1
        
        # Surface material detection
        materials = {
            'wood': ['wood', 'wooden', 'timber', 'oak', 'pine', 'mahogany'],
            'stone': ['stone', 'marble', 'granite', 'rock', 'slate'],
            'metal': ['metal', 'steel', 'iron', 'aluminum', 'brass'],
            'fabric': ['fabric', 'cloth', 'textile', 'canvas', 'linen'],
            'glass': ['glass', 'crystal'],
            'concrete': ['concrete', 'cement'],
            'grass': ['grass', 'lawn', 'turf'],
            'water': ['water', 'lake', 'river', 'ocean', 'sea']
        }
        
        for material, keywords in materials.items():
            if any(keyword in text_lower for keyword in keywords):
                analysis['selection_area']['surface_material'] = material
                break
        
        # Texture detection
        textures = ['smooth', 'rough', 'soft', 'hard', 'polished', 'weathered', 'textured', 'glossy', 'matte']
        for texture in textures:
            if texture in text_lower:
                analysis['selection_area']['texture'] = texture
                break
        
        # Lighting detection
        if any(word in text_lower for word in ['bright', 'brilliant', 'intense']):
            analysis['lighting']['quality'] = 'bright'
        elif any(word in text_lower for word in ['dim', 'dark', 'low light']):
            analysis['lighting']['quality'] = 'dim'
        elif any(word in text_lower for word in ['soft', 'gentle', 'subtle']):
            analysis['lighting']['quality'] = 'soft'
        
        if any(word in text_lower for word in ['natural', 'sunlight', 'daylight']):
            analysis['lighting']['type'] = 'natural'
        elif any(word in text_lower for word in ['artificial', 'electric', 'lamp']):
            analysis['lighting']['type'] = 'artificial'
        
        # Style detection
        styles = ['modern', 'contemporary', 'rustic', 'vintage', 'elegant', 'casual', 'industrial', 'minimalist']
        for style in styles:
            if style in text_lower:
                analysis['style_mood']['overall_style'] = style
                break
        
        # Atmosphere detection
        atmospheres = ['cozy', 'formal', 'relaxed', 'energetic', 'serene', 'busy', 'peaceful', 'dramatic']
        for atmosphere in atmospheres:
            if atmosphere in text_lower:
                analysis['style_mood']['atmosphere'] = atmosphere
                break
        
        logging.info(f"Parsed text response into structured analysis: {analysis}")
        return analysis
        
    except Exception as e:
        logging.error(f"Error parsing text response: {e}")
        return _create_fallback_scene_analysis()


def _create_fallback_scene_analysis():
    """Creates a basic fallback scene analysis when vision model fails."""
    return {
        "environment": {
            "type": "unknown",
            "location": "general indoor/outdoor space",
            "time_of_day": "unknown",
            "weather": "N/A"
        },
        "people": {
            "present": False,
            "count": 0,
            "descriptions": [],
            "activities": [],
            "clothing_style": ""
        },
        "selection_area": {
            "surface_material": "general surface",
            "texture": "unknown",
            "color": "neutral",
            "condition": "unknown",
            "size": "medium"
        },
        "lighting": {
            "type": "natural",
            "direction": "ambient",
            "quality": "moderate",
            "shadows": "soft"
        },
        "style_mood": {
            "overall_style": "neutral",
            "atmosphere": "casual",
            "color_palette": "neutral"
        },
        "context_details": {
            "surrounding_objects": [],
            "spatial_relationship": "central placement",
            "purpose": "general use",
            "formality_level": "casual"
        }
    }
