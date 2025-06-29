#!/usr/bin/env python3
"""
Name of System: Catalyst Trading System
Name of file: wsgi.py
Version: 1.0.0
Last Updated: 2025-06-29
REVISION HISTORY:
  - v1.0.0 (2025-06-29) - WSGI entry point for deployment

Purpose: WSGI entry point for DigitalOcean App Platform
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# For now, just run the dashboard as the main web interface
from dashboard_service import TradingDashboardService

# Create the service instance
service = TradingDashboardService()

# Export the Flask app for WSGI
app = service.app

if __name__ == "__main__":
    # For local testing
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)