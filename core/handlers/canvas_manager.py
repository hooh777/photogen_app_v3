"""
Canvas Management - Handles all canvas drawing, selection, and visual feedback
Extracted from i2i_handler.py for better organization
"""
import gradio as gr
import numpy as np
from PIL import Image, ImageDraw
import logging
from core import utils


class CanvasManager:
    """Manages canvas operations, selection handling, and visual feedback"""
    
    def __init__(self):
        pass
    
    def update_canvas_with_merge(self, base_img, obj_img, top_left, bottom_right):
        """Updates the canvas to show side-by-side display when both background and object are available.
        Uses new simplified workflow: [Background] | [Object] side-by-side for easy area selection."""
        if base_img and obj_img:
            # Show the side-by-side display for simplified workflow
            side_by_side_image = utils.create_side_by_side_display(base_img, obj_img)
            return side_by_side_image
        else:
            # Fall back to normal canvas redraw
            return self._redraw_canvas(base_img, obj_img, top_left, bottom_right)
    
    def handle_click(self, base_img, obj_img, top_left, bottom_right, evt: gr.SelectData):
        """Handle single-click area selection with automatic area sizing"""
        if base_img is None: 
            raise gr.Error("Please upload a background image first.")
        
        # Get click coordinates and image dimensions
        click_coords = evt.index
        img_width, img_height = base_img.size
        
        logging.info(f"Raw click coordinates: {click_coords}")
        logging.info(f"Image dimensions: {img_width}x{img_height}")
        
        # Use coordinates as-is
        x, y = click_coords
        
        # Handle edge cases - expand the clickable area
        edge_tolerance = 10  # pixels tolerance for edge detection
        
        # If click is very close to edges, snap to edge
        if x < edge_tolerance:
            x = 0
            logging.info(f"Snapped to left edge: x = 0")
        elif x > img_width - edge_tolerance:
            x = img_width - 1
            logging.info(f"Snapped to right edge: x = {img_width - 1}")
        
        if y < edge_tolerance:
            y = 0
            logging.info(f"Snapped to top edge: y = 0")
        elif y > img_height - edge_tolerance:
            y = img_height - 1
            logging.info(f"Snapped to bottom edge: y = {img_height - 1}")
        
        # Final boundary constraint
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        
        constrained_coords = (x, y)
        logging.info(f"Final coordinates: {constrained_coords}")
        
        # Single-click selection with automatic area
        # Create a square selection area around the click point
        selection_size = min(img_width, img_height) // 8  # Default to 1/8 of the smaller dimension
        selection_size = max(50, min(selection_size, 150))  # Clamp between 50-150 pixels
        
        # Calculate selection box around click point
        half_size = selection_size // 2
        left = max(0, x - half_size)
        top = max(0, y - half_size)
        right = min(img_width - 1, x + half_size)
        bottom = min(img_height - 1, y + half_size)
        
        # Ensure the box is properly sized even at edges
        if right - left < selection_size and right < img_width - 1:
            right = min(img_width - 1, left + selection_size)
        if right - left < selection_size and left > 0:
            left = max(0, right - selection_size)
            
        if bottom - top < selection_size and bottom < img_height - 1:
            bottom = min(img_height - 1, top + selection_size)
        if bottom - top < selection_size and top > 0:
            top = max(0, bottom - selection_size)
        
        new_top_left = (left, top)
        new_bottom_right = (right, bottom)
        
        # Calculate actual area size for user feedback
        width = right - left
        height = bottom - top
        gr.Info(f"✅ Area selected at ({x}, {y})! Region: {width}×{height} pixels. Click 'Generate Auto-Prompt' to analyze both images.")
        logging.info(f"Single-click selection: {new_top_left} to {new_bottom_right}")
        
        # Redraw canvas with selection box
        updated_canvas = self._redraw_canvas(base_img, obj_img, new_top_left, new_bottom_right)
        return updated_canvas, new_top_left, new_bottom_right

    def reset_selection(self, base_img, obj_img):
        """Reset the selection coordinates and redraw the canvas."""
        logging.info("Resetting selection coordinates")
        updated_canvas = self._redraw_canvas(base_img, obj_img, None, None)
        return updated_canvas, None, None

    def _redraw_canvas(self, base_img, obj_img, top_left, bottom_right):
        """Core canvas redrawing logic with selection visualization"""
        if base_img is None:
            return self._create_placeholder_canvas(obj_img)
        
        # EDIT MODE: Original canvas logic
        canvas_copy = base_img.copy().convert("RGBA")
        draw = ImageDraw.Draw(canvas_copy, "RGBA")
        
        # Get image dimensions for boundary checks
        img_width, img_height = base_img.size
        
        # Add a subtle border around the entire image to show clickable area
        edge_color = (200, 200, 200, 100)  # Light gray, semi-transparent
        border_width = 2
        
        # Draw border around entire image
        draw.rectangle((0, 0, img_width - 1, img_height - 1), 
                      fill=None, outline=edge_color, width=border_width)
        
        # Add corner indicators to show edge areas
        corner_size = 15
        corner_color = (150, 150, 150, 80)
        
        # Corner indicators
        corners = [
            (0, 0, corner_size, corner_size),  # Top-left
            (img_width - corner_size, 0, img_width, corner_size),  # Top-right
            (0, img_height - corner_size, corner_size, img_height),  # Bottom-left
            (img_width - corner_size, img_height - corner_size, img_width, img_height)  # Bottom-right
        ]
        
        for corner in corners:
            draw.rectangle(corner, fill=corner_color, outline=None)
        
        # Draw selection box if coordinates exist
        if top_left and bottom_right:
            self._draw_selection_box(draw, top_left, bottom_right, img_width, img_height)
        elif top_left:
            self._draw_click_marker(draw, top_left, img_width, img_height)
        
        return canvas_copy.convert("RGB")
    
    def _create_placeholder_canvas(self, obj_img):
        """Create placeholder canvas for Create Mode"""
        placeholder_width, placeholder_height = 512, 512
        placeholder = Image.new("RGB", (placeholder_width, placeholder_height), (240, 240, 240))
        draw = ImageDraw.Draw(placeholder, "RGBA")
        
        # Draw placeholder text and styling
        placeholder_color = (180, 180, 180)
        border_color = (200, 200, 200)
        
        # Dashed border for placeholder
        for i in range(0, placeholder_width, 20):
            draw.rectangle((i, 0, min(i + 10, placeholder_width), 2), fill=border_color)
            draw.rectangle((i, placeholder_height - 2, min(i + 10, placeholder_width), placeholder_height), fill=border_color)
        for i in range(0, placeholder_height, 20):
            draw.rectangle((0, i, 2, min(i + 10, placeholder_height)), fill=border_color)
            draw.rectangle((placeholder_width - 2, i, placeholder_width, min(i + 10, placeholder_height)), fill=border_color)
        
        # Add CREATE MODE text
        try:
            from PIL import ImageFont
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None
        
        # If object image exists, show it prominently
        if obj_img:
            # Resize object to fit nicely in the canvas
            obj_w, obj_h = obj_img.size
            max_obj_size = 300  # Larger size for better visibility
            
            # Calculate new dimensions maintaining aspect ratio
            if obj_w > obj_h:
                new_w = min(max_obj_size, obj_w)
                new_h = int(obj_h * (new_w / obj_w))
            else:
                new_h = min(max_obj_size, obj_h)
                new_w = int(obj_w * (new_h / obj_h))
            
            if new_w > 0 and new_h > 0:
                resized_obj = obj_img.resize((new_w, new_h), Image.LANCZOS)
                
                # Center the object in the canvas
                paste_x = (placeholder_width - new_w) // 2
                paste_y = (placeholder_height - new_h) // 2
                
                # Paste the actual object image onto the placeholder
                if resized_obj.mode != 'RGB':
                    # Handle RGBA or other modes
                    if resized_obj.mode == 'RGBA':
                        placeholder.paste(resized_obj, (paste_x, paste_y), resized_obj)
                    else:
                        placeholder.paste(resized_obj.convert('RGB'), (paste_x, paste_y))
                else:
                    placeholder.paste(resized_obj, (paste_x, paste_y))
                
                # Add title above the object
                title_text = "CREATE MODE"
                title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (placeholder_width - title_width) // 2
                title_y = max(20, paste_y - 60)  # Position above object
                draw.text((title_x, title_y), title_text, fill=(100, 100, 100), font=font_large)
                
                # Add subtitle below the object
                subtitle_text = "Object uploaded - Ready to generate scene"
                subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_small)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = (placeholder_width - subtitle_width) // 2
                subtitle_y = min(placeholder_height - 40, paste_y + new_h + 20)  # Position below object
                draw.text((subtitle_x, subtitle_y), subtitle_text, fill=(60, 120, 60), font=font_small)
                
            return placeholder
        
        # If no object, show the original placeholder
        # Main title
        title_text = "CREATE MODE"
        title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (placeholder_width - title_width) // 2
        draw.text((title_x, 180), title_text, fill=(100, 100, 100), font=font_large)
        
        # Subtitle
        subtitle_text = "No background image uploaded"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_small)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (placeholder_width - subtitle_width) // 2
        draw.text((subtitle_x, 220), subtitle_text, fill=(140, 140, 140), font=font_small)
        
        # Instructions
        instruction_text = "Upload a background to enter Edit Mode"
        instruction_bbox = draw.textbbox((0, 0), instruction_text, font=font_small)
        instruction_width = instruction_bbox[2] - instruction_bbox[0]
        instruction_x = (placeholder_width - instruction_width) // 2
        draw.text((instruction_x, 280), instruction_text, fill=(160, 160, 160), font=font_small)
        
        return placeholder
    
    def _draw_selection_box(self, draw, top_left, bottom_right, img_width, img_height):
        """Draw selection box with proper constraints and styling"""
        # Constrain coordinates to image bounds
        x1 = max(0, min(top_left[0], img_width - 1))
        y1 = max(0, min(top_left[1], img_height - 1))
        x2 = max(0, min(bottom_right[0], img_width - 1))
        y2 = max(0, min(bottom_right[1], img_height - 1))
        
        # Calculate proper box coordinates
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        # Ensure minimum box size for visibility
        min_size = 5
        if (right - left) < min_size:
            center_x = (left + right) // 2
            left = max(0, center_x - min_size // 2)
            right = min(img_width, left + min_size)
        
        if (bottom - top) < min_size:
            center_y = (top + bottom) // 2
            top = max(0, center_y - min_size // 2)
            bottom = min(img_height, top + min_size)
        
        box = (left, top, right, bottom)
        
        # Draw transparent selection box with visible border
        # Very light transparent fill (almost invisible)
        draw.rectangle(box, fill=(0, 100, 255, 20), outline=None)  # Much more transparent
        # White border for contrast
        draw.rectangle(box, fill=None, outline=(255, 255, 255, 255), width=3)
        # Blue border for style
        draw.rectangle(box, fill=None, outline=(0, 100, 255, 255), width=2)
        
        # Add corner markers for better visibility
        corner_marker_size = 8
        # Top-left corner
        draw.rectangle((left, top, left + corner_marker_size, top + corner_marker_size), 
                     fill=(255, 255, 255, 200), outline=(0, 100, 255, 255), width=1)
        # Bottom-right corner
        draw.rectangle((right - corner_marker_size, bottom - corner_marker_size, right, bottom), 
                     fill=(255, 255, 255, 200), outline=(0, 100, 255, 255), width=1)
    
    def _draw_click_marker(self, draw, top_left, img_width, img_height):
        """Draw marker for first click point"""
        # Constrain first click point
        x = max(0, min(top_left[0], img_width - 1))
        y = max(0, min(top_left[1], img_height - 1))
        
        radius = 8
        # Draw crosshair for first click with enhanced visibility
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), 
                    fill=(255, 255, 255, 200), outline=(0, 100, 255, 255), width=3)
        # Add small center dot
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), 
                    fill=(0, 100, 255, 255), outline=None)
        
        # Draw crosshair lines to make it more visible
        line_length = 15
        draw.line([(x - line_length, y), (x + line_length, y)], 
                 fill=(255, 255, 255, 255), width=2)
        draw.line([(x, y - line_length), (x, y + line_length)], 
                 fill=(255, 255, 255, 255), width=2)
    
    def create_multi_image_preview(self, images):
        """
        Create a preview canvas showing multiple uploaded images.
        
        Args:
            images: List of PIL Images
            
        Returns:
            PIL Image: Composite preview showing all uploaded images
        """
        if not images:
            return None
            
        if len(images) == 1:
            return images[0]
        
        # Calculate grid layout
        num_images = len(images)
        if num_images <= 2:
            cols, rows = 2, 1
        elif num_images <= 4:
            cols, rows = 2, 2
        elif num_images <= 6:
            cols, rows = 3, 2
        else:
            cols, rows = 4, 3  # Max 12 images in preview
        
        # Determine canvas size
        canvas_width = 800
        canvas_height = 600
        cell_width = canvas_width // cols
        cell_height = canvas_height // rows
        
        # Create preview canvas
        preview = Image.new('RGB', (canvas_width, canvas_height), color='white')
        
        for i, img in enumerate(images[:12]):  # Limit to 12 images
            if img is None:
                continue
                
            row = i // cols
            col = i % cols
            
            # Calculate position
            x = col * cell_width
            y = row * cell_height
            
            # Resize image to fit cell
            img_resized = img.copy()
            img_resized.thumbnail((cell_width - 10, cell_height - 10), Image.LANCZOS)
            
            # Center image in cell
            img_x = x + (cell_width - img_resized.width) // 2
            img_y = y + (cell_height - img_resized.height) // 2
            
            # Paste image
            preview.paste(img_resized, (img_x, img_y))
            
            # Draw border around cell
            draw = ImageDraw.Draw(preview)
            draw.rectangle((x, y, x + cell_width - 1, y + cell_height - 1), 
                          outline='lightgray', width=1)
            
            # Add image number
            draw.text((x + 5, y + 5), f"{i+1}", fill='black')
        
        return preview
