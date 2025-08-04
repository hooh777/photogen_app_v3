from PIL import Image
import re

def merge_multiple_images_high_quality(image_list, bg_color="black"):
    """
    Merges images. If 4 images are provided, they are arranged in a 2x2 grid.
    Otherwise, they are merged side-by-side horizontally.
    """
    if not image_list:
        return None
    if len(image_list) == 1:
        return image_list[0]

    resampling_filter = Image.Resampling.LANCZOS

    # --- 2x2 Grid Logic for exactly 4 images ---
    if len(image_list) == 4:
        cell_width = max(img.width for img in image_list)
        cell_height = max(img.height for img in image_list)
        resized_images = [
            img.resize((cell_width, cell_height), resample=resampling_filter)
            for img in image_list
        ]
        grid_image = Image.new('RGB', (cell_width * 2, cell_height * 2), color=bg_color)
        grid_image.paste(resized_images[0], (0, 0))
        grid_image.paste(resized_images[1], (cell_width, 0))
        grid_image.paste(resized_images[2], (0, cell_height))
        grid_image.paste(resized_images[3], (cell_width, cell_height))
        return grid_image

    # --- Fallback: Original horizontal merging logic for other counts ---
    max_height = max(img.height for img in image_list)
    scaled_images = []
    for img in image_list:
        if img.height != max_height:
            scale_factor = max_height / img.height
            new_width = int(img.width * scale_factor)
            scaled_images.append(img.resize((new_width, max_height), resample=resampling_filter))
        else:
            scaled_images.append(img)

    total_width = sum(img.width for img in scaled_images)
    merged_image = Image.new('RGB', (total_width, max_height), color=bg_color)
    x_offset = 0
    for img in scaled_images:
        merged_image.paste(img, (x_offset, 0))
        x_offset += img.width
    return merged_image

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

def paste_object(background_img, object_img, target_position=None):
    """Pastes an object image onto a background with smart positioning and blending."""
    if background_img.mode != 'RGBA':
        background_img = background_img.convert("RGBA")
    if object_img.mode != 'RGBA':
        object_img = object_img.convert("RGBA")

    bg_w, bg_h = background_img.size
    obj_w, obj_h = object_img.size
    
    composite = background_img.copy()
    
    if target_position:
        # Center the object at the target position
        target_x, target_y = target_position
        offset = (target_x - obj_w // 2, target_y - obj_h // 2)
        # Ensure the object stays within bounds
        offset = (max(0, min(offset[0], bg_w - obj_w)), max(0, min(offset[1], bg_h - obj_h)))
    else:
        # Calculate position to paste the object in the center
        offset = ((bg_w - obj_w) // 2, (bg_h - obj_h) // 2)
    
    # Use the object's alpha channel for clean compositing
    if object_img.mode == 'RGBA':
        alpha_mask = object_img.getchannel('A')
        composite.paste(object_img, offset, alpha_mask)
    else:
        composite.paste(object_img, offset)
    
    return composite.convert("RGB")

def stitch_images(background_img, object_img):
    """Legacy function - redirects to paste_object for better integration."""
    return paste_object(background_img, object_img)