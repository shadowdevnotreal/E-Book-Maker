#!/usr/bin/env python3
"""
Amazon KDP Print File Setup Calculator
Python implementation of Amazon's official KDP Print File Setup Calculator
Based on: KDP_Print_File_Setup_Calculator_V5._CB1538598659_.xlsm

Official KDP Resources:
- Cover requirements: https://kdp.amazon.com/en_US/help/topic/G200735480
- Trim sizes: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6#trimsize
- Spine calculator: https://kdp.amazon.com/en_US/help/topic/G201834180

This module provides KDP-compliant calculations for:
- Spine width (by page count and paper type)
- Gutter margins (by page count)
- Cover dimensions (with bleed)
- Trim size validation
- Page count validation
"""

from typing import Dict, Tuple, Optional, Literal
from dataclasses import dataclass


# Amazon KDP Constants
# Source: https://kdp.amazon.com/en_US/help/topic/G201834180
SPINE_WIDTH_FORMULAS = {
    'white': 0.002252,      # Black & White - White paper: 0.002252" per page
    'cream': 0.0025,        # Black & White - Cream paper: 0.0025" per page
    'color': 0.002347,      # Premium Color: 0.002347" per page
    'standard_color': 0.002252,  # Standard Color: 0.002252" per page
}

# Standard bleed for all covers
BLEED_SIZE = 0.125  # inches (3.175mm)

# Page count limits (Amazon KDP requirements)
MIN_PAGE_COUNT = 24
MAX_PAGE_COUNT = 828

# DPI requirements
EBOOK_DPI = 72      # Minimum for ebooks (300 recommended)
PRINT_DPI = 300     # Required for print covers


# Amazon KDP Standard Trim Sizes
# Source: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6#trimsize
TRIM_SIZES = {
    # Black & White Interior
    '5x8': {'width': 5.0, 'height': 8.0, 'type': 'bw', 'max_pages': 828},
    '5.06x7.81': {'width': 5.06, 'height': 7.81, 'type': 'bw', 'max_pages': 828},
    '5.25x8': {'width': 5.25, 'height': 8.0, 'type': 'bw', 'max_pages': 828},
    '5.5x8.5': {'width': 5.5, 'height': 8.5, 'type': 'bw', 'max_pages': 828},
    '6x9': {'width': 6.0, 'height': 9.0, 'type': 'bw', 'max_pages': 828},
    '6.14x9.21': {'width': 6.14, 'height': 9.21, 'type': 'bw', 'max_pages': 828},
    '6.69x9.61': {'width': 6.69, 'height': 9.61, 'type': 'bw', 'max_pages': 828},
    '7x10': {'width': 7.0, 'height': 10.0, 'type': 'bw', 'max_pages': 828},
    '7.44x9.69': {'width': 7.44, 'height': 9.69, 'type': 'bw', 'max_pages': 828},
    '7.5x9.25': {'width': 7.5, 'height': 9.25, 'type': 'bw', 'max_pages': 828},
    '8x10': {'width': 8.0, 'height': 10.0, 'type': 'bw', 'max_pages': 828},
    '8.25x6': {'width': 8.25, 'height': 6.0, 'type': 'bw', 'max_pages': 828},
    '8.25x8.25': {'width': 8.25, 'height': 8.25, 'type': 'bw', 'max_pages': 828},
    '8.5x11': {'width': 8.5, 'height': 11.0, 'type': 'bw', 'max_pages': 828},

    # Color Interior (Premium Color has additional restrictions)
    '6x9_color': {'width': 6.0, 'height': 9.0, 'type': 'color', 'max_pages': 828},
    '7x10_color': {'width': 7.0, 'height': 10.0, 'type': 'color', 'max_pages': 828},
    '8x10_color': {'width': 8.0, 'height': 10.0, 'type': 'color', 'max_pages': 828},
    '8.5x11_color': {'width': 8.5, 'height': 11.0, 'type': 'color', 'max_pages': 828},
}


