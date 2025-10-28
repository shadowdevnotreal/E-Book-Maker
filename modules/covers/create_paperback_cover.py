#!/usr/bin/env python3
"""
Create paperback cover with exact Amazon KDP dimensions
Expected: 18.329 x 11.250 inches at 300 DPI
"""

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import io

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

    # Resize original to fit front cover (2550 x 3375) maintaining aspect ratio
    # Create canvas for front cover
    front_canvas = Image.new('RGB', (front_width, height_px), (255, 255, 255))
    img_ratio = original.width / original.height
    front_ratio = front_width / height_px

    if img_ratio > front_ratio:
        new_width = front_width
        new_height = int(new_width / img_ratio)
    else:
        new_height = height_px
        new_width = int(new_height * img_ratio)

    front_resized = original.resize((new_width, new_height), Image.Resampling.LANCZOS)
    front_x_offset = (front_width - new_width) // 2
    front_y_offset = (height_px - new_height) // 2
    front_canvas.paste(front_resized, (front_x_offset, front_y_offset))

    # Paste front cover on the right side
    front_x = back_width + spine_width
    paperback.paste(front_canvas, (front_x, 0))

    # Create back cover (mirror/resize original or use white space) maintaining aspect ratio
    # Create canvas for back cover
    back_canvas = Image.new('RGB', (back_width, height_px), (255, 255, 255))
    back_ratio = back_width / height_px

    if img_ratio > back_ratio:
        new_width = back_width
        new_height = int(new_width / img_ratio)
    else:
        new_height = height_px
        new_width = int(new_height * img_ratio)

    back_resized = original.resize((new_width, new_height), Image.Resampling.LANCZOS)
    back_x_offset = (back_width - new_width) // 2
    back_y_offset = (height_px - new_height) // 2
    back_canvas.paste(back_resized, (back_x_offset, back_y_offset))

    paperback.paste(back_canvas, (0, 0))

    # Spine - keep simple white or very subtle
    # (Amazon will check that text doesn't go into spine safe zones)

    # Amazon KDP requires PDF format for print covers
    output_file = "IT-Career-Blueprint-Paperback.pdf"

    # Ensure RGB mode first (required for consistent conversion)
    if paperback.mode not in ('RGB', 'CMYK'):
        paperback = paperback.convert('RGB')

    # Convert to CMYK for print quality (KDP recommendation)
    if paperback.mode != 'CMYK':
        paperback = paperback.convert('CMYK')
        print("  Color mode: CMYK (print-optimized)")

    # Create PDF with exact dimensions
    c = canvas.Canvas(output_file, pagesize=(width_inches * inch, height_inches * inch))
    c.setTitle("IT Career Blueprint - Paperback Cover")
    c.setCreator("E-Book Maker v2.1")
    c.setSubject("Book Cover - Amazon KDP Compliant - Print Ready")

    # Save PIL image to buffer as high-quality JPEG
    img_buffer = io.BytesIO()
    # JPEG format supports both RGB and CMYK
    paperback.save(img_buffer, format='JPEG', quality=95, dpi=(dpi, dpi), optimize=True)
    img_buffer.seek(0)

    # Create ImageReader for reportlab compatibility
    from reportlab.lib.utils import ImageReader
    img_reader = ImageReader(img_buffer)

    # Draw image to fill entire page
    c.drawImage(img_reader, 0, 0, width=width_inches * inch, height=height_inches * inch, preserveAspectRatio=False)
    c.save()

    file_size = os.path.getsize(output_file) / 1024

    print("✅ Paperback cover created!")
    print()
    print(f"Output: {output_file} (PDF format - KDP required)")
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
