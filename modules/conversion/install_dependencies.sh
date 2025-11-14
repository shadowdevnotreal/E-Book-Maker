#!/bin/bash
################################################################################
# E-Book Builder Dependency Installation Script
# ==============================================
#
# Automatically installs all required dependencies for building e-books.
# Supports Ubuntu/Debian, Fedora/CentOS, and Arch Linux.
#
# Usage:
#   chmod +x install_dependencies.sh
#   ./install_dependencies.sh
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}E-Book Builder Dependency Installer${NC}                       ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Detect operating system
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        print_error "Cannot detect operating system"
        exit 1
    fi
}

# Install on Ubuntu/Debian
install_ubuntu_debian() {
    print_info "Detected Ubuntu/Debian system"
    echo ""

    print_info "Updating package list..."
    sudo apt update

    print_info "Installing Pandoc..."
    sudo apt install -y pandoc

    print_info "Installing wkhtmltopdf (PDF generation)..."
    sudo apt install -y wkhtmltopdf

    # Ask if user wants LaTeX (large download)
    echo ""
    print_warning "LaTeX packages are large (~500MB). They provide better PDF formatting."
    read -p "Install LaTeX for enhanced PDF generation? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing LaTeX packages (this may take a while)..."
        sudo apt install -y texlive-latex-base texlive-fonts-recommended texlive-latex-extra
        print_success "LaTeX installed"
    else
        print_info "Skipping LaTeX installation. PDF generation will use wkhtmltopdf."
    fi

    print_success "All dependencies installed successfully!"
}

# Install on Fedora/CentOS/RHEL
install_fedora() {
    print_info "Detected Fedora/CentOS/RHEL system"
    echo ""

    print_info "Installing Pandoc..."
    sudo dnf install -y pandoc

    print_info "Installing wkhtmltopdf..."
    sudo dnf install -y wkhtmltopdf

    # Ask if user wants LaTeX
    echo ""
    print_warning "LaTeX packages are large (~500MB). They provide better PDF formatting."
    read -p "Install LaTeX for enhanced PDF generation? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing LaTeX packages (this may take a while)..."
        sudo dnf install -y texlive
        print_success "LaTeX installed"
    else
        print_info "Skipping LaTeX installation. PDF generation will use wkhtmltopdf."
    fi

    print_success "All dependencies installed successfully!"
}

# Install on Arch Linux
install_arch() {
    print_info "Detected Arch Linux system"
    echo ""

    print_info "Installing Pandoc..."
    sudo pacman -S --noconfirm pandoc

    print_info "Installing wkhtmltopdf..."
    sudo pacman -S --noconfirm wkhtmltopdf-static

    # Ask if user wants LaTeX
    echo ""
    print_warning "LaTeX packages are large (~500MB). They provide better PDF formatting."
    read -p "Install LaTeX for enhanced PDF generation? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing LaTeX packages (this may take a while)..."
        sudo pacman -S --noconfirm texlive-core
        print_success "LaTeX installed"
    else
        print_info "Skipping LaTeX installation. PDF generation will use wkhtmltopdf."
    fi

    print_success "All dependencies installed successfully!"
}

# Verify installation
verify_installation() {
    echo ""
    print_info "Verifying installation..."
    echo ""

    # Check Pandoc
    if command -v pandoc &> /dev/null; then
        PANDOC_VERSION=$(pandoc --version | head -n 1)
        print_success "Pandoc found: $PANDOC_VERSION"
    else
        print_error "Pandoc not found!"
        return 1
    fi

    # Check wkhtmltopdf
    if command -v wkhtmltopdf &> /dev/null; then
        WKHTMLTOPDF_VERSION=$(wkhtmltopdf --version 2>&1 | head -n 1)
        print_success "wkhtmltopdf found: $WKHTMLTOPDF_VERSION"
    else
        print_warning "wkhtmltopdf not found (optional)"
    fi

    # Check pdflatex
    if command -v pdflatex &> /dev/null; then
        PDFLATEX_VERSION=$(pdflatex --version | head -n 1)
        print_success "pdflatex found: $PDFLATEX_VERSION"
    else
        print_warning "pdflatex not found (optional)"
    fi

    echo ""
    print_success "Installation verified! You can now build e-books."
    echo ""
    print_info "Next steps:"
    echo "  1. Run: python3 pandoc/check_dependencies.py  (to verify)"
    echo "  2. Run: python3 pandoc/convert.py             (quick build)"
    echo "  3. Run: python3 pandoc/interactive_build.py   (interactive builder)"
}

# Main installation flow
main() {
    print_header

    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Do not run this script as root. Use your regular user account."
        print_info "The script will ask for sudo password when needed."
        exit 1
    fi

    # Detect OS
    detect_os

    # Install based on OS
    case "$OS" in
        ubuntu|debian)
            install_ubuntu_debian
            ;;
        fedora|centos|rhel)
            install_fedora
            ;;
        arch|manjaro)
            install_arch
            ;;
        *)
            print_error "Unsupported operating system: $OS"
            print_info "Please install manually:"
            print_info "  - Pandoc: https://pandoc.org/installing.html"
            print_info "  - wkhtmltopdf: https://wkhtmltopdf.org/downloads.html"
            exit 1
            ;;
    esac

    # Verify installation
    verify_installation

    echo ""
    print_success "Setup complete! 🎉"
}

# Run main function
main
