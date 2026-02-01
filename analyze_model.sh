#!/bin/bash
# Quick AI Analysis - Analyze any 3D model from cloud or local

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================================"
echo "🤖 AI-POWERED 3D MODEL QUALITY ANALYZER"
echo "================================================================================"
echo ""

# Default values
CLOUD_PATH=""
LOCAL_PATH=""
OUTPUT_DIR="./analysis_output"
SKIP_RENDER=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --cloud)
            CLOUD_PATH="$2"
            shift 2
            ;;
        --local)
            LOCAL_PATH="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --render)
            SKIP_RENDER=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --cloud PATH    Analyze model from cloud (s3://...)"
            echo "  --local PATH    Analyze local model file"
            echo "  --output DIR    Output directory (default: ./analysis_output)"
            echo "  --render        Generate visual renders (requires pyrender)"
            echo "  --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  # Analyze from cloud:"
            echo "  $0 --cloud s3://my-medical-imaging/outputs/.../model.ply"
            echo ""
            echo "  # Analyze local file:"
            echo "  $0 --local ./output/brain.ply"
            echo ""
            echo "  # Default (analyzes latest full anatomy):"
            echo "  $0"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Use default if no input specified
if [[ -z "$CLOUD_PATH" ]] && [[ -z "$LOCAL_PATH" ]]; then
    echo "ℹ️ No input specified, analyzing latest full anatomy model..."
    CLOUD_PATH="s3://my-medical-imaging/outputs//lung_TCGA-17-Z054_full_anatomy/full_anatomy_combined_colored.ply"
fi

# Build command
CMD=".venv/bin/python analyze_3d_model.py"

if [[ -n "$CLOUD_PATH" ]]; then
    CMD="$CMD --cloud-path \"$CLOUD_PATH\""
    echo "📥 Source: $CLOUD_PATH"
elif [[ -n "$LOCAL_PATH" ]]; then
    CMD="$CMD --local-path \"$LOCAL_PATH\""
    echo "📂 Source: $LOCAL_PATH"
fi

CMD="$CMD --output-dir \"$OUTPUT_DIR\""

if [[ "$SKIP_RENDER" == "true" ]]; then
    CMD="$CMD --skip-render"
fi

echo "📁 Output: $OUTPUT_DIR"
echo ""

# Run analysis
eval $CMD

# Check if analysis was successful
if [[ $? -eq 0 ]]; then
    echo ""
    echo "================================================================================"
    echo "✅ ANALYSIS COMPLETE"
    echo "================================================================================"
    echo ""
    
    # Show files generated
    echo "📄 Generated files:"
    find "$OUTPUT_DIR" -type f -name "*.txt" -o -name "*.md" -o -name "*.png" | while read file; do
        size=$(du -h "$file" | cut -f1)
        echo "  • $file ($size)"
    done
    
    echo ""
    
    # Show quality report if exists
    if [[ -f "$OUTPUT_DIR/quality_report.txt" ]]; then
        echo "📊 Quick Summary:"
        grep -E "(Overall Quality Score|Vertices|Faces|Unique Colors|Watertight)" "$OUTPUT_DIR/quality_report.txt" | head -10
    fi
    
    echo ""
    echo "📖 View full report:"
    echo "   cat $OUTPUT_DIR/quality_report.txt"
    
    if [[ -f "$OUTPUT_DIR/AI_ANALYSIS_SUMMARY.md" ]]; then
        echo "   cat $OUTPUT_DIR/AI_ANALYSIS_SUMMARY.md"
    fi
    
    echo ""
    echo "🎨 View model in Blender:"
    if [[ -n "$LOCAL_PATH" ]]; then
        echo "   blender \"$LOCAL_PATH\""
    else
        # Find the downloaded PLY
        PLY_FILE=$(find "$OUTPUT_DIR" -name "*.ply" -type f | head -1)
        if [[ -n "$PLY_FILE" ]]; then
            echo "   blender \"$PLY_FILE\""
        fi
    fi
    
    echo ""
else
    echo ""
    echo "❌ Analysis failed. Check error messages above."
    exit 1
fi
