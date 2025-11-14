# Changelog

All notable changes to the E-Book Maker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2025-10-30

### Fixed - Cross-Platform Compatibility (2025-10-30)

#### 🪟 Windows-Specific Fixes
- **Windows pip detection** (`start.bat`)
  - Changed from `pip --version` to `python -m pip --version`
  - Changed from `pip install` to `python -m pip install`
  - Works with Windows Python installations where `pip` command is not in PATH
  - Automatic pip installation via `python -m ensurepip --upgrade`
  - Fixes "pip not installed" error when pip is actually available via `python -m pip`

- **Windows executable detection** (`modules/conversion/converter.py`)
  - Added `_find_executable_cross_platform()` method for Windows/Linux/Mac compatibility
  - Searches common Windows directories:
    - `C:\Program Files\MiKTeX\miktex\bin\x64` (pdflatex)
    - `C:\Program Files\wkhtmltopdf\bin`
    - `C:\Users\{USER}\AppData\Local\Programs`
  - Automatically checks for `.exe` extensions on Windows
  - Fixes "No PDF engines found" error on Windows despite proper installation

- **Windows verification script improvements** (`scripts/verify-setup-windows.ps1`)
  - Added missing packages to check: weasyprint, PyMuPDF, groq, Werkzeug (was only checking 6, now checks all 9)
  - Fixed "pillow" to "Pillow" (correct package name with capital P)
  - Implemented proper import name mapping:
    - Pillow → PIL
    - python-docx → docx
    - PyMuPDF → fitz
    - PyPDF2 → PyPDF2
    - Werkzeug → werkzeug
  - Made weasyprint optional (server works with pdflatex/wkhtmltopdf)
  - Shows "NOT INSTALLED" instead of "MISSING" for optional packages
  - Only fails verification if REQUIRED packages are missing
  - Fixes false negatives where installed packages showed as MISSING

- **Windows startup script enhancements** (`start.bat`)
  - Changed from batch install to individual package installation
  - Uses `--quiet` and `--disable-pip-version-check` flags to suppress warnings
  - Installs each package separately with clear progress messages
  - Handles both standard Python and Anaconda environments seamlessly
  - Removed verification step that caused confusing error messages
  - No more "SOME DEPENDENCIES ARE MISSING!" false alarms
  - Server starts immediately after package installation
  - All 10 packages now auto-install: Flask, Pillow, reportlab, python-docx, PyPDF2, qrcode, PyMuPDF, weasyprint, groq, Werkzeug

#### 🐧 Linux-Specific Fixes
- **Linux verification script** (`scripts/verify-setup-linux.sh`)
  - Fixed package import name mapping:
    - "Pillow" → imports as "PIL" (was checking "pillow", causing false negative)
    - "PyMuPDF" → imports as "fitz"
    - "python-docx" → imports as "docx"
    - "PyPDF2" → imports as "PyPDF2"
    - "Werkzeug" → imports as "werkzeug"
  - Added ALL packages from requirements.txt: weasyprint, PyMuPDF, groq, Werkzeug
  - Made weasyprint optional (consistent with Windows behavior)
  - Shows "NOT INSTALLED" instead of "MISSING" for optional packages
  - Color-coded output with proper ANSI codes
  - Fixes "Pillow MISSING" error when Pillow is actually installed

#### 📄 Document Conversion Fixes
- **Inline bullet list formatting** (`text_normalizer.py`)
  - Fixed: Bullet points appearing on one line instead of proper list format
  - Problem: `compatible with: - Amazon Kindle - Apple Books - Google Play Books` (all on one line)
  - Solution: Detects inline list patterns and converts to proper markdown lists
  - Now produces:
    ```
    compatible with:
    - Amazon Kindle
    - Apple Books
    - Google Play Books
    ```
  - Works across ALL output formats (PDF, EPUB, HTML, DOCX, MD)
  - Handles both `•` bullet characters and inline `-` separators

