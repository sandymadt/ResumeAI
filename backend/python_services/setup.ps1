# Setup Script for Resume Text Extraction Module
# Run this script to set up the environment

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Resume Text Extraction Module Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+ first." -ForegroundColor Red
    exit 1
}

# Navigate to the correct directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`nCurrent directory: $(Get-Location)" -ForegroundColor Cyan

# Check if requirements.txt exists
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
Write-Host "This may take a minute...`n" -ForegroundColor Gray

try {
    python -m pip install --upgrade pip | Out-Null
    python -m pip install -r requirements.txt
    
    Write-Host "`n✅ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow

try {
    python -c "import pdfplumber; import mammoth; print('✅ All modules imported successfully')"
    Write-Host "✅ Installation verified!" -ForegroundColor Green
} catch {
    Write-Host "❌ Verification failed" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "`nRunning tests..." -ForegroundColor Yellow
Write-Host "This will verify that everything works correctly.`n" -ForegroundColor Gray

try {
    python test_text_extractor.py
    Write-Host "`n✅ All tests passed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Some tests failed" -ForegroundColor Red
    Write-Host "The module may still work, but please review the errors." -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nYou can now use the text extraction module:" -ForegroundColor Green
Write-Host "  • Quick test: python text_extractor.py <resume.pdf>" -ForegroundColor White
Write-Host "  • Examples: python sample_usage.py" -ForegroundColor White
Write-Host "  • In code: from text_extractor import extract_text" -ForegroundColor White

Write-Host "`nFor more information, see README.md`n" -ForegroundColor Gray
