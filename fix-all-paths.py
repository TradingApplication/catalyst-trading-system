#!/usr/bin/env python3
"""
Catalyst Trading System
Name of file: fix_all_paths.py
Version: 1.0.0
Last Updated: 2025-06-30
REVISION HISTORY:
  - v1.0.0 (2025-06-30) - Initial release to fix DigitalOcean path issues
"""

import os
import re
import glob

def fix_paths_in_file(filepath):
    """Replace hardcoded paths with /tmp for DigitalOcean compatibility"""
    
    replacements = {
        # Log paths
        r'/tmp/logs': '/tmp/logs',
        r'/tmp/logs': '/tmp/logs',
        r'\/tmp/logs': '/tmp/logs',
        r'/tmp/logs/': '/tmp//tmp/logs/',
        
        # Data paths
        r'/tmp/data': '/tmp/data',
        r'/tmp/data': '/tmp/data',
        r'\/tmp/data': '/tmp/data',
        r'/tmp/data/': '/tmp//tmp/data/',
        
        # Database paths
        r'trading_system\.db': '/tmp//tmp/trading_system.db',
        r'catalyst\.db': '/tmp//tmp/catalyst.db',
        r'\./\*.db': '/tmp/*.db',
        
        # Cache paths
        r'\/tmp/cache': '/tmp/cache',
        r'/tmp/__pycache__': '/tmp//tmp/__pycache__',
        
        # Pattern data
        r'pattern_/tmp/data/': '/tmp/pattern_/tmp/data/',
        r'\/tmp/pattern_data': '/tmp/pattern_data',
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        for old_path, new_path in replacements.items():
            if re.search(old_path, content):
                content = re.sub(old_path, new_path, content)
                changes_made.append(f"  - {old_path} → {new_path}")
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed paths in: {filepath}")
            for change in changes_made:
                print(change)
            return True
        else:
            print(f"⏭️  No changes needed in: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def create_directory_structure():
    """Create necessary directories in /tmp"""
    directories = [
        '/tmp/logs',
        '/tmp/data',
        '/tmp/pattern_data',
        '/tmp/cache',
        '/tmp/exports',
        '/tmp/reports'
    ]
    
    print("\n📁 Creating directory structure...")
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")

def main():
    print("🔧 Catalyst Trading System - Path Fixer for DigitalOcean")
    print("=" * 50)
    
    # Create directory structure first
    create_directory_structure()
    
    # Find all Python files
    print("\n🔍 Scanning for Python files...")
    python_files = []
    
    # Add specific service files
    service_files = [
        'dashboard_service.py',
        'trading_service.py',
        'news_service.py',
        'scanner_service.py',
        'pattern_analysis.py',
        'config.py',
        'database.py',
        'app.py',
        'wsgi.py',
        'dashboard_minimal.py'
    ]
    
    # Also scan for all .py files in current directory and subdirectories
    for pattern in ['*.py', 'services/*.py', 'utils/*.py', 'models/*.py']:
        python_files.extend(glob.glob(pattern, recursive=True))
    
    # Remove duplicates
    python_files = list(set(python_files))
    
    print(f"Found {len(python_files)} Python files to check")
    
    # Process each file
    fixed_count = 0
    for filepath in sorted(python_files):
        if os.path.exists(filepath):
            if fix_paths_in_file(filepath):
                fixed_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Path fixing complete!")
    print(f"📊 Fixed {fixed_count} files out of {len(python_files)} checked")
    
    # Create a path configuration file
    print("\n📝 Creating path_config.py...")
    path_config_content = '''"""
Catalyst Trading System
Name of file: path_config.py
Version: 1.0.0
Last Updated: 2025-06-30
REVISION HISTORY:
  - v1.0.0 (2025-06-30) - Centralized path configuration for DigitalOcean
"""

import os

# Detect if running on DigitalOcean (or any read-only filesystem)
IS_DIGITALOCEAN = not os.access('/workspaces', os.W_OK) if os.path.exists('/workspaces') else True

# Base paths
BASE_PATH = '/tmp' if IS_DIGITALOCEAN else '.'
LOG_PATH = os.path.join(BASE_PATH, 'logs')
DATA_PATH = os.path.join(BASE_PATH, 'data')
PATTERN_DATA_PATH = os.path.join(BASE_PATH, 'pattern_data')
CACHE_PATH = os.path.join(BASE_PATH, 'cache')
EXPORT_PATH = os.path.join(BASE_PATH, 'exports')
REPORT_PATH = os.path.join(BASE_PATH, 'reports')

# Database
DATABASE_PATH = os.path.join(BASE_PATH, '/tmp/trading_system.db')

# Ensure directories exist
for path in [LOG_PATH, DATA_PATH, PATTERN_DATA_PATH, CACHE_PATH, EXPORT_PATH, REPORT_PATH]:
    os.makedirs(path, exist_ok=True)

print(f"📁 Path Configuration:")
print(f"  - Base: {BASE_PATH}")
print(f"  - Logs: {LOG_PATH}")
print(f"  - Database: {DATABASE_PATH}")
'''
    
    with open('path_config.py', 'w') as f:
        f.write(path_config_content)
    
    print("✅ Created path_config.py")
    print("\n🎉 All done! Your app is ready for DigitalOcean deployment!")

if __name__ == "__main__":
    main()
