#!/bin/bash

# E-Book Conversion Script for "The Complete IT Career Readiness Pipeline"
# macOS-optimized version with native integrations
# Converts Markdown source files to multiple output formats using Pandoc

set -e  # Exit on any error

# Colors and emojis for macOS Terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CHAPTERS_DIR="$PROJECT_DIR/chapters"
APPENDICES_DIR="$PROJECT_DIR/appendices"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_DIR/output}"
PANDOC_DIR="$PROJECT_DIR/pandoc"

# Book metadata
TITLE="The Complete IT Career Readiness Pipeline"
SUBTITLE="A Scientific Approach to IT Career Development"
AUTHOR="Generated with AI Assistance"
DATE=$(date +"%Y-%m-%d")

# Display banner
echo -e "${BOLD}${BLUE}🚀 E-Book Conversion for macOS${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${CYAN}📖 Title: ${BOLD}$TITLE${NC}"
echo -e "${CYAN}📅 Date: $DATE${NC}"
echo -e "${YELLOW}📁 Output: $OUTPUT_DIR${NC}"
echo

# Function to send macOS notification
send_notification() {
    local title="$1"
    local message="$2"
    osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\""
}

# Function to check and install dependencies via Homebrew
check_dependencies() {
    echo -e "${YELLOW}🔍 Checking dependencies...${NC}"

    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}❌ Homebrew not found${NC}"
        echo -e "${YELLOW}Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Check for Pandoc
    if ! command -v pandoc &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Pandoc via Homebrew...${NC}"
        brew install pandoc
    fi

    # Check for wkhtmltopdf (for PDF generation)
    if ! command -v wkhtmltopdf &> /dev/null; then
        echo -e "${YELLOW}📦 Installing wkhtmltopdf via Homebrew...${NC}"
        brew install --cask wkhtmltopdf
    fi

    # Check for MacTeX (alternative for LaTeX PDF generation)
    if ! command -v pdflatex &> /dev/null; then
        echo -e "${YELLOW}ℹ️  Note: For better PDF quality, consider installing MacTeX:${NC}"
        echo -e "${CYAN}  brew install --cask mactex${NC}"
        echo
    fi

    echo -e "${GREEN}✅ Dependencies checked${NC}"
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${YELLOW}📝 Creating combined markdown file...${NC}"

# Create temporary combined file
TEMP_FILE="$OUTPUT_DIR/complete-book.md"

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
**Format:** Multi-platform (EPUB, PDF, Web)

---

EOF

# Add table of contents if it exists
if [ -f "$PROJECT_DIR/table-of-contents.md" ]; then
    echo -e "${CYAN}📑 Adding table of contents...${NC}"
    cat "$PROJECT_DIR/table-of-contents.md" >> "$TEMP_FILE"
    echo -e "\n---\n" >> "$TEMP_FILE"
fi

# Add all chapters in order
echo -e "${CYAN}📚 Adding chapters...${NC}"
for i in $(seq -f "%02g" 0 15); do
    chapter_file="$CHAPTERS_DIR/${i}-"*.md
    if ls $chapter_file 1> /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Adding chapter $i...${NC}"
        echo -e "\n\\newpage\n" >> "$TEMP_FILE"
        cat $chapter_file >> "$TEMP_FILE"
        echo -e "\n" >> "$TEMP_FILE"
    fi
done

