# E-Book Maker - Windows Setup Verification Script
# Run this to verify all dependencies are properly installed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "E-Book Maker - Setup Verification" -ForegroundColor Cyan
Write-Host "Platform: Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Function to check if command exists
function Test-Command {
    param($CommandName)
    try {
        if (Get-Command $CommandName -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to check PATH for executable
function Test-InPath {
    param($ExecutableName)
    $env:Path -split ';' | ForEach-Object {
        $fullPath = Join-Path $_ $ExecutableName
        if (Test-Path $fullPath) {
            return $fullPath
        }
    }
    return $null
}

# Check Python
Write-Host "Checking Python..." -NoNewline
if (Test-Command python) {
    $pythonVersion = python --version 2>&1
    Write-Host " FOUND" -ForegroundColor Green
    Write-Host "  Version: $pythonVersion" -ForegroundColor Gray
} elseif (Test-Command python3) {
    $pythonVersion = python3 --version 2>&1
    Write-Host " FOUND" -ForegroundColor Green
    Write-Host "  Version: $pythonVersion" -ForegroundColor Gray
} else {
    Write-Host " NOT FOUND" -ForegroundColor Red
    Write-Host "  Install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    $allPassed = $false
}

# Check pip
Write-Host "Checking pip..." -NoNewline
if (Test-Command pip) {
    $pipVersion = pip --version 2>&1
    Write-Host " FOUND" -ForegroundColor Green
    Write-Host "  Version: $pipVersion" -ForegroundColor Gray
} elseif (Test-Command pip3) {
    $pipVersion = pip3 --version 2>&1
    Write-Host " FOUND" -ForegroundColor Green
    Write-Host "  Version: $pipVersion" -ForegroundColor Gray
} else {
    Write-Host " NOT FOUND" -ForegroundColor Red
    $allPassed = $false
}

# Check Pandoc
Write-Host "Checking Pandoc..." -NoNewline
if (Test-Command pandoc) {
    $pandocVersion = pandoc --version 2>&1 | Select-Object -First 1
    Write-Host " FOUND" -ForegroundColor Green
    Write-Host "  $pandocVersion" -ForegroundColor Gray
} else {
    Write-Host " NOT FOUND" -ForegroundColor Red
    Write-Host "  Install from https://pandoc.org/installing.html" -ForegroundColor Yellow
    $allPassed = $false
}

# Check wkhtmltopdf
Write-Host "Checking wkhtmltopdf..." -NoNewline
if (Test-Command wkhtmltopdf) {
    $wkVersion = wkhtmltopdf --version 2>&1 | Select-Object -First 1
    Write-Host " FOUND" -ForegroundColor Green
    Write-Host "  $wkVersion" -ForegroundColor Gray
} else {
    Write-Host " NOT FOUND" -ForegroundColor Yellow
    Write-Host "  Optional: Install from https://wkhtmltopdf.org/downloads.html" -ForegroundColor Gray
}

# Check pdflatex (MiKTeX)
Write-Host "Checking pdflatex (MiKTeX)..." -NoNewline
if (Test-Command pdflatex) {
    $pdflatexVersion = pdflatex --version 2>&1 | Select-Object -First 1
    Write-Host " FOUND" -ForegroundColor Green
    Write-Host "  $pdflatexVersion" -ForegroundColor Gray
} else {
    Write-Host " NOT FOUND" -ForegroundColor Yellow
    Write-Host "  Optional: Install MiKTeX from https://miktex.org/download" -ForegroundColor Gray
}

# Check weasyprint (Python package)
Write-Host "Checking weasyprint..." -NoNewline
try {
    $weasyprintCheck = python -c "import weasyprint; print(weasyprint.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " FOUND" -ForegroundColor Green
        Write-Host "  Version: $weasyprintCheck" -ForegroundColor Gray
    } else {
        Write-Host " NOT FOUND" -ForegroundColor Yellow
        Write-Host "  Optional: Install with 'pip install weasyprint'" -ForegroundColor Gray
    }
} catch {
    Write-Host " NOT FOUND" -ForegroundColor Yellow
    Write-Host "  Optional: Install with 'pip install weasyprint'" -ForegroundColor Gray
}

# Check Python packages
Write-Host ""
Write-Host "Checking Python packages..." -ForegroundColor Cyan

# Required packages (server won't work without these)
$requiredPackages = @(
    @{Name="flask"; Import="flask"},
    @{Name="Pillow"; Import="PIL"},
    @{Name="reportlab"; Import="reportlab"},
    @{Name="python-docx"; Import="docx"},
    @{Name="PyPDF2"; Import="PyPDF2"},
    @{Name="qrcode"; Import="qrcode"},
    @{Name="PyMuPDF"; Import="fitz"},
    @{Name="groq"; Import="groq"},
    @{Name="Werkzeug"; Import="werkzeug"}
)

# Optional packages (nice to have, server works without)
$optionalPackages = @(
    @{Name="weasyprint"; Import="weasyprint"}
)

$missingRequired = 0

foreach ($pkg in $requiredPackages) {
    Write-Host "  $($pkg.Name)..." -NoNewline
    try {
        $packageCheck = python -c "import $($pkg.Import)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " INSTALLED" -ForegroundColor Green
        } else {
            Write-Host " MISSING" -ForegroundColor Red
            $missingRequired++
            $allPassed = $false
        }
    } catch {
        Write-Host " MISSING" -ForegroundColor Red
        $missingRequired++
        $allPassed = $false
    }
}

foreach ($pkg in $optionalPackages) {
    Write-Host "  $($pkg.Name) (optional)..." -NoNewline
    try {
        $packageCheck = python -c "import $($pkg.Import)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " INSTALLED" -ForegroundColor Green
        } else {
            Write-Host " NOT INSTALLED" -ForegroundColor Yellow
        }
    } catch {
        Write-Host " NOT INSTALLED" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($missingRequired -eq 0) {
    Write-Host "ALL REQUIRED DEPENDENCIES INSTALLED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can run the server with:" -ForegroundColor White
    Write-Host "  python server.py" -ForegroundColor Yellow
} else {
    Write-Host "MISSING $missingRequired REQUIRED PACKAGE(S)!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run start.bat to auto-install all packages:" -ForegroundColor White
    Write-Host "  start.bat" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Note: At least one PDF engine (wkhtmltopdf, pdflatex, or weasyprint)" -ForegroundColor Yellow
    Write-Host "      is required for PDF conversion." -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
