#!/usr/bin/env python3
"""
Ultra simple server to test DigitalOcean deployment
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

PORT = int(os.environ.get('PORT', 8080))

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'healthy'}).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Catalyst Trading System - Working!</h1>')

print(f"Starting simple server on port {PORT}")
server = HTTPServer(('0.0.0.0', PORT), SimpleHandler)
print(f"Server listening on 0.0.0.0:{PORT}")
server.serve_forever()