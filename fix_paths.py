#!/usr/bin/env python3
"""
Fix all hardcoded paths in services for DigitalOcean deployment
"""

import os
import re

# Files to fix
files_to_fix = [
    'dashboard_service.py',
    'coordination_service.py',
    'reporting_service.py',
    'news_service.py',
    'scanner_service.py',
    'pattern_service.py',
    'technical_service.py',
    'trading_service.py'
]

# Replacements to make
replacements = [
    # Database paths
    (r'/workspaces/trading-system/trading_system\.db', '/tmp//tmp/trading_system.db'),
    (r'/tmp/logs', '/tmp/logs'),
    
    # Generic paths
    (r'/workspaces/trading-system', '/tmp'),
    
    # Also fix any hardcoded workspace paths
    (r'os\.makedirs\(\'/workspaces[^\']*\',', "os.makedirs('/tmp/logs',"),
    (r'\.FileHandler\(\'/workspaces[^\']*\.log\'\)', ".FileHandler('/tmp//tmp/logs/service.log')")
]

def fix_file(filename):
    """Fix paths in a single file"""
    if not os.path.exists(filename):
        print(f"Skipping {filename} - file not found")
        return False
    
    print(f"Fixing {filename}...")
    
    # Read the file
    with open(filename, 'r') as f:
        content = f.read()
    
    # Apply replacements
    original = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Write back if changed
    if content != original:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"  ✓ Fixed paths in {filename}")
        return True
    else:
        print(f"  - No changes needed in {filename}")
        return False

# Fix all files
print("Fixing hardcoded paths for DigitalOcean deployment...\n")
fixed_count = 0

for filename in files_to_fix:
    if fix_file(filename):
        fixed_count += 1

print(f"\nFixed {fixed_count} files")

# Also create the import fix for database_utils.py if it doesn't exist
if not os.path.exists('database_utils.py'):
    print("\nCreating database_utils.py...")
    with open('database_utils.py', 'w') as f:
        f.write('''#!/usr/bin/env python3
"""Database utilities for Catalyst Trading System"""

import sqlite3
import os

class DatabaseServiceMixin:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.environ.get('DATABASE_PATH', '/tmp//tmp/trading_system.db')
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
''')
    print("✓ Created database_utils.py")

print("\nDone! Now commit and push these changes.")