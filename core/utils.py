from PIL import Image
import re

def get_dimensions(aspect_ratio_str: str, base_resolution: int = 1024):
    """Calculates width and height from an aspect ratio string, keeping the longest side at base_resolution."""
    try:
        w, h = map(int, aspect_ratio_str.split(':'))
    except (ValueError, AttributeError):
        # Default to square if the format is invalid or None
        return base_resolution, base_resolution

    if w > h: # Landscape
        width = base_resolution
        height = int(base_resolution * h / w)
    elif h > w: # Portrait
        height = base_resolution
        width = int(base_resolution * w / h)
    else: # Square
        width, height = base_resolution, base_resolution

    # Ensure dimensions are multiples of 8 for stability with diffusion models
    width = (width // 8) * 8
    height = (height // 8) * 8
    
    return width, height

def parse_template(template):
    """Extracts the placeholder from a string like 'prefix {placeholder} suffix'."""
    if not isinstance(template, str):
        return '', '', ''
    match = re.search(r"\{(.*?)\}", template)
    if not match: return template, "", ""
    
    placeholder = match.group(0)
    placeholder_text = match.group(1)
    prefix, suffix = template.split(placeholder, 1)
    return prefix, placeholder_text, suffix

def paste_object(background_img, object_img):
    """Pastes an object image (with potential transparency) onto the center of a background."""
    if background_img.mode != 'RGBA':
        background_img = background_img.convert("RGBA")
    if object_img.mode != 'RGBA':
        object_img = object_img.convert("RGBA")

    bg_w, bg_h = background_img.size
    obj_w, obj_h = object_img.size
    
    composite = background_img.copy()
    
    # Calculate position to paste the object in the center
    offset = ((bg_w - obj_w) // 2, (bg_h - obj_h) // 2)
    
    # Paste using the object's alpha channel as a mask
    composite.paste(object_img, offset, object_img)
    return composite.convert("RGB")