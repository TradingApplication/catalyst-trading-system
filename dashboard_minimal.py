#!/usr/bin/env python3
"""
Name of System: Catalyst Trading System
Name of file: dashboard_minimal.py
Version: 1.0.0
Last Updated: 2025-06-29
REVISION HISTORY:
  - v1.0.0 (2025-06-29) - Minimal standalone dashboard for initial deployment

Purpose: Simplified dashboard that runs without other services
"""

import os
from flask import Flask, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Simple HTML template
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Catalyst Trading System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .status { padding: 10px; background: #e8f5e9; border-radius: 4px; margin: 10px 0; }
        .service { display: inline-block; margin: 10px; padding: 10px 20px; background: #f0f0f0; border-radius: 4px; }
        .healthy { background: #4CAF50; color: white; }
        .offline { background: #f44336; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Catalyst Trading System Dashboard</h1>
        <div class="status">
            <h2>System Status</h2>
            <p><strong>Status:</strong> Deployment Successful! 🎉</p>
            <p><strong>Time:</strong> <span id="time">{{ time }}</span></p>
            <p><strong>Environment:</strong> DigitalOcean App Platform</p>
        </div>
        
        <h2>Services</h2>
        <div>
            <div class="service healthy">Dashboard - Online</div>
            <div class="service offline">Coordination - Not Deployed</div>
            <div class="service offline">Trading - Not Deployed</div>
            <div class="service offline">News - Not Deployed</div>
            <div class="service offline">Scanner - Not Deployed</div>
            <div class="service offline">Pattern - Not Deployed</div>
        </div>
        
        <h2>Next Steps</h2>
        <ol>
            <li>✅ Basic deployment working</li>
            <li>⏳ Deploy additional services</li>
            <li>⏳ Configure database connection</li>
            <li>⏳ Add API keys for trading</li>
        </ol>
        
        <p style="margin-top: 30px; color: #666;">
            This is a minimal deployment to verify the system is working on DigitalOcean App Platform.
        </p>
    </div>
    
    <script>
        // Update time every second
        setInterval(() => {
            fetch('/api/time')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('time').innerText = data.time;
                });
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML, time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "dashboard-minimal",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/time')
def api_time():
    """Get current time"""
    return jsonify({
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify({
        "status": "operational",
        "message": "Minimal dashboard deployed successfully",
        "services": {
            "dashboard": "healthy",
            "coordination": "not_deployed",
            "trading": "not_deployed",
            "news": "not_deployed",
            "scanner": "not_deployed",
            "pattern": "not_deployed"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)