#!/usr/bin/env python3
"""
E-Book Conversion Script for "The Complete IT Career Readiness Pipeline"
Cross-platform Python version with enhanced features and progress tracking
Converts Markdown source files to multiple output formats using Pandoc
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import glob

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import text normalizer for encoding fixes
try:
    from text_normalizer import TextNormalizer
    NORMALIZER_AVAILABLE = True
except ImportError:
    NORMALIZER_AVAILABLE = False

class EBookConverter:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_dir = self.script_dir.parent
        self.ebook_dir = self.project_dir / "ebook"
        self.chapters_dir = self.ebook_dir / "chapters"
        self.appendices_dir = self.ebook_dir / "appendices"
        self.pandoc_dir = self.project_dir / "pandoc"

        self.title = "The Complete IT Career Readiness Pipeline"
        self.subtitle = "A Scientific Approach to IT Career Development"
        self.author = "Generated with AI Assistance"
        self.date = datetime.now().strftime("%Y-%m-%d")

        if RICH_AVAILABLE:
            self.console = Console()

        # Initialize text normalizer for encoding fixes
        if NORMALIZER_AVAILABLE:
            self.normalizer = TextNormalizer()
        else:
            self.normalizer = None

    def print_banner(self):
        """Print a nice banner."""
        if RICH_AVAILABLE:
            title_text = Text("🚀 E-Book Conversion Tool", style="bold blue")
            subtitle_text = Text("Cross-Platform Python Version", style="cyan")
            panel = Panel.fit(f"{title_text}\n{subtitle_text}")
            self.console.print(panel)

            self.console.print(f"📖 [cyan]Title:[/cyan] [bold]{self.title}[/bold]")
            self.console.print(f"📅 [cyan]Date:[/cyan] {self.date}")
        else:
            print("=" * 60)
            print("🚀 E-Book Conversion Tool")
            print("Cross-Platform Python Version")
            print("=" * 60)
            print(f"📖 Title: {self.title}")
            print(f"📅 Date: {self.date}")

    def check_dependencies(self):
        """Check for required dependencies."""
        missing = []

        # Check for Pandoc
        if not shutil.which("pandoc"):
            missing.append("pandoc")

        # Check for PDF engines
        pdf_engines = ["pdflatex", "wkhtmltopdf"]
        has_pdf_engine = any(shutil.which(engine) for engine in pdf_engines)

        if not has_pdf_engine:
            missing.append("wkhtmltopdf or pdflatex")

        if missing:
            if RICH_AVAILABLE:
                self.console.print("⚠️ [yellow]Missing dependencies:[/yellow]")
                for dep in missing:
                    self.console.print(f"   - {dep}")
                self.console.print("\n📥 [cyan]Installation instructions:[/cyan]")
                self.print_installation_instructions()
            else:
                print("⚠️ Missing dependencies:")
                for dep in missing:
                    print(f"   - {dep}")
                print("\n📥 Installation instructions:")
                self.print_installation_instructions()

            return False

        if RICH_AVAILABLE:
            self.console.print("✅ [green]All dependencies found[/green]")
        else:
            print("✅ All dependencies found")
        return True

    def print_installation_instructions(self):
        """Print platform-specific installation instructions."""
        system = platform.system().lower()

        instructions = {
            "windows": [
                "PowerShell (as Administrator):",
                "  choco install pandoc miktex",
                "Or download from:",
                "  https://pandoc.org/installing.html",
                "  https://miktex.org/download"
            ],
            "darwin": [  # macOS
                "Homebrew:",
                "  brew install pandoc",
                "  brew install --cask mactex",
                "Or:",
                "  brew install --cask wkhtmltopdf"
            ],
            "linux": [
                "Ubuntu/Debian:",
                "  sudo apt install pandoc wkhtmltopdf",
                "Fedora/CentOS:",
                "  sudo dnf install pandoc wkhtmltopdf",
                "Arch Linux:",
                "  sudo pacman -S pandoc wkhtmltopdf-static"
            ]
        }

        system_instructions = instructions.get(system, instructions["linux"])
        for instruction in system_instructions:
            if RICH_AVAILABLE:
                self.console.print(f"  {instruction}")
            else:
                print(f"  {instruction}")

    def create_combined_markdown(self, output_dir):
        """Create the combined markdown file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        temp_file = output_dir / "complete-book.md"

        if RICH_AVAILABLE:
            self.console.print("📝 [yellow]Creating combined markdown file...[/yellow]")
        else:
            print("📝 Creating combined markdown file...")

        # Create front matter
        front_matter = f"""---
title: "{self.title}"
subtitle: "{self.subtitle}"
author: "{self.author}"
date: "{self.date}"
documentclass: book
geometry: margin=1in
fontsize: 11pt
linestretch: 1.2
toc: true
toc-depth: 2
numbersections: true
---

# {self.title}
## {self.subtitle}

**Author:** {self.author}
**Publication Date:** {self.date}
**Format:** Multi-platform (EPUB, PDF, Web)

---

"""

        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(front_matter)

            # Add table of contents
            toc_file = self.project_dir / "table-of-contents.md"
            if toc_file.exists():
                if RICH_AVAILABLE:
                    self.console.print("📑 [cyan]Adding table of contents...[/cyan]")
                else:
                    print("📑 Adding table of contents...")
                toc_text = toc_file.read_text(encoding='utf-8', errors='replace')
                if self.normalizer:
                    toc_text = self.normalizer.normalize_text(toc_text)
                f.write(toc_text)
                f.write("\n---\n\n")

            # Add chapters
            if RICH_AVAILABLE:
                self.console.print("📚 [cyan]Adding chapters...[/cyan]")
            else:
                print("📚 Adding chapters...")

            for i in range(16):  # 0-15
                chapter_pattern = f"{i:02d}-*.md"
                chapter_files = list(self.chapters_dir.glob(chapter_pattern))

                for chapter_file in chapter_files:
                    if RICH_AVAILABLE:
                        self.console.print(f"  ✅ [green]Adding chapter {i}...[/green]")
                    else:
                        print(f"  ✅ Adding chapter {i}...")
                    f.write("\\newpage\n\n")
                    chapter_text = chapter_file.read_text(encoding='utf-8', errors='replace')
                    if self.normalizer:
                        chapter_text = self.normalizer.normalize_text(chapter_text)
                    f.write(chapter_text)
                    f.write("\n\n")

            # Add appendices
            if RICH_AVAILABLE:
                self.console.print("📋 [cyan]Adding appendices...[/cyan]")
            else:
                print("📋 Adding appendices...")

            for appendix in self.appendices_dir.glob("*.md"):
                if RICH_AVAILABLE:
                    self.console.print(f"  ✅ [green]Adding {appendix.name}...[/green]")
                else:
                    print(f"  ✅ Adding {appendix.name}...")
                f.write("\\newpage\n\n")
                appendix_text = appendix.read_text(encoding='utf-8', errors='replace')
                if self.normalizer:
                    appendix_text = self.normalizer.normalize_text(appendix_text)
                f.write(appendix_text)
                f.write("\n\n")

        if RICH_AVAILABLE:
            self.console.print(f"✅ [green]Combined file created: {temp_file}[/green]")
        else:
            print(f"✅ Combined file created: {temp_file}")

        return temp_file

    def generate_epub(self, temp_file, output_dir):
        """Generate EPUB format."""
        epub_file = output_dir / "complete-it-career-readiness-pipeline.epub"

        cmd = [
            "pandoc", str(temp_file),
            "--to", "epub3",
            "--output", str(epub_file),
            "--metadata", f"title={self.title}",
            "--metadata", f"author={self.author}",
            "--metadata", f"date={self.date}",
            "--toc",
            "--toc-depth=2"
        ]

        # Add cover image if it exists
        cover_image = self.project_dir / "assets" / "cover.png"
        if cover_image.exists():
            cmd.extend(["--epub-cover-image", str(cover_image)])

        subprocess.run(cmd, check=True)
        return epub_file

    def generate_pdf(self, temp_file, output_dir):
        """Generate PDF format with improved encoding support."""
        pdf_file = output_dir / "complete-it-career-readiness-pipeline.pdf"

        # Prefer wkhtmltopdf to avoid LaTeX Unicode issues
        if shutil.which("wkhtmltopdf"):
            pdf_engine = "wkhtmltopdf"
            extra_args = [
                "--pdf-engine-opt=--encoding",
                "--pdf-engine-opt=utf-8",
                "--pdf-engine-opt=--enable-local-file-access",
                "--pdf-engine-opt=--no-stop-slow-scripts"
            ]
        elif shutil.which("weasyprint"):
            # WeasyPrint has excellent Unicode support
            pdf_engine = "weasyprint"
            extra_args = []
        elif shutil.which("pdflatex"):
            pdf_engine = "pdflatex"
            # Add comprehensive Unicode support for LaTeX
            extra_args = [
                "--variable", "geometry:margin=1in",
                "--variable", "fontsize:11pt",
                "--variable", "linestretch:1.2",
                "--variable", "fontenc:T1",
                "--variable", "mainfont:DejaVu Sans",
                "--pdf-engine-opt=-shell-escape",
                "--pdf-engine-opt=-interaction=nonstopmode"
            ]
        else:
            raise RuntimeError("No PDF engine available. Install wkhtmltopdf, weasyprint, or pdflatex.")

        cmd = [
            "pandoc", str(temp_file),
            "--to", "pdf",
            "--pdf-engine", pdf_engine,
            "--output", str(pdf_file),
            "--metadata", f"title={self.title}",
            "--metadata", f"author={self.author}",
            "--metadata", f"date={self.date}",
            "--toc",
            "--toc-depth=2",
            "--resource-path=.:./assets"  # Help find images
        ] + extra_args

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            # If PDF generation fails, provide helpful error message
            if RICH_AVAILABLE:
                self.console.print(f"⚠️ [yellow]PDF generation error:[/yellow] {e.stderr}")
            else:
                print(f"⚠️ PDF generation error: {e.stderr}")
            raise

        return pdf_file

    def generate_html(self, temp_file, output_dir):
        """Generate HTML format with proper UTF-8 encoding."""
        html_file = output_dir / "complete-it-career-readiness-pipeline.html"

        cmd = [
            "pandoc", str(temp_file),
            "--to", "html5",
            "--output", str(html_file),
            "--metadata", f"title={self.title}",
            "--metadata", f"author={self.author}",
            "--metadata", f"date={self.date}",
            "--metadata", "charset=UTF-8",
            "--toc",
            "--toc-depth=2",
            "--standalone",
            "--self-contained"  # Embed CSS and resources (works in pandoc 2.x and 3.x)
        ]

        # Add CSS if available
        css_file = self.pandoc_dir / "style.css"
        if css_file.exists():
            cmd.extend(["--css", str(css_file)])

        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return html_file

    def convert(self, output_dir, formats=None):
        """Main conversion function."""
        if formats is None:
            formats = ["epub", "pdf", "html"]

        output_dir = Path(output_dir)

        # Check dependencies
        if not self.check_dependencies():
            return False

        # Create combined markdown
        temp_file = self.create_combined_markdown(output_dir)

        # Generate formats
        generated_files = []

        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                for fmt in formats:
                    task = progress.add_task(f"Generating {fmt.upper()}...", total=None)

                    try:
                        if fmt == "epub":
                            file_path = self.generate_epub(temp_file, output_dir)
                        elif fmt == "pdf":
                            file_path = self.generate_pdf(temp_file, output_dir)
                        elif fmt == "html":
                            file_path = self.generate_html(temp_file, output_dir)
                        else:
                            continue

                        generated_files.append((fmt.upper(), file_path))
                        progress.update(task, completed=1)

                    except subprocess.CalledProcessError as e:
                        progress.update(task, description=f"Failed to generate {fmt.upper()}")
                        if RICH_AVAILABLE:
                            self.console.print(f"❌ [red]Error generating {fmt}: {e}[/red]")
                        else:
                            print(f"❌ Error generating {fmt}: {e}")
        else:
            for fmt in formats:
                print(f"📱 Generating {fmt.upper()}...")

                try:
                    if fmt == "epub":
                        file_path = self.generate_epub(temp_file, output_dir)
                    elif fmt == "pdf":
                        file_path = self.generate_pdf(temp_file, output_dir)
                    elif fmt == "html":
                        file_path = self.generate_html(temp_file, output_dir)
                    else:
                        continue

                    generated_files.append((fmt.upper(), file_path))
                    print(f"✅ {fmt.upper()} generated successfully!")

                except subprocess.CalledProcessError as e:
                    print(f"❌ Error generating {fmt}: {e}")

        # Show results
        if RICH_AVAILABLE:
            self.console.print("\n🎉 [bold green]Conversion complete![/bold green]")
            self.console.print("📁 [cyan]Generated files:[/cyan]")
            for fmt, file_path in generated_files:
                self.console.print(f"  📄 [green]{fmt}: {file_path}[/green]")
            self.console.print(f"  📝 [green]Combined Markdown: {temp_file}[/green]")
        else:
            print("\n🎉 Conversion complete!")
            print("📁 Generated files:")
            for fmt, file_path in generated_files:
                print(f"  📄 {fmt}: {file_path}")
            print(f"  📝 Combined Markdown: {temp_file}")

        # Word count
        try:
            content = temp_file.read_text(encoding='utf-8')
            word_count = len(content.split())
            if RICH_AVAILABLE:
                self.console.print(f"📊 [cyan]Final word count: {word_count:,} words[/cyan]")
            else:
                print(f"📊 Final word count: {word_count:,} words")
        except Exception:
            pass

        return True

def main():
    parser = argparse.ArgumentParser(
        description="E-Book Conversion Tool for Diatasso PRCM IT Career Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-o", "--output",
        default="build",
        help="Output directory (default: build)"
    )
    parser.add_argument(
        "-f", "--formats",
        nargs="+",
        choices=["epub", "pdf", "html"],
        default=["epub", "pdf", "html"],
        help="Output formats to generate (default: all)"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open output directory after conversion"
    )

    args = parser.parse_args()

    converter = EBookConverter()
    converter.print_banner()

    # Convert
    success = converter.convert(args.output, args.formats)

    if success and args.open:
        output_path = Path(args.output)
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(output_path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(output_path)])

if __name__ == "__main__":
    main()