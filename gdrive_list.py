#!/usr/bin/env python3
"""
List files in Google Drive
"""

import os
import sys
import pickle
from pathlib import Path
from datetime import datetime
from path_utils import get_token_path, ensure_in_project

def list_files(folder_name=None, max_results=50):
    """List files in Google Drive"""
    ensure_in_project()
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        # Load credentials (adaptive)
        token_path = get_token_path()
        if not token_path.exists():
            print("❌ Not authenticated!")
            print("Run: python setup_google_drive.py authenticate")
            return False
        
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        service = build('drive', 'v3', credentials=creds)
        
        # Build query
        if folder_name:
            print(f"📁 Listing files in folder: {folder_name}\n")
            folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = service.files().list(q=folder_query, fields='files(id)').execute()
            folders = results.get('files', [])
            
            if not folders:
                print(f"❌ Folder not found: {folder_name}")
                return False
            
            folder_id = folders[0]['id']
            query = f"'{folder_id}' in parents and trashed=false"
        else:
            print(f"📁 Listing all files\n")
            query = "trashed=false"
        
        # Get files
        results = service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, size, modifiedTime, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("No files found.")
            return True
        
        print(f"Found {len(files)} files:\n")
        print("-" * 100)
        print(f"{'Name':<40} {'Size':<12} {'Modified':<20} {'File ID':<30}")
        print("-" * 100)
        
        total_size = 0
        
        for file in files:
            name = file.get('name', 'Unknown')[:38]
            file_id = file.get('id', 'Unknown')[:28]
            size = int(file.get('size', 0))
            modified = file.get('modifiedTime', '')[:19].replace('T', ' ')
            mime_type = file.get('mimeType', '')
            
            # Format size
            if mime_type == 'application/vnd.google-apps.folder':
                size_str = "<folder>"
            elif size < 1024:
                size_str = f"{size} B"
            elif size < 1024**2:
                size_str = f"{size/1024:.1f} KB"
            elif size < 1024**3:
                size_str = f"{size/(1024**2):.1f} MB"
            else:
                size_str = f"{size/(1024**3):.1f} GB"
            
            print(f"{name:<40} {size_str:<12} {modified:<20} {file_id:<30}")
            
            if mime_type != 'application/vnd.google-apps.folder':
                total_size += size
        
        print("-" * 100)
        total_gb = total_size / (1024**3)
        print(f"Total: {len(files)} files, {total_gb:.2f} GB")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ List failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    folder_name = None
    max_results = 50
    
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            max_results = int(sys.argv[1])
        else:
            folder_name = sys.argv[1]
    
    if len(sys.argv) > 2:
        max_results = int(sys.argv[2])
    
    list_files(folder_name, max_results)


if __name__ == "__main__":
    main()
