#!/usr/bin/env python3
"""
Generate VeriFlow IDE application icon
Creates a 256x256 PNG icon with gradient background
Uses PIL/Pillow for compatibility
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: PIL/Pillow not installed")
    print("Install with: pip install Pillow")
    exit(1)

def create_icon(size=256):
    """Create VeriFlow IDE icon with gradient background"""
    # Create image with transparent background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw gradient background (rounded rectangle)
    # Create gradient from blue to darker blue
    for y in range(10, size - 10):
        # Calculate gradient color
        ratio = (y - 10) / (size - 20)
        r = int(33 + ratio * (21 - 33))
        g = int(150 + ratio * (101 - 150))
        b = int(243 + ratio * (192 - 243))
        color = (r, g, b, 255)
        draw.line([(10, y), (size - 10, y)], fill=color, width=1)
    
    # Round the corners (simple approach)
    corner_radius = 20
    # Clear corners
    draw.rectangle([(0, 0), (corner_radius, corner_radius)], fill=(0, 0, 0, 0))
    draw.rectangle([(size - corner_radius, 0), (size, corner_radius)], fill=(0, 0, 0, 0))
    draw.rectangle([(0, size - corner_radius), (corner_radius, size)], fill=(0, 0, 0, 0))
    draw.rectangle([(size - corner_radius, size - corner_radius), (size, size)], fill=(0, 0, 0, 0))
    
    # Draw "V" text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.5))
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box for centering
    text = "V"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Draw circuit lines accent
    line_y = size // 4
    draw.line([(40, line_y), (size - 40, line_y)], fill=(255, 255, 255, 100), width=2)
    # Vertical lines
    draw.line([(size // 3, line_y - 20), (size // 3, line_y + 20)], fill=(255, 255, 255, 100), width=2)
    draw.line([(2 * size // 3, line_y - 20), (2 * size // 3, line_y + 20)], fill=(255, 255, 255, 100), width=2)
    
    return image

if __name__ == "__main__":
    import os
    
    # Create icon
    icon = create_icon(256)
    
    # Save to resources/icons/
    output_path = os.path.join(os.path.dirname(__file__), "veriflow-ide.png")
    icon.save(output_path)
    print(f"✓ Icon created: {output_path}")
    
    # Create additional sizes
    for size in [16, 32, 48, 64, 128]:
        scaled = icon.resize((size, size), Image.Resampling.LANCZOS)
        scaled_path = os.path.join(os.path.dirname(__file__), f"veriflow-ide-{size}.png")
        scaled.save(scaled_path)
        print(f"✓ Icon created: {scaled_path}")
