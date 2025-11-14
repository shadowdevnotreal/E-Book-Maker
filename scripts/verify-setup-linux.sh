#!/bin/bash
# E-Book Maker - Linux/Mac Setup Verification Script
# Run this to verify all dependencies are properly installed

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}E-Book Maker - Setup Verification${NC}"
echo -e "${CYAN}Platform: $(uname -s)${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

all_passed=true

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo -n "Checking Python..."
if command_exists python3; then
    python_version=$(python3 --version 2>&1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}Version: $python_version${NC}"
elif command_exists python; then
    python_version=$(python --version 2>&1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}Version: $python_version${NC}"
else
    echo -e " ${RED}NOT FOUND${NC}"
    echo -e "  ${YELLOW}Install Python 3.8+ from your package manager${NC}"
    all_passed=false
fi

# Check pip
echo -n "Checking pip..."
if command_exists pip3; then
    pip_version=$(pip3 --version 2>&1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}Version: $pip_version${NC}"
elif command_exists pip; then
    pip_version=$(pip --version 2>&1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}Version: $pip_version${NC}"
else
    echo -e " ${RED}NOT FOUND${NC}"
    all_passed=false
fi

# Check Pandoc
echo -n "Checking Pandoc..."
if command_exists pandoc; then
    pandoc_version=$(pandoc --version 2>&1 | head -1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}$pandoc_version${NC}"
else
    echo -e " ${RED}NOT FOUND${NC}"
    echo -e "  ${YELLOW}Install: sudo apt-get install pandoc (Ubuntu/Debian)${NC}"
    echo -e "  ${YELLOW}Install: brew install pandoc (Mac)${NC}"
    all_passed=false
fi

# Check wkhtmltopdf
echo -n "Checking wkhtmltopdf..."
if command_exists wkhtmltopdf; then
    wk_version=$(wkhtmltopdf --version 2>&1 | head -1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}$wk_version${NC}"
else
    echo -e " ${YELLOW}NOT FOUND${NC}"
    echo -e "  ${GRAY}Optional: sudo apt-get install wkhtmltopdf (Ubuntu/Debian)${NC}"
    echo -e "  ${GRAY}Optional: brew install wkhtmltopdf (Mac)${NC}"
fi

# Check pdflatex
echo -n "Checking pdflatex..."
if command_exists pdflatex; then
    pdflatex_version=$(pdflatex --version 2>&1 | head -1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}$pdflatex_version${NC}"
else
    echo -e " ${YELLOW}NOT FOUND${NC}"
    echo -e "  ${GRAY}Optional: sudo apt-get install texlive-latex-base (Ubuntu/Debian)${NC}"
    echo -e "  ${GRAY}Optional: brew install basictex (Mac)${NC}"
fi

# Check weasyprint (Python package)
echo -n "Checking weasyprint..."
if python3 -c "import weasyprint" 2>/dev/null; then
    weasyprint_version=$(python3 -c "import weasyprint; print(weasyprint.__version__)" 2>&1)
    echo -e " ${GREEN}FOUND${NC}"
    echo -e "  ${GRAY}Version: $weasyprint_version${NC}"
else
    echo -e " ${YELLOW}NOT FOUND${NC}"
    echo -e "  ${GRAY}Optional: pip3 install weasyprint${NC}"
fi

# Check Python packages
echo ""
echo -e "${CYAN}Checking Python packages...${NC}"

# Required packages
required_packages=("flask" "Pillow" "reportlab" "python-docx" "PyPDF2" "qrcode" "PyMuPDF" "groq" "Werkzeug")

for package in "${required_packages[@]}"; do
    echo -n "  $package..."
    # Convert package name for import
    import_name="${package//-/_}"

    # Special cases for package name vs import name
    if [[ "$package" == "python-docx" ]]; then
        import_name="docx"
    elif [[ "$package" == "Pillow" ]]; then
        import_name="PIL"
    elif [[ "$package" == "PyPDF2" ]]; then
        import_name="PyPDF2"
    elif [[ "$package" == "PyMuPDF" ]]; then
        import_name="fitz"
    elif [[ "$package" == "Werkzeug" ]]; then
        import_name="werkzeug"
    fi

    if python3 -c "import $import_name" 2>/dev/null; then
        echo -e " ${GREEN}INSTALLED${NC}"
    else
        echo -e " ${RED}MISSING${NC}"
        echo -e "    ${YELLOW}Install with: pip3 install $package${NC}"
        all_passed=false
    fi
done

# Optional packages
optional_packages=("weasyprint")

for package in "${optional_packages[@]}"; do
    echo -n "  $package (optional)..."
    import_name="${package//-/_}"

    if python3 -c "import $import_name" 2>/dev/null; then
        echo -e " ${GREEN}INSTALLED${NC}"
    else
        echo -e " ${YELLOW}NOT INSTALLED${NC}"
    fi
done

# Summary
echo ""
echo -e "${CYAN}========================================${NC}"
if $all_passed; then
    echo -e "${GREEN}ALL REQUIRED DEPENDENCIES INSTALLED!${NC}"
    echo ""
    echo -e "${NC}You can run the server with:${NC}"
    echo -e "  ${YELLOW}python3 server.py${NC}"
else
    echo -e "${RED}SOME DEPENDENCIES ARE MISSING!${NC}"
    echo ""
    echo -e "${NC}Install missing packages with:${NC}"
    echo -e "  ${YELLOW}pip3 install -r requirements.txt${NC}"
    echo ""
    echo -e "${YELLOW}Note: At least one PDF engine (wkhtmltopdf, pdflatex, or weasyprint)${NC}"
    echo -e "${YELLOW}      is required for PDF conversion.${NC}"
fi
echo -e "${CYAN}========================================${NC}"
echo ""
