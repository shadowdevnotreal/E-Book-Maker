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
        # Prefer pdflatex first (best image support), then weasyprint, then wkhtmltopdf
        self.pdf_engines = ['pdflatex', 'weasyprint', 'wkhtmltopdf']
        self.page_numbering = PageNumberingConfig(page_numbering_config)

    def _find_executable_cross_platform(self, executable_name: str) -> Optional[str]:
        """
        Cross-platform executable finder for Windows/Linux/Mac

        Checks:
        1. shutil.which() - standard PATH search
        2. Windows: Common installation directories
        3. Both with and without .exe extension
        """
        import platform
        import os

        # Try standard PATH search first
        found = shutil.which(executable_name)
        if found:
            return found

        # Windows-specific checks
        if platform.system() == 'Windows':
            # Check with .exe extension
            if not executable_name.endswith('.exe'):
                found = shutil.which(f'{executable_name}.exe')
                if found:
                    return found

            # Check common Windows installation directories
            common_paths = [
                r'C:\Program Files',
                r'C:\Program Files (x86)',
                os.path.expanduser(r'~\AppData\Local\Programs'),
                r'C:\tools',
            ]

            # Add MiKTeX common paths for pdflatex
            if executable_name in ['pdflatex', 'pdflatex.exe']:
                common_paths.extend([
                    r'C:\Program Files\MiKTeX\miktex\bin\x64',
                    r'C:\Users\{}\AppData\Local\Programs\MiKTeX\miktex\bin\x64'.format(os.getenv('USERNAME', '')),
                ])

            # Add wkhtmltopdf common paths
            if executable_name in ['wkhtmltopdf', 'wkhtmltopdf.exe']:
                common_paths.extend([
                    r'C:\Program Files\wkhtmltopdf\bin',
                    r'C:\Program Files (x86)\wkhtmltopdf\bin',
                ])

            exe_name = executable_name if executable_name.endswith('.exe') else f'{executable_name}.exe'

            for base_path in common_paths:
                if not os.path.exists(base_path):
                    continue

                # Check directly in the path
                full_path = os.path.join(base_path, exe_name)
                if os.path.isfile(full_path):
                    return full_path

                # Search subdirectories (one level deep)
                try:
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if os.path.isdir(item_path):
                            subdir_path = os.path.join(item_path, 'bin', exe_name)
                            if os.path.isfile(subdir_path):
                                return subdir_path
                except (PermissionError, OSError):
                    continue

        return None

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required tools are installed (cross-platform)"""
        dependencies = {
            'pandoc': self._find_executable_cross_platform('pandoc') is not None,
            'wkhtmltopdf': self._find_executable_cross_platform('wkhtmltopdf') is not None,
            'pdflatex': self._find_executable_cross_platform('pdflatex') is not None,
            'weasyprint': self._find_executable_cross_platform('weasyprint') is not None
        }
        return dependencies

    def get_available_pdf_engine(self) -> Optional[str]:
        """Get the first available PDF engine (cross-platform)"""
        for engine in self.pdf_engines:
            if self._find_executable_cross_platform(engine):
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
            # Normalize content (remove em-dashes, fix encoding, etc.)
            content = self.normalize_content(content)

            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Run pandoc with proper markdown reading options
            # Disable smart typography (-smart) to prevent --- from becoming em-dash
            cmd = [
                'pandoc',
                '-f', 'markdown+definition_lists+fancy_lists+startnum-smart',
                str(temp_file),
                '-o', str(output_path),
                '--toc',
                '--toc-depth=3',
                f'--metadata=title:{title}',
                f'--metadata=author:{author}',
            ]

            # TODO: Add cover support
            # '--epub-cover-image=' if cover_path else ''

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
            # Check if pandoc is available (cross-platform)
            if not self._find_executable_cross_platform('pandoc'):
                print("Pandoc is not installed. Please install pandoc to convert to PDF.")
                return False

            # Get list of available PDF engines to try (cross-platform)
            available_engines = [engine for engine in self.pdf_engines if self._find_executable_cross_platform(engine)]

            if not available_engines:
                print("Warning: No PDF engines found. Install wkhtmltopdf, pdflatex, or weasyprint for better results.")
                available_engines = [None]  # Try without specifying engine

            # Normalize content (remove em-dashes, fix encoding, etc.)
            content = self.normalize_content(content)

            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'
            latex_header_file = None
            css_file = None

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Try each available PDF engine until one succeeds
            last_error = None
            for pdf_engine in available_engines:
                try:
                    if pdf_engine:
                        print(f"Attempting PDF conversion with {pdf_engine}...")

                    # Run pandoc with PDF engine and proper markdown reading
                    # Disable smart typography (-smart) to prevent --- from becoming em-dash
                    cmd = [
                        'pandoc',
                        '-f', 'markdown+definition_lists+fancy_lists+startnum-smart',
                        str(temp_file),
                        '-o', str(output_path),
                        '--toc',
                        '--toc-depth=3',
                        f'--metadata=title:{title}',
                        f'--metadata=author:{author}',
                        '--standalone',
                    ]

                    # Add PDF engine-specific options
                    if pdf_engine == 'wkhtmltopdf':
                        cmd.extend(['--pdf-engine=wkhtmltopdf'])

                        # Add page numbering for wkhtmltopdf
                        if self.page_numbering.config['enabled']:
                            position = self.page_numbering.config['pdf']['position']
                            print(f"  ✓ Adding wkhtmltopdf page numbering: {position}")

                            # wkhtmltopdf uses different syntax - each option needs separate --pdf-engine-opt
                            # Format: --pdf-engine-opt=--footer-center --pdf-engine-opt="[page]"
                            if 'footer-center' in position:
                                cmd.extend(['--pdf-engine-opt', '--footer-center', '--pdf-engine-opt', '[page]'])
                            elif 'footer-left' in position:
                                cmd.extend(['--pdf-engine-opt', '--footer-left', '--pdf-engine-opt', '[page]'])
                            elif 'footer-right' in position:
                                cmd.extend(['--pdf-engine-opt', '--footer-right', '--pdf-engine-opt', '[page]'])
                            elif 'header-center' in position:
                                cmd.extend(['--pdf-engine-opt', '--header-center', '--pdf-engine-opt', '[page]'])
                            elif 'header-left' in position:
                                cmd.extend(['--pdf-engine-opt', '--header-left', '--pdf-engine-opt', '[page]'])
                            elif 'header-right' in position:
                                cmd.extend(['--pdf-engine-opt', '--header-right', '--pdf-engine-opt', '[page]'])
                    elif pdf_engine == 'pdflatex':
                        cmd.extend(['--pdf-engine=pdflatex'])

                        # Add page numbering for pdflatex
                        if self.page_numbering.config['enabled']:
                            print(f"  ✓ Page numbering enabled: {self.page_numbering.config['pdf']['position']}, style: {self.page_numbering.config['pdf']['style']}")
                            latex_header = self.page_numbering.generate_latex_header()
                            if latex_header:
                                # Create temporary file for LaTeX header
                                latex_header_file = output_path.parent / f'temp_header_{output_path.stem}.tex'
                                with open(latex_header_file, 'w', encoding='utf-8') as f:
                                    f.write(latex_header)
                                print(f"  ✓ Created LaTeX header file: {latex_header_file}")
                                print(f"  ✓ Header file exists: {latex_header_file.exists()}")
                                print(f"  ✓ Header content:\n{latex_header}")
                                cmd.extend(['-H', str(latex_header_file)])
                            else:
                                print("  ✗ LaTeX header generation returned empty string")
                        else:
                            print("  ℹ Page numbering disabled")

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

                        # Add page numbering for weasyprint using inline CSS in HTML header
                        if self.page_numbering.config['enabled']:
                            print(f"  ✓ Page numbering enabled for weasyprint: {self.page_numbering.config['pdf']['position']}")

                            # Create HTML file with embedded CSS for page numbering
                            position = self.page_numbering.config['pdf']['position']
                            css_content = """<style>
