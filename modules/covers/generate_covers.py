#!/usr/bin/env python3
"""
Generate Amazon KDP Cover Images
E-Book and Paperback versions
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_ebook_cover():
    """Create e-book cover (2560 x 1600 px)"""

    # Create image
    width, height = 2560, 1600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Create gradient background (purple-blue)
    for y in range(height):
        # Gradient from #667eea to #764ba2
        r = int(102 + (118 - 102) * (y / height))
        g = int(126 + (75 - 126) * (y / height))
        b = int(234 + (162 - 234) * (y / height))
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    # Try to load fonts, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 140)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
        tagline_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        author_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 70)
    except:
        # Fallback to default font with size
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        tagline_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Draw title
    title = "IT CAREER"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = 400
    draw.text((title_x, title_y), title, fill='white', font=title_font)

    # Draw "BLUEPRINT"
    title2 = "BLUEPRINT"
    title2_bbox = draw.textbbox((0, 0), title2, font=title_font)
    title2_width = title2_bbox[2] - title2_bbox[0]
    title2_x = (width - title2_width) // 2
    title2_y = title_y + 150
    draw.text((title2_x, title2_y), title2, fill='white', font=title_font)

    # Draw subtitle
    subtitle = "INTERACTIVE WORKBOOK"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title2_y + 180
    draw.text((subtitle_x, subtitle_y), subtitle, fill='white', font=subtitle_font)

    # Draw tagline
    tagline = "8 Tools to Manage, Track & Accelerate Your Career"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    tagline_y = 1100
    draw.text((tagline_x, tagline_y), tagline, fill='white', font=tagline_font)

    # Draw author
    author = "Diatasso™ PRCM™"
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_width = author_bbox[2] - author_bbox[0]
    author_x = (width - author_width) // 2
    author_y = 1400
    draw.text((author_x, author_y), author, fill='white', font=author_font)

    # Add decorative line
    line_y = 1050
    line_width = 800
    line_x1 = (width - line_width) // 2
    line_x2 = line_x1 + line_width
    draw.rectangle([(line_x1, line_y), (line_x2, line_y + 4)], fill='white')

    return img

def create_paperback_cover():
    """Create paperback cover (6x9 + spine + back)"""

    # Paperback specs for 6x9 book
    # Front: 6 x 9 inches = 1800 x 2700 px at 300 DPI
    # Spine: depends on page count (assume 100 pages = ~0.22 inches = 66 px)
    # Back: 6 x 9 inches = 1800 x 2700 px
    # Total width: 1800 + 66 + 1800 = 3666 px
    # Height: 2700 px

    width, height = 3666, 2700
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Create gradient background
    for y in range(height):
        r = int(102 + (118 - 102) * (y / height))
        g = int(126 + (75 - 126) * (y / height))
        b = int(234 + (162 - 234) * (y / height))
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 180)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        tagline_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 70)
        author_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 90)
        spine_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        back_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        tagline_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        spine_font = ImageFont.load_default()
        back_font = ImageFont.load_default()

    # FRONT COVER (right side)
    front_x = 1866  # spine + back

    # Draw title on front
    title = "IT CAREER"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = front_x + (1800 - title_width) // 2
    title_y = 600
    draw.text((title_x, title_y), title, fill='white', font=title_font)

    title2 = "BLUEPRINT"
    title2_bbox = draw.textbbox((0, 0), title2, font=title_font)
    title2_width = title2_bbox[2] - title2_bbox[0]
    title2_x = front_x + (1800 - title2_width) // 2
    title2_y = title_y + 200
    draw.text((title2_x, title2_y), title2, fill='white', font=title_font)

    # Subtitle
    subtitle = "INTERACTIVE"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = front_x + (1800 - subtitle_width) // 2
    subtitle_y = title2_y + 230
    draw.text((subtitle_x, subtitle_y), subtitle, fill='white', font=subtitle_font)

    subtitle2 = "WORKBOOK"
    subtitle2_bbox = draw.textbbox((0, 0), subtitle2, font=subtitle_font)
    subtitle2_width = subtitle2_bbox[2] - subtitle2_bbox[0]
    subtitle2_x = front_x + (1800 - subtitle2_width) // 2
    subtitle2_y = subtitle_y + 140
    draw.text((subtitle2_x, subtitle2_y), subtitle2, fill='white', font=subtitle_font)

    # Tagline
    tagline = "8 Tools to Manage, Track"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = front_x + (1800 - tagline_width) // 2
    tagline_y = 1900
    draw.text((tagline_x, tagline_y), tagline, fill='white', font=tagline_font)

    tagline2 = "& Accelerate Your Career"
    tagline2_bbox = draw.textbbox((0, 0), tagline2, font=tagline_font)
    tagline2_width = tagline2_bbox[2] - tagline2_bbox[0]
    tagline2_x = front_x + (1800 - tagline2_width) // 2
    tagline2_y = tagline_y + 80
    draw.text((tagline2_x, tagline2_y), tagline2, fill='white', font=tagline_font)

    # Author
    author = "Diatasso™ PRCM™"
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_width = author_bbox[2] - author_bbox[0]
    author_x = front_x + (1800 - author_width) // 2
    author_y = 2400
    draw.text((author_x, author_y), author, fill='white', font=author_font)

    # SPINE
    spine_text = "IT CAREER BLUEPRINT INTERACTIVE WORKBOOK  •  Diatasso™ PRCM™"
    # Rotate and draw on spine (vertical text)
    spine_img = Image.new('RGBA', (2700, 66), color=(102, 126, 234, 0))
    spine_draw = ImageDraw.Draw(spine_img)
    spine_draw.text((100, 8), spine_text, fill='white', font=spine_font)
    spine_img = spine_img.rotate(90, expand=True)
    # Paste spine
    img.paste(spine_img, (1800, 0), spine_img)

    # BACK COVER (left side)
    back_text = [
        "Transform IT Career Blueprint strategies into action",
        "",
        "8 INTEGRATED TOOLS:",
        "• Dashboard - Command Center",
        "• Job Application Tracker",
        "• Interview Practice (AI-Powered)",
        "• Document Generator",
        "• Email Templates",
        "• Salary Calculator",
        "• Career Progress Tracker (24-Week Plan)",
        "• Networking Tracker",
        "",
        "PLATFORM FEATURES:",
        "✓ Secure Authentication  ✓ Database Storage",
        "✓ AI Integration (Optional)  ✓ Visual Analytics",
        "✓ Import/Export Data  ✓ Achievement Badges",
        "",
        "Perfect companion to IT Career Blueprint e-book"
    ]

    back_y = 400
    for line in back_text:
        if line:
            line_bbox = draw.textbbox((0, 0), line, font=back_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (1800 - line_width) // 2
            draw.text((line_x, back_y), line, fill='white', font=back_font)
        back_y += 80

    return img

def main():
    print("="*60)
    print("GENERATING AMAZON KDP COVERS")
    print("="*60)
    print()

    # Create output directory
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate e-book cover
    print("Creating e-book cover (2560 x 1600 px)...")
    ebook_cover = create_ebook_cover()
    ebook_path = os.path.join(output_dir, "ebook_cover.jpg")
    ebook_cover.save(ebook_path, "JPEG", quality=95, dpi=(300, 300))
    print(f"✅ E-book cover saved: {ebook_path}")
    print(f"   Size: {ebook_cover.size}")
    print()

    # Generate paperback cover
    print("Creating paperback cover (3666 x 2700 px)...")
    paperback_cover = create_paperback_cover()
    paperback_path = os.path.join(output_dir, "paperback_cover.jpg")
    paperback_cover.save(paperback_path, "JPEG", quality=95, dpi=(300, 300))
    print(f"✅ Paperback cover saved: {paperback_path}")
    print(f"   Size: {paperback_cover.size}")
    print()

    print("="*60)
    print("COVERS GENERATED SUCCESSFULLY!")
    print("="*60)
    print()
    print("Files created:")
    print(f"  1. ebook_cover.jpg (for Kindle/E-book)")
    print(f"  2. paperback_cover.jpg (for Print book)")
    print()
    print("Ready to upload to Amazon KDP!")
    print()

if __name__ == '__main__':
    main()