- **Em-dash normalization across ALL formats**
  - Fixed: Em-dashes were still appearing in EPUB, HTML, DOCX outputs
  - Root cause: Normalization was only applied to PDF conversion
  - Solution: Added `normalize_content()` call to `convert_to_epub()`, `convert_to_html()`, `convert_to_docx()`
  - Converts em-dash (—) to double hyphen (--)
  - Converts en-dash (–) to single hyphen (-)
  - Handles smart quotes, ellipsis, bullets, and other Unicode characters

- **Disabled Pandoc smart typography**
  - Fixed: Pandoc was converting `---` to `—` AFTER normalization
  - Root cause: Pandoc's smart typography feature was enabled by default
  - Solution: Added `-smart` flag to all conversion methods
  - Prevents automatic conversion of `---` to em-dash, `"quotes"` to smart quotes, etc.
  - Ensures clean ASCII output in all formats (EPUB, PDF, HTML, DOCX, Markdown)

- **LaTeX header file not found**
  - Fixed: LaTeX headers weren't being injected properly for page numbering
  - Root cause: Passing content directly via `-H` flag instead of file path
  - Solution: Create temporary LaTeX header file and pass path to Pandoc
  - Fixes "File not found in resource path" error

#### 🎨 Cover Generation Fixes
- **PDF cover dimensions for KDP compliance** (`cover_generator.py`)
  - Fixed: Covers were 12.22" × 9.00" instead of required 18.33" × 11.25"
  - Root cause: Using `ALT_PAPERBACK_WIDTH/HEIGHT` constants instead of `PAPERBACK_WIDTH/HEIGHT`
  - Solution: Changed lines 478, 484 in `generate_cover()` to use correct constants
  - Paperback: 18.33" × 11.25" (5499 × 3375 px @ 300 DPI)
  - Hardback: 23.00" × 11.50" (6900 × 3450 px @ 300 DPI)

- **Cover converter hardback dimension consistency** (`cover_generator.py` line 706)
  - Fixed: `convert_cover()` was using ALT_HARDBACK dimensions (15.5" × 9.5")
  - Issue: Inconsistent with `generate_cover()` which uses standard HARDBACK dimensions (23" × 11.5")
  - Solution: Changed line 706 to use `HARDBACK_WIDTH/HEIGHT` instead of `ALT_HARDBACK_WIDTH/HEIGHT`
  - Ensures consistent hardback cover dimensions across both generation and conversion

#### 💧 Watermarking Fixes
- **Watermark position calculations**
  - Fixed: Top-right, bottom-left, bottom-right positions were not working correctly
  - Root cause: Not accounting for text width and logo dimensions in position calculation
  - Solution: Rewrote position calculation logic (lines 192-221 in `watermarker.py`)
  - Dynamic calculation based on:
    - Text width using `can.stringWidth()`
    - Logo dimensions
    - Page dimensions
    - Proper margin calculations for all 5 positions

### Added - Cross-Platform Features (2025-10-30)

#### 🚀 Startup Scripts with Auto-Install
- **start.bat** - Windows one-command startup
  - Checks Python installation
  - Checks/installs pip using `python -m pip`
  - Auto-installs all requirements.txt dependencies
  - Runs verification script
  - Starts Flask server
  - Error handling with pause on exit

- **start.sh** - Linux/Mac one-command startup
  - Detects python3/python and pip3/pip automatically
  - Auto-installs all requirements.txt dependencies
  - Runs verification script
  - Starts Flask server
  - Color-coded output with ANSI codes

#### 🔍 Verification Scripts
- **scripts/verify-setup-windows.ps1** - PowerShell verification
  - Checks Python, pip, Pandoc, PDF engines
  - Checks ALL Python packages from requirements.txt
  - Color-coded output (GREEN=found, RED=missing, YELLOW=optional)
  - Platform-specific installation instructions

