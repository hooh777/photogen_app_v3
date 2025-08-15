from PIL import Image
import re
import math
import logging

def get_dimensions(aspect_ratio_setting):
    """Get pixel dimensions for standard aspect ratios"""
    # Default high-quality size
    base_size = 1024
    
    if "Match Input" in aspect_ratio_setting:
        return (1024, 1024)  # Default fallback
    elif "1:1" in aspect_ratio_setting or "Square" in aspect_ratio_setting:
        return (1024, 1024)
    elif "16:9" in aspect_ratio_setting or "Landscape" in aspect_ratio_setting:
        return (1024, 576)  # 16:9 ratio
    elif "9:16" in aspect_ratio_setting or "Portrait" in aspect_ratio_setting:
        return (576, 1024)  # 9:16 ratio  
    elif "4:3" in aspect_ratio_setting or "Standard" in aspect_ratio_setting:
        return (1024, 768)  # 4:3 ratio
    elif "3:4" in aspect_ratio_setting:
        return (768, 1024)  # 3:4 ratio
    else:
        # Fallback to square
        return (1024, 1024)

def merge_images_with_smart_scaling(background_img, object_img, target_size=None, preserve_object_scale=False):
    """
    Intelligently merges background and object images with proportional scaling.
    Enhanced to better preserve object size for human placement scenarios.
    If target_size is provided, scales appropriately. Otherwise uses background dimensions.
    
    Args:
        preserve_object_scale (bool): If True, uses more conservative scaling to preserve object size.
                                    Recommended for human placement scenarios.
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
    
    # Enhanced object scaling to better preserve size for human placement
    bg_area = target_width * target_height
    obj_area = object_img.width * object_img.height
    
    # ENHANCED: Adaptive sizing based on use case
    if preserve_object_scale:
        # More realistic sizing for human placement in life scenes
        # Calculate based on realistic human proportions in environments
        
        # Check if this looks like a human (height > width suggests standing person)
        obj_aspect_ratio = object_img.height / object_img.width
        likely_human = obj_aspect_ratio > 1.1  # Lowered threshold for more human detection
        
        if likely_human:
            # For humans: use height-based scaling for realistic life-size appearance
            # Humans should typically occupy 60-80% of scene height in indoor environments
            target_height_ratio = 0.7  # 70% of background height for realistic scale
            scale_factor_height = (target_height * target_height_ratio) / object_img.height
            
            # Limit scaling to prevent unrealistic sizes
            scale_factor = max(0.4, min(scale_factor_height, 1.5))  # 40% to 150% of original
            
            # Calculate final dimensions
            new_obj_width = int(object_img.width * scale_factor)
            new_obj_height = int(object_img.height * scale_factor)
            
            logging.info(f"🧑 Human-optimized scaling: {scale_factor:.2f}x (height-based: {target_height_ratio*100:.0f}% of background)")
            
            # Skip the area-based calculation below for humans
            human_scaling_applied = True
        else:
            # For non-human objects with preserve_object_scale=True: use enhanced area method
            target_area_ratio = 0.35  # More conservative for objects
            max_scale_factor = 2.5
            min_dimension_ratio = 0.25
            human_scaling_applied = False
    else:
        # Standard sizing for general object placement
        target_area_ratio = 0.25  # Reduced for better composition
        max_scale_factor = 2.0    # Standard maximum scaling  
        min_dimension_ratio = 0.2  # 20% of smaller dimension minimum
        human_scaling_applied = False
    
    # Apply area-based scaling only if human scaling wasn't used
    if not human_scaling_applied:
        # Adjust based on aspect ratios
        bg_ratio = target_width / target_height
        if bg_ratio > 2.5:  # Very wide background
            target_area_ratio *= 0.85  # Less aggressive reduction
        elif bg_ratio < 0.4:  # Very tall background  
            target_area_ratio *= 0.9   # Less aggressive reduction
        
        # Calculate scale factor with ENHANCED quality preservation bias
        target_area = bg_area * target_area_ratio
        scale_factor = math.sqrt(target_area / obj_area)
        
        # ENHANCED: More liberal clamping - allow much larger objects to preserve natural scale
        scale_factor = max(0.2, min(scale_factor, max_scale_factor))
        
        # ENHANCED: Ensure better minimum viable object size for visibility
        min_obj_dimension = min(target_width, target_height) * min_dimension_ratio
        
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
    
    # DETAILED MERGING DEBUG LOGGING
    logging.info(f"🖼️ === IMAGE MERGING DEBUG ===")
    logging.info(f"🖼️ Original Background: {background_img.size}")
    logging.info(f"🖼️ Original Object: {object_img.size}")
    logging.info(f"🖼️ Target Size: {target_size}")
    logging.info(f"🖼️ Background Scaled: {background_scaled.size}")
    logging.info(f"🖼️ Object Scaled: {object_scaled.size}")
    logging.info(f"🖼️ Scale Factor Applied: {scale_factor:.3f}" if 'scale_factor' in locals() else "🖼️ No scale factor available")
    logging.info(f"🖼️ Preserve Object Scale: {preserve_object_scale}")
    
    # Create side-by-side merged image with REDUCED GAP for better FLUX Kontext integration
    # FLUX Kontext works better with more compact layouts where objects are closer together
    gap = min(2, target_width // 200)  # Much smaller gap: 2px max instead of 10px, proportional scaling reduced
    merged_width = target_width + new_obj_width + gap
    merged_height = max(target_height, new_obj_height)
    
    logging.info(f"🖼️ Gap Size: {gap}px (REDUCED for better integration)")
    logging.info(f"🖼️ Final Merged Size: {merged_width}×{merged_height}")
    logging.info(f"🖼️ Compactness Ratio: {merged_width/target_width:.2f}x width (closer = better for FLUX Kontext)")
    
    merged_image = Image.new('RGB', (merged_width, merged_height), color='white')
    
    # Paste background on the left
    merged_image.paste(background_scaled, (0, 0))
    
    # Paste object on the right with small gap, vertically centered
    obj_y_offset = max(0, (merged_height - new_obj_height) // 2)
    merged_image.paste(object_scaled, (target_width + gap, obj_y_offset))
    
    logging.info(f"🖼️ Background Position: (0, 0)")
    logging.info(f"🖼️ Object Position: ({target_width + gap}, {obj_y_offset})")
    logging.info(f"🖼️ === END IMAGE MERGING DEBUG ===")
    
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

def create_side_by_side_display(background_img, object_img):
    """
    Creates a side-by-side display of background and object images for UI visualization.
    Used for the simplified Edit mode workflow where users can see both images before selection.
    
    Format: [Background] | [Object] side-by-side
    No visual indicators, no resizing - just clean horizontal layout.
    """
    if not background_img and not object_img:
        return None
    
    if not background_img:
        return object_img
    
    if not object_img:
        return background_img
    
    # Get dimensions
    bg_width, bg_height = background_img.size
    obj_width, obj_height = object_img.size
    
    # Calculate target height (use the maximum height for better visibility)
    target_height = max(bg_height, obj_height)
    
    # Calculate proportional widths to maintain aspect ratios
    bg_target_width = int((bg_width * target_height) / bg_height)
    obj_target_width = int((obj_width * target_height) / obj_height)
    
    # Resize images to target height while maintaining aspect ratio
    bg_resized = background_img.resize((bg_target_width, target_height), Image.LANCZOS)
    obj_resized = object_img.resize((obj_target_width, target_height), Image.LANCZOS)
    
    # Create the combined image
    total_width = bg_target_width + obj_target_width
    combined = Image.new('RGB', (total_width, target_height), color='white')
    
    # Paste background on left, object on right
    combined.paste(bg_resized, (0, 0))
    combined.paste(obj_resized, (bg_target_width, 0))
    
    return combined