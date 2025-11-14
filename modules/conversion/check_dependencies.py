#!/usr/bin/env python3
"""
Dependency Check Script for E-Book Builder
==========================================

Checks all required dependencies and provides installation instructions.
Run this before attempting to build e-books.
"""

import sys
import shutil
import platform
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

def check_dependencies():
    """Check all required dependencies."""

    if RICH_AVAILABLE:
        console = Console()
        console.print("\n[bold cyan]🔍 E-Book Builder Dependency Check[/bold cyan]\n")
    else:
        print("\n🔍 E-Book Builder Dependency Check\n")

    # Check dependencies
    dependencies = {
        "pandoc": {
            "required": True,
            "description": "Core document conversion tool",
            "found": bool(shutil.which("pandoc"))
        },
        "wkhtmltopdf": {
            "required": False,
            "description": "PDF generation (alternative to LaTeX)",
            "found": bool(shutil.which("wkhtmltopdf"))
        },
        "pdflatex": {
            "required": False,
            "description": "PDF generation (preferred, part of LaTeX)",
            "found": bool(shutil.which("pdflatex"))
        }
    }

    # Display results
    if RICH_AVAILABLE:
        table = Table(title="Dependency Status")
        table.add_column("Tool", style="cyan")
        table.add_column("Required", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Description", style="dim")

        for dep, info in dependencies.items():
            status = "✅ Found" if info["found"] else "❌ Missing"
            required = "Required" if info["required"] else "Optional"
            style = "green" if info["found"] else "red" if info["required"] else "yellow"

            table.add_row(
                dep,
                required,
                f"[{style}]{status}[/{style}]",
                info["description"]
            )

        console.print(table)
    else:
        print("Dependency Status:")
        print("-" * 60)
        for dep, info in dependencies.items():
            status = "✅ Found" if info["found"] else "❌ Missing"
            required = "Required" if info["required"] else "Optional"
            print(f"  {dep:15s} [{required:8s}] {status:12s} - {info['description']}")
        print("-" * 60)

    # Check if at least one PDF engine is available
    has_pdf_engine = dependencies["wkhtmltopdf"]["found"] or dependencies["pdflatex"]["found"]

    # Determine status
    all_critical_deps = dependencies["pandoc"]["found"]

    if not all_critical_deps:
        if RICH_AVAILABLE:
            console.print("\n[bold red]❌ Critical dependencies missing![/bold red]")
            console.print("\n[yellow]📥 Installation Instructions:[/yellow]\n")
        else:
            print("\n❌ Critical dependencies missing!")
            print("\n📥 Installation Instructions:\n")

        print_installation_instructions()
        return False

    if not has_pdf_engine:
        if RICH_AVAILABLE:
            console.print("\n[yellow]⚠️ Warning: No PDF generation engine found![/yellow]")
            console.print("[dim]You can still generate EPUB and HTML formats.[/dim]")
            console.print("[dim]Install wkhtmltopdf or LaTeX for PDF support.[/dim]")
        else:
            print("\n⚠️ Warning: No PDF generation engine found!")
            print("You can still generate EPUB and HTML formats.")
            print("Install wkhtmltopdf or LaTeX for PDF support.")
        print_installation_instructions()

    if all_critical_deps and has_pdf_engine:
        if RICH_AVAILABLE:
            console.print("\n[bold green]✅ All dependencies satisfied![/bold green]")
            console.print("[green]You can build e-books in all formats (EPUB, PDF, HTML).[/green]")
        else:
            print("\n✅ All dependencies satisfied!")
            print("You can build e-books in all formats (EPUB, PDF, HTML).")
        return True
    elif all_critical_deps:
        if RICH_AVAILABLE:
            console.print("\n[yellow]⚠️ Limited functionality available[/yellow]")
            console.print("[dim]EPUB and HTML formats available, PDF generation not available.[/dim]")
        else:
            print("\n⚠️ Limited functionality available")
            print("EPUB and HTML formats available, PDF generation not available.")
        return True

    return False

def print_installation_instructions():
    """Print platform-specific installation instructions."""
    system = platform.system().lower()

    instructions = {
        "windows": """
🪟 Windows Installation:

Using Chocolatey (Recommended):
  1. Install Chocolatey if not already installed:
     https://chocolatey.org/install

  2. Open PowerShell as Administrator and run:
     choco install pandoc wkhtmltopdf

Manual Installation:
  • Pandoc: https://pandoc.org/installing.html
  • wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
  • LaTeX (optional, for better PDF): https://miktex.org/download
""",
        "darwin": """
🍎 macOS Installation:

Using Homebrew (Recommended):
  brew install pandoc wkhtmltopdf

For better PDF generation (optional):
  brew install --cask mactex

Manual Installation:
  • Pandoc: https://pandoc.org/installing.html
  • wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
""",
        "linux": """
🐧 Linux Installation:

Ubuntu/Debian:
  sudo apt update
  sudo apt install pandoc wkhtmltopdf texlive-latex-base texlive-fonts-recommended

Fedora/CentOS/RHEL:
  sudo dnf install pandoc wkhtmltopdf texlive

Arch Linux:
  sudo pacman -S pandoc wkhtmltopdf-static texlive-core

Note: For full LaTeX support (better PDF formatting):
  sudo apt install texlive-latex-extra texlive-fonts-extra  # Debian/Ubuntu
  sudo dnf install texlive-scheme-full  # Fedora
"""
    }

    instructions_text = instructions.get(system, instructions["linux"])

    if RICH_AVAILABLE:
        console = Console()
        panel = Panel(instructions_text.strip(), title="Installation Guide", border_style="cyan")
        console.print(panel)
    else:
        print(instructions_text)

def main():
    """Main entry point."""
    success = check_dependencies()

    if success:
        if RICH_AVAILABLE:
            console = Console()
            console.print("\n[bold green]🚀 Ready to build e-books![/bold green]")
            console.print("\n[cyan]To build your e-book, run:[/cyan]")
            console.print("  [bold]python3 pandoc/convert.py[/bold]          # Quick build")
            console.print("  [bold]python3 pandoc/interactive_build.py[/bold]  # Interactive builder")
        else:
            print("\n🚀 Ready to build e-books!")
            print("\nTo build your e-book, run:")
            print("  python3 pandoc/convert.py          # Quick build")
            print("  python3 pandoc/interactive_build.py  # Interactive builder")
        sys.exit(0)
    else:
        if RICH_AVAILABLE:
            console = Console()
            console.print("\n[bold red]❌ Cannot build e-books until dependencies are installed.[/bold red]")
            console.print("[dim]Please follow the installation instructions above.[/dim]")
        else:
            print("\n❌ Cannot build e-books until dependencies are installed.")
            print("Please follow the installation instructions above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
