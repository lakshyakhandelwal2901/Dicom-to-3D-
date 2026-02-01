#!/usr/bin/env python3
"""
Upload files to Google Drive (2TB storage)
Replaces/supplements DigitalOcean Spaces uploads
"""

import os
import sys
import pickle
from pathlib import Path
from datetime import datetime
from path_utils import get_token_path, get_project_root, ensure_in_project

def upload_file(file_path, folder_name="Dicom-3D-Medical-Imaging"):
    """Upload file to Google Drive"""
    ensure_in_project()
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        # Load credentials (adaptive path)
        token_path = get_token_path()
        if not token_path.exists():
            print("❌ Not authenticated!")
            print("Run: python setup_google_drive.py authenticate")
            return False
        
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        service = build('drive', 'v3', credentials=creds)
        
        # Find or create folder
        print(f"📁 Finding/creating folder: {folder_name}")
        folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=folder_query, fields='files(id, name)').execute()
        folders = results.get('files', [])
        
        if folders:
            folder_id = folders[0]['id']
            print(f"   ✓ Using existing folder: {folder_id}")
        else:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            print(f"   ✓ Created new folder: {folder_id}")
        
        # Upload file
        file_size_mb = file_path.stat().st_size / (1024**2)
        print(f"\n📤 Uploading: {file_path.name} ({file_size_mb:.1f} MB)")
        
        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(
            str(file_path),
            resumable=True,
            chunksize=10*1024*1024  # 10MB chunks
        )
        
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, size, webViewLink'
        )
        
        response = None
        last_progress = 0
        
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                if progress >= last_progress + 10:  # Update every 10%
                    print(f"   Progress: {progress}%")
                    last_progress = progress
        
        file_id = response.get('id')
        web_link = response.get('webViewLink')
        uploaded_size = int(response.get('size', 0)) / (1024**2)
        
        print(f"\n✅ Upload complete!")
        print(f"   File ID: {file_id}")
        print(f"   Size: {uploaded_size:.1f} MB")
        print(f"   Link: {web_link}")
        print("")
        
        # Save upload log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_id": file_id,
            "size_mb": uploaded_size,
            "folder": folder_name,
            "web_link": web_link
        }
        
        log_file = Path("gdrive_uploads.log")
        with open(log_file, 'a') as f:
            import json
            f.write(json.dumps(log_entry) + "\n")
        
        return file_id
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python gdrive_upload.py <file_path> [folder_name]")
        print("")
        print("Examples:")
        print("  python gdrive_upload.py output/model.ply")
        print("  python gdrive_upload.py output/brain.ply Medical-Scans")
        print("")
        return
    
    file_path = sys.argv[1]
    folder_name = sys.argv[2] if len(sys.argv) > 2 else "Dicom-3D-Medical-Imaging"
    
    upload_file(file_path, folder_name)


if __name__ == "__main__":
    main()
