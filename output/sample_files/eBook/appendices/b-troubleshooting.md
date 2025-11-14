# Appendix B: Troubleshooting Guide

Common issues and solutions.

## Dependency Issues

### Pandoc Not Found

**Problem**: `pandoc: command not found`

**Solution**:
1. Install Pandoc from https://pandoc.org
2. Verify installation: `pandoc --version`
3. Restart terminal/command prompt

### Python Packages Missing

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Conversion Issues

### PDF Generation Fails

**Possible Causes**:
1. wkhtmltopdf not installed
2. LaTeX not configured
3. Large image files

**Solutions**:
- Install wkhtmltopdf for better PDF support
- Use HTML format as alternative
- Optimize/resize images before conversion

### EPUB Invalid

**Problem**: EPUB fails validation

**Solution**:
- Ensure valid HTML in markdown
- Check for unclosed tags
- Validate with epubcheck tool

## Watermarking Issues

### Logo Not Visible

**Problem**: Logo watermark doesn't appear

**Solution**:
- Increase opacity (try 50-60%)
- Check logo file format (use PNG/JPG)
- Verify logo file exists and is readable

### DOCX Watermark Missing

**Note**: DOCX watermarks appear in header/footer only
- Logo watermarks not supported in DOCX
- Open document to see header/footer watermark

