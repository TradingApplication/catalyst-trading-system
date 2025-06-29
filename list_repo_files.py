#!/usr/bin/env python3
"""
Repository File Listing Tool
Lists all files and folders in the current directory tree
Writes output to project_index.txt
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def list_repository_contents():
    """List all files and folders in the repository and write to project_index.txt"""
    
    # Open the output file
    output_file = 'project_index.txt'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Get the current directory
            root_dir = Path.cwd()
            
            # Write header with timestamp
            f.write(f"Repository Index Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Repository Root: {root_dir}\n")
            f.write("=" * 80 + "\n")
            
            # Directories to skip
            skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', 'env', '.env', 
                         'node_modules', '.idea', '.vscode', '*.egg-info'}
            
            # File extensions to group
            file_groups = {
                'Python': ['.py'],
                'Docker': ['Dockerfile', '.dockerfile'],
                'Config': ['.yml', '.yaml', '.json', '.toml', '.ini', '.conf'],
                'Documentation': ['.md', '.txt', '.rst'],
                'Scripts': ['.sh', '.bash'],
                'Data': ['.csv', '.sql', '.db'],
                'Web': ['.html', '.css', '.js'],
                'Other': []
            }
            
            # Collect all files
            all_files = []
            all_dirs = []
            
            for dirpath, dirnames, filenames in os.walk(root_dir):
                # Skip hidden and cache directories
                dirnames[:] = [d for d in dirnames if not any(
                    d.startswith('.') and d != '.github' or 
                    d == skip_dir or 
                    d.endswith(skip_dir) 
                    for skip_dir in skip_dirs
                )]
                
                # Convert to relative path
                rel_dirpath = Path(dirpath).relative_to(root_dir)
                
                # Add directory if not root
                if str(rel_dirpath) != '.':
                    all_dirs.append(str(rel_dirpath))
                
                # Add files
                for filename in filenames:
                    if not filename.startswith('.') or filename in ['.env.example', '.gitignore']:
                        file_path = rel_dirpath / filename if str(rel_dirpath) != '.' else Path(filename)
                        all_files.append(str(file_path))
            
            # Sort directories and files
            all_dirs.sort()
            all_files.sort()
            
            # Write directory structure
            f.write("\n📁 DIRECTORY STRUCTURE:\n")
            f.write("-" * 40 + "\n")
            if all_dirs:
                for dir_name in all_dirs:
                    level = dir_name.count(os.sep)
                    indent = "  " * level
                    folder_name = os.path.basename(dir_name)
                    f.write(f"{indent}📁 {folder_name}/\n")
            else:
                f.write("No subdirectories found\n")
            
            # Group files by type
            grouped_files = {group: [] for group in file_groups}
            
            for file_path in all_files:
                categorized = False
                for group, extensions in file_groups.items():
                    if group == 'Docker' and 'Dockerfile' in file_path:
                        grouped_files[group].append(file_path)
                        categorized = True
                        break
                    elif any(file_path.endswith(ext) for ext in extensions):
                        grouped_files[group].append(file_path)
                        categorized = True
                        break
                
                if not categorized:
                    grouped_files['Other'].append(file_path)
            
            # Write files by category
            f.write("\n📄 FILES BY CATEGORY:\n")
            f.write("-" * 40 + "\n")
            
            for group, files in grouped_files.items():
                if files:
                    f.write(f"\n{group} Files ({len(files)}):\n")
                    for file_path in sorted(files):
                        f.write(f"  - {file_path}\n")
            
            # Write summary
            f.write("\n📊 SUMMARY:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Directories: {len(all_dirs)}\n")
            f.write(f"Total Files: {len(all_files)}\n")
            
            # Check for key files mentioned in the implementation document
            f.write("\n🔍 CHECKING FOR REQUIRED FILES:\n")
            f.write("-" * 40 + "\n")
            
            required_files = [
                'docker-compose.yml',
                '.env.example',
                'requirements.txt',
                'nginx.conf',
                'prometheus.yml',
                'init_database.sql',
                'Dockerfile.coordination',
                'Dockerfile.news',
                'Dockerfile.scanner',
                'Dockerfile.patterns',
                'Dockerfile.technical',
                'Dockerfile.trading',
                'Dockerfile.reporting',
                'Dockerfile.dashboard',
                'README.md'
            ]
            
            for req_file in required_files:
                exists = any(req_file in file_path for file_path in all_files)
                status = "✅" if exists else "❌"
                f.write(f"{status} {req_file}\n")
            
            # Create a simple text listing for easy copying
            f.write("\n📋 SIMPLE FILE LISTING (for copying):\n")
            f.write("-" * 40 + "\n")
            for file_path in all_files:
                f.write(f"{file_path}\n")
        
        # Print success message to console
        print(f"✅ Successfully created {output_file}")
        print(f"📊 Found {len(all_dirs)} directories and {len(all_files)} files")
        
    except IOError as e:
        print(f"❌ Error writing to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        list_repository_contents()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)