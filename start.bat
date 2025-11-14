@echo off
REM E-Book Maker - Windows Startup Script
REM Automatically installs ALL dependencies and lets you choose your interface
REM Handles both standard Python and Anaconda environments

echo ============================================================
echo E-Book Maker - Complete Setup and Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version
echo.

echo [2/3] Installing/Updating ALL Python dependencies...
echo This may take a few minutes on first run...
echo.

REM Upgrade pip first (use python -m pip for Anaconda compatibility)
echo  ^> Upgrading pip...
python -m pip install --upgrade pip --quiet --disable-pip-version-check 2>nul

REM Install all dependencies from requirements.txt
echo  ^> Installing packages from requirements.txt...
echo    (Flask, Streamlit, Pillow, PyPDF2, reportlab, python-docx,
echo     PyMuPDF, weasyprint, qrcode, groq, Werkzeug)
echo.
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

if errorlevel 1 (
    echo.
    echo [WARNING] Some packages may have failed to install
    echo This might affect functionality
    echo.
    pause
)

echo.
echo ✓ All Python packages installed successfully!
echo.

echo [3/3] Launching E-Book Maker...
echo.
echo ============================================================
echo Choose your interface:
echo ============================================================
echo.

REM Launch the interface chooser
python launch.py

REM If launcher exits with error, pause so user can see message
if errorlevel 1 (
    echo.
    echo ============================================================
    echo [ERROR] Launcher exited with an error
    echo ============================================================
    pause
)
