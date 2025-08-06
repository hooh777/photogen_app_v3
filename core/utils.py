from PIL import Image
import re
import math

def merge_images_with_smart_scaling(background_img, object_img, target_size=None):
    """
    Intelligently merges background and object images with proportional scaling.
    If target_size is provided, scales appropriately. Otherwise uses background dimensions.
    """
    if not background_img:
        return object_img if object_img else None
    if not object_img:
        return background_img
    
    # Determine target size
    if target_size is None:
        target_size = background_img.size
    target_width, target_height = target_size
    
    # Scale background to target size
    if background_img.size != target_size:
        background_scaled = background_img.resize(target_size, Image.LANCZOS)
    else:
        background_scaled = background_img
    
    # Improved object scaling to preserve quality
    bg_area = target_width * target_height
    obj_area = object_img.width * object_img.height
    
    # More conservative scaling - keep object larger to preserve detail
    # Use 20% of background area instead of 15% for better object preservation
    target_area_ratio = 0.20
    
    # Adjust based on aspect ratios
    bg_ratio = target_width / target_height
    if bg_ratio > 2.5:  # Very wide background
        target_area_ratio *= 0.8  # Less aggressive reduction
    elif bg_ratio < 0.4:  # Very tall background  
        target_area_ratio *= 0.9  # Less aggressive reduction
    
    # Calculate scale factor with quality preservation bias
    target_area = bg_area * target_area_ratio
    scale_factor = math.sqrt(target_area / obj_area)
    
    # More conservative clamping - allow larger objects to preserve detail
    scale_factor = max(0.15, min(scale_factor, 1.5))  # Don't shrink too much, don't grow too much
    
    # Ensure minimum viable object size for quality preservation
    min_obj_dimension = min(target_width, target_height) * 0.15  # At least 15% of smaller dimension
    
    # Scale object proportionally
    new_obj_width = max(int(min_obj_dimension), int(object_img.width * scale_factor))
    new_obj_height = max(int(min_obj_dimension), int(object_img.height * scale_factor))
    
    # Maintain aspect ratio if one dimension was clamped
    obj_aspect_ratio = object_img.width / object_img.height
    if new_obj_width / new_obj_height != obj_aspect_ratio:
        if new_obj_width < new_obj_height * obj_aspect_ratio:
            new_obj_width = int(new_obj_height * obj_aspect_ratio)
        else:
            new_obj_height = int(new_obj_width / obj_aspect_ratio)
    
    object_scaled = object_img.resize((new_obj_width, new_obj_height), Image.LANCZOS)
    
    # Create side-by-side merged image with better proportions
    # Reduce gap between background and object
    gap = min(10, target_width // 50)  # Small gap, proportional to image size
    merged_width = target_width + new_obj_width + gap
    merged_height = max(target_height, new_obj_height)
    
    merged_image = Image.new('RGB', (merged_width, merged_height), color='white')
    
    # Paste background on the left
    merged_image.paste(background_scaled, (0, 0))
    
    # Paste object on the right with small gap, vertically centered
    obj_y_offset = max(0, (merged_height - new_obj_height) // 2)
    merged_image.paste(object_scaled, (target_width + gap, obj_y_offset))
    
    return merged_image

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