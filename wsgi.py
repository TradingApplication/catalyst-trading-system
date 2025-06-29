#!/usr/bin/env python3
"""
WSGI entry point for DigitalOcean App Platform
"""

import os
import sys

# Ensure the app can find modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the minimal dashboard app
    from dashboard_minimal import app
    print("Successfully imported dashboard_minimal app")
except ImportError as e:
    print(f"Error importing dashboard_minimal: {e}")
    # Fallback to a basic app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({"status": "minimal app running", "error": str(e)})
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})

# This is what gunicorn looks for
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)