#!/usr/bin/env python3
"""
Interactive E-Book Builder for "The IT Career Blueprint™"
=========================================================

Enhanced interactive version with menu-driven interface, preview options,
custom configurations, and selective chapter building.

Features:
- Interactive menu system
- Chapter preview and validation
- Custom metadata configuration
- Selective chapter building
- Template customization
- Progress tracking with detailed feedback
- Build validation and quality checks
"""

import os
import sys
import platform
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime
import glob
import re

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback for systems without rich
    def Prompt(text, default=None):
        user_input = input(f"{text} [{default}]: " if default else f"{text}: ")
        return user_input if user_input else default

    def Confirm(text, default=True):
        response = input(f"{text} [{'Y/n' if default else 'y/N'}]: ").lower()
        if not response:
            return default
        return response in ['y', 'yes', 'true', '1']

    def IntPrompt(text, default=None):
        while True:
            try:
                response = input(f"{text} [{default}]: " if default else f"{text}: ")
                return int(response) if response else default
            except ValueError:
                print("Please enter a valid number.")

class InteractiveEBookBuilder:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_dir = self.script_dir.parent
        self.ebook_dir = self.project_dir / "ebook"
        self.chapters_dir = self.ebook_dir / "chapters"
        self.appendices_dir = self.ebook_dir / "appendices"
        self.templates_dir = self.project_dir / "templates"
        self.pandoc_dir = self.project_dir / "pandoc"

        # Configuration
        self.config = {
            "title": "The IT Career Blueprint™",
            "subtitle": "A Complete Professional Development System",
            "author": "Generated with Diatasso PRCM™",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "output_dir": "build",  # This maps to output/ebooks via symlink
            "formats": ["epub", "pdf", "html"],
            "include_chapters": "all",
            "include_appendices": True,
            "custom_css": True,
            "word_count_target": 50000
        }

        if RICH_AVAILABLE:
            self.console = Console()

    def print_banner(self):
        """Print an interactive banner."""
        if RICH_AVAILABLE:
            title = Text("🚀 Interactive E-Book Builder", style="bold blue")
            subtitle = Text("The IT Career Blueprint™", style="bold cyan")
            version = Text("Enhanced Interactive Version v2.0", style="green")

            banner_content = f"{title}\n{subtitle}\n{version}"
            panel = Panel.fit(banner_content, border_style="blue")
            self.console.print(panel)
        else:
            print("=" * 70)
            print("🚀 Interactive E-Book Builder")
            print("The IT Career Blueprint™")
            print("Enhanced Interactive Version v2.0")
            print("=" * 70)

    def check_environment(self):
        """Check environment and dependencies with interactive feedback."""
        if RICH_AVAILABLE:
            self.console.print("\n🔍 [yellow]Checking build environment...[/yellow]")
        else:
            print("\n🔍 Checking build environment...")

        # Check directory structure
        missing_dirs = []
        required_dirs = [
            ("E-book chapters", self.chapters_dir),
            ("E-book appendices", self.appendices_dir),
            ("Templates", self.templates_dir),
            ("Pandoc tools", self.pandoc_dir)
        ]

        for name, path in required_dirs:
            if not path.exists():
                missing_dirs.append((name, path))

        if missing_dirs:
            if RICH_AVAILABLE:
                self.console.print("❌ [red]Missing directories:[/red]")
                for name, path in missing_dirs:
                    self.console.print(f"   - {name}: {path}")
                self.console.print("\n[yellow]💡 Solution:[/yellow]")
                self.console.print("Make sure you're running this from the project root directory.")
                self.console.print("Your content should be organized as:")
                self.console.print("  ebook/chapters/    - Chapter markdown files")
                self.console.print("  ebook/appendices/  - Appendix markdown files")
            else:
                print("❌ Missing directories:")
                for name, path in missing_dirs:
                    print(f"   - {name}: {path}")
                print("\n💡 Solution:")
                print("Make sure you're running this from the project root directory.")
                print("Your content should be organized as:")
                print("  ebook/chapters/    - Chapter markdown files")
                print("  ebook/appendices/  - Appendix markdown files")
            return False

        # Check dependencies
        dependencies = {
            "pandoc": "Core conversion tool",
            "wkhtmltopdf": "PDF generation (alternative)",
            "pdflatex": "PDF generation (preferred)"
        }

        missing_deps = []
        available_deps = []

        for dep, description in dependencies.items():
            if shutil.which(dep):
                available_deps.append((dep, description))
            else:
                missing_deps.append((dep, description))

        if RICH_AVAILABLE:
            # Create a table for dependency status
            table = Table(title="Dependency Status")
            table.add_column("Tool", style="cyan")
            table.add_column("Status", justify="center")
            table.add_column("Description", style="dim")

            for dep, desc in available_deps:
                table.add_row(dep, "✅ Available", desc)

            for dep, desc in missing_deps:
                table.add_row(dep, "❌ Missing", desc)

            self.console.print(table)
        else:
            print("📊 Dependency Status:")
            for dep, desc in available_deps:
                print(f"   ✅ {dep}: {desc}")
            for dep, desc in missing_deps:
                print(f"   ❌ {dep}: {desc}")

        # Critical check for Pandoc
        if "pandoc" in [dep for dep, _ in missing_deps]:
            if RICH_AVAILABLE:
                self.console.print("\n❌ [red]Pandoc is required and not found![/red]")
                self.console.print("📥 [cyan]Installation instructions:[/cyan]")
            else:
                print("\n❌ Pandoc is required and not found!")
                print("📥 Installation instructions:")

            self.print_installation_instructions()
            return False

        if RICH_AVAILABLE:
            self.console.print("\n✅ [green]Environment check passed![/green]")
        else:
            print("\n✅ Environment check passed!")

        return True

    def print_installation_instructions(self):
        """Print platform-specific installation instructions."""
        system = platform.system().lower()

        instructions = {
            "windows": [
                "🪟 Windows Installation:",
                "   PowerShell (as Administrator):",
                "   > choco install pandoc wkhtmltopdf",
                "   Or download from:",
                "   > https://pandoc.org/installing.html"
            ],
            "darwin": [  # macOS
                "🍎 macOS Installation:",
                "   Homebrew:",
                "   $ brew install pandoc wkhtmltopdf",
                "   For LaTeX (better PDF):",
                "   $ brew install --cask mactex"
            ],
            "linux": [
                "🐧 Linux Installation:",
                "   Ubuntu/Debian:",
                "   $ sudo apt install pandoc wkhtmltopdf texlive-latex-base",
                "   Fedora/CentOS:",
                "   $ sudo dnf install pandoc wkhtmltopdf texlive",
                "   Arch Linux:",
                "   $ sudo pacman -S pandoc wkhtmltopdf-static texlive-core"
            ]
        }

        system_instructions = instructions.get(system, instructions["linux"])
        for instruction in system_instructions:
            if RICH_AVAILABLE:
                self.console.print(instruction)
            else:
                print(instruction)

    def analyze_content(self):
        """Analyze available content and show statistics."""
        if RICH_AVAILABLE:
            self.console.print("\n📊 [yellow]Analyzing content...[/yellow]")
        else:
            print("\n📊 Analyzing content...")

        # Find chapters
        chapter_files = sorted(self.chapters_dir.glob("*.md"))
        appendix_files = sorted(self.appendices_dir.glob("*.md"))

        total_words = 0
        chapter_info = []

        # Analyze chapters
        for i, chapter_file in enumerate(chapter_files):
            try:
                content = chapter_file.read_text(encoding='utf-8')
                words = len(content.split())
                total_words += words

                # Extract title from first heading
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else chapter_file.stem

                chapter_info.append({
                    "number": i,
                    "file": chapter_file.name,
                    "title": title,
                    "words": words,
                    "size": chapter_file.stat().st_size
                })
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"⚠️ [yellow]Warning: Could not read {chapter_file.name}: {e}[/yellow]")
                else:
                    print(f"⚠️ Warning: Could not read {chapter_file.name}: {e}")

        # Analyze appendices
        appendix_info = []
        for appendix_file in appendix_files:
            try:
                content = appendix_file.read_text(encoding='utf-8')
                words = len(content.split())
                total_words += words

                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else appendix_file.stem

                appendix_info.append({
                    "file": appendix_file.name,
                    "title": title,
                    "words": words,
                    "size": appendix_file.stat().st_size
                })
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"⚠️ [yellow]Warning: Could not read {appendix_file.name}: {e}[/yellow]")
                else:
                    print(f"⚠️ Warning: Could not read {appendix_file.name}: {e}")

        # Display analysis
        if RICH_AVAILABLE:
            # Summary table
            summary_table = Table(title="Content Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", justify="right", style="green")

            summary_table.add_row("Total Chapters", str(len(chapter_info)))
            summary_table.add_row("Total Appendices", str(len(appendix_info)))
            summary_table.add_row("Total Word Count", f"{total_words:,} words")
            summary_table.add_row("Target Progress", f"{(total_words/self.config['word_count_target']*100):.1f}%")

            self.console.print(summary_table)

            # Chapter details
            if chapter_info:
                chapter_table = Table(title="Available Chapters")
                chapter_table.add_column("#", justify="center", style="cyan")
                chapter_table.add_column("File", style="blue")
                chapter_table.add_column("Title", style="white")
                chapter_table.add_column("Words", justify="right", style="green")

                for chapter in chapter_info:
                    chapter_table.add_row(
                        str(chapter["number"]),
                        chapter["file"],
                        chapter["title"][:50] + "..." if len(chapter["title"]) > 50 else chapter["title"],
                        f"{chapter['words']:,}"
                    )

                self.console.print(chapter_table)
        else:
            print(f"\n📊 Content Summary:")
            print(f"   Total Chapters: {len(chapter_info)}")
            print(f"   Total Appendices: {len(appendix_info)}")
            print(f"   Total Word Count: {total_words:,} words")
            print(f"   Target Progress: {(total_words/self.config['word_count_target']*100):.1f}%")

            if chapter_info:
                print(f"\n📚 Available Chapters:")
                for chapter in chapter_info:
                    print(f"   {chapter['number']:2d}. {chapter['title'][:60]} ({chapter['words']:,} words)")

        return {
            "chapters": chapter_info,
            "appendices": appendix_info,
            "total_words": total_words
        }

    def interactive_configuration(self):
        """Interactive configuration menu."""
        if RICH_AVAILABLE:
            self.console.print("\n⚙️ [yellow]Configuration Setup[/yellow]")
            self.console.print("[dim]💡 Press Enter to keep current values, or type new values to change[/dim]")
        else:
            print("\n⚙️ Configuration Setup")
            print("💡 Press Enter to keep current values, or type new values to change")

        # Book metadata
        if RICH_AVAILABLE:
            self.console.print("\n📖 [cyan]Book Metadata:[/cyan]")
            self.console.print("[dim]This information will appear in your e-book's title page and metadata[/dim]")
        else:
            print("\n📖 Book Metadata:")
            print("This information will appear in your e-book's title page and metadata")

        self.config["title"] = Prompt.ask(
            "📚 Book title (appears on cover and in metadata)",
            default=self.config["title"]
        )

        self.config["subtitle"] = Prompt.ask(
            "📄 Book subtitle (optional descriptive text)",
            default=self.config["subtitle"]
        )

        self.config["author"] = Prompt.ask(
            "✍️  Author name (your name or organization)",
            default=self.config["author"]
        )

        # Output configuration
        if RICH_AVAILABLE:
            self.console.print("\n📁 [cyan]Output Configuration:[/cyan]")
            self.console.print("[dim]Choose where your generated e-books will be saved[/dim]")
        else:
            print("\n📁 Output Configuration:")
            print("Choose where your generated e-books will be saved")

        self.config["output_dir"] = Prompt.ask(
            "📂 Output directory (relative to project root)",
            default=self.config["output_dir"]
        )

        # Format selection
        if RICH_AVAILABLE:
            self.console.print("\n📄 [cyan]Select output formats:[/cyan]")
            self.console.print("[dim]💡 You can generate multiple formats at once. Choose what you need:[/dim]")

            format_table = Table()
            format_table.add_column("Format", style="cyan")
            format_table.add_column("Description", style="white")
            format_table.add_column("Best for", style="green")
            format_table.add_column("File Size", style="yellow")

            formats_info = [
                ("EPUB", "E-reader format", "Kindle, tablets, e-readers", "Small"),
                ("PDF", "Portable document", "Printing, sharing, archiving", "Medium"),
                ("HTML", "Web format", "Online reading, websites", "Small")
            ]

            for fmt, desc, best, size in formats_info:
                format_table.add_row(fmt, desc, best, size)

            self.console.print(format_table)
        else:
            print("\n📄 Available formats:")
            print("💡 You can generate multiple formats at once. Choose what you need:")
            print("   EPUB - E-reader format (Kindle, tablets) - Small file size")
            print("   PDF  - Portable document (printing, sharing) - Medium file size")
            print("   HTML - Web format (online reading) - Small file size")

        selected_formats = []
        for fmt in ["epub", "pdf", "html"]:
            format_desc = {
                "epub": "📱 EPUB (for e-readers and tablets)",
                "pdf": "📄 PDF (for printing and professional sharing)",
                "html": "🌐 HTML (for web publishing and online reading)"
            }
            if Confirm.ask(f"Generate {format_desc[fmt]}", default=fmt in self.config["formats"]):
                selected_formats.append(fmt)

        if not selected_formats:
            if RICH_AVAILABLE:
                self.console.print("⚠️ [yellow]No formats selected! Defaulting to EPUB and PDF.[/yellow]")
            else:
                print("⚠️ No formats selected! Defaulting to EPUB and PDF.")
            selected_formats = ["epub", "pdf"]

        self.config["formats"] = selected_formats

        # Advanced options
        if RICH_AVAILABLE:
            self.console.print("\n🔧 [cyan]Advanced Options:[/cyan]")
            self.console.print("[dim]Optional settings for customization and selective building[/dim]")
        else:
            print("\n🔧 Advanced Options:")
            print("Optional settings for customization and selective building")

        if Confirm.ask("Configure advanced options (appendices, styling, chapter selection)", default=False):
            self.config["include_appendices"] = Confirm.ask(
                "📋 Include appendices (supplementary content)",
                default=self.config["include_appendices"]
            )

            self.config["custom_css"] = Confirm.ask(
                "🎨 Use custom CSS styling (enhanced appearance)",
                default=self.config["custom_css"]
            )

            if Confirm.ask("📚 Select specific chapters to include (useful for drafts)", default=False):
                self.config["include_chapters"] = self.select_chapters()

        # Show summary
        if RICH_AVAILABLE:
            self.console.print(f"\n✅ [green]Configuration complete![/green]")
            self.console.print(f"📚 Book: [bold]{self.config['title']}[/bold] by {self.config['author']}")
            self.console.print(f"📁 Output: {self.config['output_dir']}")
            self.console.print(f"📄 Formats: {', '.join(self.config['formats'])}")
        else:
            print(f"\n✅ Configuration complete!")
            print(f"📚 Book: {self.config['title']} by {self.config['author']}")
            print(f"📁 Output: {self.config['output_dir']}")
            print(f"📄 Formats: {', '.join(self.config['formats'])}")

    def select_chapters(self):
        """Interactive chapter selection."""
        chapter_files = sorted(self.chapters_dir.glob("*.md"))

        if RICH_AVAILABLE:
            self.console.print("\n📚 [cyan]Chapter Selection:[/cyan]")
        else:
            print("\n📚 Chapter Selection:")

        if Confirm.ask("Include all chapters", default=True):
            return "all"

        # Manual selection
        selected = []
        for i, chapter_file in enumerate(chapter_files):
            # Extract title
            try:
                content = chapter_file.read_text(encoding='utf-8')
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else chapter_file.stem
            except:
                title = chapter_file.stem

            if Confirm.ask(f"Include Chapter {i}: {title}", default=True):
                selected.append(i)

        return selected

    def preview_build(self):
        """Preview what will be built."""
        if RICH_AVAILABLE:
            self.console.print("\n👀 [yellow]Build Preview[/yellow]")

            preview_table = Table(title="Build Configuration")
            preview_table.add_column("Setting", style="cyan")
            preview_table.add_column("Value", style="white")

            preview_table.add_row("Title", self.config["title"])
            preview_table.add_row("Author", self.config["author"])
            preview_table.add_row("Output Directory", self.config["output_dir"])
            preview_table.add_row("Formats", ", ".join(self.config["formats"]))
            preview_table.add_row("Include Chapters",
                                str(self.config["include_chapters"]) if isinstance(self.config["include_chapters"], list)
                                else self.config["include_chapters"])
            preview_table.add_row("Include Appendices", "Yes" if self.config["include_appendices"] else "No")
            preview_table.add_row("Custom CSS", "Yes" if self.config["custom_css"] else "No")

            self.console.print(preview_table)
        else:
            print("\n👀 Build Preview:")
            print(f"   Title: {self.config['title']}")
            print(f"   Author: {self.config['author']}")
            print(f"   Output Directory: {self.config['output_dir']}")
            print(f"   Formats: {', '.join(self.config['formats'])}")
            print(f"   Include Chapters: {self.config['include_chapters']}")
            print(f"   Include Appendices: {'Yes' if self.config['include_appendices'] else 'No'}")
            print(f"   Custom CSS: {'Yes' if self.config['custom_css'] else 'No'}")

        return Confirm.ask("\nProceed with build", default=True)

    def create_combined_markdown(self, output_dir):
        """Create combined markdown with interactive progress."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        temp_file = output_dir / "complete-book.md"

        if RICH_AVAILABLE:
            self.console.print("\n📝 [yellow]Creating combined markdown...[/yellow]")
        else:
            print("\n📝 Creating combined markdown...")

        # Front matter
        front_matter = f"""---
