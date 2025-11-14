#!/bin/bash

# E-Book Conversion Script for "The Complete IT Career Readiness Pipeline"
# Converts Markdown source files to multiple output formats using Pandoc

set -e  # Exit on any error

# Project directories
PROJECT_DIR="/mnt/c/Users/Mishka/Desktop/ASSISTANTS/E-Book Project"
CHAPTERS_DIR="$PROJECT_DIR/chapters"
APPENDICES_DIR="$PROJECT_DIR/appendices"
OUTPUT_DIR="$PROJECT_DIR/output"
PANDOC_DIR="$PROJECT_DIR/pandoc"

# Book metadata
TITLE="The Complete IT Career Readiness Pipeline"
SUBTITLE="A Scientific Approach to Cybersecurity Career Development"
AUTHOR="Generated with AI Assistance"
DATE=$(date +"%Y-%m-%d")

echo "Starting e-book conversion process..."
echo "Title: $TITLE"
echo "Date: $DATE"

# Create temporary combined file
TEMP_FILE="$OUTPUT_DIR/complete-book.md"

echo "Creating combined markdown file..."

# Start with title page
cat > "$TEMP_FILE" << EOF
---
title: "$TITLE"
subtitle: "$SUBTITLE"
author: "$AUTHOR"
date: "$DATE"
documentclass: book
geometry: margin=1in
fontsize: 11pt
linestretch: 1.2
toc: true
toc-depth: 2
numbersections: true
---

# $TITLE
## $SUBTITLE

**Author:** $AUTHOR
**Publication Date:** $DATE
**Word Count:** ~76,000 words
**Format:** Multi-platform (EPUB, PDF, Web)

---

EOF

# Add table of contents
echo "Adding table of contents..."
cat "$PROJECT_DIR/table-of-contents.md" >> "$TEMP_FILE"
echo -e "\n---\n" >> "$TEMP_FILE"

# Add all chapters in order
echo "Adding chapters..."
for i in $(seq -f "%02g" 0 15); do
    chapter_file="$CHAPTERS_DIR/${i}-*.md"
    if ls $chapter_file 1> /dev/null 2>&1; then
        echo "Adding chapter $i..."
        echo -e "\n\\newpage\n" >> "$TEMP_FILE"
        cat $chapter_file >> "$TEMP_FILE"
        echo -e "\n" >> "$TEMP_FILE"
    fi
done

# Add appendices
echo "Adding appendices..."
for appendix in "$APPENDICES_DIR"/*.md; do
    if [ -f "$appendix" ]; then
        echo "Adding $(basename "$appendix")..."
        echo -e "\n\\newpage\n" >> "$TEMP_FILE"
        cat "$appendix" >> "$TEMP_FILE"
        echo -e "\n" >> "$TEMP_FILE"
    fi
done

echo "Combined file created: $TEMP_FILE"

# Check if pandoc is available
if ! command -v pandoc &> /dev/null; then
    echo "Warning: Pandoc not found. Please install Pandoc to generate output formats."
    echo "Combined markdown file is available at: $TEMP_FILE"
    exit 0
fi

echo "Pandoc found. Generating output formats..."

# Generate EPUB
echo "Generating EPUB..."
pandoc "$TEMP_FILE" \
    --to epub3 \
    --output "$OUTPUT_DIR/complete-it-career-readiness-pipeline.epub" \
    --metadata title="$TITLE" \
    --metadata author="$AUTHOR" \
    --metadata date="$DATE" \
    --toc \
    --toc-depth=2

# Generate PDF
echo "Generating PDF..."
pandoc "$TEMP_FILE" \
    --to pdf \
    --output "$OUTPUT_DIR/complete-it-career-readiness-pipeline.pdf" \
    --metadata title="$TITLE" \
    --metadata author="$AUTHOR" \
    --metadata date="$DATE" \
    --toc \
    --toc-depth=2 \
    --variable geometry:margin=1in \
    --variable fontsize:11pt \
    --variable linestretch:1.2

# Generate HTML
echo "Generating HTML..."
pandoc "$TEMP_FILE" \
    --to html5 \
    --output "$OUTPUT_DIR/complete-it-career-readiness-pipeline.html" \
    --metadata title="$TITLE" \
    --metadata author="$AUTHOR" \
    --metadata date="$DATE" \
    --toc \
    --toc-depth=2 \
    --standalone \
    --css-reference="$PANDOC_DIR/style.css"

echo "Conversion complete!"
echo "Output files:"
echo "- EPUB: $OUTPUT_DIR/complete-it-career-readiness-pipeline.epub"
echo "- PDF: $OUTPUT_DIR/complete-it-career-readiness-pipeline.pdf"
echo "- HTML: $OUTPUT_DIR/complete-it-career-readiness-pipeline.html"
echo "- Combined Markdown: $TEMP_FILE"

# Get final word count
WORD_COUNT=$(wc -w < "$TEMP_FILE")
echo "Final word count: $WORD_COUNT words"