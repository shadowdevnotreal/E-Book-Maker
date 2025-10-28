#!/bin/bash
# E-Book Maker - Linux/macOS Startup Script

echo "==============================================="
echo "E-Book Maker - Starting Web Interface"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "Installing/updating dependencies from requirements.txt..."
echo "This includes: Flask, Pillow, PyPDF2, reportlab, python-docx, PyMuPDF, Werkzeug"
echo ""
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "==============================================="
    echo "WARNING: Some dependencies failed to install!"
    echo "==============================================="
    echo "The application may not function properly."
    echo ""
    echo "Try running these commands manually:"
    echo "  source venv/bin/activate"
    echo "  pip install Flask Pillow PyPDF2 reportlab python-docx PyMuPDF Werkzeug"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

# Start the server
echo ""
echo "Starting E-Book Maker server..."
echo ""
python3 server.py

# Deactivate on exit
deactivate