title: "{self.config['title']}"
subtitle: "{self.config['subtitle']}"
author: "{self.config['author']}"
date: "{self.config['date']}"
documentclass: book
geometry: margin=1in
fontsize: 11pt
linestretch: 1.2
toc: true
toc-depth: 2
numbersections: true
---

# {self.config['title']}
## {self.config['subtitle']}

**Author:** {self.config['author']}
**Publication Date:** {self.config['date']}
**Format:** Multi-platform (EPUB, PDF, Web)

---

"""

        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(front_matter)

            # Add chapters
            chapter_files = sorted(self.chapters_dir.glob("*.md"))

            if self.config["include_chapters"] == "all":
                selected_chapters = list(range(len(chapter_files)))
            else:
                selected_chapters = self.config["include_chapters"]

            if RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=self.console
                ) as progress:

                    chapter_task = progress.add_task("Adding chapters...", total=len(selected_chapters))

                    for i, chapter_idx in enumerate(selected_chapters):
                        if chapter_idx < len(chapter_files):
                            chapter_file = chapter_files[chapter_idx]
                            progress.update(chapter_task, description=f"Adding {chapter_file.name}...")

                            f.write("\\newpage\n\n")
                            f.write(chapter_file.read_text(encoding='utf-8'))
                            f.write("\n\n")

                        progress.advance(chapter_task)

                    # Add appendices
                    if self.config["include_appendices"]:
                        appendix_files = list(self.appendices_dir.glob("*.md"))
                        appendix_task = progress.add_task("Adding appendices...", total=len(appendix_files))

                        for appendix_file in appendix_files:
                            progress.update(appendix_task, description=f"Adding {appendix_file.name}...")

                            f.write("\\newpage\n\n")
                            f.write(appendix_file.read_text(encoding='utf-8'))
                            f.write("\n\n")

                            progress.advance(appendix_task)
            else:
                print("📚 Adding chapters...")
                for i, chapter_idx in enumerate(selected_chapters):
                    if chapter_idx < len(chapter_files):
                        chapter_file = chapter_files[chapter_idx]
                        print(f"   ✅ Adding {chapter_file.name}")

                        f.write("\\newpage\n\n")
                        f.write(chapter_file.read_text(encoding='utf-8'))
                        f.write("\n\n")

                if self.config["include_appendices"]:
                    print("📋 Adding appendices...")
                    for appendix_file in self.appendices_dir.glob("*.md"):
                        print(f"   ✅ Adding {appendix_file.name}")

                        f.write("\\newpage\n\n")
                        f.write(appendix_file.read_text(encoding='utf-8'))
                        f.write("\n\n")

        return temp_file

    def build_formats(self, temp_file, output_dir):
        """Build all selected formats with detailed progress."""
        output_dir = Path(output_dir)
        generated_files = []

        if RICH_AVAILABLE:
            self.console.print("\n🔨 [yellow]Building e-book formats...[/yellow]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:

                build_task = progress.add_task("Building formats...", total=len(self.config["formats"]))

                for fmt in self.config["formats"]:
                    progress.update(build_task, description=f"Generating {fmt.upper()}...")

                    try:
                        if fmt == "epub":
                            file_path = self.generate_epub(temp_file, output_dir, progress)
                        elif fmt == "pdf":
                            file_path = self.generate_pdf(temp_file, output_dir, progress)
                        elif fmt == "html":
                            file_path = self.generate_html(temp_file, output_dir, progress)
                        else:
                            continue

                        generated_files.append((fmt.upper(), file_path))
                        progress.update(build_task, description=f"✅ {fmt.upper()} complete")

                    except subprocess.CalledProcessError as e:
                        progress.update(build_task, description=f"❌ {fmt.upper()} failed")
                        self.console.print(f"❌ [red]Error generating {fmt}: {e}[/red]")

                    progress.advance(build_task)
        else:
            print("\n🔨 Building e-book formats...")

            for fmt in self.config["formats"]:
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

        return generated_files

    def generate_epub(self, temp_file, output_dir, progress=None):
        """Generate EPUB format."""
        epub_file = output_dir / f"{self.config['title'].lower().replace(' ', '-')}.epub"

        cmd = [
            "pandoc", str(temp_file),
            "--to", "epub3",
            "--output", str(epub_file),
            "--metadata", f"title={self.config['title']}",
            "--metadata", f"author={self.config['author']}",
            "--metadata", f"date={self.config['date']}",
            "--toc",
            "--toc-depth=2"
        ]

        # Add cover image if it exists
        cover_image = self.project_dir / "assets" / "cover.png"
        if cover_image.exists():
            cmd.extend(["--epub-cover-image", str(cover_image)])

        subprocess.run(cmd, check=True)
        return epub_file

    def generate_pdf(self, temp_file, output_dir, progress=None):
        """Generate PDF format."""
        pdf_file = output_dir / f"{self.config['title'].lower().replace(' ', '-')}.pdf"

        # Prefer wkhtmltopdf to avoid LaTeX Unicode issues
        if shutil.which("wkhtmltopdf"):
            pdf_engine = "wkhtmltopdf"
            extra_args = []
        elif shutil.which("pdflatex"):
            pdf_engine = "pdflatex"
            # Add Unicode support for LaTeX
            extra_args = [
                "--variable", "geometry:margin=1in",
                "--variable", "fontsize:11pt",
                "--variable", "linestretch:1.2",
                "--pdf-engine-opt=-shell-escape"
            ]
        else:
            raise RuntimeError("No PDF engine available. Install wkhtmltopdf or pdflatex.")

        cmd = [
            "pandoc", str(temp_file),
            "--to", "pdf",
            "--pdf-engine", pdf_engine,
            "--output", str(pdf_file),
            "--metadata", f"title={self.config['title']}",
            "--metadata", f"author={self.config['author']}",
            "--metadata", f"date={self.config['date']}",
            "--toc",
            "--toc-depth=2"
        ] + extra_args

        subprocess.run(cmd, check=True)
        return pdf_file

    def generate_html(self, temp_file, output_dir, progress=None):
        """Generate HTML format."""
        html_file = output_dir / f"{self.config['title'].lower().replace(' ', '-')}.html"

        cmd = [
            "pandoc", str(temp_file),
            "--to", "html5",
            "--output", str(html_file),
            "--metadata", f"title={self.config['title']}",
            "--metadata", f"author={self.config['author']}",
            "--metadata", f"date={self.config['date']}",
            "--toc",
            "--toc-depth=2",
            "--standalone",
            "--self-contained"  # Embed CSS instead of referencing
        ]

        # Add CSS if available and requested
        if self.config["custom_css"]:
            css_file = self.pandoc_dir / "style.css"
            if css_file.exists():
                cmd.extend(["--css", str(css_file)])

        subprocess.run(cmd, check=True)
        return html_file

    def show_results(self, generated_files, temp_file):
        """Show build results with statistics."""
        if RICH_AVAILABLE:
            self.console.print("\n🎉 [bold green]Build Complete![/bold green]")

            # Results table
            results_table = Table(title="Generated Files")
            results_table.add_column("Format", style="cyan")
            results_table.add_column("File", style="white")
            results_table.add_column("Size", justify="right", style="green")

            for fmt, file_path in generated_files:
                size = file_path.stat().st_size
                size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                results_table.add_row(fmt, str(file_path.name), size_str)

            self.console.print(results_table)

            # Word count and statistics
            try:
                content = temp_file.read_text(encoding='utf-8')
                word_count = len(content.split())
                char_count = len(content)

                stats_table = Table(title="Content Statistics")
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", justify="right", style="green")

                stats_table.add_row("Word Count", f"{word_count:,}")
                stats_table.add_row("Character Count", f"{char_count:,}")
                stats_table.add_row("Target Progress", f"{(word_count/self.config['word_count_target']*100):.1f}%")
                stats_table.add_row("Estimated Pages", f"{word_count//250}")  # ~250 words per page

                self.console.print(stats_table)

            except Exception:
                pass

        else:
            print("\n🎉 Build Complete!")
            print("📁 Generated files:")
            for fmt, file_path in generated_files:
                size = file_path.stat().st_size
                size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                print(f"   📄 {fmt}: {file_path.name} ({size_str})")

            try:
                content = temp_file.read_text(encoding='utf-8')
                word_count = len(content.split())
                print(f"\n📊 Word count: {word_count:,} words")
                print(f"📊 Target progress: {(word_count/self.config['word_count_target']*100):.1f}%")
                print(f"📊 Estimated pages: {word_count//250}")
            except Exception:
                pass

    def save_configuration(self):
        """Save current configuration for future use."""
        config_file = self.pandoc_dir / "build_config.json"

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)

            if RICH_AVAILABLE:
                self.console.print(f"💾 [green]Configuration saved to {config_file}[/green]")
            else:
                print(f"💾 Configuration saved to {config_file}")

        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"⚠️ [yellow]Could not save configuration: {e}[/yellow]")
            else:
                print(f"⚠️ Could not save configuration: {e}")

    def load_configuration(self):
        """Load saved configuration."""
        config_file = self.pandoc_dir / "build_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)

                # Merge with defaults
                self.config.update(saved_config)

                if RICH_AVAILABLE:
                    self.console.print(f"📖 [green]Configuration loaded from {config_file}[/green]")
                else:
                    print(f"📖 Configuration loaded from {config_file}")

                return True

            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"⚠️ [yellow]Could not load configuration: {e}[/yellow]")
                else:
                    print(f"⚠️ Could not load configuration: {e}")

        return False

    def show_help(self):
        """Display help information."""
        if RICH_AVAILABLE:
            help_panel = Panel.fit("""
