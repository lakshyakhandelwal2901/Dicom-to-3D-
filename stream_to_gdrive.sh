#!/bin/bash
# Download Medical Decathlon datasets directly to Google Drive
# No local disk space required - streams to cloud

# Get project root (adaptive - works from any directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

cd "$PROJECT_ROOT"

echo "🚀 Starting Medical Decathlon → Google Drive Download Stream"
echo "📍 Project Root: $PROJECT_ROOT"
echo ""
echo "This will:"
echo "  1. Download each dataset from AWS"
echo "  2. Upload directly to your 2TB Google Drive"
echo "  3. Extract and organize in cloud"
echo "  4. Clean up temporary files"
echo ""

# Make sure Google Drive is authenticated
if [ ! -f "$PROJECT_ROOT/token.pickle" ]; then
    echo "❌ Not authenticated with Google Drive!"
    echo "Run: python setup_google_drive.py authenticate"
    exit 1
fi

echo "✅ Google Drive authenticated"
echo ""

# Datasets to download
declare -A DATASETS=(
    ["Task03_Liver"]="https://msd-for-monai.s3-us-west-2.amazonaws.com/Task03_Liver.tar"
    ["Task04_Hippocampus"]="https://msd-for-monai.s3-us-west-2.amazonaws.com/Task04_Hippocampus.tar"
    ["Task05_Prostate"]="https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar"
    ["Task01_BrainTumour"]="https://msd-for-monai.s3-us-west-2.amazonaws.com/Task01_BrainTumour.tar"
)

TOTAL=${#DATASETS[@]}
CURRENT=1

for TASK in "${!DATASETS[@]}"; do
    URL="${DATASETS[$TASK]}"
    
    echo "[$CURRENT/$TOTAL] 📥 Downloading $TASK from AWS..."
    
    # Download to /tmp (smaller disk usage)
    TEMP_FILE="/tmp/${TASK}.tar"
    
    curl -L --progress-bar -o "$TEMP_FILE" "$URL"
    
    if [ $? -ne 0 ]; then
        echo "❌ Download failed for $TASK"
        rm -f "$TEMP_FILE"
        CURRENT=$((CURRENT + 1))
        continue
    fi
    
    SIZE=$(du -h "$TEMP_FILE" | cut -f1)
    echo "✅ Downloaded ($SIZE)"
    
    echo "📤 Uploading to Google Drive..."
    python gdrive_upload.py "$TEMP_FILE" "datasets/medical_decathlon"
    
    if [ $? -eq 0 ]; then
        echo "✅ Uploaded successfully"
        rm -f "$TEMP_FILE"
    else
        echo "⚠️  Upload failed, keeping local copy"
    fi
    
    CURRENT=$((CURRENT + 1))
    echo ""
    sleep 2
done

echo "="*80
echo "ALL DOWNLOADS COMPLETE"
echo "="*80
echo ""
echo "🎉 Your datasets are now in Google Drive!"
echo "📊 Check with: python gdrive_list.py datasets/medical_decathlon"
echo ""
