# Appendix C: API Reference

Python API for programmatic usage.

## Conversion Module

### EBookConverter Class

```python
from modules.conversion.converter import EBookConverter

converter = EBookConverter()

# Convert documents
results = converter.convert(
    input_files=[Path('chapter1.md'), Path('chapter2.md')],
    output_formats=['epub', 'pdf', 'html'],
    title='My E-Book',
    author='Author Name',
    output_dir=Path('output/ebooks')
)
```

### Methods

- `convert()` - Convert documents to e-book formats
- `check_dependencies()` - Check if required tools are installed
- `normalize_text()` - Fix text encoding issues

## Cover Generation Module

### CoverGenerator Class

```python
from modules.covers.cover_generator import CoverGenerator

generator = CoverGenerator()

# Create e-book cover
cover_path = generator.create_cover(
    cover_type='ebook',
    title='Book Title',
    subtitle='Optional Subtitle',
    author='Author Name',
    style='gradient',
    colors={'primary': '#667eea', 'secondary': '#764ba2'},
    output_dir=Path('output/covers')
)
```

## Watermarking Module

### Watermarker Class

```python
from modules.watermarking.watermarker import Watermarker

watermarker = Watermarker()

# Apply watermark
output_path = watermarker.apply_watermark(
    input_file=Path('document.pdf'),
    watermark_text='CONFIDENTIAL',
    logo_path=Path('logo.png'),
    opacity=0.4,
    position='center',
    output_dir=Path('output/watermarked')
)
```

### Supported Formats

- PDF: Full support (text + logo)
- HTML: Full support (text + logo)
- DOCX: Text only (header/footer)