[bold cyan]📚 Interactive E-Book Builder Help[/bold cyan]

[yellow]Getting Started:[/yellow]
• First time? Start with option [bold]1[/bold] to analyze your content
• Configure your book with option [bold]2[/bold] (title, author, formats)
• Preview your settings with option [bold]3[/bold] before building
• Use option [bold]7[/bold] for quick builds with current settings

[yellow]Build Options:[/yellow]
• [bold]EPUB[/bold]: Best for e-readers (Kindle, tablets)
• [bold]PDF[/bold]: Best for printing and sharing
• [bold]HTML[/bold]: Best for web publishing

[yellow]Tips:[/yellow]
• Save configurations with option [bold]6[/bold] for reuse
• Use selective chapter building for drafts or specific sections
• Check word count progress against your target goals

[yellow]Requirements:[/yellow]
• Pandoc must be installed for document conversion
• LaTeX or wkhtmltopdf for PDF generation
• Content must be in [bold]ebook/chapters/[/bold] and [bold]ebook/appendices/[/bold]

[dim]Press any key to continue...[/dim]
            """, border_style="blue")
            self.console.print(help_panel)
        else:
            print("\n" + "="*60)
            print("📚 Interactive E-Book Builder Help")
            print("="*60)
            print("\nGetting Started:")
            print("• First time? Start with option 1 to analyze your content")
            print("• Configure your book with option 2 (title, author, formats)")
            print("• Preview your settings with option 3 before building")
            print("• Use option 7 for quick builds with current settings")
            print("\nBuild Options:")
            print("• EPUB: Best for e-readers (Kindle, tablets)")
            print("• PDF: Best for printing and sharing")
            print("• HTML: Best for web publishing")
            print("\nTips:")
            print("• Save configurations with option 6 for reuse")
            print("• Use selective chapter building for drafts")
            print("• Check word count progress against target goals")
            print("\nRequirements:")
            print("• Pandoc must be installed for document conversion")
            print("• LaTeX or wkhtmltopdf for PDF generation")
            print("• Content in ebook/chapters/ and ebook/appendices/")
            print("\nPress Enter to continue...")

        input()

    def main_menu(self):
        """Main interactive menu."""
        while True:
            if RICH_AVAILABLE:
                self.console.print("\n📋 [bold cyan]Main Menu[/bold cyan]")
                self.console.print("[dim]Type 'help' or 'h' for detailed assistance[/dim]")

                menu_table = Table()
                menu_table.add_column("Option", style="cyan", justify="center")
                menu_table.add_column("Description", style="white")
                menu_table.add_column("Best For", style="dim")

                menu_options = [
                    ("1", "Analyze content and show statistics", "First-time users, content review"),
                    ("2", "Configure build settings", "Customizing title, author, formats"),
                    ("3", "Preview build configuration", "Checking settings before build"),
                    ("4", "Start build process", "Full interactive build with preview"),
                    ("5", "Load saved configuration", "Reusing previous settings"),
                    ("6", "Save current configuration", "Storing settings for future use"),
                    ("7", "Quick build (use current settings)", "Fast build with defaults"),
                    ("H", "Show detailed help", "New users, troubleshooting"),
                    ("Q", "Quit", "Exit the builder")
                ]

                for option, description, best_for in menu_options:
                    menu_table.add_row(option, description, best_for)

                self.console.print(menu_table)
            else:
                print("\n📋 Main Menu:")
                print("   Type 'help' or 'h' for detailed assistance")
                print("")
                print("   1. Analyze content and show statistics")
                print("   2. Configure build settings")
                print("   3. Preview build configuration")
                print("   4. Start build process")
                print("   5. Load saved configuration")
                print("   6. Save current configuration")
                print("   7. Quick build (use current settings)")
                print("   H. Show detailed help")
                print("   Q. Quit")

            choice = Prompt.ask("Select option (or 'help' for assistance)", default="7").lower()

            if choice == "1":
                self.analyze_content()
            elif choice == "2":
                self.interactive_configuration()
            elif choice == "3":
                self.preview_build()
            elif choice == "4":
                self.build_process()
            elif choice == "5":
                self.load_configuration()
            elif choice == "6":
                self.save_configuration()
            elif choice == "7":
                self.quick_build()
            elif choice in ["h", "help"]:
                self.show_help()
            elif choice in ["q", "quit", "exit"]:
                if RICH_AVAILABLE:
                    self.console.print("👋 [cyan]Thank you for using the Interactive E-Book Builder![/cyan]")
                    self.console.print("[dim]💡 Tip: Use './launch.sh --build' to start quickly next time[/dim]")
                else:
                    print("👋 Thank you for using the Interactive E-Book Builder!")
                    print("💡 Tip: Use './launch.sh --build' to start quickly next time")
                break
            else:
                if RICH_AVAILABLE:
                    self.console.print(f"❌ [red]Invalid option '{choice}'. Please try again or type 'help' for assistance.[/red]")
                else:
                    print(f"❌ Invalid option '{choice}'. Please try again or type 'help' for assistance.")

    def build_process(self):
        """Full interactive build process."""
        if not self.check_environment():
            return

        if not self.preview_build():
            return

        # Create combined markdown
        temp_file = self.create_combined_markdown(self.config["output_dir"])

        # Build formats
        generated_files = self.build_formats(temp_file, self.config["output_dir"])

        # Show results
        self.show_results(generated_files, temp_file)

        # Open output directory option
        if Confirm.ask("\nOpen output directory", default=True):
            self.open_output_directory()

    def quick_build(self):
        """Quick build with current settings."""
        if not self.check_environment():
            return

        if RICH_AVAILABLE:
            self.console.print("\n🚀 [yellow]Quick Build Starting...[/yellow]")
            self.console.print("[dim]Using current configuration without prompts[/dim]")
        else:
            print("\n🚀 Quick Build Starting...")
            print("Using current configuration without prompts")

        # Show what will be built
        if RICH_AVAILABLE:
            self.console.print(f"📚 Building: [bold]{self.config['title']}[/bold]")
            self.console.print(f"📄 Formats: {', '.join(self.config['formats'])}")
            self.console.print(f"📁 Output: {self.config['output_dir']}")
        else:
            print(f"📚 Building: {self.config['title']}")
            print(f"📄 Formats: {', '.join(self.config['formats'])}")
            print(f"📁 Output: {self.config['output_dir']}")

        # Create combined markdown
        temp_file = self.create_combined_markdown(self.config["output_dir"])

        # Build formats
        generated_files = self.build_formats(temp_file, self.config["output_dir"])

        # Show results
        self.show_results(generated_files, temp_file)

        # Ask if user wants to open the output directory
        if generated_files and Confirm.ask("\n📂 Open output directory to view your e-books", default=True):
            self.open_output_directory()

    def open_output_directory(self):
        """Open the output directory in file manager."""
        output_path = Path(self.config["output_dir"])

        try:
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(output_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(output_path)])

            if RICH_AVAILABLE:
                self.console.print(f"📂 [green]Opened {output_path}[/green]")
            else:
                print(f"📂 Opened {output_path}")

        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"⚠️ [yellow]Could not open directory: {e}[/yellow]")
            else:
                print(f"⚠️ Could not open directory: {e}")

    def show_welcome_guide(self):
        """Show welcome guide for first-time users."""
        if RICH_AVAILABLE:
            welcome_panel = Panel.fit("""