- **scripts/verify-setup-linux.sh** - Bash verification
  - Same functionality as Windows script
  - ANSI color codes for terminal output
  - Made executable with proper shebang
  - Checks all dependencies and shows installation commands

#### 📊 Startup Diagnostics
- **server.py** - Real-time dependency checking
  - Shows platform (Windows/Linux/Mac)
  - Displays status of each dependency (Pandoc, wkhtmltopdf, pdflatex, weasyprint)
  - ✓ Found / ✗ NOT FOUND / ○ Not found (optional) indicators
  - Warns if no PDF engines available
  - Shows which PDF engine will be used for conversions

#### 🔄 PDF Engine Fallback System
- **modules/conversion/converter.py** - Intelligent engine selection
  - Tries all available engines in priority order: pdflatex → weasyprint → wkhtmltopdf
  - Loop continues until one succeeds
  - Clear error messages for each attempt
  - Only fails if ALL engines fail
  - Eliminates "No PDF engines found" errors when engines are actually available

### Changed - Cross-Platform Improvements (2025-10-30)

#### 📦 Dependencies
- **requirements.txt** - Added Python-based PDF engine
  - Added `weasyprint>=60.0` - Python-based PDF engine (no system install needed)
  - Added `qrcode>=7.4.0` - QR code generation for covers/watermarks
  - Added `groq>=0.4.0` - AI assistant integration (already in use)
  - Note: weasyprint provides fallback PDF generation without requiring system tools

#### 📚 Documentation
- **README.md** - Updated for cross-platform setup
  - Quick Start section with `start.bat` and `start.sh` commands
  - Updated Python package list (now includes weasyprint, qrcode, groq)
  - Updated Core Technologies section with all dependencies
  - Python version updated from 3.7+ to 3.8+

- **SETUP.md** - Comprehensive cross-platform guide
  - Added Windows pip workarounds (`python -m pip` commands)
  - Complete Python package list with import name mappings
  - weasyprint installation instructions for all platforms
  - Platform-specific troubleshooting sections
  - Windows PATH configuration guide

- **TODO.md** - Created project status and roadmap
  - Current project status (v2.1.0)
  - Completed features list
  - Planned features roadmap (v2.2.0, v2.3.0, v3.0.0)
  - Known issues section
  - Technical debt tracking
  - Testing status (36/36 KDP compliance tests)

- **CHANGELOG.md** - Updated with cross-platform fixes (this section)

### Fixed - Original v2.1.0 Features (2025-10-28)

#### 🖼️ Cover Conversion UI Enhancement
- **Added missing text overlay controls** to Convert Cover form
  - Title input field for spine text
  - Author input field for spine text
  - Subtitle input field (optional)
  - "Add Text Overlay" checkbox with toggle functionality
  - "Add Barcode Safe Area" checkbox for KDP compliance
  - Backend already supported these features; UI now exposes them
  - Enables custom spine text when converting uploaded covers

#### 📋 Cover Page Requirements Banner
- **Added requirements info banner** to Covers page
  - Shows Python packages needed (Pillow, PyMuPDF) with auto-install note
  - Displays cover features overview (create, convert, spine text, barcode, 300 DPI)
  - Expandable "First Time Setup (Windows)" section with step-by-step instructions
  - Clear indication that `start.bat` automatically installs all dependencies
  - Link to Settings page for additional tools (Pandoc for document conversion)
  - Fully responsive design with gradient styling

### Added - Professional Publishing Features

#### 📄 Document Conversion Enhancements
- **Automatic Page Numbering** for PDF and DOCX outputs
  - Position control (header/footer, left/center/right)
  - Numbering style selection (Arabic, Roman uppercase/lowercase, Alphabet uppercase/lowercase)
  - Front matter support with different numbering styles (e.g., roman for preface, arabic for chapters)
  - LaTeX fancyhdr integration for PDF page numbers
  - Reference DOCX template with embedded page numbers
  - Full web interface controls for page numbering configuration

