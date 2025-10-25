# E-Book Maker - Quick Start Guide

Get up and running in 3 steps!

---

## Step 1: Install Dependencies

### Required: Python & Pandoc

**Windows:**
```batch
# Install Python from https://www.python.org/downloads/
# Install Pandoc
choco install pandoc
```

**macOS:**
```bash
brew install python3 pandoc
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3 pandoc
```

### Optional (for better PDF support):
```bash
# Windows
choco install wkhtmltopdf

# macOS
brew install wkhtmltopdf

# Linux
sudo apt-get install wkhtmltopdf
```

---

## Step 2: Start E-Book Maker

### Windows
**Double-click** `start.bat`

### Linux/macOS
```bash
./start.sh
```

The web interface will automatically open in your browser at `http://127.0.0.1:5000`

---

## Step 3: Create Your First E-Book

1. **Click "Convert"** in the top menu
2. **Upload your markdown files** (drag & drop)
3. **Enter book title and author**
4. **Select output formats** (EPUB, PDF, HTML)
5. **Click "Convert to E-Book"**
6. **Download** your generated files!

---

## What Can You Do?

### 📄 Document Conversion
- Markdown → EPUB, PDF, HTML
- Multi-chapter books
- Automatic table of contents

### 🎨 Cover Creation
- Generate professional covers
- Amazon KDP compliant
- Custom colors and text

### 💧 Watermarking
- Protect your documents
- Text and logo watermarks
- PDF, HTML, DOCX support

---

## Troubleshooting

**Server won't start?**
- Make sure Python is installed: `python --version`
- Delete the `venv` folder and try again

**Conversion fails?**
- Install Pandoc (required!)
- Check that files are `.md`, `.txt`, or `.html`

**Need help?**
- Check `README.md` for full documentation
- Go to Settings page to check dependencies

---

## Next Steps

- Read the full [README.md](README.md) for detailed instructions
- Explore all features in the web interface
- Check Settings to verify all dependencies are installed

---

**Enjoy creating professional e-books!**