[bold cyan]🎉 Welcome to the Interactive E-Book Builder![/bold cyan]

[yellow]📚 What this tool does:[/yellow]
• Converts your markdown chapters into professional e-books
• Generates EPUB (e-readers), PDF (printing), and HTML (web) formats
• Provides interactive configuration and progress tracking

[yellow]🚀 Quick Start Guide:[/yellow]
• [bold]First time?[/bold] Choose option [bold]1[/bold] to analyze your content
• [bold]Ready to build?[/bold] Choose option [bold]7[/bold] for quick build with defaults
• [bold]Want to customize?[/bold] Choose option [bold]2[/bold] to configure settings

[yellow]💡 Pro Tips:[/yellow]
• Save your settings with option [bold]6[/bold] to reuse later
• Use option [bold]4[/bold] for guided builds with previews
• Type [bold]'help'[/bold] at any menu for detailed assistance

[dim]Ready to transform your content into professional e-books? Let's go![/dim]
            """, border_style="green")
            self.console.print(welcome_panel)
        else:
            print("\n" + "="*70)
            print("🎉 Welcome to the Interactive E-Book Builder!")
            print("="*70)
            print("\n📚 What this tool does:")
            print("• Converts your markdown chapters into professional e-books")
            print("• Generates EPUB (e-readers), PDF (printing), and HTML (web) formats")
            print("• Provides interactive configuration and progress tracking")
            print("\n🚀 Quick Start Guide:")
            print("• First time? Choose option 1 to analyze your content")
            print("• Ready to build? Choose option 7 for quick build with defaults")
            print("• Want to customize? Choose option 2 to configure settings")
            print("\n💡 Pro Tips:")
            print("• Save your settings with option 6 to reuse later")
            print("• Use option 4 for guided builds with previews")
            print("• Type 'help' at any menu for detailed assistance")
            print("\nReady to transform your content into professional e-books? Let's go!")

        input("\nPress Enter to continue...")

    def run(self):
        """Main entry point."""
        self.print_banner()

        # Check if this is first time (no saved config)
        config_file = self.pandoc_dir / "build_config.json"
        is_first_time = not config_file.exists()

        # Try to load saved configuration
        config_loaded = self.load_configuration()

        # Show welcome guide for first-time users
        if is_first_time:
            self.show_welcome_guide()
        elif RICH_AVAILABLE:
            self.console.print("[dim]💡 Type 'help' at any menu for assistance, or press Enter to continue...[/dim]")
            input()

        # Run main menu
        self.main_menu()

def main():
    """Main entry point for the interactive builder."""
    builder = InteractiveEBookBuilder()
    builder.run()

if __name__ == "__main__":
    main()