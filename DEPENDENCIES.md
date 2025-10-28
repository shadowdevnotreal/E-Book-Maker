# E-Book Maker - Dependencies Guide

## Automatic Installation

The startup scripts **automatically install ALL dependencies**:

### Windows
```batch
start.bat
```

### Linux/macOS
```bash
./start.sh
```

Both scripts will:
1. ✅ Create virtual environment (if needed)
2. ✅ Upgrade pip
3. ✅ Install ALL packages from `requirements.txt`
4. ✅ Start the server

---

## What Gets Installed

### Python Packages (Automatic)

These are **automatically installed** by `start.bat` / `start.sh`:

| Package | Version | Purpose |
|---------|---------|---------|
| **Flask** | ≥2.3.0 | Web framework for the UI |
| **Pillow** | ≥10.0.0 | Image processing for covers |
| **PyPDF2** | ≥3.0.0 | PDF reading/writing |
| **reportlab** | ≥4.0.0 | PDF watermark generation |
| **python-docx** | ≥0.8.11 | DOCX watermarking & page numbering |
| **PyMuPDF** | ≥1.23.0 | **PDF cover input support** (NEW v2.1!) |
| **Werkzeug** | ≥2.3.0 | HTTP utilities |

**Total:** 7 packages

---

## System Tools (Manual Installation)

These must be installed **separately** on your system:

### Required

**Pandoc** - Document conversion engine
- Windows: `choco install pandoc`
- macOS: `brew install pandoc`
- Linux: `sudo apt-get install pandoc`
- Download: https://pandoc.org/installing.html

### Optional (Recommended)

**wkhtmltopdf** - Better PDF generation
- Windows: `choco install wkhtmltopdf`
- macOS: `brew install wkhtmltopdf`
- Linux: `sudo apt-get install wkhtmltopdf`
- Download: https://wkhtmltopdf.org/downloads.html

**LaTeX** - Advanced PDF formatting (~500MB)
- Windows: https://miktex.org/download
- macOS: `brew install --cask mactex`
- Linux: `sudo apt-get install texlive-latex-base`

---

## Verification

### Check Python Packages

Run this to verify all Python packages:
```bash
python check_install.py
```

Should show:
```
✓ Flask
✓ Pillow
✓ PyPDF2
✓ reportlab
✓ python-docx
✓ PyMuPDF
```

### Check System Tools

The **Settings** page in the web interface shows:
- ✓ Pandoc (required)
- ✓ wkhtmltopdf (optional)
- ✓ LaTeX (optional)

---

## Features by Dependency

### With Python Packages Only

✅ Web interface
✅ Cover generation
✅ Cover conversion
✅ PDF watermarking (text + logo)
✅ HTML watermarking
✅ DOCX watermarking (header/footer)

### With Pandoc

✅ All above +
✅ Markdown → EPUB conversion
✅ Markdown → HTML conversion
✅ Multi-chapter books
✅ Table of contents

### With Pandoc + wkhtmltopdf

✅ All above +
✅ Markdown → PDF conversion
✅ Better PDF quality

### With Pandoc + LaTeX

✅ All above +
✅ Professional PDF formatting
✅ Advanced typography

---

## Troubleshooting

### "python-docx not installed"

**Solution:** Restart the server with `start.bat` or `./start.sh`

The startup scripts will automatically install it.

### "Pandoc not found"

**Solution:** Install Pandoc separately (see above)

### "pip install failed"

**Manual installation:**
```bash
# Windows
venv\Scripts\activate.bat
pip install Flask Pillow PyPDF2 reportlab python-docx PyMuPDF Werkzeug

# Linux/macOS
source venv/bin/activate
pip install Flask Pillow PyPDF2 reportlab python-docx PyMuPDF Werkzeug
```

### Check what's installed

```bash
pip list | grep -E "Flask|Pillow|PyPDF2|reportlab|python-docx|PyMuPDF|Werkzeug"
```

---

## Updates

If new dependencies are added in the future, just **restart** with `start.bat` / `start.sh` - they will be automatically installed!

---

## Quick Reference

**Start server (installs everything):**
- Windows: `start.bat`
- Linux/Mac: `./start.sh`

**Check installation:**
```bash
python check_install.py
```

**Manual install if needed:**
```bash
pip install -r requirements.txt
```

**Verify system tools:**
- Open web interface → Settings page
- Or run: `pandoc --version`, `wkhtmltopdf --version`

---

**Everything is automatic!** Just run the start script and all Python dependencies will be installed. 🚀