# Gutter Margins by Page Count
# Amazon KDP gutter margin recommendations for perfect binding
# Source: KDP Excel Calculator "Interior-Bleed" and "Interior-NoBleed" sheets
GUTTER_MARGINS = [
    (24, 150, 0.375),    # 24-150 pages: 0.375" gutter
    (151, 300, 0.5),     # 151-300 pages: 0.5" gutter
    (301, 500, 0.625),   # 301-500 pages: 0.625" gutter
    (501, 700, 0.75),    # 501-700 pages: 0.75" gutter
    (701, 828, 0.875),   # 701-828 pages: 0.875" gutter
]


@dataclass
class CoverDimensions:
    """KDP-compliant cover dimensions"""
    width_inches: float
    height_inches: float
    width_pixels: int
    height_pixels: int
    spine_width_inches: float
    spine_width_pixels: int
    bleed_inches: float = BLEED_SIZE
    dpi: int = PRINT_DPI

    def __str__(self) -> str:
        return (
            f"Cover: {self.width_inches:.3f}\" × {self.height_inches:.3f}\" "
            f"({self.width_pixels} × {self.height_pixels} px)\n"
            f"Spine: {self.spine_width_inches:.3f}\" ({self.spine_width_pixels} px)\n"
            f"DPI: {self.dpi}, Bleed: {self.bleed_inches}\""
        )


@dataclass
class ManuscriptMargins:
    """KDP-compliant manuscript margins"""
    top: float
    bottom: float
    outside: float
    gutter: float
    bleed: float = BLEED_SIZE

    def __str__(self) -> str:
        return (
            f"Top: {self.top}\", Bottom: {self.bottom}\", "
            f"Outside: {self.outside}\", Gutter: {self.gutter}\", "
            f"Bleed: {self.bleed}\""
        )


