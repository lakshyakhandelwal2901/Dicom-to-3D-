#!/usr/bin/env python3
"""
Download files from Google Drive
"""

import os
import sys
import pickle
from pathlib import Path
from path_utils import get_token_path, ensure_in_project

def download_file(file_id_or_name, output_path=None):
    """Download file from Google Drive by ID or name"""
    ensure_in_project()
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        import io
        
        # Load credentials (adaptive path)
        token_path = get_token_path()
        if not token_path.exists():
            print("❌ Not authenticated!")
            print("Run: python setup_google_drive.py authenticate")
            return False
        
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        service = build('drive', 'v3', credentials=creds)
        
        # If input looks like a name, search for it
        if not file_id_or_name.startswith('1'):  # Google Drive IDs start with 1
            print(f"🔍 Searching for file: {file_id_or_name}")
            query = f"name='{file_id_or_name}' and trashed=false"
            results = service.files().list(
                q=query,
                fields='files(id, name, size)',
                pageSize=10
            ).execute()
            files = results.get('files', [])
            
            if not files:
                print(f"❌ File not found: {file_id_or_name}")
                return False
            
            if len(files) > 1:
                print(f"⚠️  Multiple files found ({len(files)}). Using first:")
                for i, f in enumerate(files, 1):
                    size_mb = int(f.get('size', 0)) / (1024**2)
                    print(f"   {i}. {f['name']} ({size_mb:.1f} MB)")
                print("")
            
            file_id = files[0]['id']
            file_name = files[0]['name']
        else:
            file_id = file_id_or_name
            # Get file metadata
            file_metadata = service.files().get(fileId=file_id, fields='name, size').execute()
            file_name = file_metadata.get('name', 'downloaded_file')
        
        # Determine output path
        if output_path is None:
            output_path = Path(file_name)
        else:
            output_path = Path(output_path)
            if output_path.is_dir():
                output_path = output_path / file_name
        
        # Get file size
        file_metadata = service.files().get(fileId=file_id, fields='size').execute()
        file_size = int(file_metadata.get('size', 0))
        file_size_mb = file_size / (1024**2)
        
        print(f"\n📥 Downloading: {file_name} ({file_size_mb:.1f} MB)")
        print(f"   Saving to: {output_path}")
        
        # Download
        request = service.files().get_media(fileId=file_id)
        
        with open(output_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            last_progress = 0
            
            while done is False:
                status, done = downloader.next_chunk()
                progress = int(status.progress() * 100)
                if progress >= last_progress + 10:
                    print(f"   Progress: {progress}%")
                    last_progress = progress
        
        print(f"\n✅ Download complete!")
        print(f"   File: {output_path.absolute()}")
        print(f"   Size: {file_size_mb:.1f} MB")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python gdrive_download.py <file_id_or_name> [output_path]")
        print("")
        print("Examples:")
        print("  python gdrive_download.py 1ABC123xyz456...")
        print("  python gdrive_download.py model.ply")
        print("  python gdrive_download.py model.ply output/")
        print("")
        return
    
    file_id_or_name = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    download_file(file_id_or_name, output_path)


if __name__ == "__main__":
    main()
