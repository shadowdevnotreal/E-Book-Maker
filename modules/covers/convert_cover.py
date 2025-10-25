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

    # Amazon KDP e-book cover requirements: 2560 x 1600 (1.6:1 ratio)
    target_width = 2560
    target_height = 1600

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

    # Resize to Amazon KDP dimensions
    # Use LANCZOS for high-quality downsampling
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

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

    # Delete the old PNG file
    os.remove(input_file)
    print(f"🗑️  Deleted old file: {input_file}")
    print()
    print("✅ Ready to upload to Amazon KDP!")

if __name__ == '__main__':
    convert_cover()
