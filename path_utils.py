#!/usr/bin/env python3
"""
Path Utilities - Adaptive paths for any location
Handles relative/absolute paths, script locations, etc.
"""

import os
import sys
from pathlib import Path

def get_project_root():
    """Get project root directory (where this script is or parent)"""
    # If called from within project
    if Path('setup_google_drive.py').exists() or Path('gdrive_upload.py').exists():
        return Path.cwd()
    
    # If script is in project root
    script_dir = Path(__file__).parent
    if (script_dir / 'gdrive_upload.py').exists():
        return script_dir
    
    # Fallback to cwd
    return Path.cwd()

def ensure_in_project():
    """Ensure we're in the project directory"""
    root = get_project_root()
    if root != Path.cwd():
        os.chdir(root)
    return root

def get_token_path():
    """Get token.pickle path (adaptive)"""
    return get_project_root() / 'token.pickle'

def get_credentials_path():
    """Get credentials.json path (adaptive)"""
    return get_project_root() / 'credentials.json'

def get_src_dir():
    """Get src/ directory path (adaptive)"""
    src = get_project_root() / 'src'
    if src.exists():
        return src
    return None

def get_data_dir():
    """Get data/ directory path (adaptive)"""
    return get_project_root() / 'data'

def get_output_dir():
    """Get output/ directory path (adaptive)"""
    output = get_project_root() / 'output'
    output.mkdir(exist_ok=True)
    return output

def add_src_to_path():
    """Add src/ to Python path if it exists"""
    src_dir = get_src_dir()
    if src_dir and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

def find_gdrive_script(script_name):
    """Find a Google Drive utility script"""
    root = get_project_root()
    script_path = root / script_name
    if script_path.exists():
        return script_path
    return None

def run_gdrive_script(script_name, *args):
    """Run a Google Drive utility script with proper path handling"""
    import subprocess
    
    root = get_project_root()
    script_path = root / script_name
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_name}")
    
    cmd = ['python3', str(script_path)] + list(args)
    result = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
    
    return result

# Initialize on import
if __name__ != '__main__':
    ensure_in_project()
    add_src_to_path()
