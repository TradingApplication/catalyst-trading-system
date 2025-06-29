#!/bin/bash
# Catalyst Trading System - Install Requirements
# Version: 1.0.0
# Last Updated: 2025-06-30

echo "🔧 Installing Catalyst Trading System Requirements"
echo "================================================"

# Create a minimal requirements file for testing
cat > requirements_minimal.txt << EOF
# Core dependencies
flask==3.0.0
gunicorn==21.2.0

# Alpaca for paper trading
alpaca-py==0.13.3

# API and data handling
requests==2.31.0
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.26.2

# Database
sqlalchemy==2.0.23

# For news and APIs
beautifulsoup4==4.12.2
EOF

echo "📦 Installing packages..."
pip install -r requirements_minimal.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "Now you can run:"
echo "  python verify_trading_config.py"
