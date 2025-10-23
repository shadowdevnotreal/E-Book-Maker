# E-Book Conversion Script for "The Complete IT Career Readiness Pipeline"
# PowerShell version for Windows with enhanced features
# Converts Markdown source files to multiple output formats using Pandoc

[CmdletBinding()]
param(
    [switch]$SkipPDF,
    [switch]$SkipEPUB,
    [switch]$SkipHTML,
    [switch]$OpenOutput,
    [string]$OutputDir
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Project directories
$ProjectDir = Split-Path -Parent $PSScriptRoot
$ChaptersDir = Join-Path $ProjectDir "chapters"
$AppendicesDir = Join-Path $ProjectDir "appendices"
if ($OutputDir) {
    $OutputPath = $OutputDir
} else {
    $OutputPath = Join-Path $ProjectDir "output"
}
$PandocDir = Join-Path $ProjectDir "pandoc"

# Book metadata
$Title = "The Complete IT Career Readiness Pipeline"
$Subtitle = "A Scientific Approach to IT Career Development"
$Author = "Generated with AI Assistance"
$Date = Get-Date -Format "yyyy-MM-dd"

Write-Host "🚀 Starting E-Book Conversion Process..." -ForegroundColor Green
Write-Host "📖 Title: $Title" -ForegroundColor Cyan
Write-Host "📅 Date: $Date" -ForegroundColor Cyan
Write-Host "📁 Output Directory: $OutputPath" -ForegroundColor Yellow

# Ensure output directory exists
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    Write-Host "✅ Created output directory" -ForegroundColor Green
}

# Create temporary combined file
$TempFile = Join-Path $OutputPath "complete-book.md"

Write-Host "📝 Creating combined markdown file..." -ForegroundColor Yellow

# Start with title page and metadata
$frontMatter = @"
---
title: "$Title"
subtitle: "$Subtitle"
author: "$Author"
date: "$Date"
documentclass: book
geometry: margin=1in
fontsize: 11pt
linestretch: 1.2
toc: true
toc-depth: 2
numbersections: true
---

# $Title
## $Subtitle

**Author:** $Author
**Publication Date:** $Date
**Format:** Multi-platform (EPUB, PDF, Web)

---

"@

Set-Content -Path $TempFile -Value $frontMatter -Encoding UTF8

# Add table of contents
$tocFile = Join-Path $ProjectDir "table-of-contents.md"
if (Test-Path $tocFile) {
    Write-Host "📑 Adding table of contents..." -ForegroundColor Yellow
    Add-Content -Path $TempFile -Value (Get-Content $tocFile -Raw) -Encoding UTF8
    Add-Content -Path $TempFile -Value "`n---`n" -Encoding UTF8
}

# Add all chapters in order
Write-Host "📚 Adding chapters..." -ForegroundColor Yellow
for ($i = 0; $i -le 15; $i++) {
    $chapterPattern = "{0:D2}-*.md" -f $i
    $chapterFiles = Get-ChildItem -Path $ChaptersDir -Filter $chapterPattern -ErrorAction SilentlyContinue

    foreach ($chapterFile in $chapterFiles) {
        Write-Host "  ✅ Adding chapter $i..." -ForegroundColor Gray
        Add-Content -Path $TempFile -Value "`n\newpage`n" -Encoding UTF8
        Add-Content -Path $TempFile -Value (Get-Content $chapterFile.FullName -Raw) -Encoding UTF8
        Add-Content -Path $TempFile -Value "`n" -Encoding UTF8
    }
}

# Add appendices
Write-Host "📋 Adding appendices..." -ForegroundColor Yellow
$appendixFiles = Get-ChildItem -Path $AppendicesDir -Filter "*.md" -ErrorAction SilentlyContinue
foreach ($appendix in $appendixFiles) {
    Write-Host "  ✅ Adding $($appendix.Name)..." -ForegroundColor Gray
    Add-Content -Path $TempFile -Value "`n\newpage`n" -Encoding UTF8
    Add-Content -Path $TempFile -Value (Get-Content $appendix.FullName -Raw) -Encoding UTF8
    Add-Content -Path $TempFile -Value "`n" -Encoding UTF8
}

Write-Host "✅ Combined file created: $TempFile" -ForegroundColor Green

