#!/usr/bin/env python3
"""
Simple Flask app for DigitalOcean deployment
"""

import os
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Simple HTML template
SIMPLE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Catalyst Trading System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Catalyst Trading System</h1>
        <p class="success">✅ Deployment Successful!</p>
        <p>Running on DigitalOcean App Platform</p>
        <hr>
        <p>Next steps: Fix permission issues in services</p>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(SIMPLE_HTML)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/status')
def status():
    return jsonify({
        "app": "catalyst-trading-system",
        "status": "running",
        "environment": "digitalocean"
    })

# Gunicorn entry point
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)