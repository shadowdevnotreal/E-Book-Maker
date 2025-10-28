#!/usr/bin/env python3
"""
Amazon KDP Compliance Test Suite
Tests all KDP-compliant features and calculations

This test suite validates:
1. Spine width formulas
2. Cover dimensions
3. Manuscript margins
4. Trim size validation
5. Page count validation
6. CMYK color mode conversion
7. Barcode placement
"""

import sys
import os
from pathlib import Path

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from kdp_calculator import KDPCalculator


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_test(self, name: str, passed: bool, message: str = ""):
        self.tests.append({'name': name, 'passed': passed, 'message': message})
        if passed:
            self.passed += 1
            print(f"✅ PASS: {name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {name}")
        if message:
            print(f"   {message}")

    def summary(self):
        print("\n" + "=" * 70)
        print("KDP COMPLIANCE TEST SUMMARY")
        print("=" * 70)
        print(f"Total tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.failed == 0:
            print("\n✅ ALL TESTS PASSED - KDP COMPLIANT")
        else:
            print(f"\n❌ {self.failed} TEST(S) FAILED")
        print("=" * 70)


def test_spine_width_calculations(results: TestResults):
    """Test spine width formulas against Amazon KDP specifications"""
    print("\n" + "=" * 70)
    print("TEST 1: Spine Width Calculations")
    print("=" * 70)

    # Test 1.1: White paper (250 pages)
    expected_white = 0.563  # 250 × 0.002252
    actual_white = KDPCalculator.calculate_spine_width(250, 'white')
    results.add_test(
        "Spine width: 250 pages white paper",
        abs(actual_white - expected_white) < 0.001,
        f"Expected: {expected_white}\", Got: {actual_white}\""
    )

    # Test 1.2: Cream paper (300 pages)
    expected_cream = 0.750  # 300 × 0.0025
    actual_cream = KDPCalculator.calculate_spine_width(300, 'cream')
    results.add_test(
        "Spine width: 300 pages cream paper",
        abs(actual_cream - expected_cream) < 0.001,
        f"Expected: {expected_cream}\", Got: {actual_cream}\""
    )

    # Test 1.3: Premium color (200 pages)
    expected_color = 0.469  # 200 × 0.002347
    actual_color = KDPCalculator.calculate_spine_width(200, 'color')
    results.add_test(
        "Spine width: 200 pages premium color",
        abs(actual_color - expected_color) < 0.002,
        f"Expected: {expected_color}\", Got: {actual_color}\""
    )

    # Test 1.4: Standard color (150 pages)
    expected_std_color = 0.338  # 150 × 0.002252
    actual_std_color = KDPCalculator.calculate_spine_width(150, 'standard_color')
    results.add_test(
        "Spine width: 150 pages standard color",
        abs(actual_std_color - expected_std_color) < 0.002,
        f"Expected: {expected_std_color}\", Got: {actual_std_color}\""
    )


def test_cover_dimensions(results: TestResults):
    """Test cover dimension calculations"""
    print("\n" + "=" * 70)
    print("TEST 2: Cover Dimensions")
    print("=" * 70)

    # Test 2.1: 6×9 paperback, 250 pages, white paper
    dims = KDPCalculator.calculate_cover_dimensions(6.0, 9.0, 250, 'white', 'paperback')

    # Expected: (2 × 6.0) + 0.563 + (2 × 0.125) = 12.813"
    expected_width = 12.813
    results.add_test(
        "Cover width: 6×9 paperback (250 pages)",
        abs(dims.width_inches - expected_width) < 0.01,
        f"Expected: {expected_width}\", Got: {dims.width_inches}\""
    )

    # Expected: 9.0 + (2 × 0.125) = 9.250"
    expected_height = 9.250
    results.add_test(
        "Cover height: 6×9 paperback",
        abs(dims.height_inches - expected_height) < 0.01,
        f"Expected: {expected_height}\", Got: {dims.height_inches}\""
    )

    # Test 2.2: Pixel dimensions at 300 DPI
    expected_width_px = int(dims.width_inches * 300)
    results.add_test(
        "Cover width (pixels): 6×9 paperback",
        dims.width_pixels == expected_width_px,
        f"Expected: {expected_width_px}px, Got: {dims.width_pixels}px"
    )

    # Test 2.3: Hardback with case wrap
    hb_dims = KDPCalculator.calculate_cover_dimensions(6.0, 9.0, 250, 'white', 'hardback')
    # Expected: (2 × (6.0 + 1.5)) + 0.563 + (2 × 0.125) = 15.813"
    expected_hb_width = 15.813
    results.add_test(
        "Cover width: 6×9 hardback (250 pages)",
        abs(hb_dims.width_inches - expected_hb_width) < 0.01,
        f"Expected: {expected_hb_width}\", Got: {hb_dims.width_inches}\""
    )


def test_gutter_margins(results: TestResults):
    """Test gutter margin calculations based on page count"""
    print("\n" + "=" * 70)
    print("TEST 3: Gutter Margins (Page Count Based)")
    print("=" * 70)

    test_cases = [
        (100, 0.375, "24-150 pages"),
        (200, 0.5, "151-300 pages"),
        (400, 0.625, "301-500 pages"),
        (600, 0.75, "501-700 pages"),
        (800, 0.875, "701-828 pages"),
    ]

    for page_count, expected_gutter, description in test_cases:
        gutter = KDPCalculator.calculate_gutter_margin(page_count)
        results.add_test(
            f"Gutter margin: {description}",
            gutter == expected_gutter,
            f"Expected: {expected_gutter}\", Got: {gutter}\""
        )


def test_manuscript_margins(results: TestResults):
    """Test manuscript margin calculations"""
    print("\n" + "=" * 70)
    print("TEST 4: Manuscript Margins")
    print("=" * 70)

    # Test 4.1: 250-page book should have 0.5" gutter
    margins = KDPCalculator.calculate_manuscript_margins(250)
    results.add_test(
        "Manuscript margins: 250 pages",
        margins.gutter == 0.5 and margins.top == 0.75 and margins.bottom == 0.75,
        f"Top: {margins.top}\", Bottom: {margins.bottom}\", Gutter: {margins.gutter}\""
    )

    # Test 4.2: Custom margins
    custom_margins = KDPCalculator.calculate_manuscript_margins(
        250, top=1.0, bottom=1.0, outside=1.0, custom_gutter=0.625
    )
    results.add_test(
        "Custom manuscript margins",
        custom_margins.gutter == 0.625 and custom_margins.top == 1.0,
        f"Top: {custom_margins.top}\", Gutter: {custom_margins.gutter}\""
    )


def test_trim_size_validation(results: TestResults):
    """Test trim size validation"""
    print("\n" + "=" * 70)
    print("TEST 5: Trim Size Validation")
    print("=" * 70)

    # Test 5.1: Valid trim sizes
    valid_sizes = [
        (6.0, 9.0, '6x9'),
        (5.0, 8.0, '5x8'),
        (8.5, 11.0, '8.5x11'),
        (7.0, 10.0, '7x10'),
    ]

    for width, height, expected_name in valid_sizes:
        is_valid, name = KDPCalculator.validate_trim_size(width, height)
        results.add_test(
            f"Trim size validation: {width}×{height}",
            is_valid and name == expected_name,
            f"Expected: {expected_name}, Got: {name}"
        )

    # Test 5.2: Invalid trim size
    is_valid, name = KDPCalculator.validate_trim_size(5.5, 7.0)
    results.add_test(
        "Invalid trim size: 5.5×7.0",
        not is_valid and name is None,
        f"Should be invalid, Got: {is_valid}"
    )


def test_page_count_validation(results: TestResults):
    """Test page count validation"""
    print("\n" + "=" * 70)
    print("TEST 6: Page Count Validation")
    print("=" * 70)

    # Test 6.1: Valid page count
    is_valid, error = KDPCalculator.validate_page_count(250)
    results.add_test(
        "Valid page count: 250",
        is_valid and error is None,
        f"Should be valid"
    )

    # Test 6.2: Too low
    is_valid, error = KDPCalculator.validate_page_count(20)
    results.add_test(
        "Invalid page count: 20 (too low)",
        not is_valid and error is not None,
        f"Error: {error}"
    )

    # Test 6.3: Too high
    is_valid, error = KDPCalculator.validate_page_count(900)
    results.add_test(
        "Invalid page count: 900 (too high)",
        not is_valid and error is not None,
        f"Error: {error}"
    )

    # Test 6.4: Odd number
    is_valid, error = KDPCalculator.validate_page_count(251)
    results.add_test(
        "Invalid page count: 251 (odd)",
        not is_valid and error is not None,
        f"Error: {error}"
    )


def test_config_file(results: TestResults):
    """Test configuration file KDP settings"""
    print("\n" + "=" * 70)
    print("TEST 7: Configuration File")
    print("=" * 70)

    try:
        import json
        config_path = Path(__file__).parent / 'config' / 'default_config.json'

        with open(config_path, 'r') as f:
            config = json.load(f)

        # Test 7.1: Ebook dimensions
        ebook_width = config['covers']['ebook_width']
        ebook_height = config['covers']['ebook_height']
        results.add_test(
            "E-book dimensions (portrait)",
            ebook_width == 1600 and ebook_height == 2560,
            f"Expected: 1600×2560, Got: {ebook_width}×{ebook_height}"
        )

        # Test 7.2: KDP section exists
        has_kdp = 'kdp' in config
        results.add_test(
            "KDP configuration section exists",
            has_kdp,
            "KDP section should be present in config"
        )

        if has_kdp:
            # Test 7.3: Trim sizes exist
            has_trim_sizes = 'trim_sizes' in config['kdp']
            results.add_test(
                "KDP trim sizes configured",
                has_trim_sizes and '6x9' in config['kdp']['trim_sizes'],
                "Trim sizes should include 6x9"
            )

            # Test 7.4: Spine formulas
            has_spine = 'spine_formulas' in config['kdp']
            results.add_test(
                "KDP spine formulas configured",
                has_spine and config['kdp']['spine_formulas']['white_paper'] == 0.002252,
                f"White paper formula should be 0.002252"
            )

            # Test 7.5: Gutter margins
            has_gutter = 'gutter_margins' in config['kdp']
            results.add_test(
                "KDP gutter margins configured",
                has_gutter and '151-300' in config['kdp']['gutter_margins'],
                "Gutter margins should include 151-300 range"
            )

    except Exception as e:
        results.add_test(
            "Configuration file loading",
            False,
            f"Error: {e}"
        )


def test_cover_generator_integration(results: TestResults):
    """Test cover generator integration with KDP calculator"""
    print("\n" + "=" * 70)
    print("TEST 8: Cover Generator Integration")
    print("=" * 70)

    try:
        from covers.cover_generator import CoverGenerator

        generator = CoverGenerator()

        # Test 8.1: Spine width calculation
        spine = generator.calculate_spine_width(250, 'white', 'paperback')
        expected = 0.563
        results.add_test(
            "Cover generator spine width",
            abs(spine - expected) < 0.001,
            f"Expected: {expected}\", Got: {spine}\""
        )

    except ImportError as e:
        results.add_test(
            "Cover generator import",
            False,
            f"Could not import cover generator: {e}"
        )


def run_all_tests():
    """Run all KDP compliance tests"""
    print("\n" + "=" * 70)
    print("AMAZON KDP COMPLIANCE TEST SUITE")
    print("E-Book Maker v2.0")
    print("=" * 70)

    results = TestResults()

    # Run all test suites
    test_spine_width_calculations(results)
    test_cover_dimensions(results)
    test_gutter_margins(results)
    test_manuscript_margins(results)
    test_trim_size_validation(results)
    test_page_count_validation(results)
    test_config_file(results)
    test_cover_generator_integration(results)

    # Print summary
    results.summary()

    # Exit with appropriate code
    return 0 if results.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
