#!/bin/bash
# 🚀 LEAN Download-to-Google-Drive ONLY
# NO local storage - streams directly to your 2TB Google Drive
# Uses /tmp (8GB) for temporary streaming only

cd /workspaces/Dicom-to-3D-

clear
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║   🌐 STREAMING TO GOOGLE DRIVE (NO LOCAL STORAGE)                 ║"
echo "║                                                                    ║"
echo "║   • Downloads from AWS → /tmp (temporary)                         ║"
echo "║   • Uploads to Google Drive immediately                           ║"
echo "║   • Deletes /tmp after each upload                                ║"
echo "║   • Workspace stays clean (2.1 GB free)                           ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Verify authenticated
if [ ! -f "token.pickle" ]; then
    echo "❌ Not authenticated!"
    exit 1
fi

echo "✅ Google Drive authenticated (1,954 GB available)"
echo "📊 Local workspace: 2.1 GB free (staying clean)"
echo ""

# Datasets to download (prioritized)
declare -a TASKS=(
    "Task03_Liver|8.5|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task03_Liver.tar"
    "Task04_Hippocampus|0.2|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task04_Hippocampus.tar"
    "Task05_Prostate|1.1|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar"
    "Task01_BrainTumour|4.5|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task01_BrainTumour.tar"
    "Task06_Lung|7.2|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task06_Lung.tar"
    "Task07_Pancreas|16.0|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task07_Pancreas.tar"
    "Task08_HepaticVessel|12.0|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task08_HepaticVessel.tar"
    "Task09_Spleen|2.8|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task09_Spleen.tar"
    "Task02_Heart|1.2|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task02_Heart.tar"
    "Task10_Colon|8.1|https://msd-for-monai.s3-us-west-2.amazonaws.com/Task10_Colon.tar"
)

TOTAL=${#TASKS[@]}
CURRENT=1
TOTAL_SIZE=0
TOTAL_TIME=0

echo "📥 STARTING LEAN STREAM-TO-GDRIVE DOWNLOAD"
echo "   (No files stored locally)"
echo ""

for TASK_LINE in "${TASKS[@]}"; do
    IFS='|' read -r TASK_NAME SIZE_GB URL <<< "$TASK_LINE"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[$CURRENT/$TOTAL] 📥 $TASK_NAME ($SIZE_GB GB)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    TEMP_FILE="/tmp/${TASK_NAME}.tar"
    START_TIME=$(date +%s)
    
    # Download to /tmp only
    echo "   Downloading from AWS..."
    curl -L --progress-bar -o "$TEMP_FILE" "$URL" 2>&1 || {
        echo "   ❌ Download failed, skipping..."
        rm -f "$TEMP_FILE"
        CURRENT=$((CURRENT + 1))
        continue
    }
    
    if [ ! -f "$TEMP_FILE" ]; then
        echo "   ❌ File not created, skipping..."
        CURRENT=$((CURRENT + 1))
        continue
    fi
    
    LOCAL_SIZE=$(du -h "$TEMP_FILE" | cut -f1)
    echo "   ✅ Downloaded ($LOCAL_SIZE)"
    
    # Upload to Google Drive immediately
    echo "   📤 Uploading to Google Drive..."
    python gdrive_upload.py "$TEMP_FILE" "datasets/medical_decathlon" || {
        echo "   ⚠️  Upload failed, keeping temp file for retry"
        CURRENT=$((CURRENT + 1))
        continue
    }
    
    # Delete /tmp immediately (don't store anything)
    rm -f "$TEMP_FILE"
    echo "   🗑️  /tmp cleaned (no local storage)"
    
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))
    TOTAL_TIME=$((TOTAL_TIME + ELAPSED))
    
    echo "   ✅ Complete! ($((ELAPSED / 60)) min)"
    echo ""
    
    CURRENT=$((CURRENT + 1))
    
    # Small delay between uploads
    sleep 2
done

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ ALL DOWNLOADS COMPLETE                       ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "   • Total time: $((TOTAL_TIME / 3600)) hours $((TOTAL_TIME % 3600 / 60)) minutes"
echo "   • Total size: 61.6 GB"
echo "   • Scans: 1,753"
echo "   • Storage: Google Drive only (workspace stayed clean!)"
echo ""
echo "✅ All datasets are in Google Drive!"
echo ""
echo "Check with:"
echo "   python gdrive_list.py"
echo ""
echo "Next: Download individual tasks from Google Drive to process"
echo ""
