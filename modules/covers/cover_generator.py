"""
Book Cover Generator Module
Creates and converts book covers for e-books and paperbacks
Consolidated from AMAZON_KDP_PACKAGE cover tools

Supports:
- PDF, PNG, JPG, JPEG input formats
- 300 DPI print-ready output
- KDP-compliant barcode safe area (2.0" × 1.2")
- Vertical spine text (centered)
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Dict, Optional, Tuple
import fitz  # PyMuPDF for PDF support
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kdp_calculator import KDPCalculator


class CoverGenerator:
    """Generate and convert book covers"""

    # KDP Requirements (based on official KDP documentation)
    # Source: https://kdp.amazon.com/en_US/help/topic/G201953020
    MIN_SPINE_TEXT_PAGES = 79  # Minimum pages required for spine text
    SPINE_TEXT_CLEARANCE = 0.0625  # 0.0625" (1.6mm) minimum clearance from spine edges
    PRODUCTION_VARIANCE = 0.0125  # ±0.0125" (3.2mm) production tolerance
    MIN_FONT_SIZE = 7  # Minimum 7pt font for readability

    # E-book cover specifications (Amazon KDP compliant)
    # KDP requires: 1600 × 2560 pixels (portrait orientation, 1.6:1 aspect ratio)
    EBOOK_WIDTH = 1600  # Portrait width
    EBOOK_HEIGHT = 2560  # Portrait height
    EBOOK_DPI = 300

    # Paperback specifications (6" x 9" book, ~100 pages)
    # For 6"x9" book: back (6") + spine (~0.2") + front (6") = ~12.2" width x 9" height
    PAPERBACK_WIDTH = 3666  # 12.22" at 300 DPI (wrap width)
    PAPERBACK_HEIGHT = 2700  # 9" at 300 DPI (book height)
    PAPERBACK_SPINE_WIDTH = 66
    PAPERBACK_DPI = 300

    # Alternative paperback size
    ALT_PAPERBACK_WIDTH = 3666
    ALT_PAPERBACK_HEIGHT = 2700
    ALT_PAPERBACK_SPINE_WIDTH = 66

    # Hardback/Hardcover specifications (6.5" x 9.5" book with dust jacket)
    # Hardbacks are typically 0.25-0.5" larger than paperback trim
    # For 6"x9" paperback -> 6.5"x9.5" hardback with dust jacket
    HARDBACK_WIDTH = 4650   # Total width including flaps (15.5" at 300 DPI)
    HARDBACK_HEIGHT = 2850  # 9.5" at 300 DPI (0.5" taller than paperback)
    HARDBACK_SPINE_WIDTH = 450  # Slightly thicker spine for hard covers
    HARDBACK_FLAP_WIDTH = 900  # 3" flaps on each side (300 DPI)
    HARDBACK_DPI = 300

    # Alternative hardback size (for 6"x9" content -> 6.5"x9.5" hardback)
    ALT_HARDBACK_WIDTH = 4650   # Total width including flaps
    ALT_HARDBACK_HEIGHT = 2850  # 9.5" at 300 DPI
    ALT_HARDBACK_SPINE_WIDTH = 450
    ALT_HARDBACK_FLAP_WIDTH = 900  # 3" flaps

    def __init__(self):
        """Initialize cover generator"""
        self.default_font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            'C:\\Windows\\Fonts\\arial.ttf',
            'C:\\Windows\\Fonts\\arialbd.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
        ]
        # Try to import AI assistant for color suggestions
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from ai.groq_assistant import GroqAssistant
            self.ai_assistant = GroqAssistant()
            self.ai_enabled = self.ai_assistant.is_enabled()
        except:
            self.ai_assistant = None
            self.ai_enabled = False

    def calculate_spine_width(self, page_count: int, paper_type: str = 'white',
                            binding_type: str = 'paperback') -> float:
        """
        Calculate spine width based on Amazon KDP specifications

        Uses centralized KDP calculator module for consistent calculations.

        Args:
            page_count: Number of pages in the book
            paper_type: 'white', 'cream', or 'color'
            binding_type: 'paperback' or 'hardcover'

        Returns:
            Spine width in inches
        """
        # Use centralized KDP calculator
        spine_width = KDPCalculator.calculate_spine_width(page_count, paper_type)

        # Hardcover boards add thickness
        if binding_type == 'hardcover':
            spine_width += 0.25  # Add 0.25" for hardcover boards

        return spine_width

    def calculate_cover_dimensions(self, trim_width: float, trim_height: float,
                                  page_count: int, paper_type: str = 'white',
                                  binding_type: str = 'paperback',
                                  dpi: int = 300) -> Dict[str, int]:
        """
        Calculate complete cover dimensions for Amazon KDP

        Args:
            trim_width: Book width in inches (e.g., 6 for 6x9 book)
            trim_height: Book height in inches (e.g., 9 for 6x9 book)
            page_count: Number of pages
            paper_type: 'white', 'cream', or 'color'
            binding_type: 'paperback' or 'hardcover'
            dpi: Resolution (typically 300)

        Returns:
            Dictionary with cover dimensions in pixels
        """
        # Calculate spine width
        spine_width_inches = self.calculate_spine_width(page_count, paper_type, binding_type)

        # Add bleed (0.125" on all edges for paperback, 0.125" for hardcover)
        bleed = 0.125

        # For hardcover, account for board thickness
        if binding_type == 'hardcover':
            # Hardcover is typically 0.25" wider and taller
            trim_width += 0.25
            trim_height += 0.25

        # Calculate full wrap dimensions
        # Width: bleed + back + spine + front + bleed
        cover_width_inches = (bleed * 2) + (trim_width * 2) + spine_width_inches
        # Height: bleed + height + bleed
        cover_height_inches = (bleed * 2) + trim_height

        # Convert to pixels
        cover_width_px = int(cover_width_inches * dpi)
        cover_height_px = int(cover_height_inches * dpi)
        spine_width_px = int(spine_width_inches * dpi)

        return {
            'cover_width': cover_width_px,
            'cover_height': cover_height_px,
            'spine_width': spine_width_px,
            'trim_width': trim_width,
            'trim_height': trim_height,
            'spine_width_inches': spine_width_inches,
            'cover_width_inches': cover_width_inches,
            'cover_height_inches': cover_height_inches,
            'dpi': dpi,
            'page_count': page_count,
            'paper_type': paper_type,
            'binding_type': binding_type
        }

    def get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with fallback to default if TrueType fonts unavailable"""
        font_paths = self.default_font_paths if not bold else [self.default_font_paths[0]] + self.default_font_paths

        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (IOError, OSError):
                continue

        # Fallback to default font
        return ImageFont.load_default()

    def create_gradient(self, width: int, height: int,
                       color1: Tuple[int, int, int],
                       color2: Tuple[int, int, int]) -> Image.Image:
        """Create a gradient background"""
        base = Image.new('RGB', (width, height), color1)
        top = Image.new('RGB', (width, height), color2)

        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            for x in range(width):
                mask_data.append(int(255 * (y / height)))
        mask.putdata(mask_data)

        base.paste(top, (0, 0), mask)
        return base

    def extract_dominant_colors(self, img: Image.Image, num_colors: int = 5) -> list:
        """
        Extract dominant colors from image using K-means clustering

        Args:
            img: PIL Image
            num_colors: Number of dominant colors to extract

        Returns:
            List of RGB tuples representing dominant colors
        """
        # Resize image for faster processing
        img_small = img.copy()
        img_small.thumbnail((100, 100))

        # Convert to RGB if needed
        if img_small.mode != 'RGB':
            img_small = img_small.convert('RGB')

        # Get pixel data
        pixels = list(img_small.getdata())

        # Simple approach: get most common colors by frequency
        from collections import Counter
        color_counts = Counter(pixels)
        dominant = color_counts.most_common(num_colors)

        return [color for color, count in dominant]

    def get_ai_spine_color(self, cover_colors: list, title: str = "") -> Tuple[int, int, int]:
        """
        Use AI to suggest the best spine color based on cover colors

        Args:
            cover_colors: List of RGB tuples from the cover
            title: Book title for context

        Returns:
            RGB tuple for spine color
        """
        if not self.ai_enabled or not self.ai_assistant:
            # Fallback to simple average
            if cover_colors:
                avg_r = sum(c[0] for c in cover_colors) // len(cover_colors)
                avg_g = sum(c[1] for c in cover_colors) // len(cover_colors)
                avg_b = sum(c[2] for c in cover_colors) // len(cover_colors)
                return (avg_r, avg_g, avg_b)
            return (128, 128, 128)

        try:
            # Convert colors to hex for AI
            hex_colors = ['#{:02x}{:02x}{:02x}'.format(r, g, b) for r, g, b in cover_colors[:3]]

            prompt = f"""Based on these dominant colors from a book cover: {', '.join(hex_colors)}
Book title: {title if title else 'Generic Book'}

Suggest the BEST single color for the book spine that:
1. Complements the cover colors
2. Creates visual harmony
3. Will stand out on a bookshelf
4. Looks professional

Return ONLY the hex color code in format: #RRGGBB
No explanation, just the color code."""

            response = self.ai_assistant._make_request(prompt, max_tokens=20)

            if response and '#' in response:
                # Extract hex code
                hex_code = response.strip().split('#')[1][:6]
                # Convert to RGB
                r = int(hex_code[0:2], 16)
                g = int(hex_code[2:4], 16)
                b = int(hex_code[4:6], 16)
                print(f"  🤖 AI suggested spine color: #{hex_code} (RGB: {r}, {g}, {b})")
                return (r, g, b)
        except Exception as e:
            print(f"  AI spine color suggestion failed: {e}")

        # Fallback to dominant color
        return cover_colors[0] if cover_colors else (128, 128, 128)

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int,
                  draw: ImageDraw.ImageDraw) -> list:
        """
        Wrap text to fit within max_width

        Args:
            text: Text to wrap
            font: Font to use for measuring
            max_width: Maximum width in pixels
            draw: ImageDraw object for text measurement

        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Try adding word to current line
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start new line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)

        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def calculate_luminance(self, img: Image.Image, sample_area: Tuple[int, int, int, int] = None) -> float:
        """
        Calculate perceived luminance of an image or region
        Uses ITU-R BT.709 coefficients for accurate brightness perception

        Args:
            img: PIL Image to analyze
            sample_area: Optional (x1, y1, x2, y2) tuple to sample specific area

        Returns:
            Luminance value from 0 (black) to 255 (white)
        """
        # Sample the area where text will be placed, or entire image
        if sample_area:
            sample = img.crop(sample_area)
        else:
            # Sample center area where most text appears
            width, height = img.size
            sample = img.crop((
                width // 4,
                height // 4,
                3 * width // 4,
                3 * height // 4
            ))

        # Convert to RGB if needed
        if sample.mode != 'RGB':
            sample = sample.convert('RGB')

        # Get pixel data
        pixels = list(sample.getdata())

        # Calculate average luminance using ITU-R BT.709
        # Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
        total_luminance = 0
        for r, g, b in pixels:
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            total_luminance += luminance

        avg_luminance = total_luminance / len(pixels)
        return avg_luminance

    def get_optimal_text_color(self, img: Image.Image, sample_area: Tuple[int, int, int, int] = None) -> Tuple[int, int, int]:
        """
        Determine optimal text color (black or white) based on background brightness

        Args:
            img: Background image
            sample_area: Optional area to sample

        Returns:
            RGB tuple for text color (either white or black)
        """
        luminance = self.calculate_luminance(img, sample_area)

        # Threshold at 127.5 (middle of 0-255 range)
        # For bright backgrounds (>127.5), use black text
        # For dark backgrounds (≤127.5), use white text
        if luminance > 127.5:
            return (0, 0, 0)  # Black text
        else:
            return (255, 255, 255)  # White text

    def draw_text_with_stroke(self, img: Image.Image, text: str,
                              position: Tuple[int, int], font: ImageFont.FreeTypeFont,
                              text_color: Tuple[int, int, int],
                              add_stroke: bool = True) -> Image.Image:
        """
        Draw text with stroke (outline) and shadow for better readability - blends naturally

        Args:
            img: PIL Image to draw on
            text: Text to draw
            position: (x, y) position for text
            font: Font to use
            text_color: RGB color for text
            add_stroke: Whether to add stroke and shadow

        Returns:
            Modified image
        """
        draw = ImageDraw.Draw(img)

        if add_stroke:
            # Determine stroke color (inverse of text color)
            if text_color == (255, 255, 255):  # White text
                stroke_color = (0, 0, 0)  # Black stroke
                shadow_color = (0, 0, 0, 80)  # Semi-transparent black shadow
            else:  # Black text
                stroke_color = (255, 255, 255)  # White stroke
                shadow_color = (255, 255, 255, 80)  # Semi-transparent white shadow

            # For shadow, we need to use RGBA mode temporarily
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Create shadow layer
            shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)

            # Draw subtle shadow for depth (offset by 4 pixels)
            shadow_pos = (position[0] + 4, position[1] + 4)
            shadow_draw.text(shadow_pos, text, fill=shadow_color, font=font)

            # Composite shadow onto image
            img = Image.alpha_composite(img, shadow_layer)

            # Convert back to RGB for main text
            img = img.convert('RGB')
            draw = ImageDraw.Draw(img)

            # Draw text with stroke (outline) - this blends naturally
            draw.text(position, text, fill=text_color, font=font, stroke_width=3, stroke_fill=stroke_color)
        else:
            # Draw text without stroke
            draw.text(position, text, fill=text_color, font=font)

        return img

    def save_optimized_jpeg(self, img: Image.Image, output_path: Path,
                           dpi: int = 300, quality: int = 95) -> None:
        """
        Save image as optimized JPEG with best practices

        Args:
            img: PIL Image to save
            output_path: Path to save to
            dpi: Resolution in DPI
            quality: JPEG quality (1-100)
        """
        # Ensure RGB mode
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save with optimized settings
        img.save(
            str(output_path),
            'JPEG',
            quality=quality,
            dpi=(dpi, dpi),
            optimize=True,
            progressive=True,
            subsampling=0  # 4:4:4 for best quality
        )

    def save_as_pdf(self, img: Image.Image, output_path: Path,
                   dpi: int = 300, title: str = "Book Cover", use_cmyk: bool = True) -> None:
        """
        Save image as PDF with KDP compliance (PDF/X-1a compatible)

        Amazon KDP requirements for print covers:
        - PDF format (paperback/hardback)
        - 300 DPI minimum resolution
        - CMYK color mode for print quality (KDP recommendation)
        - All fonts embedded (not applicable for image-based covers)
        - Max file size: 650MB

        Args:
            img: PIL Image to save
            output_path: Path to save to
            dpi: Resolution in DPI (should be 300 for KDP)
            title: PDF document title metadata
            use_cmyk: Convert to CMYK for print (default: True)

        Note:
            Amazon KDP accepts RGB images and converts to CMYK during printing.
            However, pre-converting to CMYK ensures better color accuracy.
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.utils import ImageReader
        import io

        # Ensure RGB mode first (required for consistent conversion)
        if img.mode not in ('RGB', 'CMYK'):
            img = img.convert('RGB')

        # Convert to CMYK for print quality (KDP recommendation)
        if use_cmyk and img.mode != 'CMYK':
            # Convert RGB to CMYK for professional printing
            # Note: Amazon KDP will also apply their own color management
            img = img.convert('CMYK')
            print(f"  Color mode: CMYK (print-optimized)")
        elif img.mode == 'RGB':
            print(f"  Color mode: RGB (will be converted by KDP)")

        # Calculate page size in inches (at specified DPI)
        width_inches = img.width / dpi
        height_inches = img.height / dpi

        # Create PDF with exact dimensions
        c = canvas.Canvas(str(output_path), pagesize=(width_inches * inch, height_inches * inch))

        # Set PDF metadata for KDP compliance
        c.setTitle(title)
        c.setCreator("E-Book Maker v2.1")
        c.setSubject("Book Cover - Amazon KDP Compliant - Print Ready")

        # Save PIL image to temporary buffer as high-quality JPEG
        img_buffer = io.BytesIO()
        # JPEG format supports both RGB and CMYK
        img.save(img_buffer, format='JPEG', quality=95, dpi=(dpi, dpi), optimize=True)
        img_buffer.seek(0)

        # Create ImageReader for reportlab compatibility
        img_reader = ImageReader(img_buffer)

        # Draw image to fill entire page (no margins, exact fit)
        c.drawImage(
            img_reader,
            0, 0,
            width=width_inches * inch,
            height=height_inches * inch,
            preserveAspectRatio=False
        )

        # Save PDF
        c.save()

        color_mode = "CMYK" if use_cmyk else "RGB"
        print(f"PDF saved: {output_path} ({img.width}x{img.height}px @ {dpi} DPI, {color_mode})")

    def create_cover(self, cover_type: str, title: str, subtitle: str,
                    author: str, style: str, colors: Dict[str, str],
                    output_dir: Path, background_image: Optional[Path] = None,
                    add_barcode_area: bool = True,
                    page_count: int = 100,
                    paper_type: str = 'white',
                    trim_width: float = 6.0,
                    trim_height: float = 9.0) -> Path:
        """
        Create a book cover from scratch

        Args:
            cover_type: 'ebook', 'paperback', or 'hardback'
            title: Book title
            subtitle: Book subtitle
            author: Author name
            style: Cover style ('gradient', 'solid', 'minimalist')
            colors: Dictionary with 'primary' and 'secondary' hex colors
            output_dir: Output directory
            background_image: Optional path to background image/PDF
            add_barcode_area: Add KDP barcode safe area for paperback/hardback (default: True)
            page_count: Number of pages (used for spine width calculation, default: 100)
            paper_type: Paper type for spine calculation ('white', 'cream', 'color', default: 'white')
            trim_width: Book width in inches (default: 6.0 for 6x9)
            trim_height: Book height in inches (default: 9.0 for 6x9)

        Returns:
            Path to created cover
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Calculate actual dimensions using KDP specifications
        if cover_type == 'ebook':
            width, height = self.EBOOK_WIDTH, self.EBOOK_HEIGHT
            dpi = self.EBOOK_DPI
            title_size = 140
            subtitle_size = 100
            author_size = 70
            spine_width_px = 0
        elif cover_type in ['paperback', 'hardback']:
            # Use KDP calculator for accurate dimensions
            binding_type = 'hardcover' if cover_type == 'hardback' else 'paperback'
            dims = KDPCalculator.calculate_cover_dimensions(
                trim_width=trim_width,
                trim_height=trim_height,
                page_count=page_count,
                paper_type=paper_type,
                binding_type=binding_type,
                dpi=300
            )

            width = dims.width_pixels
            height = dims.height_pixels
            spine_width_px = dims.spine_width_pixels
            dpi = 300

            if cover_type == 'hardback':
                title_size = 200
                subtitle_size = 130
                author_size = 95
            else:
                title_size = 180
                subtitle_size = 120
                author_size = 90
        else:
            # Fallback for unknown type - use paperback defaults
            width, height = self.PAPERBACK_WIDTH, self.PAPERBACK_HEIGHT
            dpi = self.PAPERBACK_DPI
            spine_width_px = self.PAPERBACK_SPINE_WIDTH
            title_size = 180
            subtitle_size = 120
            author_size = 90

        # Create background
        if background_image and Path(background_image).exists():
            # Load background image/PDF
            bg_path = Path(background_image)
            if bg_path.suffix.lower() == '.pdf':
                # Load first page of PDF
                pdf_doc = fitz.open(str(bg_path))
                page = pdf_doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                pdf_doc.close()
            else:
                # Load image file
                img = Image.open(bg_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

            # Resize to target dimensions
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            # Create gradient/solid background
            primary_rgb = self.hex_to_rgb(colors.get('primary', '#667eea'))
            secondary_rgb = self.hex_to_rgb(colors.get('secondary', '#764ba2'))

            if style == 'gradient':
                img = self.create_gradient(width, height, primary_rgb, secondary_rgb)
            elif style == 'solid':
                img = Image.new('RGB', (width, height), primary_rgb)
            else:  # minimalist
                img = Image.new('RGB', (width, height), (255, 255, 255))

        # Load fonts
        title_font = self.get_font(title_size, bold=True)
        subtitle_font = self.get_font(subtitle_size, bold=True)
        author_font = self.get_font(author_size, bold=False)

        # Smart text color selection based on background brightness
        text_color = self.get_optimal_text_color(img)

        # Determine if we need text stroke for better readability
        # Use stroke primarily for custom background images
        # For generated gradients, only use stroke if luminance is in the difficult mid-range
        luminance = self.calculate_luminance(img)
        if background_image is not None:
            # Always use stroke for custom background images (photos, patterns, etc.)
            use_stroke = True
        else:
            # For generated backgrounds, only use stroke in problematic mid-range (110-145)
            # This range is where neither black nor white text stands out well
            use_stroke = (luminance > 110 and luminance < 145)

        draw = ImageDraw.Draw(img)

        # Set margins (100px on each side for safety)
        margin = 100
        max_text_width = width - (2 * margin)

        # Draw title (centered, with wrapping)
        title_lines = self.wrap_text(title, title_font, max_text_width, draw)
        title_y = height // 3

        # Calculate line height for title
        title_bbox = draw.textbbox((0, 0), "Ay", font=title_font)  # Use sample for height
        title_line_height = title_bbox[3] - title_bbox[1]

        # Draw each title line centered
        current_y = title_y
        for line in title_lines:
            line_bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (width - line_width) // 2
            # Use stroke for better readability
            img = self.draw_text_with_stroke(img, line, (line_x, current_y), title_font, text_color, use_stroke)
            # Recreate draw object after modifying image
            draw = ImageDraw.Draw(img)
            current_y += title_line_height + 20  # 20px spacing between lines

        # Draw subtitle if provided (with wrapping)
        if subtitle:
            subtitle_lines = self.wrap_text(subtitle, subtitle_font, max_text_width, draw)
            subtitle_y = current_y + 100  # Space after title

            # Calculate line height for subtitle
            subtitle_bbox = draw.textbbox((0, 0), "Ay", font=subtitle_font)
            subtitle_line_height = subtitle_bbox[3] - subtitle_bbox[1]

            # Draw each subtitle line centered
            current_y = subtitle_y
            for line in subtitle_lines:
                line_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (width - line_width) // 2
                # Use stroke for better readability
                img = self.draw_text_with_stroke(img, line, (line_x, current_y), subtitle_font, text_color, use_stroke)
                # Recreate draw object after modifying image
                draw = ImageDraw.Draw(img)
                current_y += subtitle_line_height + 15  # 15px spacing between lines

        # Draw author (bottom, with wrapping)
        author_lines = self.wrap_text(author, author_font, max_text_width, draw)
        author_y = height - 300

        # Calculate line height for author
        author_bbox = draw.textbbox((0, 0), "Ay", font=author_font)
        author_line_height = author_bbox[3] - author_bbox[1]

        # Draw each author line centered
        current_y = author_y
        for line in author_lines:
            line_bbox = draw.textbbox((0, 0), line, font=author_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (width - line_width) // 2
            # Use stroke for better readability
            img = self.draw_text_with_stroke(img, line, (line_x, current_y), author_font, text_color, use_stroke)
            # Recreate draw object after modifying image
            draw = ImageDraw.Draw(img)
            current_y += author_line_height + 10  # 10px spacing between lines

        # Add decorative element for e-book
        if cover_type == 'ebook' and style != 'minimalist':
            line_y = title_y - 50
            line_width = 600
            line_x = (width - line_width) // 2
            draw.rectangle([line_x, line_y, line_x + line_width, line_y + 5], fill=text_color)

        # Add barcode safe area for paperback/hardback
        if add_barcode_area and cover_type in ['paperback', 'hardback']:
            img = self._add_barcode_safe_area(img, cover_type, dpi)

        # Save cover with appropriate format
        # KDP Requirements: eBook = JPEG, Paperback/Hardback = PDF
        if cover_type == 'ebook':
            output_filename = f"{cover_type}_cover_{title.lower().replace(' ', '_')}.jpg"
            output_path = output_dir / output_filename
            print(f"[DEBUG] Creating ebook cover: {output_path}")
            print(f"[DEBUG] Filename: {output_filename}")
            print(f"[DEBUG] Extension check: {output_path.suffix}")
            self.save_optimized_jpeg(img, output_path, dpi=dpi, quality=95)
        else:  # paperback or hardback
            output_filename = f"{cover_type}_cover_{title.lower().replace(' ', '_')}.pdf"
            output_path = output_dir / output_filename
            print(f"[DEBUG] Creating {cover_type} cover: {output_path}")
            print(f"[DEBUG] Filename: {output_filename}")
            print(f"[DEBUG] Extension check: {output_path.suffix}")
            self.save_as_pdf(img, output_path, dpi=dpi, title=f"{title} - {cover_type.capitalize()} Cover")

        print(f"[DEBUG] File created successfully, checking existence: {output_path.exists()}")
        if output_path.exists():
            print(f"[DEBUG] File size: {output_path.stat().st_size} bytes")
        return output_path

    def _load_cover_image(self, input_file: Path) -> Image.Image:
        """
        Load cover from PDF or image file

        Args:
            input_file: Path to input file (PDF, PNG, JPG, JPEG)

        Returns:
            PIL Image object
        """
        input_file = Path(input_file)
        file_ext = input_file.suffix.lower()

        # Handle PDF files
        if file_ext == '.pdf':
            try:
                pdf_document = fitz.open(str(input_file))
                # Get first page
                page = pdf_document[0]
                # Convert to image at 300 DPI
                pix = page.get_pixmap(dpi=300)
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                pdf_document.close()
                return img
            except Exception as e:
                raise Exception(f"Error loading PDF: {e}")

        # Handle image files
        elif file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            return Image.open(input_file)

        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Use PDF, PNG, JPG, or JPEG.")

    def convert_cover(self, input_file: Path, target_type: str,
                     output_dir: Path, title: str = '', subtitle: str = '',
                     author: str = '', add_text: bool = True,
                     title_color: str = '#FFFFFF', spine_color: str = '#FF6B35',
                     title_position: str = 'top', add_barcode_area: bool = True,
                     page_count: int = 100) -> Path:
        """
        Convert cover image to target format with optional text overlay

        Args:
            input_file: Path to input cover (PDF, PNG, JPG, JPEG)
            target_type: 'ebook', 'paperback', or 'hardback'
            output_dir: Output directory
            title: Book title (optional, will add overlay if provided)
            subtitle: Book subtitle (optional)
            author: Author name (optional)
            add_text: Whether to add text overlays (default: True if title provided)
            title_color: Hex color for title text (default: white)
            spine_color: Hex color for spine background band (default: orange)
            title_position: 'top', 'center', or 'bottom' (default: 'top')
            add_barcode_area: Add KDP barcode safe area for paperback/hardback (default: True)
            page_count: Number of pages (used for spine text validation, default: 100)

        Returns:
            Path to converted cover
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load image (supports PDF and images)
        img = self._load_cover_image(input_file)

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # Resize to target dimensions
        if target_type == 'ebook':
            target_size = (self.EBOOK_WIDTH, self.EBOOK_HEIGHT)
            dpi = self.EBOOK_DPI
        elif target_type == 'hardback':
            target_size = (self.HARDBACK_WIDTH, self.HARDBACK_HEIGHT)
            dpi = self.HARDBACK_DPI
        else:  # paperback
            target_size = (self.PAPERBACK_WIDTH, self.PAPERBACK_HEIGHT)
            dpi = self.PAPERBACK_DPI

        # Resize image while maintaining aspect ratio for ebook only
        # For paperback/hardback, we'll handle aspect ratio per section
        if target_type == 'ebook':
            # Use "cover/fill" mode for ebook - fills entire frame, crops if needed
            # This eliminates white bars and looks more professional for ebook covers
            img_ratio = img.width / img.height
            target_ratio = target_size[0] / target_size[1]

            if img_ratio > target_ratio:
                # Image is wider than target - fit to height and crop width
                new_height = target_size[1]
                new_width = int(new_height * img_ratio)
            else:
                # Image is taller than target - fit to width and crop height
                new_width = target_size[0]
                new_height = int(new_width / img_ratio)

            # Resize image maintaining aspect ratio
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Center crop to exact target size
            x_offset = (new_width - target_size[0]) // 2
            y_offset = (new_height - target_size[1]) // 2
            img_resized = img_resized.crop((
                x_offset,
                y_offset,
                x_offset + target_size[0],
                y_offset + target_size[1]
            ))

        # For paperback, create wrap layout
        if target_type == 'paperback':
            # Create white background for full wrap
            wrap = Image.new('RGB', target_size, (255, 255, 255))

            # Calculate sections
            back_width = (target_size[0] - self.PAPERBACK_SPINE_WIDTH) // 2
            front_width = back_width
            spine_width = self.PAPERBACK_SPINE_WIDTH

            # Place front cover using FILL mode (no white space)
            # Zoom to fill entire section, center crop if needed
            img_ratio = img.width / img.height
            front_ratio = front_width / target_size[1]

            if img_ratio > front_ratio:
                # Image wider - fit to height, crop width
                new_height = target_size[1]
                new_width = int(new_height * img_ratio)
            else:
                # Image taller - fit to width, crop height
                new_width = front_width
                new_height = int(new_width / img_ratio)

            front_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Center crop to exact front size
            front_x_offset = (new_width - front_width) // 2
            front_y_offset = (new_height - target_size[1]) // 2
            front_cover = front_resized.crop((
                front_x_offset,
                front_y_offset,
                front_x_offset + front_width,
                front_y_offset + target_size[1]
            ))

            front_x = back_width + spine_width
            wrap.paste(front_cover, (front_x, 0))

            # Place back cover using FILL mode (no white space)
            back_ratio = back_width / target_size[1]

            if img_ratio > back_ratio:
                # Image wider - fit to height, crop width
                new_height = target_size[1]
                new_width = int(new_height * img_ratio)
            else:
                # Image taller - fit to width, crop height
                new_width = back_width
                new_height = int(new_width / img_ratio)

            back_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Center crop to exact back size
            back_x_offset = (new_width - back_width) // 2
            back_y_offset = (new_height - target_size[1]) // 2
            back_cover = back_resized.crop((
                back_x_offset,
                back_y_offset,
                back_x_offset + back_width,
                back_y_offset + target_size[1]
            ))

            wrap.paste(back_cover, (0, 0))

            # Fill spine with AI-suggested color
            print(f"  Extracting dominant colors from cover...")
            dominant_colors = self.extract_dominant_colors(img, num_colors=5)
            print(f"  Found {len(dominant_colors)} dominant colors")

            # Use AI to select best spine color
            spine_color = self.get_ai_spine_color(dominant_colors, title=title)

            # Create spine background with AI-selected color
            spine_canvas = Image.new('RGB', (spine_width, target_size[1]), spine_color)

            # Add vertical spine text if title provided
            if title:
                from PIL import ImageDraw, ImageFont
                spine_draw = ImageDraw.Draw(spine_canvas)

                # Get contrasting text color
                brightness = sum(spine_color) / 3
                text_color = (255, 255, 255) if brightness < 128 else (0, 0, 0)

                # Get font for spine
                spine_font_size = min(spine_width - 20, 60)  # Fit within spine width with margin
                spine_font = self.get_font(spine_font_size, bold=True)

                # Draw vertical text (rotated 90 degrees)
                # Create temp image for text rotation
                text_img = Image.new('RGBA', (target_size[1], spine_width), (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_img)

                # Center text vertically in spine height
                bbox = text_draw.textbbox((0, 0), title, font=spine_font)
                text_width = bbox[2] - bbox[0]
                text_x = (target_size[1] - text_width) // 2

                # Draw text horizontally first
                text_draw.text((text_x, 10), title, font=spine_font, fill=text_color)

                # Rotate 90 degrees counter-clockwise for proper spine orientation
                text_img_rotated = text_img.rotate(90, expand=True)

                # Paste onto spine canvas
                spine_canvas.paste(text_img_rotated, (0, 0), text_img_rotated)

            # Paste spine between back and front
            wrap.paste(spine_canvas, (back_width, 0))

            img_resized = wrap

        # For hardback, create dust jacket with flaps
        elif target_type == 'hardback':
            # Create white background for dust jacket
            jacket = Image.new('RGB', target_size, (255, 255, 255))

            # Calculate sections: front flap + back cover + spine + front cover + back flap
            flap_width = self.ALT_HARDBACK_FLAP_WIDTH
            spine_width = self.ALT_HARDBACK_SPINE_WIDTH
            cover_width = (target_size[0] - (2 * flap_width) - spine_width) // 2

            # Place front cover using FILL mode (no white space)
            img_ratio = img.width / img.height
            front_ratio = cover_width / target_size[1]

            if img_ratio > front_ratio:
                # Image wider - fit to height, crop width
                new_height = target_size[1]
                new_width = int(new_height * img_ratio)
            else:
                # Image taller - fit to width, crop height
                new_width = cover_width
                new_height = int(new_width / img_ratio)

            front_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Center crop to exact cover size
            front_x_offset = (new_width - cover_width) // 2
            front_y_offset = (new_height - target_size[1]) // 2
            front_cover = front_resized.crop((
                front_x_offset,
                front_y_offset,
                front_x_offset + cover_width,
                front_y_offset + target_size[1]
            ))

            front_x = flap_width + cover_width + spine_width
            jacket.paste(front_cover, (front_x, 0))

            # Place back cover using FILL mode (no white space)
            back_ratio = cover_width / target_size[1]

            if img_ratio > back_ratio:
                # Image wider - fit to height, crop width
                new_height = target_size[1]
                new_width = int(new_height * img_ratio)
            else:
                # Image taller - fit to width, crop height
                new_width = cover_width
                new_height = int(new_width / img_ratio)

            back_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Center crop to exact cover size
            back_x_offset = (new_width - cover_width) // 2
            back_y_offset = (new_height - target_size[1]) // 2
            back_cover = back_resized.crop((
                back_x_offset,
                back_y_offset,
                back_x_offset + cover_width,
                back_y_offset + target_size[1]
            ))

            back_x = flap_width
            jacket.paste(back_cover, (back_x, 0))

            # Extract dominant colors and use AI to select best spine color
            print(f"  Extracting dominant colors from cover...")
            dominant_colors = self.extract_dominant_colors(img, num_colors=5)
            print(f"  Found {len(dominant_colors)} dominant colors")

            # Use AI to select best spine color
            spine_color = self.get_ai_spine_color(dominant_colors, title=title)

            # Create spine background with AI-selected color
            spine_canvas = Image.new('RGB', (spine_width, target_size[1]), spine_color)

            # Add vertical spine text if title provided
            if title:
                from PIL import ImageDraw, ImageFont
                # Get contrasting text color
                brightness = sum(spine_color) / 3
                text_color = (255, 255, 255) if brightness < 128 else (0, 0, 0)

                # Get font for spine
                spine_font_size = min(spine_width - 20, 60)
                spine_font = self.get_font(spine_font_size, bold=True)

                # Create temp image for text rotation
                text_img = Image.new('RGBA', (target_size[1], spine_width), (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_img)

                # Center text
                bbox = text_draw.textbbox((0, 0), title, font=spine_font)
                text_width = bbox[2] - bbox[0]
                text_x = (target_size[1] - text_width) // 2

                # Draw and rotate text
                text_draw.text((text_x, 10), title, font=spine_font, fill=text_color)
                text_img_rotated = text_img.rotate(90, expand=True)
                spine_canvas.paste(text_img_rotated, (0, 0), text_img_rotated)

            # Paste spine between back and front
            spine_x = flap_width + cover_width
            jacket.paste(spine_canvas, (spine_x, 0))

            # Add text to flaps (optional - placeholder for now)
            draw = ImageDraw.Draw(jacket)
            # Left flap and right flap remain white or can have text

            img_resized = jacket

        # Add text overlays if requested
        if add_text and title:
            img_resized = self._add_text_overlays(
                img_resized, target_type, title, subtitle, author,
                title_color, spine_color, title_position, target_size
            )

        # Add barcode safe area for paperback/hardback
        if add_barcode_area and target_type in ['paperback', 'hardback']:
            img_resized = self._add_barcode_safe_area(img_resized, target_type, dpi)

        # Save converted cover with appropriate format
        # KDP Requirements: eBook = JPEG, Paperback/Hardback = PDF
        input_stem = Path(input_file).stem
        if target_type == 'ebook':
            output_filename = f"{target_type}_converted_{input_stem}.jpg"
            output_path = output_dir / output_filename
            print(f"[DEBUG] Converting to ebook: {output_path}")
            print(f"[DEBUG] Input stem: {input_stem}")
            print(f"[DEBUG] Output filename: {output_filename}")
            print(f"[DEBUG] Extension check: {output_path.suffix}")
            self.save_optimized_jpeg(img_resized, output_path, dpi=dpi, quality=95)
        else:  # paperback or hardback
            output_filename = f"{target_type}_converted_{input_stem}.pdf"
            output_path = output_dir / output_filename
            print(f"[DEBUG] Converting to {target_type}: {output_path}")
            print(f"[DEBUG] Input stem: {input_stem}")
            print(f"[DEBUG] Output filename: {output_filename}")
            print(f"[DEBUG] Extension check: {output_path.suffix}")
            cover_title = title if title else f"Converted {target_type.capitalize()} Cover"
            self.save_as_pdf(img_resized, output_path, dpi=dpi, title=cover_title)

        print(f"Original: {img.size} -> Converted: {img_resized.size}")
        print(f"Saved to: {output_path}")
        print(f"[DEBUG] File exists after save: {output_path.exists()}")
        if output_path.exists():
            print(f"[DEBUG] File size: {output_path.stat().st_size} bytes")

        return output_path

    def _add_text_overlays(self, img: Image.Image, cover_type: str,
                          title: str, subtitle: str, author: str,
                          title_color: str, spine_color: str,
                          title_position: str, target_size: Tuple[int, int]) -> Image.Image:
        """Add text overlays to cover image"""
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Convert colors
        text_rgb = self.hex_to_rgb(title_color)
        spine_rgb = self.hex_to_rgb(spine_color)

        # Font sizes based on cover type
        if cover_type == 'ebook':
            title_size = 120
            subtitle_size = 80
            author_size = 60
        elif cover_type == 'hardback':
            title_size = 140
            subtitle_size = 100
            author_size = 80
        else:  # paperback
            title_size = 130
            subtitle_size = 90
            author_size = 70

        # Get fonts
        title_font = self.get_font(title_size, bold=True)
        subtitle_font = self.get_font(subtitle_size, bold=False)
        author_font = self.get_font(author_size, bold=False)

        # For paperback/hardback, calculate front cover area
        if cover_type in ['paperback', 'hardback']:
            if cover_type == 'paperback':
                spine_width = self.PAPERBACK_SPINE_WIDTH
                back_width = (width - spine_width) // 2
                spine_x = back_width
                front_x = back_width + spine_width
                front_width = width - front_x
            else:  # hardback
                flap_width = self.ALT_HARDBACK_FLAP_WIDTH
                spine_width = self.ALT_HARDBACK_SPINE_WIDTH
                cover_width = (width - (2 * flap_width) - spine_width) // 2
                back_width = cover_width  # For consistency with paperback
                spine_x = flap_width + cover_width  # Start of spine section
                front_x = flap_width + cover_width + spine_width
                front_width = cover_width

            # Add colored band for title (horizontal at top/center/bottom)
            if title_position == 'top':
                band_y = int(height * 0.1)
                band_height = int(height * 0.15)
            elif title_position == 'center':
                band_y = int(height * 0.4)
                band_height = int(height * 0.2)
            else:  # bottom
                band_y = int(height * 0.75)
                band_height = int(height * 0.15)

            # Draw semi-transparent colored band
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [front_x, band_y, front_x + front_width, band_y + band_height],
                fill=(*spine_rgb, 200)  # Semi-transparent
            )
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(img)

            # Draw title on band
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = front_x + (front_width - title_width) // 2
            title_y = band_y + (band_height - (title_bbox[3] - title_bbox[1])) // 2
            draw.text((title_x, title_y), title, fill=text_rgb, font=title_font)

            # Draw subtitle if provided (below title band)
            if subtitle:
                subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = front_x + (front_width - subtitle_width) // 2
                subtitle_y = band_y + band_height + 30

                # Add semi-transparent background for subtitle
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle(
                    [subtitle_x - 20, subtitle_y - 10,
                     subtitle_x + subtitle_width + 20, subtitle_y + (subtitle_bbox[3] - subtitle_bbox[1]) + 10],
                    fill=(0, 0, 0, 150)
                )
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)

                draw.text((subtitle_x, subtitle_y), subtitle, fill=text_rgb, font=subtitle_font)

            # Add spine text (vertical)
            # KDP Requirement: Minimum 79 pages required for spine text
            # Source: https://kdp.amazon.com/en_US/help/topic/G201953020
            if author and cover_type in ['paperback', 'hardback']:
                if page_count >= self.MIN_SPINE_TEXT_PAGES:
                    spine_font = self.get_font(45, bold=True)
                    spine_text = f"{title[:30]}  •  {author}"

                    # Create vertical spine text
                    spine_img = Image.new('RGBA', (height, spine_width), (0, 0, 0, 0))
                    spine_draw = ImageDraw.Draw(spine_img)

                    # Add background to spine
                    spine_draw.rectangle([0, 0, height, spine_width], fill=(*spine_rgb, 255))

                    # Draw spine text (centered horizontally on the spine)
                    # KDP Requirement: 0.0625" (1.6mm) clearance from spine edges
                    clearance_px = int(self.SPINE_TEXT_CLEARANCE * dpi)
                    spine_text_bbox = spine_draw.textbbox((0, 0), spine_text, font=spine_font)
                    spine_text_width = spine_text_bbox[2] - spine_text_bbox[0]
                    spine_text_height = spine_text_bbox[3] - spine_text_bbox[1]

                    # Center the text on the spine with clearance
                    spine_text_x = (height - spine_text_width) // 2
                    # Ensure text has proper clearance from spine edges
                    spine_text_y = max(clearance_px, (spine_width - spine_text_height) // 2)
                    spine_text_y = min(spine_text_y, spine_width - spine_text_height - clearance_px)

                    spine_draw.text((spine_text_x, spine_text_y), spine_text, fill=text_rgb, font=spine_font)

                    # Rotate and paste spine
                    spine_img = spine_img.rotate(90, expand=True)
                    img.paste(spine_img, (spine_x, 0), spine_img)
                else:
                    # Warning: Book is too thin for spine text
                    print(f"Warning: Page count ({page_count}) is below KDP minimum ({self.MIN_SPINE_TEXT_PAGES}) for spine text. Skipping spine text.")
                    # Still add spine background without text
                    spine_img = Image.new('RGBA', (spine_width, height), (*spine_rgb, 255))
                    spine_img = spine_img.rotate(90, expand=True)
                    img.paste(spine_img, (spine_x, 0), spine_img)

        else:  # ebook - simpler layout
            # Add title
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            title_x = (width - title_width) // 2

            if title_position == 'top':
                title_y = int(height * 0.15)
            elif title_position == 'center':
                title_y = (height - title_height) // 2
            else:  # bottom
                title_y = int(height * 0.75)

            # Add background rectangle for text
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [title_x - 40, title_y - 30, title_x + title_width + 40, title_y + title_height + 30],
                fill=(*spine_rgb, 200)
            )
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(img)

            draw.text((title_x, title_y), title, fill=text_rgb, font=title_font)

            # Add subtitle if provided
            if subtitle:
                subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = (width - subtitle_width) // 2
                subtitle_y = title_y + title_height + 50
                draw.text((subtitle_x, subtitle_y), subtitle, fill=text_rgb, font=subtitle_font)

            # Add author
            if author:
                author_bbox = draw.textbbox((0, 0), author, font=author_font)
                author_width = author_bbox[2] - author_bbox[0]
                author_x = (width - author_width) // 2
                author_y = height - 200
                draw.text((author_x, author_y), author, fill=text_rgb, font=author_font)

        return img

    def _add_barcode_safe_area(self, img: Image.Image, cover_type: str, dpi: int = 300) -> Image.Image:
        """
        Add KDP barcode safe area to paperback/hardback back cover

        Amazon KDP requirements:
        - White box: 2.0" × 1.2" (600 × 360 pixels at 300 DPI)
        - Position: Lower-right of back cover
        - Paperback clearance: 0.25" from trim edges and spine
        - Hardcover clearance: 0.76" from bottom, 0.25" from spine hinge

        Args:
            img: Cover image
            cover_type: 'paperback' or 'hardback'
            dpi: Resolution (default 300)

        Returns:
            Image with barcode safe area
        """
        if cover_type not in ['paperback', 'hardback']:
            return img  # E-books don't need barcode area

        width, height = img.size
        draw = ImageDraw.Draw(img)

        # Calculate dimensions in pixels
        barcode_width = int(2.0 * dpi)   # 2.0 inches = 600 pixels at 300 DPI
        barcode_height = int(1.2 * dpi)  # 1.2 inches = 360 pixels at 300 DPI

        # KDP clearance requirements differ by cover type
        if cover_type == 'hardback':
            # Hardcover: 0.76" from bottom, 0.25" from spine (KDP requirement)
            clearance_bottom = int(0.76 * dpi)  # 0.76 inches = 228 pixels at 300 DPI
            clearance_side = int(0.25 * dpi)    # 0.25 inches = 75 pixels at 300 DPI
        else:  # paperback
            # Paperback: 0.25" from all edges (standard practice)
            clearance_bottom = int(0.25 * dpi)  # 0.25 inches = 75 pixels at 300 DPI
            clearance_side = int(0.25 * dpi)    # 0.25 inches = 75 pixels at 300 DPI

        # Determine back cover position
        if cover_type == 'paperback':
            spine_width = self.PAPERBACK_SPINE_WIDTH
            back_width = (width - spine_width) // 2
            back_start_x = 0
            back_end_x = back_width
        else:  # hardback
            flap_width = self.ALT_HARDBACK_FLAP_WIDTH
            spine_width = self.ALT_HARDBACK_SPINE_WIDTH
            cover_width = (width - (2 * flap_width) - spine_width) // 2
            back_start_x = flap_width
            back_end_x = flap_width + cover_width

        # Position barcode area on lower-right of back cover
        # Clear space from right edge and bottom edge (using type-specific clearances)
        barcode_x1 = back_end_x - barcode_width - clearance_side
        barcode_y1 = height - barcode_height - clearance_bottom
        barcode_x2 = back_end_x - clearance_side
        barcode_y2 = height - clearance_bottom

        # Draw white rectangle for barcode
        draw.rectangle([barcode_x1, barcode_y1, barcode_x2, barcode_y2], fill=(255, 255, 255))

        # Add thin border for visibility during design
        draw.rectangle([barcode_x1, barcode_y1, barcode_x2, barcode_y2], outline=(200, 200, 200), width=2)

        return img


if __name__ == '__main__':
    # Test the cover generator
    generator = CoverGenerator()

    # Test e-book cover creation
    cover_path = generator.create_cover(
        cover_type='ebook',
        title='Test Book',
        subtitle='A Great Subtitle',
        author='Author Name',
        style='gradient',
        colors={'primary': '#667eea', 'secondary': '#764ba2'},
        output_dir=Path('output/covers')
    )

    print(f"Test cover created: {cover_path}")
