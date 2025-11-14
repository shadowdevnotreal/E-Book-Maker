@echo off
REM E-Book Conversion Script for "The Complete IT Career Readiness Pipeline"
REM Windows Batch version for command prompt compatibility
REM Converts Markdown source files to multiple output formats using Pandoc

title IT Career Pipeline - Document Converter

echo.
echo ========================================================
echo   IT Career Pipeline Document Converter (Windows)
echo ========================================================
echo.

REM Check if pandoc is installed
where pandoc >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Pandoc not found. Please install pandoc first.
    echo Download from: https://pandoc.org/installing.html
    echo.
    pause
    exit /b 1
)

REM Set source and output directories
set "SOURCE_DIR=..\chapters"
set "OUTPUT_DIR=..\generated\ebook"

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo Converting IT Career Pipeline documents...
echo.

REM Convert to PDF
echo [1/4] Generating PDF version...
pandoc "%SOURCE_DIR%\*.md" ^
    --from markdown ^
    --to pdf ^
    --output "%OUTPUT_DIR%\IT_Career_Pipeline_Complete.pdf" ^
    --pdf-engine=wkhtmltopdf ^
    --css style.css ^
    --toc ^
    --toc-depth=3 ^
    --number-sections ^
    --metadata title="IT Career Pipeline - Complete Guide" ^
    --metadata author="Diatasso PRCM" ^
    --metadata date="%date%"

if %ERRORLEVEL% equ 0 (
    echo    ✓ PDF generated successfully
) else (
    echo    ✗ PDF generation failed
)

REM Convert to EPUB
echo [2/4] Generating EPUB version...
pandoc "%SOURCE_DIR%\*.md" ^
    --from markdown ^
    --to epub ^
    --output "%OUTPUT_DIR%\IT_Career_Pipeline_Complete.epub" ^
    --css style.css ^
    --toc ^
    --toc-depth=3 ^
    --number-sections ^
    --metadata title="IT Career Pipeline - Complete Guide" ^
    --metadata author="Diatasso PRCM" ^
    --metadata date="%date%"

if %ERRORLEVEL% equ 0 (
    echo    ✓ EPUB generated successfully
) else (
    echo    ✗ EPUB generation failed
)

REM Convert to HTML
echo [3/4] Generating HTML version...
pandoc "%SOURCE_DIR%\*.md" ^
    --from markdown ^
    --to html5 ^
    --output "%OUTPUT_DIR%\IT_Career_Pipeline_Complete.html" ^
    --css style.css ^
    --toc ^
    --toc-depth=3 ^
    --number-sections ^
    --self-contained ^
    --metadata title="IT Career Pipeline - Complete Guide" ^
    --metadata author="Diatasso PRCM" ^
    --metadata date="%date%"

if %ERRORLEVEL% equ 0 (
    echo    ✓ HTML generated successfully
) else (
    echo    ✗ HTML generation failed
)

REM Convert to DOCX
echo [4/4] Generating Word document...
pandoc "%SOURCE_DIR%\*.md" ^
    --from markdown ^
    --to docx ^
    --output "%OUTPUT_DIR%\IT_Career_Pipeline_Complete.docx" ^
    --toc ^
    --toc-depth=3 ^
    --number-sections ^
    --metadata title="IT Career Pipeline - Complete Guide" ^
    --metadata author="Diatasso PRCM" ^
    --metadata date="%date%"

if %ERRORLEVEL% equ 0 (
    echo    ✓ Word document generated successfully
) else (
    echo    ✗ Word document generation failed
)

echo.
echo ========================================================
echo   Conversion Complete!
echo ========================================================
echo.
echo Output files saved to: %OUTPUT_DIR%
echo.
echo Available formats:
echo   • PDF (for printing and professional sharing)
echo   • EPUB (for e-readers like Kindle)
echo   • HTML (for web viewing)
echo   • DOCX (for editing in Microsoft Word)
echo.

REM Ask if user wants to open output directory
set /p "OPEN_DIR=Would you like to open the output directory? (y/n): "
if /i "%OPEN_DIR%"=="y" (
    start "" "%OUTPUT_DIR%"
)

echo.
echo Press any key to exit...
pause >nul