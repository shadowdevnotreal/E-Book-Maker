#!/usr/bin/env python3
"""
E-Book Conversion Launcher
==========================

Universal launcher that auto-detects the operating system and runs the
appropriate platform-optimized e-book conversion script.

Supports:
- Windows (PowerShell)
- macOS (Bash with macOS optimizations)
- Linux (Bash with Linux optimizations)
- Python cross-platform fallback
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def detect_platform():
    """Detect the current platform and return appropriate script info."""
    system = platform.system().lower()

    if system == "windows":
        return {
            "name": "Windows",
            "script": "convert.ps1",
            "command": ["powershell", "-ExecutionPolicy", "Bypass", "-File"],
            "description": "PowerShell script with Windows integrations"
        }
    elif system == "darwin":  # macOS
        return {
            "name": "macOS",
            "script": "convert-macos.sh",
            "command": ["bash"],
            "description": "Bash script with macOS native integrations"
        }
    elif system == "linux":
        return {
            "name": "Linux",
            "script": "convert-linux.sh",
            "command": ["bash"],
            "description": "Bash script optimized for Linux distributions"
        }
    else:
        return {
            "name": "Unknown",
            "script": "convert.py",
            "command": ["python3"],
            "description": "Cross-platform Python fallback"
        }


def check_dependencies(platform_info):
    """Check if required dependencies are available."""
    missing = []

    if platform_info["name"] == "Windows":
        # Check for PowerShell
        if not shutil.which("powershell"):
            missing.append("PowerShell")
    else:
        # Check for bash
        if not shutil.which("bash"):
            missing.append("Bash")

    # Check for Python (always useful as fallback)
    if not shutil.which("python3") and not shutil.which("python"):
        missing.append("Python 3")

    # Check for Pandoc (core requirement)
    if not shutil.which("pandoc"):
        missing.append("Pandoc")

    return missing


def find_script_path(script_name):
    """Find the script in the current directory."""
    current_dir = Path.cwd()
    script_path = current_dir / script_name

    if script_path.exists():
        return script_path

    # If we're not in the pandoc directory, try looking there
    pandoc_dir = current_dir / "pandoc"
    if pandoc_dir.exists():
        script_path = pandoc_dir / script_name
        if script_path.exists():
            return script_path

    # Try parent directory's pandoc folder
    parent_pandoc = current_dir.parent / "pandoc"
    if parent_pandoc.exists():
        script_path = parent_pandoc / script_name
        if script_path.exists():
            return script_path

    return None


def print_banner():
    """Print a nice banner."""
    print("=" * 70)
    print("🚀 E-BOOK CONVERSION LAUNCHER")
    print("=" * 70)
    print("📚 Generate professional e-books from markdown")
    print("🔧 Platform-optimized for best experience")
    print("=" * 70)


def print_help():
    """Print help information."""
    print("\n📖 Available formats: EPUB, PDF, HTML")
    print("📁 Output directory: ./output/ (default)")
    print("\n🎯 Usage examples:")
    print("  python convert-launcher.py")
    print("  python convert-launcher.py --formats epub pdf")
    print("  python convert-launcher.py --output /path/to/output")
    print("  python convert-launcher.py --open")


def main():
    """Main launcher function."""
    print_banner()

    # Detect platform
    platform_info = detect_platform()
    print(f"🖥️  Detected Platform: {platform_info['name']}")
    print(f"📋 Script Type: {platform_info['description']}")
    print()

    # Check dependencies
    missing_deps = check_dependencies(platform_info)
    if missing_deps:
        print("⚠️  Warning: Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print()

        # If Pandoc is missing, that's critical
        if "Pandoc" in missing_deps:
            print("❌ Pandoc is required for e-book conversion.")
            print("📥 Installation instructions:")

            if platform_info["name"] == "Windows":
                print("   PowerShell: choco install pandoc")
                print("   Or download: https://pandoc.org/installing.html")
            elif platform_info["name"] == "macOS":
                print("   Homebrew: brew install pandoc")
            elif platform_info["name"] == "Linux":
                print("   Ubuntu/Debian: sudo apt install pandoc")
                print("   Fedora/CentOS: sudo dnf install pandoc")
                print("   Arch Linux: sudo pacman -S pandoc")
            else:
                print("   Visit: https://pandoc.org/installing.html")

            sys.exit(1)

        # Offer Python fallback if available
        if ("Python 3" not in missing_deps and
            platform_info["script"] != "convert.py"):
            print("🔄 Falling back to Python script...")
            platform_info = {
                "name": "Python Fallback",
                "script": "convert.py",
                "command": ["python3"],
                "description": "Cross-platform Python script"
            }

    # Find the script
    script_path = find_script_path(platform_info["script"])
    if not script_path:
        print(f"❌ Could not find script: {platform_info['script']}")
        print("   Searched in:")
        print("   - Current directory")
        print("   - ./pandoc/")
        print("   - ../pandoc/")

        # Try Python fallback as last resort
        if platform_info["script"] != "convert.py":
            print("\n🔄 Trying Python fallback...")
            python_script = find_script_path("convert.py")
            if python_script:
                platform_info = {
                    "name": "Python Fallback",
                    "script": "convert.py",
                    "command": ["python3"],
                    "description": "Cross-platform Python script"
                }
                script_path = python_script
            else:
                print("❌ Python fallback script not found either.")
                sys.exit(1)
        else:
            sys.exit(1)

    print(f"✅ Found script: {script_path}")
    print()

    # Show help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print_help()
        return

    # Run the platform-specific script
    try:
        print(f"🚀 Launching {platform_info['name']} e-book converter...")
        print("-" * 70)

        # Change to the script's directory for proper relative paths
        os.chdir(script_path.parent)

        if platform_info["script"].endswith(".py"):
            # For Python scripts, run directly
            subprocess.run([sys.executable, str(script_path.name)] + sys.argv[1:])
        else:
            # For shell scripts, use the appropriate command
            subprocess.run(platform_info["command"] + [str(script_path.name)] + sys.argv[1:])

    except KeyboardInterrupt:
        print("\n\n👋 E-book conversion cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running script: {e}")
        print("\n🔄 Trying Python fallback...")

        # Try Python fallback
        python_script = find_script_path("convert.py")
        if python_script and python_script != script_path:
            try:
                os.chdir(python_script.parent)
                subprocess.run([sys.executable, str(python_script.name)] + sys.argv[1:])
            except Exception as fallback_error:
                print(f"❌ Python fallback also failed: {fallback_error}")
                sys.exit(1)
        else:
            print("❌ Python fallback not available.")
            sys.exit(1)


if __name__ == "__main__":
    main()