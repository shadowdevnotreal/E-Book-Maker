#!/usr/bin/env python3
"""
Check if all dependencies are installed for E-Book Maker
"""

import sys

def check_python_packages():
    """Check if required Python packages are installed"""
    print("Checking Python packages...")
    packages = {
        'flask': 'Flask',
        'PIL': 'Pillow',
        'PyPDF2': 'PyPDF2',
        'reportlab': 'reportlab',
        'docx': 'python-docx',
        'fitz': 'PyMuPDF',
    }

    missing = []
    for module, package_name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} - MISSING")
            missing.append(package_name)

    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    return True


def check_system_tools():
    """Check if required system tools are installed"""
    print("\nChecking system tools...")
    import shutil
    import subprocess
    import os
    import platform

    # Get full PATH on Windows (venv may have truncated PATH)
    full_path = os.environ.get('PATH', '')
    if platform.system() == 'Windows':
        try:
            import winreg
            # Get system PATH
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
                system_path = winreg.QueryValueEx(key, 'Path')[0]
            # Get user PATH
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as key:
                    user_path = winreg.QueryValueEx(key, 'Path')[0]
            except:
                user_path = ''
            # Combine paths
            full_path = f"{system_path};{user_path}"
        except:
            pass  # Fall back to environment PATH

    def check_command(cmd):
        """Check if a command exists - more robust on Windows"""
        # First try shutil.which with full PATH
        if shutil.which(cmd, path=full_path):
            return True

        # Fallback: try to actually run the command with --version
        try:
            kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'timeout': 3,
                'env': {**os.environ, 'PATH': full_path}
            }
            if os.name == 'nt':
                kwargs['creationflags'] = 0x08000000  # CREATE_NO_WINDOW

            result = subprocess.run([cmd, '--version'], **kwargs)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    tools = {
        'pandoc': 'Required for document conversion',
        'wkhtmltopdf': 'Optional for better PDF generation',
        'pdflatex': 'Optional for advanced PDF formatting'
    }

    found = {}
    for tool, description in tools.items():
        installed = check_command(tool)
        status = "✓" if installed else "✗"
        found[tool] = installed
        print(f"  {status} {tool} - {description}")

    if not found['pandoc']:
        print("\n⚠ WARNING: Pandoc is required for document conversion!")
        print("Install: https://pandoc.org/installing.html")
        return False

    return True


def main():
    print("=" * 60)
    print("E-Book Maker - Dependency Check")
    print("=" * 60)
    print()

    python_ok = check_python_packages()
    system_ok = check_system_tools()

    print()
    print("=" * 60)
    if python_ok and system_ok:
        print("✓ All required dependencies are installed!")
        print("You can now run: python server.py")
    else:
        print("✗ Some dependencies are missing. Please install them.")
        sys.exit(1)
    print("=" * 60)


if __name__ == '__main__':
    main()