# Add appendices
echo -e "${CYAN}📋 Adding appendices...${NC}"
for appendix in "$APPENDICES_DIR"/*.md; do
    if [ -f "$appendix" ]; then
        echo -e "  ${GREEN}✅ Adding $(basename "$appendix")...${NC}"
        echo -e "\n\\newpage\n" >> "$TEMP_FILE"
        cat "$appendix" >> "$TEMP_FILE"
        echo -e "\n" >> "$TEMP_FILE"
    fi
done

echo -e "${GREEN}✅ Combined file created: $TEMP_FILE${NC}"

# Check dependencies
check_dependencies

# Check if pandoc is available
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}❌ Pandoc not found after installation attempt${NC}"
    echo -e "${YELLOW}📄 Combined markdown file is available at: $TEMP_FILE${NC}"
    send_notification "E-Book Conversion" "Pandoc installation failed, only markdown available"
    open "$OUTPUT_DIR"
    exit 0
fi

echo -e "${GREEN}🔧 Pandoc found. Generating output formats...${NC}"

# Define output files
EPUB_FILE="$OUTPUT_DIR/complete-it-career-readiness-pipeline.epub"
PDF_FILE="$OUTPUT_DIR/complete-it-career-readiness-pipeline.pdf"
HTML_FILE="$OUTPUT_DIR/complete-it-career-readiness-pipeline.html"

# Generate EPUB
echo -e "${YELLOW}📱 Generating EPUB...${NC}"
pandoc "$TEMP_FILE" \
    --to epub3 \
    --output "$EPUB_FILE" \
    --metadata title="$TITLE" \
    --metadata author="$AUTHOR" \
    --metadata date="$DATE" \
    --toc \
    --toc-depth=2

# Generate PDF (try multiple engines)
echo -e "${YELLOW}📄 Generating PDF...${NC}"
if command -v pdflatex &> /dev/null; then
    # Use LaTeX engine for better quality
    pandoc "$TEMP_FILE" \
        --to pdf \
        --pdf-engine=pdflatex \
        --output "$PDF_FILE" \
        --metadata title="$TITLE" \
        --metadata author="$AUTHOR" \
        --metadata date="$DATE" \
        --toc \
        --toc-depth=2 \
        --variable geometry:margin=1in \
        --variable fontsize:11pt \
        --variable linestretch:1.2
else
    # Fallback to wkhtmltopdf
    pandoc "$TEMP_FILE" \
        --to pdf \
        --pdf-engine=wkhtmltopdf \
        --output "$PDF_FILE" \
        --metadata title="$TITLE" \
        --metadata author="$AUTHOR" \
        --metadata date="$DATE" \
        --toc \
        --toc-depth=2
fi

# Generate HTML
echo -e "${YELLOW}🌐 Generating HTML...${NC}"
CSS_FILE="$PANDOC_DIR/style.css"
if [ -f "$CSS_FILE" ]; then
    pandoc "$TEMP_FILE" \
        --to html5 \
        --output "$HTML_FILE" \
        --metadata title="$TITLE" \
        --metadata author="$AUTHOR" \
        --metadata date="$DATE" \
        --toc \
        --toc-depth=2 \
        --standalone \
        --css-reference="$CSS_FILE"
else
    pandoc "$TEMP_FILE" \
        --to html5 \
        --output "$HTML_FILE" \
        --metadata title="$TITLE" \
        --metadata author="$AUTHOR" \
        --metadata date="$DATE" \
        --toc \
        --toc-depth=2 \
        --standalone
fi

echo
echo -e "${BOLD}${GREEN}🎉 Conversion complete!${NC}"
echo -e "${BLUE}📁 Output files:${NC}"

if [ -f "$EPUB_FILE" ]; then
    echo -e "${GREEN}  📱 EPUB: $EPUB_FILE${NC}"
fi

if [ -f "$PDF_FILE" ]; then
    echo -e "${GREEN}  📄 PDF: $PDF_FILE${NC}"
fi

if [ -f "$HTML_FILE" ]; then
    echo -e "${GREEN}  🌐 HTML: $HTML_FILE${NC}"
fi

echo -e "${GREEN}  📝 Combined Markdown: $TEMP_FILE${NC}"

# Get final word count
if [ -f "$TEMP_FILE" ]; then
    WORD_COUNT=$(wc -w < "$TEMP_FILE" | xargs)
    echo -e "${CYAN}📊 Final word count: $WORD_COUNT words${NC}"
fi

# Send completion notification
send_notification "E-Book Conversion Complete" "Your Diatasso PRCM IT Career Pipeline book is ready!"

# Open output directory in Finder
echo -e "${YELLOW}📂 Opening output directory in Finder...${NC}"
open "$OUTPUT_DIR"

# Offer to open files in default applications
echo
read -p "Would you like to preview the generated files? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "$PDF_FILE" ]; then
        echo -e "${CYAN}📖 Opening PDF in Preview...${NC}"
        open "$PDF_FILE"
    fi

    if [ -f "$EPUB_FILE" ]; then
        echo -e "${CYAN}📚 Opening EPUB in default reader...${NC}"
        open "$EPUB_FILE"
    fi

    if [ -f "$HTML_FILE" ]; then
        echo -e "${CYAN}🌐 Opening HTML in default browser...${NC}"
        open "$HTML_FILE"
    fi
fi

echo -e "${BOLD}${GREEN}✅ All done! Enjoy your e-book!${NC}"