- **Folder Upload Support** for organized book structure
  - Web interface folder upload with `webkitdirectory` attribute
  - Automatic detection of `chapters/` and `appendixes/` folders
  - Alphabetical sorting within each folder category
  - Chapters processed first, then appendixes
  - Visual folder structure preview in web interface
  - Seamless integration matching CLI tool functionality

#### 🎨 Cover Generation Enhancements
- **PDF Input Support** for cover conversion
  - Load PDF files using PyMuPDF (fitz)
  - Automatic first-page extraction at 300 DPI
  - Convert PDF covers to KDP-compliant formats
  - Support for PDF, PNG, JPG, JPEG, BMP, GIF inputs

- **Barcode Safe Area** for paperback and hardback covers
  - KDP-compliant 2.0" × 1.2" white box (600 × 360 pixels at 300 DPI)
  - Positioned on lower-right of back cover
  - 0.25" clearance from trim edges and spine (75 pixels at 300 DPI)
  - Automatic calculation for both paperback and hardback formats
  - Thin border for visibility during design phase

- **Improved Spine Text**
  - Properly centered horizontally and vertically on spine
  - Vertical orientation (rotated 90 degrees)
  - Dynamic positioning based on spine width
  - Professional typography

- **Enhanced Print Quality**
  - All print covers (paperback/hardback) guaranteed 300 DPI
  - Optimized JPEG saving with progressive encoding
  - 4:4:4 chroma subsampling for best quality
  - Quality 95 JPEG compression

#### 🌐 Web Interface Improvements
- **Upload Mode Toggle** - Switch between individual files and folder uploads
- **Page Numbering Controls** - Comprehensive UI for configuring page numbers
- **Radio Button Styling** - Professional UI for upload mode selection
- **Folder File Preview** - Shows organized chapter/appendix structure before conversion
- **Cover Format Support** - Updated file type restrictions to accept PDFs

#### 📝 Infrastructure & Tooling
- **Page Numbering Module** (`modules/conversion/page_numbering.py`)
  - PageNumberingConfig class for managing all page numbering settings
  - LaTeX header generation for PDF output
  - Reference document path management for DOCX
  - Support for multiple numbering styles and positions

- **Reference DOCX Template** (`config/templates/reference-with-pagenumbers.docx`)
  - Pandoc reference document with embedded page numbers
  - Centered footer page numbering
  - Used automatically for all DOCX conversions

- **Setup Script** (`setup_reference_docx.py`)
  - Programmatic page number insertion using python-docx
  - Automated setup for DOCX page numbering template
  - PAGE field insertion for dynamic page numbers

### Changed

#### 📄 Conversion System
- **modules/conversion/converter.py**
  - Added `page_numbering_config` parameter to `__init__`
  - Enhanced `create_metadata()` to inject LaTeX headers for PDF
  - Updated `convert_to_docx()` to use reference document template
  - Improved `_ensure_blank_before_lists()` for better markdown parsing
  - Added Pandoc markdown extensions: `+definition_lists+fancy_lists+startnum`

#### 🎨 Cover Generator
- **modules/covers/cover_generator.py**
  - Added `_load_cover_image()` method for PDF and image loading
  - Updated `convert_cover()` to accept `add_barcode_area` parameter
  - Added `_add_barcode_safe_area()` method for KDP barcode positioning
  - Fixed spine text centering calculation
  - Improved aspect ratio preservation for all cover types
  - Enhanced error handling for unsupported file formats

#### 🌐 Server & API
- **server.py**
  - Added `cover` file type to allowed extensions (PDF, PNG, JPG, JPEG, BMP, GIF)
  - Updated `/api/convert` endpoint to handle folder uploads
  - Added folder structure detection (chapters/appendixes)
  - Integrated page numbering configuration builder
  - Enhanced `/api/convert-cover` endpoint with PDF support and barcode options
  - Added title, author, subtitle parameters to cover conversion

