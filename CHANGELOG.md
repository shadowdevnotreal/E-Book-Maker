# Changelog

All notable changes to the E-Book Maker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2025-10-28

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
