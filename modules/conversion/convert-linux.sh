#!/bin/bash

# E-Book Conversion Script for "The Complete IT Career Readiness Pipeline"
# Linux-optimized version with distribution detection and package management
# Converts Markdown source files to multiple output formats using Pandoc

set -e  # Exit on any error

# Colors and emojis for Linux terminals
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Check if terminal supports emojis
if locale charmap | grep -q "UTF-8"; then
    EMOJI_SUPPORT=true
else
    EMOJI_SUPPORT=false
fi

# Function to print with emoji if supported
print_with_emoji() {
    local emoji="$1"
    local text="$2"
    local color="$3"

    if [ "$EMOJI_SUPPORT" = true ]; then
        echo -e "${color}${emoji} ${text}${NC}"
    else
        echo -e "${color}[*] ${text}${NC}"
    fi
}

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
echo -e "${BOLD}${BLUE}E-Book Conversion for Linux${NC}"
echo -e "${BLUE}====================================${NC}"
print_with_emoji "📖" "Title: ${BOLD}$TITLE${NC}" "${CYAN}"
print_with_emoji "📅" "Date: $DATE" "${CYAN}"
print_with_emoji "📁" "Output: $OUTPUT_DIR" "${YELLOW}"
echo

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Function to install packages based on distribution
install_packages() {
    local packages="$1"
    local distro=$(detect_distro)

    case "$distro" in
        ubuntu|debian|pop|mint|elementary)
            print_with_emoji "📦" "Installing packages via apt..." "${YELLOW}"
            sudo apt-get update
            sudo apt-get install -y $packages
            ;;
        fedora|centos|rhel|rocky|almalinux)
            if command -v dnf &> /dev/null; then
                print_with_emoji "📦" "Installing packages via dnf..." "${YELLOW}"
                sudo dnf install -y $packages
            elif command -v yum &> /dev/null; then
                print_with_emoji "📦" "Installing packages via yum..." "${YELLOW}"
                sudo yum install -y $packages
            fi
            ;;
        arch|manjaro|endeavouros)
            print_with_emoji "📦" "Installing packages via pacman..." "${YELLOW}"
            sudo pacman -S --noconfirm $packages
            ;;
        opensuse*|sles)
            print_with_emoji "📦" "Installing packages via zypper..." "${YELLOW}"
            sudo zypper install -y $packages
            ;;
        alpine)
            print_with_emoji "📦" "Installing packages via apk..." "${YELLOW}"
            sudo apk add $packages
            ;;
        *)
            print_with_emoji "⚠️" "Unknown distribution. Please install manually: $packages" "${RED}"
            return 1
            ;;
    esac
}

# Function to check and install dependencies
check_dependencies() {
    print_with_emoji "🔍" "Checking dependencies..." "${YELLOW}"

    local missing_packages=""
    local distro=$(detect_distro)

    # Check for Pandoc
    if ! command -v pandoc &> /dev/null; then
        case "$distro" in
            ubuntu|debian|pop|mint|elementary)
                missing_packages="$missing_packages pandoc"
                ;;
            fedora|centos|rhel|rocky|almalinux)
                missing_packages="$missing_packages pandoc"
                ;;
            arch|manjaro|endeavouros)
                missing_packages="$missing_packages pandoc"
                ;;
            opensuse*|sles)
                missing_packages="$missing_packages pandoc"
                ;;
            alpine)
                missing_packages="$missing_packages pandoc"
                ;;
        esac
    fi

    # Check for wkhtmltopdf
    if ! command -v wkhtmltopdf &> /dev/null; then
        case "$distro" in
            ubuntu|debian|pop|mint|elementary)
                missing_packages="$missing_packages wkhtmltopdf"
                ;;
            fedora|centos|rhel|rocky|almalinux)
                missing_packages="$missing_packages wkhtmltopdf"
                ;;
            arch|manjaro|endeavouros)
                missing_packages="$missing_packages wkhtmltopdf-static"
                ;;
            opensuse*|sles)
                missing_packages="$missing_packages wkhtmltopdf"
                ;;
            alpine)
                missing_packages="$missing_packages wkhtmltopdf"
                ;;
        esac
    fi

    # Check for texlive (for better PDF generation)
    if ! command -v pdflatex &> /dev/null; then
        case "$distro" in
            ubuntu|debian|pop|mint|elementary)
                print_with_emoji "ℹ️" "For better PDF quality, consider installing: sudo apt install texlive-latex-recommended" "${CYAN}"
                ;;
            fedora|centos|rhel|rocky|almalinux)
                print_with_emoji "ℹ️" "For better PDF quality, consider installing: sudo dnf install texlive-latex" "${CYAN}"
                ;;
            arch|manjaro|endeavouros)
                print_with_emoji "ℹ️" "For better PDF quality, consider installing: sudo pacman -S texlive-core" "${CYAN}"
                ;;
        esac
    fi

    # Install missing packages
    if [ -n "$missing_packages" ]; then
        print_with_emoji "📦" "Missing packages detected: $missing_packages" "${YELLOW}"
        read -p "Would you like to install them automatically? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_packages "$missing_packages"
        else
            print_with_emoji "⚠️" "Please install manually: $missing_packages" "${RED}"
        fi
    fi

    print_with_emoji "✅" "Dependencies checked" "${GREEN}"
}

