#!/usr/bin/env python3
"""
Universal Watermark Generator System
Add watermarks to documents using ANY logo files you provide
Place your logo files in the './logos' directory and this tool will detect and use them
"""

import os
import sys
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
import argparse
import json
from datetime import datetime

# Get the directory where this script is located
_SCRIPT_DIR = Path(__file__).parent
_DEFAULT_LOGO_DIR = _SCRIPT_DIR / "logos"

# Supported image formats
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}


class UniversalWatermarkSystem:
    """Universal watermarking system - works with ANY logo files"""

    def __init__(self, custom_logo_dir: Optional[str] = None):
        """Initialize watermark system

        Args:
            custom_logo_dir: Optional custom directory for logos
        """
        # Set logo directory
        if custom_logo_dir:
            self.logo_dir = Path(custom_logo_dir)
        else:
            self.logo_dir = _DEFAULT_LOGO_DIR

        # Watermark configuration
        self.watermark_config = {
            'opacity': 0.05,  # 5% opacity for subtle background watermark
            'position': 'center',
            'size': 'auto',
            'repeat': False
        }

        # Copyright information
        self.copyright = f"© {datetime.now().year} Watermarked Document. All Rights Reserved."

        # Auto-detect available logos
        self.available_logos = self.scan_logos()
        self.current_logo = self.available_logos[0] if self.available_logos else None

    def ensure_logo_directory(self) -> bool:
        """Create logos directory if it doesn't exist"""
        try:
            self.logo_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating logo directory: {e}")
            return False

    def scan_logos(self) -> List[Path]:
        """Scan logos directory and return list of all image files

        Returns:
            List of Path objects for all found image files
        """
        if not self.logo_dir.exists():
            return []

        logos = []
        for file_path in self.logo_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
                logos.append(file_path)

        # Sort alphabetically for consistent ordering
        return sorted(logos)

    def list_available_logos(self) -> None:
        """Display available logos in a user-friendly format"""
        print(f"\n{'='*70}")
        print("📷 Logo Detection Report")
        print(f"{'='*70}")
        print(f"Logo Directory: {self.logo_dir}")
        print(f"Directory Exists: {'Yes ✓' if self.logo_dir.exists() else 'No ✗'}")

        if not self.available_logos:
            print(f"\n⚠️  No logo files found!")
            print(f"\nSupported formats: {', '.join(SUPPORTED_FORMATS)}")
            print(f"\nPlace any image file in: {self.logo_dir}")
            print(f"{'='*70}\n")
            return

        print(f"\n{'#':<5} {'Filename':<40} {'Size':<15} {'Active':<10}")
        print(f"{'-'*70}")

        for idx, logo_path in enumerate(self.available_logos, 1):
            size_kb = logo_path.stat().st_size / 1024
            active = "◄ ACTIVE" if logo_path == self.current_logo else ""
            print(f"{idx:<5} {logo_path.name:<40} {size_kb:>8.1f} KB    {active:<10}")

        print(f"\n{'='*70}")
        print(f"Total: {len(self.available_logos)} logo(s) found")
        print(f"Current logo: {self.current_logo.name if self.current_logo else 'None'}")
        print(f"{'='*70}\n")

    def select_logo(self, index: int = None, filename: str = None) -> bool:
        """Select a logo to use for watermarking

        Args:
            index: Logo number (1-based index from list)
            filename: Logo filename

        Returns:
            True if logo selected successfully
        """
        if not self.available_logos:
            print("No logos available to select")
            return False

        if index is not None:
            if 1 <= index <= len(self.available_logos):
                self.current_logo = self.available_logos[index - 1]
                print(f"✓ Selected logo: {self.current_logo.name}")
                return True
            else:
                print(f"✗ Invalid index. Choose 1-{len(self.available_logos)}")
                return False

        if filename is not None:
            for logo in self.available_logos:
                if logo.name == filename:
                    self.current_logo = logo
                    print(f"✓ Selected logo: {self.current_logo.name}")
                    return True
            print(f"✗ Logo '{filename}' not found")
            return False

        return False

    def get_logo_base64(self, logo_path: Optional[Path] = None) -> str:
        """Convert logo to base64 for embedding in HTML/CSS

        Args:
            logo_path: Specific logo to encode (uses current_logo if None)

        Returns:
            Base64 encoded string of the logo image
        """
        logo = logo_path or self.current_logo

        if not logo or not logo.exists():
            print(f"Warning: Logo not found at {logo}")
            return ""

        try:
            with open(logo, 'rb') as f:
                logo_data = f.read()

            # Detect image type from extension
            ext = logo.suffix.lower()[1:]  # Remove the dot
            if ext == 'jpg':
                ext = 'jpeg'

            encoded = base64.b64encode(logo_data).decode('utf-8')
            return f"data:image/{ext};base64,{encoded}"

        except Exception as e:
            print(f"Error loading logo: {e}")
            return ""

    def generate_html_watermark_css(self, explain: bool = False) -> str:
        """Generate CSS for HTML watermarking

        Args:
            explain: If True, include detailed comments explaining what CSS does

        Returns:
            CSS code as string
        """
        logo_base64 = self.get_logo_base64()
        if not logo_base64:
            return "/* No logo available for watermark */"

        if explain:
            return f"""
/* ═══════════════════════════════════════════════════════════════
   UNIVERSAL WATERMARK CSS - HOW IT WORKS
   ═══════════════════════════════════════════════════════════════ */

/* 1. WATERMARK ELEMENT (.watermark class)
   ─────────────────────────────────────────────────────────────── */

.watermark {{
    /* POSITIONING: Fixed means it stays in same spot even when scrolling */
    position: fixed;

    /* CENTER THE WATERMARK: These three properties work together */
    top: 50%;              /* Move down 50% from top */
    left: 50%;             /* Move right 50% from left */
    transform: translate(-50%, -50%);  /* Shift back by half its own size = perfect center */

    /* SIZE: How big the watermark appears */
    width: 400px;
    height: 400px;

    /* THE LOGO IMAGE: Embedded as base64 data */
    background-image: url('{logo_base64[:50]}...');  /* Your logo (truncated in display) */
    background-repeat: no-repeat;     /* Don't tile/repeat the image */
    background-position: center;      /* Center image within the element */
    background-size: contain;         /* Scale to fit, keeping aspect ratio */

    /* TRANSPARENCY: Makes it subtle and non-intrusive */
    opacity: {self.watermark_config['opacity']};  /* {int(self.watermark_config['opacity']*100)}% visible */

    /* LAYERING: Controls what appears on top of what */
    z-index: -1;           /* Behind content (-1 = behind normal elements) */

    /* INTERACTION: Watermark won't block clicks/selections */
    pointer-events: none;  /* Click/touch events pass through watermark */
}}

/* 2. PRINT SUPPORT (for PDFs and printing)
   ─────────────────────────────────────────────────────────────── */

@media print {{
    .watermark {{
        position: fixed !important;              /* Stay fixed when printing */
        print-color-adjust: exact;               /* Force exact colors when printing */
        -webkit-print-color-adjust: exact;       /* Safari/Chrome version */
    }}
}}

/* 3. COPYRIGHT TEXT (.copyright class)
   ─────────────────────────────────────────────────────────────── */

.copyright {{
    /* POSITIONING: Bottom-right corner */
    position: fixed;
    bottom: 10px;          /* 10px from bottom */
    right: 10px;           /* 10px from right */

    /* STYLING: Small, subtle text */
    font-size: 8pt;        /* Small text size */
    color: #999;           /* Light gray color */
    opacity: 0.7;          /* 70% visible */

    /* LAYERING: Appears on top */
    z-index: 1000;         /* High number = on top of most elements */
}}

/* ═══════════════════════════════════════════════════════════════
   HOW TO USE THIS CSS
   ═══════════════════════════════════════════════════════════════

   In your HTML, add these two elements:

   <div class="watermark"></div>
   <div class="copyright">{self.copyright}</div>

   The watermark will appear centered, subtle, and non-intrusive!
   ═══════════════════════════════════════════════════════════════ */
"""
        else:
            return f"""
/* Universal Watermark CSS */
.watermark {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 400px;
    height: 400px;
    background-image: url('{logo_base64}');
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
    opacity: {self.watermark_config['opacity']};
    z-index: -1;
    pointer-events: none;
}}

@media print {{
    .watermark {{
        position: fixed !important;
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }}
}}

.copyright {{
    position: fixed;
    bottom: 10px;
    right: 10px;
    font-size: 8pt;
    color: #999;
    opacity: 0.7;
    z-index: 1000;
}}
"""

    def generate_cover_page_html(self, title: str, subtitle: str = "") -> str:
        """Generate HTML cover page with logo"""
        logo_base64 = self.get_logo_base64()

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        .cover-page {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            position: relative;
        }}

        .logo-container {{
            width: 300px;
            height: 300px;
            margin-bottom: 3em;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .logo-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            filter: drop-shadow(0 10px 30px rgba(0,0,0,0.4));
        }}

        .cover-title {{
            font-size: 48pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5em;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            max-width: 80%;
        }}

        .cover-subtitle {{
            font-size: 24pt;
            text-align: center;
            margin-bottom: 2em;
            opacity: 0.9;
            max-width: 70%;
        }}

        .copyright-footer {{
            position: absolute;
            bottom: 30px;
            font-size: 11pt;
            opacity: 0.8;
        }}

        @media print {{
            .cover-page {{
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="logo-container">
            <img src="{logo_base64}" alt="Logo">
        </div>
        <div class="cover-title">{title}</div>
        {f'<div class="cover-subtitle">{subtitle}</div>' if subtitle else ''}
        <div class="copyright-footer">{self.copyright}</div>
    </div>
</body>
</html>"""

    def apply_watermark_to_pdf(self, input_pdf: str, output_pdf: str) -> bool:
        """Apply watermark to existing PDF (requires PyPDF2)"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            import io

            if not self.current_logo:
                print("✗ No logo available for watermarking")
                return False

            # Create watermark PDF in memory
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)

            # Add logo watermark
            if self.current_logo.exists():
                c.saveState()
                c.setFillAlpha(self.watermark_config['opacity'])
                c.drawImage(str(self.current_logo), 200, 300, width=200, height=200, mask='auto')
                c.restoreState()

            # Add copyright text
            c.setFont("Helvetica", 8)
            c.setFillAlpha(0.5)
            c.drawRightString(letter[0] - 20, 20, self.copyright)
            c.save()

            # Apply watermark to each page
            packet.seek(0)
            watermark = PdfReader(packet)
            watermark_page = watermark.pages[0]

            pdf_reader = PdfReader(input_pdf)
            pdf_writer = PdfWriter()

            for page in pdf_reader.pages:
                page.merge_page(watermark_page)
                pdf_writer.add_page(page)

            with open(output_pdf, 'wb') as f:
                pdf_writer.write(f)

            return True

        except ImportError:
            print("✗ PyPDF2 and reportlab required for PDF watermarking")
            print("Install with: pip install PyPDF2 reportlab")
            return False
        except Exception as e:
            print(f"✗ Error watermarking PDF: {e}")
            return False

    def generate_watermark_config(self) -> Dict[str, Any]:
        """Generate watermark configuration for web interface"""
        return {
            'enabled': True,
            'logo_file': self.current_logo.name if self.current_logo else None,
            'logo_base64': self.get_logo_base64(),
            'opacity': self.watermark_config['opacity'],
            'position': self.watermark_config['position'],
            'copyright': self.copyright,
            'available_logos': [logo.name for logo in self.available_logos],
            'css': self.generate_html_watermark_css()
        }

    def save_watermark_metadata(self, file_path: str):
        """Save watermark metadata for tracking"""
        metadata = {
            'file': file_path,
            'watermarked': True,
            'timestamp': datetime.now().isoformat(),
            'copyright': self.copyright,
            'logo_used': self.current_logo.name if self.current_logo else None,
            'opacity': self.watermark_config['opacity']
        }

        metadata_file = Path(file_path).with_suffix('.watermark.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata_file


def interactive_menu():
    """Interactive menu for watermark system"""
    print("\n" + "="*70)
    print("🎨 Universal Watermark Generator - Interactive Mode")
    print("="*70)

    # Get custom logo directory if needed
    custom_logo_dir = input("\n📁 Logo directory (press Enter for default './logos'): ").strip()
    watermark = UniversalWatermarkSystem(custom_logo_dir if custom_logo_dir else None)

    # Ensure logo directory exists
    if watermark.ensure_logo_directory():
        print(f"✓ Logo directory ready: {watermark.logo_dir}")

    # Rescan logos
    watermark.available_logos = watermark.scan_logos()
    watermark.current_logo = watermark.available_logos[0] if watermark.available_logos else None

    while True:
        print("\n" + "="*70)
        print("Main Menu")
        print("="*70)
        print("1. 📋 List available logos")
        print("2. 🎯 Select logo to use")
        print("3. 📄 Generate watermark CSS for HTML")
        print("4. 📖 Generate watermark CSS with explanation")
        print("5. 🖼️  Generate cover page HTML")
        print("6. 📊 Apply watermark to PDF")
        print("7. 🔧 Generate configuration JSON")
        print("8. ℹ️  Show system information")
        print("9. 🔄 Refresh/rescan logos")
        print("0. 🚪 Exit")
        print("="*70)

        choice = input("\n👉 Select option (0-9): ").strip()

        if choice == '1':
            watermark.list_available_logos()
            input("\nPress Enter to continue...")

        elif choice == '2':
            watermark.list_available_logos()
            if watermark.available_logos:
                try:
                    idx = int(input(f"\nEnter logo number (1-{len(watermark.available_logos)}): "))
                    watermark.select_logo(index=idx)
                except ValueError:
                    print("✗ Invalid number")
            input("\nPress Enter to continue...")

        elif choice == '3':
            css = watermark.generate_html_watermark_css()
            output = input("\n💾 Save to file? (Enter filename or press Enter to display): ").strip()
            if output:
                try:
                    with open(output, 'w') as f:
                        f.write(css)
                    print(f"✓ CSS saved to: {output}")
                except Exception as e:
                    print(f"✗ Error: {e}")
            else:
                print("\n" + "="*70)
                print(css)
                print("="*70)
            input("\nPress Enter to continue...")

        elif choice == '4':
            css = watermark.generate_html_watermark_css(explain=True)
            output = input("\n💾 Save to file? (Enter filename or press Enter to display): ").strip()
            if output:
                try:
                    with open(output, 'w') as f:
                        f.write(css)
                    print(f"✓ Explained CSS saved to: {output}")
                except Exception as e:
                    print(f"✗ Error: {e}")
            else:
                print("\n" + "="*70)
                print(css)
                print("="*70)
            input("\nPress Enter to continue...")

        elif choice == '5':
            title = input("\n📝 Document title: ").strip() or "Professional Document"
            subtitle = input("📝 Document subtitle (optional): ").strip()
            html = watermark.generate_cover_page_html(title, subtitle)
            output = input("\n💾 Save to file? (Enter filename or press Enter to skip): ").strip()
            if output:
                try:
                    with open(output, 'w') as f:
                        f.write(html)
                    print(f"✓ Cover page saved to: {output}")
                except Exception as e:
                    print(f"✗ Error: {e}")
            else:
                print("✓ HTML generated (not saved)")
            input("\nPress Enter to continue...")

        elif choice == '6':
            input_pdf = input("\n📂 Input PDF path: ").strip()
            output_pdf = input("📂 Output PDF path: ").strip()
            if input_pdf and output_pdf:
                if watermark.apply_watermark_to_pdf(input_pdf, output_pdf):
                    print(f"✓ Watermarked PDF saved to: {output_pdf}")
                    watermark.save_watermark_metadata(output_pdf)
                else:
                    print("✗ Failed to watermark PDF")
            else:
                print("✗ Both paths required")
            input("\nPress Enter to continue...")

        elif choice == '7':
            config = watermark.generate_watermark_config()
            output = input("\n💾 Save to file? (Enter filename or press Enter to display): ").strip()
            if output:
                try:
                    with open(output, 'w') as f:
                        json.dump(config, f, indent=2)
                    print(f"✓ Config saved to: {output}")
                except Exception as e:
                    print(f"✗ Error: {e}")
            else:
                print("\n" + "="*70)
                print(json.dumps(config, indent=2))
                print("="*70)
            input("\nPress Enter to continue...")

        elif choice == '8':
            print("\n" + "="*70)
            print("System Information")
            print("="*70)
            print(f"Script Directory: {_SCRIPT_DIR}")
            print(f"Logo Directory: {watermark.logo_dir}")
            print(f"Copyright Text: {watermark.copyright}")
            print(f"Watermark Opacity: {int(watermark.watermark_config['opacity']*100)}%")
            print(f"Available Logos: {len(watermark.available_logos)}")
            if watermark.current_logo:
                print(f"Current Logo: {watermark.current_logo.name}")
            print(f"\nSupported Formats: {', '.join(SUPPORTED_FORMATS)}")
            print("="*70)
            input("\nPress Enter to continue...")

        elif choice == '9':
            watermark.available_logos = watermark.scan_logos()
            watermark.current_logo = watermark.available_logos[0] if watermark.available_logos else None
            print(f"\n✓ Rescanned logos - found {len(watermark.available_logos)} logo(s)")
            input("\nPress Enter to continue...")

        elif choice == '0':
            print("\n👋 Thank you for using Universal Watermark Generator!")
            break

        else:
            print("\n✗ Invalid option. Please select 0-9.")
            input("\nPress Enter to continue...")


def main():
    """CLI interface for watermark system"""
    parser = argparse.ArgumentParser(
        description='Universal Watermark Generator - Works with ANY logo files',
        epilog='Run without arguments for interactive mode'
    )
    parser.add_argument('action', nargs='?',
                        choices=['test', 'list', 'pdf', 'html', 'cover', 'config', 'interactive'],
                        help='Action to perform')
    parser.add_argument('--input', help='Input file path')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--subtitle', help='Document subtitle')
    parser.add_argument('--logo-dir', help='Custom logo directory path')
    parser.add_argument('--logo', help='Specific logo filename to use')
    parser.add_argument('--explain', action='store_true', help='Add explanations to CSS output')

    args = parser.parse_args()

    # If no action specified, launch interactive mode
    if args.action is None or args.action == 'interactive':
        interactive_menu()
        return

    # Create watermark system
    watermark = UniversalWatermarkSystem(custom_logo_dir=args.logo_dir)

    # Select specific logo if requested
    if args.logo:
        watermark.select_logo(filename=args.logo)

    if args.action == 'test' or args.action == 'list':
        print("\n" + "="*70)
        print("Universal Watermark Generator - System Test")
        print("="*70)
        print(f"Script Directory: {_SCRIPT_DIR}")
        watermark.list_available_logos()

    elif args.action == 'pdf':
        if not args.input or not args.output:
            print("✗ Both --input and --output required for PDF watermarking")
            return
        print("\n🔄 Applying watermark to PDF...")
        if watermark.apply_watermark_to_pdf(args.input, args.output):
            print(f"✓ Watermarked PDF saved to: {args.output}")
            watermark.save_watermark_metadata(args.output)
        else:
            print("✗ Failed to watermark PDF")

    elif args.action == 'html':
        print("\n🔄 Generating HTML watermark CSS...")
        css = watermark.generate_html_watermark_css(explain=args.explain)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(css)
            print(f"✓ CSS saved to: {args.output}")
        else:
            print(css)

    elif args.action == 'cover':
        print("\n🔄 Generating cover page...")
        title = args.title or "Professional Document"
        subtitle = args.subtitle or ""
        html = watermark.generate_cover_page_html(title, subtitle)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(html)
            print(f"✓ Cover page saved to: {args.output}")
        else:
            print(html)

    elif args.action == 'config':
        print("\n🔄 Generating configuration...")
        config = watermark.generate_watermark_config()
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✓ Config saved to: {args.output}")
        else:
            print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
