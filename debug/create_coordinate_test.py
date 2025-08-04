#!/usr/bin/env python3
"""
Test the actual PhotoGen app to verify coordinate scaling fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont
import logging

def create_scaling_test_image():
    """Create a test image that demonstrates the scaling issue."""
    width, height = 382, 384
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([0, 0, width-1, height-1], outline='black', width=2)
    
    # Mark all four corners with large red squares
    corner_size = 30
    corners = [
        (0, 0, corner_size, corner_size),  # Top-left
        (width-corner_size, 0, width, corner_size),  # Top-right
        (0, height-corner_size, corner_size, height),  # Bottom-left
        (width-corner_size, height-corner_size, width, height)  # Bottom-right
    ]
    
    for corner in corners:
        draw.rectangle(corner, fill='red', outline='darkred', width=2)
    
    # Add coordinate labels
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    # Add corner coordinates with white background for visibility
    coords_text = [
        ((5, 5), "(0,0)"),
        ((width-60, 5), f"({width-1},0)"),
        ((5, height-25), f"(0,{height-1})"),
        ((width-80, height-25), f"({width-1},{height-1})")
    ]
    
    for (x, y), text in coords_text:
        # White background rectangle
        bbox = draw.textbbox((x, y), text, font=font)
        draw.rectangle(bbox, fill='white', outline='black')
        draw.text((x, y), text, fill='black', font=font)
    
    # Add center text
    center_text = f"382x384 Image\nClick corners to test\nMax coords: (381,383)"
    text_bbox = draw.textbbox((width//2, height//2), center_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # White background for center text
    draw.rectangle([text_x-5, text_y-5, text_x+text_width+5, text_y+text_height+5], 
                   fill='white', outline='blue', width=2)
    draw.text((text_x, text_y), center_text, fill='blue', font=font, align='center')
    
    return img

def main():
    """Create test image and save it."""
    print("Creating coordinate scaling test image...")
    
    # Create debug directory if it doesn't exist
    debug_dir = "debug"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    
    # Create test image
    test_img = create_scaling_test_image()
    output_path = os.path.join(debug_dir, "coordinate_test_382x384.png")
    test_img.save(output_path)
    
    print(f"✅ Test image created: {output_path}")
    print("\n🧪 TEST INSTRUCTIONS:")
    print("1. Start PhotoGen: python app.py")
    print("2. Go to Edit tab")
    print(f"3. Upload the test image: {output_path}")
    print("4. Try clicking on the RED CORNER SQUARES")
    print("5. Expected results:")
    print("   - Top-left corner: Should give coordinates near (0, 0)")
    print("   - Top-right corner: Should give coordinates near (381, 0)")
    print("   - Bottom-left corner: Should give coordinates near (0, 383)")
    print("   - Bottom-right corner: Should give coordinates near (381, 383)")
    print("\n🔍 WHAT TO LOOK FOR:")
    print("   - If you can only click up to ~(307, 315), scaling issue still exists")
    print("   - If you can click near (381, 383), the fix is working!")
    print("   - Check console logs for scaling detection messages")
    print("   - Look for 'SCALING DETECTED!' messages with scale factors")

if __name__ == "__main__":
    main()
