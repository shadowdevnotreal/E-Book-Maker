# E-Book Maker - Setup Guide

Complete installation guide for **Windows**, **Linux**, and **macOS**.

---

## Quick Start

### Step 1: Verify Setup
Run the appropriate verification script for your platform:

**Windows (PowerShell):**
```powershell
.\scripts\verify-setup-windows.ps1
```

**Linux/Mac (bash):**
```bash
bash scripts/verify-setup-linux.sh
```

This will check all dependencies and tell you what's missing.

---

## Required Dependencies

### 1. Python 3.8+
**All platforms:** Required for running the application.

- **Windows:** Download from [python.org](https://www.python.org/downloads/)
  - ✓ Check "Add Python to PATH" during installation
- **Linux:** `sudo apt-get install python3 python3-pip` (Ubuntu/Debian)
- **Mac:** `brew install python3`

### 2. Pandoc
**Required** for document conversion (markdown → PDF/EPUB/HTML/DOCX).

- **Windows:** Download from [pandoc.org](https://pandoc.org/installing.html)
  - Install the `.msi` package
  - Verify: `pandoc --version` in Command Prompt
- **Linux:** `sudo apt-get install pandoc`
- **Mac:** `brew install pandoc`

### 3. PDF Engines (At Least One Required)

You need **at least ONE** of these for PDF generation:

#### Option A: pdflatex (Recommended - Best quality)
- **Windows:** Install [MiKTeX](https://miktex.org/download)
  - Choose "Install MiKTeX for all users"
  - Add to PATH during installation
  - Verify: `pdflatex --version` in Command Prompt
- **Linux:** `sudo apt-get install texlive-latex-base texlive-fonts-recommended`
- **Mac:** `brew install --cask mactex-no-gui`

#### Option B: wkhtmltopdf (Good for HTML-based PDFs)
- **Windows:** Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
  - Choose Windows installer
  - Add to PATH: `C:\Program Files\wkhtmltopdf\bin`
  - Verify: `wkhtmltopdf --version` in Command Prompt
- **Linux:** `sudo apt-get install wkhtmltopdf`
- **Mac:** `brew install wkhtmltopdf`

#### Option C: weasyprint (Python-based)
- **All platforms:** Auto-installed with `pip install -r requirements.txt`
  - No system dependencies needed on Windows/Mac
  - Linux may require: `sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangocairo-1.0-0`

---

## Python Package Installation

After installing system dependencies:

```bash
# Install all required Python packages
pip install -r requirements.txt

# Windows users: use this if pip command doesn't work
python -m pip install -r requirements.txt
```

**Required packages:**
- `flask` - Web server
- `Pillow` - Image processing (imports as PIL)
- `reportlab` - PDF generation for covers
- `python-docx` - DOCX file handling (imports as docx)
- `PyPDF2` - PDF manipulation
- `PyMuPDF` - PDF processing (imports as fitz)
- `qrcode` - QR code generation
- `weasyprint` - Python-based PDF engine
- `groq` - AI assistant integration

---

## Windows-Specific Setup Issues

### Problem: "PDF engines not found" on Windows

**Cause:** PATH not updated or terminal needs restart.

**Solutions:**

1. **Restart your terminal** after installing software
   - Close Command Prompt/PowerShell completely
   - Open a new window
   - Try again

2. **Manually verify PATH:**
   ```powershell
   # Check if executables are accessible
   where pandoc
   where pdflatex
   where wkhtmltopdf
   ```

3. **Manually add to PATH** (if not found):
   - Open System Properties → Environment Variables
   - Edit "Path" under System Variables
   - Add these directories (adjust based on your installation):
     - `C:\Program Files\Pandoc`
     - `C:\Program Files\MiKTeX\miktex\bin\x64`
     - `C:\Program Files\wkhtmltopdf\bin`
   - Click OK and **restart terminal**

4. **Use PowerShell as Administrator:**
   - Right-click PowerShell → "Run as Administrator"
   - This ensures proper PATH access

---

## Verification

### Method 1: Run Verification Script

**Windows:**
```powershell
.\scripts\verify-setup-windows.ps1
```

**Linux/Mac:**
```bash
bash scripts/verify-setup-linux.sh
```

### Method 2: Manual Checks

```bash
# Check Python
python --version

# Check pip
python -m pip --version

# Check Pandoc
pandoc --version

# Check PDF engines (at least one should work)
pdflatex --version
wkhtmltopdf --version
python -c "import weasyprint; print(weasyprint.__version__)"
```

---

## Running the Application

Once all dependencies are verified:

```bash
# Start the server
python server.py
```

The application will:
1. Check all dependencies
2. Show which PDF engines are available
3. Open your browser to `http://127.0.0.1:5000`

**Expected startup output:**
```
============================================================
E-Book Maker - Web Interface
Platform: Windows 10
============================================================

Checking dependencies...
  Pandoc:       ✓ Found
  wkhtmltopdf:  ✓ Found
  pdflatex:     ✓ Found
  weasyprint:   ○ Not found (optional)

✓ PDF engine available: pdflatex

✓ AI Assistant: Not configured
  Configure in Settings to enable AI features
============================================================
Starting server on http://127.0.0.1:5000
Press Ctrl+C to stop the server
============================================================
```

---

## Troubleshooting

### Issue: "No PDF engines found" but I installed them

1. **Restart your terminal/IDE completely**
2. **Check PATH manually:**
   ```powershell
   # Windows
   $env:Path -split ';' | Select-String -Pattern "pdflatex|wkhtmltopdf|pandoc"
   ```
3. **Try running from a fresh terminal window**
4. **Verify installation:**
   - Open a NEW Command Prompt
   - Type `pdflatex --version`
   - If it shows "not recognized", the PATH is not set correctly

### Issue: Python can't find modules

```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Windows users: use this if pip doesn't work
python -m pip install -r requirements.txt --force-reinstall
```

### Issue: Permission errors on Windows

- Run PowerShell/Command Prompt as **Administrator**
- Or use a virtual environment:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate  # Windows
  pip install -r requirements.txt
  ```

---

## Platform-Specific Notes

### Windows
- **Always restart your terminal** after installing software
- Use Command Prompt or PowerShell (not Git Bash for setup)
- Install software "for all users" when possible
- MiKTeX and wkhtmltopdf must be manually added to PATH

### Linux
- Most tools available through package manager
- Ubuntu/Debian: `apt-get`
- Fedora/RHEL: `dnf` or `yum`
- May need `sudo` for system-wide installation

### macOS
- Use Homebrew for easiest installation: `brew install pandoc pdflatex wkhtmltopdf`
- Some packages may require Xcode Command Line Tools

---

## Minimal Installation

If you only need basic conversion:

1. **Python 3.8+**
2. **Pandoc**
3. **ONE PDF engine** (pdflatex recommended)
4. **Python packages** (requirements.txt)

This gives you:
- ✓ Markdown → PDF/EPUB/HTML/DOCX conversion
- ✓ Cover generation
- ✓ Watermarking
- ✗ AI features (requires Groq API key)

---

## Getting Help

If you encounter issues:

1. Run the verification script first
2. Check this guide's Troubleshooting section
3. Ensure PATH is correctly set (Windows especially)
4. Try from a fresh terminal window
5. Check that software is installed "for all users"

---

## Summary Checklist

- [ ] Python 3.8+ installed and in PATH
- [ ] pip installed and working
- [ ] Pandoc installed and in PATH
- [ ] At least ONE PDF engine installed (pdflatex/wkhtmltopdf/weasyprint)
- [ ] Python packages installed (`pip install -r requirements.txt`)
- [ ] Terminal restarted after installations
- [ ] Verification script shows all green checkmarks
- [ ] `python server.py` starts without errors
