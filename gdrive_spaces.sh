#!/bin/bash
# Google Drive Manager - Replaces DigitalOcean Spaces
# All storage now uses FREE 2TB Google Drive

echo "Google Drive Manager (replaces DigitalOcean Spaces)"
echo "=================================================="
echo ""

case "$1" in
  upload)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: ./gdrive_spaces.sh upload <local_path> <remote_folder>"
      echo "Example: ./gdrive_spaces.sh upload output/results results/segmentations"
      exit 1
    fi
    echo "📤 Uploading to Google Drive: $3"
    python3 gdrive_upload.py "$2" "$3"
    ;;
    
  download)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: ./gdrive_spaces.sh download <remote_file_or_folder> <local_path>"
      echo "Example: ./gdrive_spaces.sh download 'datasets/medical_decathlon' data/"
      exit 1
    fi
    echo "📥 Downloading from Google Drive: $2"
    python3 gdrive_download.py "$2" "$3"
    ;;
    
  list)
    REMOTE_PATH="${2:-/}"
    echo "📋 Listing Google Drive: $REMOTE_PATH"
    python3 gdrive_list.py "$REMOTE_PATH"
    ;;
    
  du)
    REMOTE_PATH="${2:-/}"
    echo "💾 Storage usage: $REMOTE_PATH"
    python3 gdrive_list.py "$REMOTE_PATH" | grep -E "size|total"
    ;;
    
  help)
    echo "Google Drive Manager Commands:"
    echo ""
    echo "  upload <local> <remote>      Upload file/folder to Google Drive"
    echo "  download <remote> <local>    Download file/folder from Google Drive"
    echo "  list [path]                  List files in Google Drive folder"
    echo "  du [path]                    Show storage usage"
    echo ""
    echo "Examples:"
    echo "  ./gdrive_spaces.sh upload output/brain_model results/models/"
    echo "  ./gdrive_spaces.sh download 'datasets/medical_decathlon' data/"
    echo "  ./gdrive_spaces.sh list datasets"
    ;;
    
  *)
    echo "Usage: ./gdrive_spaces.sh [upload|download|list|du|help]"
    echo "       ./gdrive_spaces.sh help"
    exit 1
    ;;
esac
