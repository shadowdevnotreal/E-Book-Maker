# Appendix A: Installation Guide

Complete installation instructions for all platforms.

## System Requirements

### Minimum Requirements

- **Python**: 3.7 or higher
- **RAM**: 2GB minimum
- **Storage**: 500MB for application + dependencies
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Recommended Tools

- **Pandoc**: Required for document conversion
- **wkhtmltopdf**: Recommended for PDF generation
- **LaTeX (MiKTeX/TeX Live)**: Optional for advanced PDF formatting

## Installation Steps

### Windows

```batch
# Install Python from python.org
# Install Pandoc
choco install pandoc

# Install wkhtmltopdf
choco install wkhtmltopdf

# Install MiKTeX (optional)
choco install miktex

# Run E-Book Maker
start.bat
```

### macOS

```bash
# Install via Homebrew
brew install python3 pandoc wkhtmltopdf

# Optional: Install LaTeX
brew install --cask mactex

# Run E-Book Maker
./start.sh
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 pandoc wkhtmltopdf

# Optional: Install LaTeX
sudo apt install texlive-latex-base

# Run E-Book Maker
./start.sh
```