#### 🎨 Web Interface
- **web/templates/convert.html**
  - Added upload mode toggle (files vs folder)
  - Added folder input with webkitdirectory support
  - Added page numbering configuration section
  - Implemented JavaScript for folder file organization display
  - Added toggles for page numbering visibility
  - Enhanced form submission to include page numbering config

- **web/static/css/style.css**
  - Added radio button styling for upload modes
  - Added hover effects and active states
  - Consistent styling across all form controls

### Fixed

#### 🐛 Critical Bug Fixes
- **Aspect Ratio Preservation** - Fixed image squeezing/stretching in cover conversions
- **E-book Dimensions** - Corrected from landscape (2560×1600) to portrait (1600×2560)
- **Spine Text Positioning** - Fixed undefined `spine_x` variable in hardback covers
- **File Deletion Bug** - Removed dangerous `os.remove()` call that deleted original files
- **List Formatting** - Fixed markdown list conversion to DOCX with proper blank lines

### Dependencies

#### 🔧 New Required Dependencies
- **PyMuPDF (fitz)** - PDF file support for cover conversion
- **python-docx** - DOCX page number field insertion (already required)

#### 📦 Updated Requirements
- All existing dependencies remain the same
- PyMuPDF should be added to `requirements.txt`

### Documentation

#### 📚 Updated Documentation
- **README.md** - Updated with v2.1 features, new badges, and feature descriptions
- **CHANGELOG.md** - Created comprehensive changelog (this file)
- Inline documentation improvements across all modified modules

---

## [2.0.0] - 2025-10-23

### Added - Initial Release
- Universal document converter (9+ input formats, 5 output formats)
- KDP-compliant cover generation (e-book, paperback, hardback)
- Multi-format watermarking (PDF, HTML, DOCX, MD)
- Web interface with Flask
- CLI tools for all modules
- Text normalization and bullet point fixing
- Dynamic spine width calculator
- 100% Amazon KDP compliance (36/36 tests passed)
- Windows setup installers (Pandoc, wkhtmltopdf, MiKTeX)
- Comprehensive documentation and test reports

---

## Version History Summary

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| **2.1.0** | 2025-10-28 | Page numbering, folder uploads, PDF covers, barcode area |
| **2.0.0** | 2025-10-23 | Initial release with full KDP compliance |

---

## Upgrade Notes

### Upgrading from v2.0 to v2.1

#### Required Actions:
1. **Update Python Dependencies**
   ```bash
   pip install pymupdf  # For PDF cover support
   ```

2. **Generate Reference DOCX** (if using page numbering)
   ```bash
   python setup_reference_docx.py
   ```

#### Optional Actions:
- Clear browser cache for updated web interface
- Review new page numbering options in Advanced Options
- Try new folder upload mode for organized book projects

#### Breaking Changes:
- **None** - v2.1 is fully backward compatible with v2.0

---

## Roadmap

### Planned for v2.2
- MOBI support (direct Kindle format output)
- Batch cover processing
- Cover template library
- Enhanced watermarking options

### Planned for v3.0
- AI-powered cover design suggestions
- Direct KDP upload integration
- Cloud storage support
- Multi-user collaboration

---

## Contributors

**Development Team:**
- **Lead Developer**: Diatasso LLC Development Team
- **Testing**: Community Beta Testers
- **Documentation**: Technical Writing Team

**Special Thanks:**
- Amazon KDP Team for clear specifications
- Pandoc community for excellent documentation
- Python community for amazing libraries

---

## License

© 2025 Diatasso LLC. All Rights Reserved.

This software is proprietary. See [LICENSE](LICENSE) for details.

---

**For support, bug reports, or feature requests:**
- 🐛 GitHub Issues: https://github.com/shadowdevnotreal/E-Book-Maker/issues
- 💡 Discussions: https://github.com/shadowdevnotreal/E-Book-Maker/discussions
- 📧 Email: 43219706+shadowdevnotreal@users.noreply.github.com
