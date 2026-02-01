#!/bin/bash
# Monitor the lean download progress

cd /workspaces/Dicom-to-3D-

while true; do
    clear
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║          📊 DOWNLOAD MONITOR - STREAMING TO GOOGLE DRIVE          ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Check if download is running
    if pgrep -f "lean_gdrive_download" > /dev/null; then
        echo "✅ Download process: ACTIVE"
    else
        echo "⏸️  Download process: COMPLETED or PAUSED"
    fi
    
    echo ""
    echo "📥 PROGRESS:"
    tail -20 lean_download.log | grep -E "^\[|Downloading|Uploading|Complete|✅"
    
    echo ""
    echo "💾 TEMPORARY FILES:"
    ls -lh /tmp/*.tar 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  (none - staying clean!)"
    
    echo ""
    echo "📊 WORKSPACE:"
    df -h /workspaces/Dicom-to-3D- | tail -1 | awk '{print "  Space free: " $4 " / " $2}'
    
    echo ""
    echo "🌐 GOOGLE DRIVE:"
    python gdrive_list.py 2>/dev/null | tail -5 | grep -E "Found|Total"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Refreshing every 30 seconds... (Ctrl+C to stop)"
    echo "Full log: tail -f lean_download.log"
    echo ""
    
    sleep 30
done
