# DICOM to 3D Converter

Convert DICOM medical imaging files to 3D models.

## Quick Start

### 1. Setup
```bash
git clone https://github.com/lakshyakhandelwal2901/Dicom-to-3D-.git
cd Dicom-to-3D-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Sample 3D Model
```bash
python3 generate_3d_model.py
```

## Google Drive Integration

Upload/download files to Google Drive for cloud storage:

```bash
# List files
python3 gdrive_list.py

# Upload
python3 gdrive_upload.py <file> <folder>

# Download
python3 gdrive_download.py <filename> <destination>
```

## Project Structure

```
Dicom-to-3D-/
├── generate_3d_model.py    # Create 3D models from DICOM
├── gdrive_upload.py         # Upload to Google Drive
├── gdrive_download.py       # Download from Google Drive
├── gdrive_list.py           # List Google Drive files
├── path_utils.py            # Path handling utilities
├── credentials.json         # Google Drive credentials (gitignored)
└── token.pickle             # Google Drive token (gitignored)
```

## Status

🚧 **Project Reset - Clean Slate**

Ready for fresh implementation of DICOM to 3D conversion pipeline.