class KDPCalculator:
    """
    Amazon KDP Print File Setup Calculator

    Provides calculations for KDP-compliant book covers and manuscripts:
    - Spine width calculations
    - Cover dimensions with bleed
    - Manuscript margins
    - Trim size validation
    - Page count validation
    """

    @staticmethod
    def calculate_spine_width(
        page_count: int,
        paper_type: Literal['white', 'cream', 'color', 'standard_color'] = 'white'
    ) -> float:
        """
        Calculate spine width using Amazon KDP official formulas

        Source: https://kdp.amazon.com/en_US/help/topic/G201834180

        KDP Spine Width Formulas:
        - Black & White - White paper: page_count × 0.002252"
        - Black & White - Cream paper: page_count × 0.0025"
        - Premium Color: page_count × 0.002347"
        - Standard Color: page_count × 0.002252"

        Args:
            page_count: Number of pages in the book (must be 24-828)
            paper_type: Type of paper ('white', 'cream', 'color', 'standard_color')

        Returns:
            Spine width in inches

        Raises:
            ValueError: If page count is out of range or paper type is invalid

        Example:
            >>> KDPCalculator.calculate_spine_width(250, 'white')
            0.563
        """
        if not MIN_PAGE_COUNT <= page_count <= MAX_PAGE_COUNT:
            raise ValueError(
                f"Page count must be between {MIN_PAGE_COUNT} and {MAX_PAGE_COUNT}. "
                f"Got: {page_count}"
            )

        if paper_type not in SPINE_WIDTH_FORMULAS:
            raise ValueError(
                f"Invalid paper type: {paper_type}. "
                f"Must be one of: {list(SPINE_WIDTH_FORMULAS.keys())}"
            )

        thickness_per_page = SPINE_WIDTH_FORMULAS[paper_type]
        spine_width = page_count * thickness_per_page

        return round(spine_width, 3)

    @staticmethod
    def calculate_gutter_margin(page_count: int) -> float:
        """
        Calculate recommended gutter margin based on page count

        Amazon KDP gutter margins for perfect binding:
        - 24-150 pages: 0.375"
        - 151-300 pages: 0.5"
        - 301-500 pages: 0.625"
        - 501-700 pages: 0.75"
        - 701-828 pages: 0.875"

        Args:
            page_count: Number of pages in the book

        Returns:
            Recommended gutter margin in inches

        Raises:
            ValueError: If page count is out of range
        """
        if not MIN_PAGE_COUNT <= page_count <= MAX_PAGE_COUNT:
            raise ValueError(
                f"Page count must be between {MIN_PAGE_COUNT} and {MAX_PAGE_COUNT}. "
                f"Got: {page_count}"
            )

        for min_pages, max_pages, gutter in GUTTER_MARGINS:
            if min_pages <= page_count <= max_pages:
                return gutter

        # Fallback (should never reach here with valid page count)
        return 0.875

    @staticmethod
    def calculate_cover_dimensions(
        trim_width: float,
        trim_height: float,
        page_count: int,
        paper_type: Literal['white', 'cream', 'color', 'standard_color'] = 'white',
        cover_type: Literal['paperback', 'hardback'] = 'paperback',
        dpi: int = PRINT_DPI
    ) -> CoverDimensions:
        """
        Calculate full cover dimensions for paperback or hardback

        Amazon KDP cover formula:
        Cover width = (2 × trim width) + spine width + (2 × bleed)
        Cover height = trim height + (2 × bleed)

        For hardback:
        - Add case wrap: 3" × 1.5" (front and back)
        - Total width: (2 × (trim + 1.5")) + spine + (2 × bleed)

        Args:
            trim_width: Interior trim width in inches
            trim_height: Interior trim height in inches
            page_count: Number of pages in the book
            paper_type: Type of paper for spine calculation
            cover_type: 'paperback' or 'hardback'
            dpi: Dots per inch (default: 300)

        Returns:
            CoverDimensions object with full specifications

        Example:
            >>> dims = KDPCalculator.calculate_cover_dimensions(6.0, 9.0, 250, 'white')
            >>> print(f"{dims.width_inches:.3f}\" × {dims.height_inches:.3f}\"")
            12.813" × 9.250"
        """
        spine_width = KDPCalculator.calculate_spine_width(page_count, paper_type)

        if cover_type == 'hardback':
            # Hardback case wrap: 1.5" on each side
            wrap_width = 1.5
            cover_width = (2 * (trim_width + wrap_width)) + spine_width + (2 * BLEED_SIZE)
        else:  # paperback
            cover_width = (2 * trim_width) + spine_width + (2 * BLEED_SIZE)

        cover_height = trim_height + (2 * BLEED_SIZE)

        # Convert to pixels
        width_px = int(cover_width * dpi)
        height_px = int(cover_height * dpi)
        spine_px = int(spine_width * dpi)

        return CoverDimensions(
            width_inches=round(cover_width, 3),
            height_inches=round(cover_height, 3),
            width_pixels=width_px,
            height_pixels=height_px,
            spine_width_inches=round(spine_width, 3),
            spine_width_pixels=spine_px,
            bleed_inches=BLEED_SIZE,
            dpi=dpi
        )

    @staticmethod
    def calculate_manuscript_margins(
        page_count: int,
        top: float = 0.75,
        bottom: float = 0.75,
        outside: float = 0.75,
        custom_gutter: Optional[float] = None
    ) -> ManuscriptMargins:
        """
        Calculate KDP-compliant manuscript margins

        Default margins (Amazon KDP recommendations):
        - Top: 0.75"
        - Bottom: 0.75"
        - Outside: 0.75"
        - Gutter: Based on page count (auto-calculated)
        - Bleed: 0.125" (if using bleed)

        Args:
            page_count: Number of pages (determines gutter)
            top: Top margin in inches
            bottom: Bottom margin in inches
            outside: Outside margin in inches
            custom_gutter: Override auto-calculated gutter (optional)

        Returns:
            ManuscriptMargins object
        """
        gutter = custom_gutter if custom_gutter is not None else \
                 KDPCalculator.calculate_gutter_margin(page_count)

        return ManuscriptMargins(
            top=top,
            bottom=bottom,
            outside=outside,
            gutter=gutter,
            bleed=BLEED_SIZE
        )

    @staticmethod
    def validate_trim_size(width: float, height: float) -> Tuple[bool, Optional[str]]:
        """
        Validate if trim size is a standard KDP size

        Args:
            width: Trim width in inches
            height: Trim height in inches

        Returns:
            (is_valid, trim_size_name) tuple

        Example:
            >>> KDPCalculator.validate_trim_size(6.0, 9.0)
            (True, '6x9')
            >>> KDPCalculator.validate_trim_size(5.5, 7.0)
            (False, None)
        """
        for name, specs in TRIM_SIZES.items():
            if abs(specs['width'] - width) < 0.01 and abs(specs['height'] - height) < 0.01:
                return True, name

        return False, None

    @staticmethod
    def get_trim_size_info(trim_size_name: str) -> Optional[Dict]:
        """
        Get specifications for a standard trim size

        Args:
            trim_size_name: Standard trim size name (e.g., '6x9', '8.5x11')

        Returns:
            Dictionary with trim size specifications or None if not found

        Example:
            >>> info = KDPCalculator.get_trim_size_info('6x9')
            >>> print(f"{info['width']}\" × {info['height']}\"")
            6.0" × 9.0"
        """
        return TRIM_SIZES.get(trim_size_name)

    @staticmethod
    def list_trim_sizes(interior_type: Optional[Literal['bw', 'color']] = None) -> Dict[str, Dict]:
        """
        List all available KDP trim sizes

        Args:
            interior_type: Filter by 'bw' (black & white) or 'color' (optional)

        Returns:
            Dictionary of trim sizes
        """
        if interior_type is None:
            return TRIM_SIZES

        return {
            name: specs for name, specs in TRIM_SIZES.items()
            if specs['type'] == interior_type
        }

    @staticmethod
    def validate_page_count(page_count: int) -> Tuple[bool, Optional[str]]:
        """
        Validate if page count meets KDP requirements

        KDP Requirements:
        - Minimum: 24 pages
        - Maximum: 828 pages
        - Must be even number (books are printed in signatures)

        Args:
            page_count: Number of pages

        Returns:
            (is_valid, error_message) tuple
        """
        if page_count < MIN_PAGE_COUNT:
            return False, f"Page count too low. Minimum: {MIN_PAGE_COUNT} pages"

        if page_count > MAX_PAGE_COUNT:
            return False, f"Page count too high. Maximum: {MAX_PAGE_COUNT} pages"

        if page_count % 2 != 0:
            return False, "Page count must be even (books are printed in signatures)"

        return True, None


