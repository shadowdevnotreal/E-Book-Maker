#!/usr/bin/env python3
"""
Create paperback cover with exact Amazon KDP dimensions
Expected: 18.329 x 11.250 inches at 300 DPI
"""

from PIL import Image
import os

def create_paperback_cover():
    """Create paperback cover with Amazon's expected dimensions"""

    # Amazon's expected dimensions
    # 18.329 x 11.250 inches at 300 DPI
    width_inches = 18.329
    height_inches = 11.250
    dpi = 300

    width_px = int(width_inches * dpi)   # 5498.7 ≈ 5499 pixels
    height_px = int(height_inches * dpi)  # 3375 pixels

    print("Creating paperback cover for Amazon KDP...")
    print(f"Dimensions: {width_px} x {height_px} pixels")
    print(f"Size: {width_inches} x {height_inches} inches at {dpi} DPI")
    print()

    # Open the original cover image
    input_file = "IT-Career-Blueprint.jpg"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    original = Image.open(input_file)
    print(f"Original cover: {original.size}")
    print()

    # Create the full paperback wrap
    # This is a full wrap cover: Back + Spine + Front

    # Calculate sections (approximate - spine is ~1.329" based on total width)
    # For an 8.5 x 11" book:
    # Back: 8.5" = 2550 px
    # Spine: 1.329" = 399 px
    # Front: 8.5" = 2550 px
    # Total: 18.329" = 5499 px

    back_width = 2550
    spine_width = 399
    front_width = 2550

    # Create new image with white background
    paperback = Image.new('RGB', (width_px, height_px), 'white')

    # Resize original to fit front cover (2550 x 3375)
    front_cover = original.resize((front_width, height_px), Image.Resampling.LANCZOS)

    # Paste front cover on the right side
    front_x = back_width + spine_width
    paperback.paste(front_cover, (front_x, 0))

    # Create back cover (mirror/resize original or use white space)
    # For now, let's resize the original to fit back as well
    back_cover = original.resize((back_width, height_px), Image.Resampling.LANCZOS)
    paperback.paste(back_cover, (0, 0))

    # Spine - keep simple white or very subtle
    # (Amazon will check that text doesn't go into spine safe zones)

    output_file = "IT-Career-Blueprint-Paperback.jpg"
    paperback.save(output_file, "JPEG", quality=95, dpi=(dpi, dpi))

    file_size = os.path.getsize(output_file) / 1024

    print("✅ Paperback cover created!")
    print()
    print(f"Output: {output_file}")
    print(f"Dimensions: {paperback.size} pixels")
    print(f"Size: {width_inches} x {height_inches} inches")
    print(f"Resolution: {dpi} DPI")
    print(f"File size: {file_size:.1f} KB")
    print()
    print("✅ Ready to upload to Amazon KDP as paperback cover!")
    print()
    print("Note: This cover has:")
    print(f"  - Back cover: {back_width}px (8.5\")")
    print(f"  - Spine: {spine_width}px (1.329\")")
    print(f"  - Front cover: {front_width}px (8.5\")")
    print(f"  - Total: {width_px}px ({width_inches}\")")

if __name__ == '__main__':
    create_paperback_cover()