@page {
    margin: 1in;
    @bottom-center {
        content: counter(page);
    }
}
</style>"""
                            # Create temporary HTML header file
                            css_file = output_path.parent / f'temp_pagenumbers_{output_path.stem}.html'
                            with open(css_file, 'w', encoding='utf-8') as f:
                                f.write(css_content)
                            print(f"  ✓ Created WeasyPrint CSS header file: {css_file}")
                            cmd.extend(['--include-in-header', str(css_file)])

                    # Debug: Print the exact command being run
                    print(f"  → Running command: {' '.join(cmd)}")

                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        print(f"✓ PDF created successfully with {pdf_engine if pdf_engine else 'default engine'}")
                        # Clean up temp files
                        if temp_file.exists():
                            temp_file.unlink()
                        if latex_header_file and latex_header_file.exists():
                            latex_header_file.unlink()
                        if css_file and css_file.exists():
                            css_file.unlink()
                        return True
                    else:
                        last_error = result.stderr
                        if pdf_engine:
                            # Print full error for debugging
                            error_msg = result.stderr.strip()
                            if len(error_msg) > 500:
                                error_msg = error_msg[:500] + "... (truncated)"
                            print(f"  {pdf_engine} failed with error:")
                            print(f"  {error_msg}")
                        # Try next engine
                        continue

                except Exception as e:
                    last_error = str(e)
                    print(f"  Error with {pdf_engine}: {e}")
                    continue

            # All engines failed
            # Clean up temp files
            if temp_file.exists():
                temp_file.unlink()
            if latex_header_file and latex_header_file.exists():
                latex_header_file.unlink()
            if css_file and css_file.exists():
                css_file.unlink()

            # Provide helpful error message
            error_msg = f"PDF conversion failed. Last error: {last_error}\n\n"
            error_msg += "PDF conversion requires a PDF engine. Please install one of:\n"
            error_msg += "  • wkhtmltopdf (Recommended): https://wkhtmltopdf.org/downloads.html\n"
            error_msg += "  • pdflatex (MiKTeX/TeX Live): https://miktex.org/download\n"
            error_msg += "  • weasyprint: pip install weasyprint\n\n"
            error_msg += "On Streamlit Cloud, add 'wkhtmltopdf' to packages.txt"

            print(error_msg)
            raise Exception(error_msg)

        except Exception as e:
            print(f"Error converting to PDF: {e}")
            return False

    def convert_to_html(self, content: str, output_path: Path, title: str, author: str,
                       css_file: Optional[Path] = None) -> bool:
        """Convert content to HTML format"""
        try:
            # Normalize content (remove em-dashes, fix encoding, etc.)
            content = self.normalize_content(content)

            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Run pandoc with proper markdown reading
            # Disable smart typography (-smart) to prevent --- from becoming em-dash
            cmd = [
                'pandoc',
                '-f', 'markdown+definition_lists+fancy_lists+startnum-smart',
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
            # Normalize content (remove em-dashes, fix encoding, etc.)
            content = self.normalize_content(content)

            # Create temporary file with content
            temp_file = output_path.parent / f'temp_{output_path.stem}.md'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Run pandoc with proper markdown reading options
            # Disable smart typography (-smart) to prevent --- from becoming em-dash
            cmd = [
                'pandoc',
                '-f', 'markdown+definition_lists+fancy_lists+startnum-smart',
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
            metadata: Additional metadata dictionary (description, publisher, language, etc.)
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

        # Check for PDF engine if PDF format requested
        if 'pdf' in output_formats:
            pdf_engines_available = any([deps.get(engine, False) for engine in self.pdf_engines])
            if not pdf_engines_available:
                error_msg = "PDF conversion requires a PDF engine, but none are installed.\n\n"
                error_msg += "Please install one of:\n"
                error_msg += "  • wkhtmltopdf (Recommended): https://wkhtmltopdf.org/downloads.html\n"
                error_msg += "  • pdflatex (MiKTeX/TeX Live): https://miktex.org/download\n"
                error_msg += "  • weasyprint: pip install weasyprint\n\n"
                error_msg += "Other formats (EPUB, HTML, DOCX, Markdown) will work without a PDF engine.\n\n"
                error_msg += "On Streamlit Cloud, add 'wkhtmltopdf' to packages.txt"
                raise Exception(error_msg)

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
