"""
E-Book Converter Module
Converts markdown/text/HTML to EPUB, PDF, and HTML using Pandoc
Consolidated from IT-Career-Blueprint-EBook pandoc tools

Supports:
- Amazon KDP-compliant margins for print books
- Multiple PDF engines (wkhtmltopdf, pdflatex, weasyprint)
- Page count-based gutter margins
"""

import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .text_normalizer import TextNormalizer
from .page_numbering import PageNumberingConfig

try:
    from kdp_calculator import KDPCalculator
except ImportError:
    # Fallback if kdp_calculator not available
    KDPCalculator = None


class EBookConverter:
    """Main e-book conversion class"""

    def __init__(self, page_numbering_config: Optional[Dict] = None):
        self.text_normalizer = TextNormalizer()
        self.supported_formats = ['epub', 'pdf', 'html', 'docx', 'md']
        self.pdf_engines = ['wkhtmltopdf', 'pdflatex', 'weasyprint']
        self.page_numbering = PageNumberingConfig(page_numbering_config)

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required tools are installed"""
        dependencies = {
            'pandoc': shutil.which('pandoc') is not None,
            'wkhtmltopdf': shutil.which('wkhtmltopdf') is not None,
            'pdflatex': shutil.which('pdflatex') is not None,
            'weasyprint': shutil.which('weasyprint') is not None
        }
        return dependencies

    def get_available_pdf_engine(self) -> Optional[str]:
        """Get the first available PDF engine"""
        for engine in self.pdf_engines:
            if shutil.which(engine):
                return engine
        return None

    def combine_files(self, input_files: List[Path]) -> str:
        """Combine multiple input files into one content"""
        # Check if files are binary formats that need Pandoc to read
        binary_formats = {'.docx', '.epub', '.odt'}
        has_binary = any(f.suffix.lower() in binary_formats for f in input_files)

        if has_binary:
            # For binary files, use Pandoc to convert to markdown first
            return self._combine_binary_files(input_files)

        # For text files, read directly
        combined_content = []
        for file_path in input_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append(content)
                    combined_content.append('\n\n')  # Add spacing between files
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

        return '\n'.join(combined_content)

    def _combine_binary_files(self, input_files: List[Path]) -> str:
        """Convert binary files to markdown and combine them"""
        combined_content = []

        for file_path in input_files:
            try:
                # Use Pandoc to convert to markdown
                result = subprocess.run(
                    ['pandoc', str(file_path), '-t', 'markdown'],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    combined_content.append(result.stdout)
                    combined_content.append('\n\n')
                else:
                    print(f"Warning: Could not convert {file_path}: {result.stderr}")
            except Exception as e:
                print(f"Warning: Error processing {file_path}: {e}")

        return '\n'.join(combined_content)

    def normalize_content(self, content: str) -> str:
        """Normalize text encoding and formatting"""
        content = self.text_normalizer.normalize_text(content)
        # Add blank lines before lists that follow other content (for proper markdown)
        content = self._ensure_blank_before_lists(content)
        return content

    def _ensure_blank_before_lists(self, content: str) -> str:
        """Ensure blank lines before list items for proper markdown parsing"""
        import re

        # Pattern: non-empty line followed immediately by bullet/numbered list
        # This adds a blank line before lists that don't already have one
        lines = content.split('\n')
        result = []

        for i, line in enumerate(lines):
            result.append(line)

            # Check if next line is a list item and current line is not blank
            if i < len(lines) - 1:
                current_stripped = line.strip()
                next_line = lines[i + 1].strip()

                # Check if next line is a list item
                next_is_list = (
                    next_line.startswith('- ') or
                    next_line.startswith('* ') or
                    re.match(r'^\d+\.\s', next_line)
                )

                # Check if current line is also a list item
                current_is_list = (
                    current_stripped.startswith('- ') or
                    current_stripped.startswith('* ') or
                    re.match(r'^\d+\.\s', current_stripped)
                )

                # If current line has content, next line is a list, and current is not a list
                if (current_stripped and
                    not current_stripped.startswith('#') and  # Not a header
                    not current_is_list and  # Current line is not a list item
                    next_is_list):  # Next line is a list item
                    # Add blank line before the list
                    result.append('')

        return '\n'.join(result)

    def create_metadata(self, title: str, author: str, subtitle: str = '',
                        has_frontmatter: bool = False) -> str:
        """Create YAML front matter for pandoc"""
        metadata = [
            '---',
            f'title: "{title}"',
            f'author: "{author}"',
        ]

        if subtitle:
            metadata.append(f'subtitle: "{subtitle}"')

        metadata.extend([
            f'date: "{datetime.now().strftime("%Y-%m-%d")}"',
            'toc: true',
            'toc-depth: 3',
        ])

        # Add page numbering configuration for PDF
        if self.page_numbering.config['enabled']:
            # For book-style front matter
            if has_frontmatter:
                metadata.append('documentclass: book')

            # Add LaTeX header includes
            latex_header = self.page_numbering.generate_latex_header()
            if latex_header:
                metadata.append('header-includes: |')
                for line in latex_header.split('\n'):
                    metadata.append(f'  {line}')

        metadata.extend([
            '---',
            ''
        ])

        return '\n'.join(metadata)

    def convert_to_epub(self, content: str, output_path: Path, title: str, author: str) -> bool:
        """Convert content to EPUB format"""
        try:
            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Run pandoc with proper markdown reading options
            cmd = [
                'pandoc',
                '-f', 'markdown+definition_lists+fancy_lists+startnum',
                str(temp_file),
                '-o', str(output_path),
                '--toc',
                '--toc-depth=3',
                f'--metadata=title:{title}',
                f'--metadata=author:{author}',
                '--epub-cover-image=' if False else '',  # TODO: Add cover support
            ]

            # Remove empty arguments
            cmd = [arg for arg in cmd if arg]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

            if result.returncode == 0:
                return True
            else:
                print(f"EPUB conversion error: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error converting to EPUB: {e}")
            return False

    def convert_to_pdf(self, content: str, output_path: Path, title: str, author: str,
                      kdp_compliant: bool = False, page_count: Optional[int] = None,
                      custom_margins: Optional[Dict[str, float]] = None) -> bool:
        """
        Convert content to PDF format

        Args:
            content: Markdown content to convert
            output_path: Output PDF file path
            title: Book title
            author: Book author
            kdp_compliant: Use Amazon KDP-compliant margins (default: False)
            page_count: Page count for KDP gutter calculation (required if kdp_compliant=True)
            custom_margins: Custom margins dict {'top': 0.75, 'bottom': 0.75, 'outside': 0.75, 'gutter': 0.5}

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get available PDF engine
            pdf_engine = self.get_available_pdf_engine()

            if not pdf_engine and not shutil.which('pandoc'):
                print("No PDF engine available. Install wkhtmltopdf, pdflatex, or weasyprint.")
                return False

            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Run pandoc with PDF engine and proper markdown reading
            cmd = [
                'pandoc',
                '-f', 'markdown+definition_lists+fancy_lists+startnum',
                str(temp_file),
                '-o', str(output_path),
                '--toc',
                '--toc-depth=3',
                f'--metadata=title:{title}',
                f'--metadata=author:{author}',
            ]

            # Add PDF engine if available
            if pdf_engine == 'wkhtmltopdf':
                cmd.extend(['--pdf-engine=wkhtmltopdf'])
            elif pdf_engine == 'pdflatex':
                cmd.extend(['--pdf-engine=pdflatex'])

                # Add KDP-compliant margins for pdflatex
                if kdp_compliant and KDPCalculator and page_count:
                    margins = KDPCalculator.calculate_manuscript_margins(page_count)
                    geometry = (
                        f'top={margins.top}in,'
                        f'bottom={margins.bottom}in,'
                        f'outer={margins.outside}in,'
                        f'inner={margins.gutter}in'
                    )
                    cmd.extend(['-V', f'geometry:{geometry}'])
                    print(f"  KDP Margins: Top={margins.top}\", Bottom={margins.bottom}\", "
                          f"Outer={margins.outside}\", Gutter={margins.gutter}\"")
                elif custom_margins:
                    # Use custom margins
                    geometry = (
                        f'top={custom_margins.get("top", 0.75)}in,'
                        f'bottom={custom_margins.get("bottom", 0.75)}in,'
                        f'outer={custom_margins.get("outside", 0.75)}in,'
                        f'inner={custom_margins.get("gutter", 0.5)}in'
                    )
                    cmd.extend(['-V', f'geometry:{geometry}'])

            elif pdf_engine == 'weasyprint':
                cmd.extend(['--pdf-engine=weasyprint'])

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

            if result.returncode == 0:
                return True
            else:
                print(f"PDF conversion error: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error converting to PDF: {e}")
            return False

    def convert_to_html(self, content: str, output_path: Path, title: str, author: str,
                       css_file: Optional[Path] = None) -> bool:
        """Convert content to HTML format"""
        try:
            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Run pandoc with proper markdown reading
            cmd = [
                'pandoc',
                '-f', 'markdown+definition_lists+fancy_lists+startnum',
                str(temp_file),
                '-o', str(output_path),
                '--standalone',
                '--toc',
                '--toc-depth=3',
                f'--metadata=title:{title}',
                f'--metadata=author:{author}',
                '--self-contained',
            ]

            # Add CSS if provided
            if css_file and css_file.exists():
                cmd.extend(['--css', str(css_file)])

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

            if result.returncode == 0:
                return True
            else:
                print(f"HTML conversion error: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error converting to HTML: {e}")
            return False

    def convert_to_docx(self, content: str, output_path: Path, title: str, author: str) -> bool:
        """Convert content to DOCX format with page numbering support"""
        try:
            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Run pandoc with proper markdown reading options
            cmd = [
                'pandoc',
                '-f', 'markdown+definition_lists+fancy_lists+startnum',
                str(temp_file),
                '-o', str(output_path),
                '--toc',
                '--toc-depth=3',
                f'--metadata=title:{title}',
                f'--metadata=author:{author}',
            ]

            # Add reference document if available for page numbering
            ref_doc = self.page_numbering.get_reference_doc_path()
            if ref_doc:
                cmd.extend(['--reference-doc', str(ref_doc)])

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

            if result.returncode == 0:
                return True
            else:
                print(f"DOCX conversion error: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error converting to DOCX: {e}")
            return False

    def convert_to_md(self, content: str, output_path: Path, title: str, author: str) -> bool:
        """Convert content to Markdown format"""
        try:
            # For MD output, we can just write the content with metadata
            # Or use pandoc to normalize the markdown
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        except Exception as e:
            print(f"Error converting to Markdown: {e}")
            return False

    def convert(self, input_files: List[Path], output_formats: List[str],
                title: str, author: str, subtitle: str = '',
                output_dir: Path = None, normalize_text: bool = True,
                css_file: Optional[Path] = None) -> List[Dict[str, str]]:
        """
        Main conversion method

        Args:
            input_files: List of input file paths
            output_formats: List of output formats (epub, pdf, html)
            title: Book title
            author: Author name
            subtitle: Book subtitle (optional)
            output_dir: Output directory
            normalize_text: Whether to normalize text encoding
            css_file: CSS file for HTML output

        Returns:
            List of dictionaries with file information
        """
        # Check dependencies
        deps = self.check_dependencies()
        if not deps['pandoc']:
            raise Exception("Pandoc is not installed. Please install pandoc to continue.")

        # Combine input files
        content = self.combine_files(input_files)

        # Normalize text if requested
        if normalize_text:
            content = self.normalize_content(content)

        # Add metadata
        metadata = self.create_metadata(title, author, subtitle)
        full_content = metadata + '\n\n' + content

        # Ensure output directory exists
        if output_dir is None:
            output_dir = Path.cwd() / 'output'

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert to requested formats
        results = []
        base_filename = title.lower().replace(' ', '-').replace('_', '-')

        for fmt in output_formats:
            if fmt not in self.supported_formats:
                print(f"Warning: Unsupported format '{fmt}'. Skipping.")
                continue

            output_path = output_dir / f'{base_filename}.{fmt}'

            print(f"Converting to {fmt.upper()}...")

            success = False
            if fmt == 'epub':
                success = self.convert_to_epub(full_content, output_path, title, author)
            elif fmt == 'pdf':
                success = self.convert_to_pdf(full_content, output_path, title, author)
            elif fmt == 'html':
                success = self.convert_to_html(full_content, output_path, title, author, css_file)
            elif fmt == 'docx':
                success = self.convert_to_docx(full_content, output_path, title, author)
            elif fmt == 'md':
                success = self.convert_to_md(full_content, output_path, title, author)

            if success and output_path.exists():
                results.append({
                    'name': output_path.name,
                    'path': str(output_path.relative_to(output_dir.parent)),
                    'size': output_path.stat().st_size,
                    'format': fmt
                })
                print(f"✓ {fmt.upper()} created: {output_path}")
            else:
                print(f"✗ {fmt.upper()} conversion failed")

        return results


if __name__ == '__main__':
    # Test the converter
    converter = EBookConverter()
    deps = converter.check_dependencies()

    print("Dependency Check:")
    for dep, installed in deps.items():
        status = "✓" if installed else "✗"
        print(f"  {status} {dep}")
