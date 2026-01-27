# 🚀 Backend Deployment Script (PowerShell)
# This script automates the deployment process for Windows

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🔥 Resume Analyzer Backend Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "firebase.json")) {
    Write-Host "❌ Error: firebase.json not found" -ForegroundColor Red
    Write-Host "📁 Please run this script from the backend/ directory" -ForegroundColor Yellow
    exit 1
}

# Check if Firebase CLI is installed
try {
    $null = firebase --version
    Write-Host "✅ Firebase CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ Firebase CLI not found" -ForegroundColor Red
    Write-Host "📦 Install with: npm install -g firebase-tools" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
Write-Host "🔐 Checking Firebase authentication..." -ForegroundColor Cyan
try {
    firebase login:list | Out-Null
    Write-Host "✅ Logged in to Firebase" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Firebase" -ForegroundColor Red
    Write-Host "🔑 Please run: firebase login" -ForegroundColor Yellow
    exit 1
}

# Check if dependencies are installed
if (-not (Test-Path "functions/node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
    Set-Location functions
    npm install
    Set-Location ..
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

# Check if OpenAI key is configured
Write-Host "🔑 Checking OpenAI API key configuration..." -ForegroundColor Cyan
$configResult = firebase functions:config:get openai.key 2>&1

if ($configResult -match "undefined" -or $configResult -eq "{}") {
    Write-Host ""
    Write-Host "⚠️  OpenAI API key not configured!" -ForegroundColor Yellow
    Write-Host ""
    $apiKey = Read-Host "Enter your OpenAI API key (sk-...)"
    
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "❌ No API key provided. Exiting." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🔧 Setting OpenAI API key..." -ForegroundColor Cyan
    firebase functions:config:set openai.key="$apiKey"
    Write-Host "✅ API key configured" -ForegroundColor Green
} else {
    Write-Host "✅ OpenAI API key is configured" -ForegroundColor Green
}

# Deploy functions
Write-Host ""
Write-Host "🚀 Deploying Cloud Functions..." -ForegroundColor Cyan
firebase deploy --only functions

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Check logs: firebase functions:log"
Write-Host "  2. Test from frontend"
Write-Host "  3. Monitor usage in Firebase Console"
Write-Host ""
