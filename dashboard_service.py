"""
Catalyst Trading System
Name of file: dashboard_service.py
Version: 1.0.0
Last Updated: 2025-06-30
REVISION HISTORY:
  - v1.0.0 (2025-06-30) - Wrapper for DigitalOcean deployment
"""

# Import the Flask app from app.py
from app_v200 import app

# This makes 'app' available when gunicorn runs dashboard_service:app