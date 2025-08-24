#!/bin/bash

# Setup script for Selenium WebDriver on macOS

echo "Setting up Selenium for HR&CE Temple Scraper..."
echo "============================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install from https://brew.sh"
    exit 1
fi

# Install Chrome if not present
if ! [ -d "/Applications/Google Chrome.app" ]; then
    echo "📦 Installing Google Chrome..."
    brew install --cask google-chrome
else
    echo "✅ Google Chrome already installed"
fi

# Install ChromeDriver
echo "📦 Installing ChromeDriver..."
brew install --cask chromedriver

# Allow ChromeDriver in Security settings
echo "🔓 Allowing ChromeDriver in macOS security..."
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver 2>/dev/null || true

# Install Python packages
echo "📦 Installing Python packages..."
pip install selenium webdriver-manager

echo ""
echo "✅ Setup complete!"
echo ""
echo "You can now run the scraper with:"
echo "  python hrce_selenium_scraper.py"
echo ""
echo "If you get security warnings, go to:"
echo "  System Preferences > Security & Privacy > General"
echo "  And click 'Allow Anyway' for chromedriver"