def demo():
    """Demonstration of KDP Calculator usage"""
    print("=" * 70)
    print("Amazon KDP Print File Setup Calculator - Python Implementation")
    print("=" * 70)
    print()

    # Example 1: Calculate spine width
    page_count = 250
    paper_type = 'white'
    spine = KDPCalculator.calculate_spine_width(page_count, paper_type)
    print(f"Example 1: Spine Width Calculation")
    print(f"  Page count: {page_count}")
    print(f"  Paper type: {paper_type}")
    print(f"  Spine width: {spine}\" ({int(spine * 300)} pixels at 300 DPI)")
    print()

    # Example 2: Calculate cover dimensions for 6x9 paperback
    trim_width = 6.0
    trim_height = 9.0
    dims = KDPCalculator.calculate_cover_dimensions(
        trim_width, trim_height, page_count, paper_type
    )
    print(f"Example 2: Cover Dimensions (6×9 Paperback, {page_count} pages)")
    print(f"  {dims}")
    print()

    # Example 3: Calculate manuscript margins
    margins = KDPCalculator.calculate_manuscript_margins(page_count)
    print(f"Example 3: Manuscript Margins ({page_count} pages)")
    print(f"  {margins}")
    print()

    # Example 4: Validate trim sizes
    print("Example 4: Trim Size Validation")
    valid, name = KDPCalculator.validate_trim_size(6.0, 9.0)
    print(f"  6.0\" × 9.0\": {valid} (Standard size: {name})")
    valid, name = KDPCalculator.validate_trim_size(5.5, 7.0)
    print(f"  5.5\" × 7.0\": {valid} (Not a standard KDP size)")
    print()

    # Example 5: List all trim sizes
    print("Example 5: Standard KDP Trim Sizes (Black & White)")
    bw_sizes = KDPCalculator.list_trim_sizes('bw')
    for name, specs in list(bw_sizes.items())[:5]:  # Show first 5
        print(f"  {name}: {specs['width']}\" × {specs['height']}\" (max {specs['max_pages']} pages)")
    print(f"  ... and {len(bw_sizes) - 5} more")
    print()


if __name__ == '__main__':
    demo()
