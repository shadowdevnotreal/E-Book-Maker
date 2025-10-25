"""
Book Cover Generator Module
Creates and converts book covers for e-books and paperbacks
Consolidated from AMAZON_KDP_PACKAGE cover tools
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Dict, Optional, Tuple


class CoverGenerator:
    """Generate and convert book covers"""

    # E-book cover specifications (Amazon KDP compliant)
    # KDP recommends: 1600 × 2560 pixels (portrait, aspect ratio 1.6:1)
    EBOOK_WIDTH = 1600  # CORRECTED: Was 2560 (landscape), now portrait
    EBOOK_HEIGHT = 2560  # CORRECTED: Was 1600 (landscape), now portrait
    EBOOK_DPI = 300

    # Paperback specifications (6" x 9" book, ~100 pages)
    PAPERBACK_WIDTH = 5499
    PAPERBACK_HEIGHT = 3375
    PAPERBACK_SPINE_WIDTH = 399
    PAPERBACK_DPI = 300

    # Alternative paperback size
    ALT_PAPERBACK_WIDTH = 3666
    ALT_PAPERBACK_HEIGHT = 2700
    ALT_PAPERBACK_SPINE_WIDTH = 66

    # Hardback/Hardcover specifications (6.5" x 9.5" book with dust jacket)
    # Hardbacks are typically 0.25-0.5" larger than paperback trim
    # For an 8.5x11 paperback content, hardback would be ~9x11.5
    HARDBACK_WIDTH = 6900   # Total width including flaps (23" at 300 DPI)
    HARDBACK_HEIGHT = 3450  # 11.5" at 300 DPI (0.5" taller than paperback)
    HARDBACK_SPINE_WIDTH = 450  # Slightly thicker spine for hard covers
    HARDBACK_FLAP_WIDTH = 1050  # 3.5" flaps on each side (300 DPI)
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

    def calculate_spine_width(self, page_count: int, paper_type: str = 'white',
                            binding_type: str = 'paperback') -> float:
        """
        Calculate spine width based on Amazon KDP specifications

        Args:
            page_count: Number of pages in the book
            paper_type: 'white', 'cream', or 'color'
            binding_type: 'paperback' or 'hardcover'

        Returns:
            Spine width in inches
        """
        # KDP spine width calculations (inches per page)
        # Source: https://kdp.amazon.com/en_US/help/topic/G201834180
        paper_thickness = {
            'white': 0.0025,      # White paper: 0.0025" per page
            'cream': 0.0027,      # Cream paper: 0.0027" per page
            'color': 0.0025,      # Color paper: 0.0025" per page
        }

        thickness_per_page = paper_thickness.get(paper_type.lower(), 0.0025)
        spine_width = page_count * thickness_per_page

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

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def create_cover(self, cover_type: str, title: str, subtitle: str,
                    author: str, style: str, colors: Dict[str, str],
                    output_dir: Path) -> Path:
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

        Returns:
            Path to created cover
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Determine dimensions
        if cover_type == 'ebook':
            width, height = self.EBOOK_WIDTH, self.EBOOK_HEIGHT
            dpi = self.EBOOK_DPI
            title_size = 140
            subtitle_size = 100
            author_size = 70
        elif cover_type == 'hardback':
            width, height = self.ALT_HARDBACK_WIDTH, self.ALT_HARDBACK_HEIGHT
            dpi = self.HARDBACK_DPI
            title_size = 200
            subtitle_size = 130
            author_size = 95
        else:  # paperback
            width, height = self.ALT_PAPERBACK_WIDTH, self.ALT_PAPERBACK_HEIGHT
            dpi = self.PAPERBACK_DPI
            title_size = 180
            subtitle_size = 120
            author_size = 90

        # Create background
        primary_rgb = self.hex_to_rgb(colors.get('primary', '#667eea'))
        secondary_rgb = self.hex_to_rgb(colors.get('secondary', '#764ba2'))

        if style == 'gradient':
            img = self.create_gradient(width, height, primary_rgb, secondary_rgb)
        elif style == 'solid':
            img = Image.new('RGB', (width, height), primary_rgb)
        else:  # minimalist
            img = Image.new('RGB', (width, height), (255, 255, 255))

        draw = ImageDraw.Draw(img)

        # Load fonts
        title_font = self.get_font(title_size, bold=True)
        subtitle_font = self.get_font(subtitle_size, bold=True)
        author_font = self.get_font(author_size, bold=False)

        # Text color
        text_color = (255, 255, 255) if style in ['gradient', 'solid'] else (0, 0, 0)

        # Draw title (centered)
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 3

        draw.text((title_x, title_y), title, fill=text_color, font=title_font)

        # Draw subtitle if provided
        if subtitle:
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (width - subtitle_width) // 2
            subtitle_y = title_y + 200

            draw.text((subtitle_x, subtitle_y), subtitle, fill=text_color, font=subtitle_font)

        # Draw author (bottom)
        author_bbox = draw.textbbox((0, 0), author, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (width - author_width) // 2
        author_y = height - 300

        draw.text((author_x, author_y), author, fill=text_color, font=author_font)

        # Add decorative element for e-book
        if cover_type == 'ebook' and style != 'minimalist':
            line_y = title_y - 50
            line_width = 600
            line_x = (width - line_width) // 2
            draw.rectangle([line_x, line_y, line_x + line_width, line_y + 5], fill=text_color)

        # Save cover
        output_filename = f"{cover_type}_cover_{title.lower().replace(' ', '_')}.jpg"
        output_path = output_dir / output_filename

        img.save(str(output_path), 'JPEG', quality=95, dpi=(dpi, dpi))

        return output_path

    def convert_cover(self, input_file: Path, target_type: str,
                     output_dir: Path) -> Path:
        """
        Convert cover image to target format

        Args:
            input_file: Path to input cover image
            target_type: 'ebook', 'paperback', or 'hardback'
            output_dir: Output directory

        Returns:
            Path to converted cover
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load image
        img = Image.open(input_file)

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
            target_size = (self.ALT_HARDBACK_WIDTH, self.ALT_HARDBACK_HEIGHT)
            dpi = self.HARDBACK_DPI
        else:  # paperback
            target_size = (self.PAPERBACK_WIDTH, self.PAPERBACK_HEIGHT)
            dpi = self.PAPERBACK_DPI

        # Resize image
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

        # For paperback, create wrap layout
        if target_type == 'paperback':
            # Create white background for full wrap
            wrap = Image.new('RGB', target_size, (255, 255, 255))

            # Calculate sections
            back_width = (target_size[0] - self.PAPERBACK_SPINE_WIDTH) // 2
            front_width = back_width
            spine_width = self.PAPERBACK_SPINE_WIDTH

            # Place front cover (resize source image)
            front_cover = img.resize((front_width, target_size[1]), Image.Resampling.LANCZOS)
            front_x = back_width + spine_width
            wrap.paste(front_cover, (front_x, 0))

            # Place back cover (resize source image)
            back_cover = img.resize((back_width, target_size[1]), Image.Resampling.LANCZOS)
            wrap.paste(back_cover, (0, 0))

            img_resized = wrap

        # For hardback, create dust jacket with flaps
        elif target_type == 'hardback':
            # Create white background for dust jacket
            jacket = Image.new('RGB', target_size, (255, 255, 255))

            # Calculate sections: front flap + back cover + spine + front cover + back flap
            flap_width = self.ALT_HARDBACK_FLAP_WIDTH
            spine_width = self.ALT_HARDBACK_SPINE_WIDTH
            cover_width = (target_size[0] - (2 * flap_width) - spine_width) // 2

            # Place front cover (center-right)
            front_cover = img.resize((cover_width, target_size[1]), Image.Resampling.LANCZOS)
            front_x = flap_width + cover_width + spine_width
            jacket.paste(front_cover, (front_x, 0))

            # Place back cover (center-left)
            back_cover = img.resize((cover_width, target_size[1]), Image.Resampling.LANCZOS)
            back_x = flap_width
            jacket.paste(back_cover, (back_x, 0))

            # Add text to flaps (optional - placeholder for now)
            draw = ImageDraw.Draw(jacket)
            # Left flap and right flap remain white or can have text

            img_resized = jacket

        # Save converted cover
        input_stem = Path(input_file).stem
        output_filename = f"{target_type}_converted_{input_stem}.jpg"
        output_path = output_dir / output_filename

        img_resized.save(str(output_path), 'JPEG', quality=95, dpi=(dpi, dpi))

        print(f"Original: {img.size} -> Converted: {img_resized.size}")
        print(f"Saved to: {output_path}")

        return output_path


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
