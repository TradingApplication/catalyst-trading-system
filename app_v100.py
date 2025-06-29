#!/usr/bin/env python3
"""
Name of System: Catalyst Trading System
Name of file: app.py
Version: 1.0.0
Last Updated: 2025-06-29
REVISION HISTORY:
  - v1.0.0 (2025-06-29) - Entry point for DigitalOcean deployment

Purpose: Main entry point that routes to the appropriate service
"""

import os
import sys

# Determine which service to run based on environment variable
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'dashboard').lower()
PORT = int(os.environ.get('PORT', 8080))

print(f"Starting Catalyst Trading System - Service: {SERVICE_NAME} on port {PORT}")

if SERVICE_NAME == 'coordination':
    from coordination_service import NewsDriverCoordinationService
    service = NewsDriverCoordinationService()
    # Override the port
    service.app.run(host='0.0.0.0', port=PORT, debug=False)
    
elif SERVICE_NAME == 'dashboard' or SERVICE_NAME == 'web_dashboard':
    from dashboard_service_v100 import TradingDashboardService
    service = TradingDashboardService()
    # Override the port
    service.app.run(host='0.0.0.0', port=PORT, debug=False)
    
elif SERVICE_NAME == 'reporting':
    from reporting_service import TradingAccuracyReporting
    service = TradingAccuracyReporting()
    # Override the port
    service.app.run(host='0.0.0.0', port=PORT, debug=False)
    
elif SERVICE_NAME == 'news' or SERVICE_NAME == 'news_collection':
    # Import news service when available
    print("News service not yet implemented in app.py")
    sys.exit(1)
    
elif SERVICE_NAME == 'scanner' or SERVICE_NAME == 'security_scanner':
    # Import scanner service when available
    print("Scanner service not yet implemented in app.py")
    sys.exit(1)
    
else:
    print(f"Unknown service: {SERVICE_NAME}")
    print("Available services: coordination, dashboard, reporting")
    sys.exit(1)