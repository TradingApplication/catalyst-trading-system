#!/usr/bin/env python3
"""
Name of System: Catalyst Trading System
Name of file: app_config.py
Version: 1.0.0
Last Updated: 2025-06-29
REVISION HISTORY:
  - v1.0.0 (2025-06-29) - Environment-aware configuration

Purpose: Handle different paths for local vs DigitalOcean deployment
"""

import os

# Detect if we're running on DigitalOcean App Platform
IS_DIGITALOCEAN = (
    os.path.exists('/workspace') or 
    os.environ.get('DYNO') is not None or
    os.environ.get('PORT', '').isdigit() and int(os.environ.get('PORT', 0)) == 8080
)

# Set paths based on environment
if IS_DIGITALOCEAN:
    # DigitalOcean App Platform - only /tmp is writable
    BASE_DIR = '/tmp'
    LOG_DIR = '/tmp/logs'
    DB_PATH = '/tmp//tmp/trading_system.db'
else:
    # Local development
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    DB_PATH = os.path.join(BASE_DIR, '/tmp/trading_system.db')

# Create directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)

print(f"Running on {'DigitalOcean' if IS_DIGITALOCEAN else 'Local'}")
print(f"Log directory: {LOG_DIR}")
print(f"Database path: {DB_PATH}")