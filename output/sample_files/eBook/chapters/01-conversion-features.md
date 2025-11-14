# Chapter 1: Document Conversion Features

This chapter tests various document conversion capabilities.

## Supported Input Formats

The system accepts the following input formats:

- **Markdown** (.md, .markdown)
- **Plain Text** (.txt)
- **HTML** (.html, .htm)

## Supported Output Formats

### EPUB Format

EPUB is the standard e-reader format compatible with:
- Amazon Kindle
- Apple Books
- Google Play Books
- Kobo readers

### PDF Format

PDF generation with multiple engines:
- **wkhtmltopdf** - Fast, web-based rendering
- **LaTeX (pdflatex)** - Professional typography
- **WeasyPrint** - CSS-based layout

### HTML Format

Standalone HTML with embedded styles for:
- Web publishing
- Email distribution
- Archive purposes

## Text Formatting Tests

### Bold and Italic

This is **bold text** and this is *italic text* and this is ***bold italic***.

### Lists

Ordered list:
1. First item
2. Second item
3. Third item

Unordered list:
- Item A
- Item B
- Item C

### Code Blocks

```python
def hello_world():
    print("Hello from E-Book Maker!")
    return True
```

### Blockquotes

> This is a blockquote to test formatting.
> It can span multiple lines.

### Tables

| Feature | Status | Priority |
|---------|--------|----------|
| Conversion | ✓ Working | High |
| Covers | ✓ Working | High |
| Watermarking | ✓ Working | Medium |

