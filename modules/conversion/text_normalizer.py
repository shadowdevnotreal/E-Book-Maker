#!/usr/bin/env python3
"""
Text Normalizer for E-Book Conversion
Fixes encoding and formatting issues before Pandoc conversion
"""

import re
import unicodedata
from pathlib import Path


class TextNormalizer:
    """Normalizes text to prevent encoding issues during format conversion"""

    def __init__(self):
        # Character replacements for common encoding issues
        self.replacements = {
            # Non-breaking spaces
            '\u00A0': ' ',  # Non-breaking space
            '\u202F': ' ',  # Narrow no-break space
            '\u2007': ' ',  # Figure space
            '\u2060': '',   # Word joiner

            # Various dashes and hyphens (AI detection removal)
            '\u2013': '-',   # En dash → regular dash
            '\u2014': ' - ', # Em dash → space-dash-space (natural, non-AI style)
            '\u2015': ' - ', # Horizontal bar → space-dash-space
            '\u2212': '-',   # Minus sign → regular dash

            # Quotation marks
            '\u2018': "'",   # Left single quotation
            '\u2019': "'",   # Right single quotation / apostrophe
            '\u201A': "'",   # Single low-9 quotation
            '\u201B': "'",   # Single high-reversed-9 quotation
            '\u201C': '"',   # Left double quotation
            '\u201D': '"',   # Right double quotation
            '\u201E': '"',   # Double low-9 quotation
            '\u201F': '"',   # Double high-reversed-9 quotation
            '\u2032': "'",   # Prime
            '\u2033': '"',   # Double prime

            # Ellipsis
            '\u2026': '...',

            # Bullet points
            '\u2022': '-',   # Bullet
            '\u2023': '>',   # Triangular bullet
            '\u2043': '-',   # Hyphen bullet

            # Whitespace
            '\u2028': '\n',  # Line separator
            '\u2029': '\n\n', # Paragraph separator
            '\t': '    ',    # Tab to spaces

            # Other problematic characters
            '\u00AD': '',    # Soft hyphen
            '\uFEFF': '',    # Zero width no-break space (BOM)
        }

    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters to their closest ASCII equivalents
        while preserving readability
        """
        # First, apply specific replacements
        for char, replacement in self.replacements.items():
            text = text.replace(char, replacement)

        # Normalize to NFKD (compatibility decomposition)
        # This breaks down complex characters into simpler forms
        text = unicodedata.normalize('NFKD', text)

        # Remove combining marks that can cause rendering issues
        text = ''.join(
            char for char in text
            if not unicodedata.combining(char)
        )

        return text

    def fix_list_formatting(self, text: str) -> str:
        """
        Ensure proper spacing around list items and convert inline bullets to proper lists
        """
        # Fix inline bullets that were converted from • to -
        # Pattern: "text: - item - item - item" → "text:\n- item\n- item\n- item"
        # This handles lists that were inline in the original document

        # Step 1: Fix inline list patterns (items separated by " - " on same line)
        # Look for pattern: ": - item - item" or "text - item - item"
        lines = text.split('\n')
        fixed_lines = []

        for line in lines:
            # Check if line contains inline list pattern: multiple " - " separators
            if line.count(' - ') >= 2 or (': -' in line and ' - ' in line):
                # This looks like an inline list
                # Split on " - " and create proper list items
                parts = re.split(r'\s+-\s+', line)

                # First part might contain text before the list
                if ':' in parts[0]:
                    # Split at colon
                    prefix, first_item = parts[0].rsplit(':', 1)
                    first_item = first_item.strip()

                    fixed_lines.append(prefix + ':')
                    if first_item:  # If there's content after colon, treat as first item
                        fixed_lines.append('- ' + first_item)

                    # Add remaining items
                    for item in parts[1:]:
                        if item.strip():
                            fixed_lines.append('- ' + item.strip())
                else:
                    # No colon, just add all parts as list items
                    for item in parts:
                        if item.strip():
                            fixed_lines.append('- ' + item.strip())
            else:
                # Normal line, keep as is
                fixed_lines.append(line)

        text = '\n'.join(fixed_lines)

        # Fix bullet lists - ensure blank line before first list item
        text = re.sub(r'([a-z.:,;])\n([-*+]\s)', r'\1\n\n\2', text)

        # Fix lists with colons - ensure newline after colon before first item
        text = re.sub(r':\n([-*+]\s)', r':\n\n\1', text)

        # Remove blank lines BETWEEN consecutive list items (keep lists tight)
        # Apply multiple times to handle all consecutive list items
        prev = ""
        while prev != text:
            prev = text
            text = re.sub(r'(^[-*+]\s+[^\n]+)\n\n(^[-*+]\s+)', r'\1\n\2', text, flags=re.MULTILINE)

        # Clean up any excessive blank lines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def fix_line_breaks(self, text: str) -> str:
        """
        Normalize line breaks and prevent unwanted line wrapping
        """
        # Remove trailing whitespace
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)

        # Normalize multiple blank lines to maximum of 2
        text = re.sub(r'\n{4,}', '\n\n\n', text)

        # Fix orphaned punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)

        return text

    def fix_special_symbols(self, text: str) -> str:
        """
        Handle special symbols that may cause encoding issues
        """
        # Fix degree symbol
        text = text.replace('°', ' degrees')

        # Fix copyright and trademark
        text = text.replace('©', '(c)')
        text = text.replace('®', '(R)')
        # Keep ™ as-is or replace if needed
        # text = text.replace('™', '(TM)')

        # Fix mathematical operators
        text = text.replace('×', 'x')
        text = text.replace('÷', '/')
        text = text.replace('≈', '~')
        text = text.replace('≠', '!=')
        text = text.replace('≤', '<=')
        text = text.replace('≥', '>=')

        return text

    def normalize_file(self, input_path: Path, output_path: Path = None) -> Path:
        """
        Normalize a markdown file

        Args:
            input_path: Path to input markdown file
            output_path: Optional output path (defaults to input_path with .normalized.md)

        Returns:
            Path to normalized file
        """
        if output_path is None:
            output_path = input_path.with_suffix('.normalized.md')

        # Read with UTF-8 encoding
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()

        # Apply normalizations
        text = self.normalize_unicode(text)
        text = self.fix_list_formatting(text)
        text = self.fix_line_breaks(text)
        text = self.fix_special_symbols(text)

        # Write with UTF-8 encoding
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)

        return output_path

    def normalize_text(self, text: str) -> str:
        """
        Normalize text string directly

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        text = self.normalize_unicode(text)
        text = self.fix_list_formatting(text)
        text = self.fix_line_breaks(text)
        text = self.fix_special_symbols(text)
        return text


def main():
    """CLI interface for text normalizer"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Normalize text files to prevent encoding issues'
    )
    parser.add_argument('input', type=Path, help='Input markdown file')
    parser.add_argument('-o', '--output', type=Path, help='Output file path')
    parser.add_argument('--test', action='store_true', help='Test mode - print to stdout')

    args = parser.parse_args()

    normalizer = TextNormalizer()

    if args.test:
        with open(args.input, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()

        normalized = normalizer.normalize_text(text)
        print(normalized)
    else:
        output_path = normalizer.normalize_file(args.input, args.output)
        print(f"✅ Normalized file saved to: {output_path}")


if __name__ == "__main__":
    main()
