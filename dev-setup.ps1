# Aegis Lens Development Environment Setup Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AEGIS LENS DEV ENVIRONMENT SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        if (Get-Command $Command) {
            return $true
        }
    }
    catch {
        return $false
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js installed: $nodeVersion" -ForegroundColor Green
    $majorVersion = [int]($nodeVersion -replace 'v', '').Split('.')[0]
    if ($majorVersion -lt 20) {
        Write-Host "[FAIL] Node.js version must be 20+. Current: $nodeVersion" -ForegroundColor Red
        Write-Host "Please install Node.js 20+ from https://nodejs.org/" -ForegroundColor Yellow
    }
} else {
    Write-Host "[FAIL] Node.js not found" -ForegroundColor Red
    Write-Host "Please install Node.js 20+ from https://nodejs.org/" -ForegroundColor Yellow
}

# Check Python
Write-Host ""
Write-Host "Checking Python..." -ForegroundColor Yellow
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Host "[OK] Python installed: $pythonVersion" -ForegroundColor Green
    $versionParts = $pythonVersion -replace 'Python ', '' -split '\.'
    $majorVersion = [int]$versionParts[0]
    $minorVersion = [int]$versionParts[1]
    if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 11)) {
        Write-Host "[FAIL] Python version must be 3.11+. Current: $pythonVersion" -ForegroundColor Red
        Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    }
} else {
    Write-Host "[FAIL] Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
}

# Check Rust
Write-Host ""
Write-Host "Checking Rust..." -ForegroundColor Yellow
if (Test-Command "rustc") {
    $rustVersion = rustc --version
    Write-Host "[OK] Rust installed: $rustVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Rust not found" -ForegroundColor Red
    Write-Host "Please install Rust from https://rustup.rs/" -ForegroundColor Yellow
}

# Check Docker
Write-Host ""
Write-Host "Checking Docker..." -ForegroundColor Yellow
if (Test-Command "docker") {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker installed: $dockerVersion" -ForegroundColor Green
    try {
        docker ps | Out-Null
        Write-Host "[OK] Docker is running" -ForegroundColor Green
    }
    catch {
        Write-Host "[FAIL] Docker is not running" -ForegroundColor Red
        Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
    }
} else {
    Write-Host "[FAIL] Docker not found" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
}

# Check wasm-pack
Write-Host ""
Write-Host "Checking wasm-pack..." -ForegroundColor Yellow
if (Test-Command "wasm-pack") {
    $wasmPackVersion = wasm-pack --version
    Write-Host "[OK] wasm-pack installed: $wasmPackVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] wasm-pack not found" -ForegroundColor Red
    Write-Host "Installing wasm-pack via cargo..." -ForegroundColor Yellow
    cargo install wasm-pack
    Write-Host "[OK] wasm-pack installed" -ForegroundColor Green
}

# Check Rust WASM target
Write-Host ""
Write-Host "Checking Rust WASM target..." -ForegroundColor Yellow
$wasmTarget = rustup target list --installed | Select-String "wasm32-unknown-unknown"
if ($wasmTarget) {
    Write-Host "[OK] wasm32-unknown-unknown target installed" -ForegroundColor Green
} else {
    Write-Host "[FAIL] wasm32-unknown-unknown target not found" -ForegroundColor Red
    Write-Host "Installing wasm32-unknown-unknown target..." -ForegroundColor Yellow
    rustup target add wasm32-unknown-unknown
    Write-Host "[OK] wasm32-unknown-unknown target installed" -ForegroundColor Green
}

# Check Git
Write-Host ""
Write-Host "Checking Git..." -ForegroundColor Yellow
if (Test-Command "git") {
    $gitVersion = git --version
    Write-Host "[OK] Git installed: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Git not found" -ForegroundColor Red
    Write-Host "Please install Git from https://git-scm.com/downloads" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: npm install" -ForegroundColor White
Write-Host "2. Run: pip install -r requirements.txt" -ForegroundColor White
Write-Host "3. Run: docker-compose up -d" -ForegroundColor White
Write-Host "4. Run: npm run dev" -ForegroundColor White
Write-Host ""