# Check if pandoc is available
$pandocPath = Get-Command pandoc -ErrorAction SilentlyContinue
if (!$pandocPath) {
    Write-Warning "⚠️  Pandoc not found. Please install Pandoc to generate output formats."
    Write-Host "📥 Download from: https://pandoc.org/installing.html" -ForegroundColor Yellow
    Write-Host "📄 Combined markdown file is available at: $TempFile" -ForegroundColor Green

    if ($OpenOutput) {
        Start-Process explorer.exe -ArgumentList $OutputPath
    }
    return
}

Write-Host "🔧 Pandoc found. Generating output formats..." -ForegroundColor Green

# Define output files
$epubFile = Join-Path $OutputPath "complete-it-career-readiness-pipeline.epub"
$pdfFile = Join-Path $OutputPath "complete-it-career-readiness-pipeline.pdf"
$htmlFile = Join-Path $OutputPath "complete-it-career-readiness-pipeline.html"

try {
    # Generate EPUB
    if (!$SkipEPUB) {
        Write-Host "📱 Generating EPUB..." -ForegroundColor Yellow
        & pandoc $TempFile `
            --to epub3 `
            --output $epubFile `
            --metadata title="$Title" `
            --metadata author="$Author" `
            --metadata date="$Date" `
            --toc `
            --toc-depth=2

        if (Test-Path $epubFile) {
            Write-Host "✅ EPUB generated successfully!" -ForegroundColor Green
        }
    }

    # Generate PDF
    if (!$SkipPDF) {
        Write-Host "📄 Generating PDF..." -ForegroundColor Yellow
        & pandoc $TempFile `
            --to pdf `
            --output $pdfFile `
            --metadata title="$Title" `
            --metadata author="$Author" `
            --metadata date="$Date" `
            --toc `
            --toc-depth=2 `
            --variable geometry:margin=1in `
            --variable fontsize:11pt `
            --variable linestretch:1.2

        if (Test-Path $pdfFile) {
            Write-Host "✅ PDF generated successfully!" -ForegroundColor Green
        }
    }

    # Generate HTML
    if (!$SkipHTML) {
        Write-Host "🌐 Generating HTML..." -ForegroundColor Yellow
        $cssFile = Join-Path $PandocDir "style.css"
        $cssArg = if (Test-Path $cssFile) { "--css-reference=`"$cssFile`"" } else { "" }

        $pandocArgs = @(
            $TempFile,
            "--to", "html5",
            "--output", $htmlFile,
            "--metadata", "title=`"$Title`"",
            "--metadata", "author=`"$Author`"",
            "--metadata", "date=`"$Date`"",
            "--toc",
            "--toc-depth=2",
            "--standalone"
        )

        if ($cssArg) {
            $pandocArgs += $cssArg
        }

        & pandoc @pandocArgs

        if (Test-Path $htmlFile) {
            Write-Host "✅ HTML generated successfully!" -ForegroundColor Green
        }
    }

    Write-Host "`n🎉 Conversion complete!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "📁 Output files:" -ForegroundColor Cyan

    if (Test-Path $epubFile) {
        Write-Host "  📱 EPUB: $epubFile" -ForegroundColor White
    }
    if (Test-Path $pdfFile) {
        Write-Host "  📄 PDF: $pdfFile" -ForegroundColor White
    }
    if (Test-Path $htmlFile) {
        Write-Host "  🌐 HTML: $htmlFile" -ForegroundColor White
    }
    Write-Host "  📝 Combined Markdown: $TempFile" -ForegroundColor White

    # Get final word count
    if (Test-Path $TempFile) {
        $content = Get-Content $TempFile -Raw
        $wordCount = ($content -split '\s+').Count
        Write-Host "📊 Final word count: $wordCount words" -ForegroundColor Cyan
    }

    # Open output directory if requested
    if ($OpenOutput) {
        Write-Host "📂 Opening output directory..." -ForegroundColor Yellow
        Start-Process explorer.exe -ArgumentList $OutputPath
    }

    # Show completion notification
    if (Get-Command New-BurntToastNotification -ErrorAction SilentlyContinue) {
        New-BurntToastNotification -Text "E-Book Conversion Complete!", "Your Diatasso PRCM IT Career Pipeline book is ready!"
    }

} catch {
    Write-Error "❌ Error during conversion: $($_.Exception.Message)"
    exit 1
}