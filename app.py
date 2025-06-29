#!/usr/bin/env python3
"""
Simple Flask app for DigitalOcean deployment
"""

import os
import sys

# Try to import the full dashboard, fall back to minimal if it fails
try:
    # First, fix the paths for DigitalOcean
    if os.path.exists('/workspace'):
        # We're on DigitalOcean - monkey patch the paths
        import dashboard_service
        dashboard_service.LOG_DIR = '/tmp/logs'
        dashboard_service.DB_PATH = '/tmp/trading_system.db'
    
    from dashboard_minimal import app
    print("Using dashboard_minimal (no file permission issues)")
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to simple app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({
            "status": "running",
            "message": "Catalyst Trading System - Basic Mode",
            "error": str(e)
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})

# Gunicorn entry point
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)