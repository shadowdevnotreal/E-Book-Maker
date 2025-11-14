#!/bin/bash
# E-Book Maker - Linux/Mac Startup Script
# Automatically installs dependencies and starts the server

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}E-Book Maker - Startup Script for Linux/Mac${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3 && ! command_exists python; then
    echo -e "${RED}[ERROR] Python is not installed!${NC}"
    echo ""
    echo "Please install Python 3.8+ from your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  Mac: brew install python3"
    echo ""
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command_exists python3; then
    PYTHON_CMD="python"
fi

PIP_CMD="pip3"
if ! command_exists pip3; then
    PIP_CMD="pip"
fi

echo -e "${GREEN}[1/4] Checking Python installation...${NC}"
$PYTHON_CMD --version
echo ""

# Check if pip is available
if ! command_exists $PIP_CMD; then
    echo -e "${RED}[ERROR] pip is not installed!${NC}"
    echo ""
    echo "Try: $PYTHON_CMD -m ensurepip --upgrade"
    echo ""
    exit 1
fi

echo -e "${GREEN}[2/4] Installing/Updating Python dependencies...${NC}"
echo ""
$PYTHON_CMD -m pip install --upgrade pip
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}[WARNING] Some packages failed to install.${NC}"
    echo -e "${YELLOW}This might affect functionality.${NC}"
    echo ""
    read -p "Press Enter to continue..."
fi

echo ""
echo -e "${GREEN}[3/4] Verifying setup...${NC}"
echo ""

# Run bash verification script if available
if [ -f "scripts/verify-setup-linux.sh" ]; then
    bash scripts/verify-setup-linux.sh
    echo ""
else
    echo -e "${YELLOW}[INFO] Verification script not found, skipping detailed check${NC}"
    echo ""
fi

echo -e "${GREEN}[4/4] Launching E-Book Maker...${NC}"
echo ""
echo -e "${CYAN}============================================================${NC}"
echo "Choose your interface:"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Launch the interface chooser
$PYTHON_CMD launch.py

# If launcher exits with error, pause
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${RED}[ERROR] Launcher exited with an error${NC}"
    echo -e "${CYAN}============================================================${NC}"
    read -p "Press Enter to exit..."
fi
