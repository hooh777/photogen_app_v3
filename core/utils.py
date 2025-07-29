# core/utils.py
from PIL import Image
import re

def parse_template(template):
    """Extracts the placeholder from a string like 'prefix {placeholder} suffix'."""
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
    
    # Create a new blank canvas with the background
    composite = background_img.copy()
    
    # Calculate position to paste the object in the center
    offset = ((bg_w - obj_w) // 2, (bg_h - obj_h) // 2)
    
    # Paste using the object's alpha channel as a mask
    composite.paste(object_img, offset, object_img)
    return composite.convert("RGB")