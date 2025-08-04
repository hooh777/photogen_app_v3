#!/usr/bin/env python3
"""
Test normal clicking behavior after removing aggressive scaling detection.
"""

def simulate_click_handling(img_width, img_height, click_x, click_y):
    """Simulate the new click handling logic."""
    x, y = click_x, click_y
    
    print(f"Raw click: ({x}, {y}) on {img_width}x{img_height} image")
    
    # Edge snapping logic
    edge_tolerance = 10
    
    # If click is very close to edges, snap to edge
    if x < edge_tolerance:
        x = 0
        print(f"Snapped to left edge: x = 0")
    elif x > img_width - edge_tolerance:
        x = img_width - 1
        print(f"Snapped to right edge: x = {img_width - 1}")
    
    if y < edge_tolerance:
        y = 0
        print(f"Snapped to top edge: y = 0")
    elif y > img_height - edge_tolerance:
        y = img_height - 1
        print(f"Snapped to bottom edge: y = {img_height - 1}")
    
    # Final boundary constraint
    x = max(0, min(x, img_width - 1))
    y = max(0, min(y, img_height - 1))
    
    print(f"Final coordinates: ({x}, {y})")
    print()
    return (x, y)

def main():
    """Test various click scenarios."""
    print("🧪 TESTING SIMPLIFIED CLICK HANDLING")
    print("=" * 50)
    
    # Test with a 714x714 image (like in your logs)
    img_width, img_height = 714, 714
    
    test_cases = [
        # Middle clicks should remain unchanged
        (350, 350, "Middle of image"),
        (200, 400, "Normal click 1"),
        (500, 300, "Normal click 2"),
        
        # Edge clicks should snap
        (5, 350, "Near left edge"),
        (708, 350, "Near right edge"),
        (350, 5, "Near top edge"),
        (350, 708, "Near bottom edge"),
        
        # Corner clicks should snap to corners
        (5, 5, "Near top-left corner"),
        (708, 5, "Near top-right corner"),
        (5, 708, "Near bottom-left corner"),
        (708, 708, "Near bottom-right corner"),
        
        # Exact edge coordinates should work
        (0, 350, "Exact left edge"),
        (713, 350, "Exact right edge"),
        (350, 0, "Exact top edge"),
        (350, 713, "Exact bottom edge"),
    ]
    
    for click_x, click_y, description in test_cases:
        print(f"📍 {description}:")
        result = simulate_click_handling(img_width, img_height, click_x, click_y)
    
    print("✅ All test cases completed!")
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("- Middle clicks: Should remain exactly as clicked")
    print("- Near edges: Should snap to exact edge coordinates")
    print("- No more aggressive scaling or coordinate distortion")
    print("- You should be able to click anywhere in the middle of images")

if __name__ == "__main__":
    main()
