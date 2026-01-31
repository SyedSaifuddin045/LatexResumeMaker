# Quick Setup Script for API Key Security
# Run this if you're setting up the project for the first time

Write-Host "🔐 API Key Security Setup" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if secrets.json already exists
if (Test-Path "secrets.json") {
    Write-Host "✅ secrets.json already exists" -ForegroundColor Green
} else {
    # Check if settings.json has a real API key
    if (Test-Path "settings.json") {
        Write-Host "ℹ️  Found existing settings.json, running migration..." -ForegroundColor Yellow
        python migrate_api_key.py
    } else {
        # Create new secrets.json from template
        Write-Host "📝 Creating secrets.json from template..." -ForegroundColor Yellow
        Copy-Item "secrets.example.json" "secrets.json"
        Write-Host "✅ Created secrets.json" -ForegroundColor Green
        Write-Host "⚠️  Please edit secrets.json and add your actual API key!" -ForegroundColor Yellow
    }
}

# Create settings.json if it doesn't exist
if (-not (Test-Path "settings.json")) {
    Write-Host "📝 Creating settings.json from template..." -ForegroundColor Yellow
    Copy-Item "settings.example.json" "settings.json"
    Write-Host "✅ Created settings.json" -ForegroundColor Green
}

Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit secrets.json with your actual API key"
Write-Host "2. Run your application normally"
Write-Host "3. Read SECURITY.md for more information"
Write-Host ""
Write-Host "⚠️  IMPORTANT: Never commit secrets.json to Git!" -ForegroundColor Red
