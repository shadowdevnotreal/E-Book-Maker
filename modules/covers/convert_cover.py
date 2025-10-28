#!/usr/bin/env python3
"""
Convert IT-Career-Blueprint.png to proper Amazon KDP format
"""

from PIL import Image
import os

def convert_cover():
    """Convert PNG to JPEG with proper Amazon KDP dimensions"""

    # Paths
    input_file = "IT-Career-Blueprint.png"
    output_file = "IT-Career-Blueprint.jpg"

    print("Converting IT-Career-Blueprint.png to Amazon KDP format...")
    print()

    # Open the image
    img = Image.open(input_file)

    print(f"Original dimensions: {img.size}")
    print(f"Original format: {img.format}")
    print()

    # Amazon KDP e-book cover requirements: 1600 x 2560 portrait (1.6:1 ratio)
    target_width = 1600
    target_height = 2560

    # Convert to RGB if needed (PNG might have transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize to Amazon KDP dimensions while maintaining aspect ratio
    # Create white background canvas
    canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))

    # Calculate scaling to fit within target while maintaining aspect ratio
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Image is wider than target - fit to width
        new_width = target_width
        new_height = int(new_width / img_ratio)
    else:
        # Image is taller than target - fit to height
        new_height = target_height
        new_width = int(new_height * img_ratio)

    # Resize image maintaining aspect ratio
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center the resized image on the canvas
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    canvas.paste(img_resized, (x_offset, y_offset))

    img_resized = canvas

    print(f"New dimensions: {img_resized.size}")
    print(f"Aspect ratio: 1.6:1 (Amazon KDP compliant)")
    print()

    # Save as high-quality JPEG at 300 DPI
    img_resized.save(output_file, "JPEG", quality=95, dpi=(300, 300))

    # Get file sizes
    old_size = os.path.getsize(input_file) / 1024
    new_size = os.path.getsize(output_file) / 1024

    print(f"✅ Conversion complete!")
    print()
    print(f"Output file: {output_file}")
    print(f"Format: JPEG")
    print(f"Quality: 95%")
    print(f"Resolution: 300 DPI")
    print(f"Color Mode: RGB")
    print(f"Old file size: {old_size:.1f} KB")
    print(f"New file size: {new_size:.1f} KB")
    print()

    # IMPORTANT: We do NOT delete the original input file
    # Users may need to keep their original files for archival, backup, or future use
    # Deleting user files without explicit permission is a serious data loss risk
    # os.remove(input_file)  # DANGEROUS - Never auto-delete user input files!

    print(f"ℹ️  Original file preserved: {input_file}")
    print()
    print("✅ Ready to upload to Amazon KDP!")

if __name__ == '__main__':
    convert_cover()