# Function to send desktop notification
send_notification() {
    local title="$1"
    local message="$2"

    if command -v notify-send &> /dev/null; then
        notify-send "$title" "$message" --icon=dialog-information
    elif command -v zenity &> /dev/null; then
        zenity --info --text="$title: $message" &
    fi
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

print_with_emoji "📝" "Creating combined markdown file..." "${YELLOW}"

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
    print_with_emoji "📑" "Adding table of contents..." "${CYAN}"
    cat "$PROJECT_DIR/table-of-contents.md" >> "$TEMP_FILE"
    echo -e "\n---\n" >> "$TEMP_FILE"
fi

# Add all chapters in order
print_with_emoji "📚" "Adding chapters..." "${CYAN}"
for i in $(seq -f "%02g" 0 15); do
    chapter_file="$CHAPTERS_DIR/${i}-"*.md
    if ls $chapter_file 1> /dev/null 2>&1; then
        print_with_emoji "✅" "Adding chapter $i..." "${GREEN}"
        echo -e "\n\\newpage\n" >> "$TEMP_FILE"
        cat $chapter_file >> "$TEMP_FILE"
        echo -e "\n" >> "$TEMP_FILE"
    fi
done

# Add appendices
print_with_emoji "📋" "Adding appendices..." "${CYAN}"
for appendix in "$APPENDICES_DIR"/*.md; do
    if [ -f "$appendix" ]; then
        print_with_emoji "✅" "Adding $(basename "$appendix")..." "${GREEN}"
        echo -e "\n\\newpage\n" >> "$TEMP_FILE"
        cat "$appendix" >> "$TEMP_FILE"
        echo -e "\n" >> "$TEMP_FILE"
    fi
done

print_with_emoji "✅" "Combined file created: $TEMP_FILE" "${GREEN}"

# Check dependencies
check_dependencies

# Check if pandoc is available
if ! command -v pandoc &> /dev/null; then
    print_with_emoji "❌" "Pandoc not found" "${RED}"
    print_with_emoji "📄" "Combined markdown file is available at: $TEMP_FILE" "${YELLOW}"
    send_notification "E-Book Conversion" "Pandoc not found, only markdown available"

    # Try to open file manager
    if command -v xdg-open &> /dev/null; then
        xdg-open "$OUTPUT_DIR"
    elif command -v nautilus &> /dev/null; then
        nautilus "$OUTPUT_DIR" &
    elif command -v dolphin &> /dev/null; then
        dolphin "$OUTPUT_DIR" &
    fi
    exit 0
fi

print_with_emoji "🔧" "Pandoc found. Generating output formats..." "${GREEN}"

# Define output files
EPUB_FILE="$OUTPUT_DIR/complete-it-career-readiness-pipeline.epub"
PDF_FILE="$OUTPUT_DIR/complete-it-career-readiness-pipeline.pdf"
HTML_FILE="$OUTPUT_DIR/complete-it-career-readiness-pipeline.html"

# Generate EPUB
print_with_emoji "📱" "Generating EPUB..." "${YELLOW}"
pandoc "$TEMP_FILE" \
    --to epub3 \
    --output "$EPUB_FILE" \
    --metadata title="$TITLE" \
    --metadata author="$AUTHOR" \
    --metadata date="$DATE" \
    --toc \
    --toc-depth=2

# Generate PDF (try multiple engines)
print_with_emoji "📄" "Generating PDF..." "${YELLOW}"
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
print_with_emoji "🌐" "Generating HTML..." "${YELLOW}"
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
print_with_emoji "🎉" "Conversion complete!" "${BOLD}${GREEN}"
print_with_emoji "📁" "Output files:" "${BLUE}"

if [ -f "$EPUB_FILE" ]; then
    print_with_emoji "📱" "EPUB: $EPUB_FILE" "${GREEN}"
fi

if [ -f "$PDF_FILE" ]; then
    print_with_emoji "📄" "PDF: $PDF_FILE" "${GREEN}"
fi

if [ -f "$HTML_FILE" ]; then
    print_with_emoji "🌐" "HTML: $HTML_FILE" "${GREEN}"
fi

print_with_emoji "📝" "Combined Markdown: $TEMP_FILE" "${GREEN}"

# Get final word count
if [ -f "$TEMP_FILE" ]; then
    WORD_COUNT=$(wc -w < "$TEMP_FILE" | xargs)
    print_with_emoji "📊" "Final word count: $WORD_COUNT words" "${CYAN}"
fi

# Send completion notification
send_notification "E-Book Conversion Complete" "Your Diatasso PRCM IT Career Pipeline book is ready!"

# Open output directory
print_with_emoji "📂" "Opening output directory..." "${YELLOW}"
if command -v xdg-open &> /dev/null; then
    xdg-open "$OUTPUT_DIR"
elif command -v nautilus &> /dev/null; then
    nautilus "$OUTPUT_DIR" &
elif command -v dolphin &> /dev/null; then
    dolphin "$OUTPUT_DIR" &
elif command -v thunar &> /dev/null; then
    thunar "$OUTPUT_DIR" &
fi

print_with_emoji "✅" "All done! Enjoy your e-book!" "${BOLD}${GREEN}"