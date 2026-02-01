#!/bin/bash
# Download Medical Segmentation Decathlon Dataset
# 10 tasks, 2633 3D images with ground truth segmentation

set -e

WORKSPACE="/workspaces/Dicom-to-3D-"
OUTPUT_DIR="$WORKSPACE/data/medical_decathlon"

echo "════════════════════════════════════════════════════════════════════════════════"
echo "MEDICAL SEGMENTATION DECATHLON DATASET"
echo "10 segmentation tasks with ground truth labels"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "📥 Available Tasks:"
echo ""
echo "Task 01: Brain Tumors (484 scans, 4.5 GB)"
echo "Task 02: Heart (30 scans, 1.2 GB)"
echo "Task 03: Liver & Tumors (131 scans, 8.5 GB)"
echo "Task 04: Hippocampus (260 scans, 0.2 GB)"
echo "Task 05: Prostate (32 scans, 1.1 GB)"
echo "Task 06: Lung Tumors (64 scans, 7.2 GB)"
echo "Task 07: Pancreas & Tumor (282 scans, 16 GB)"
echo "Task 08: Hepatic Vessel (303 scans, 12 GB)"
echo "Task 09: Spleen (41 scans, 2.8 GB)"
echo "Task 10: Colon Cancer (126 scans, 8.1 GB)"
echo ""
echo "Total: 2633 scans, ~50 GB"
echo ""

read -p "Download ALL tasks? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Downloading all tasks..."
    
    BASE_URL="https://msd-for-monai.s3-us-west-2.amazonaws.com"
    
    for i in {01..10}; do
        TASK="Task${i}"
        echo ""
        echo "📥 Downloading $TASK..."
        
        wget -c "${BASE_URL}/${TASK}_*.tar" -P "$OUTPUT_DIR/"
        tar -xf "$OUTPUT_DIR/${TASK}_*.tar" -C "$OUTPUT_DIR/"
    done
    
    echo ""
    echo "✅ All tasks downloaded!"
else
    echo ""
    read -p "Enter task numbers to download (e.g., 1 3 7): " TASKS
    
    BASE_URL="https://msd-for-monai.s3-us-west-2.amazonaws.com"
    
    for task_num in $TASKS; do
        TASK=$(printf "Task%02d" $task_num)
        echo ""
        echo "📥 Downloading $TASK..."
        
        wget -c "${BASE_URL}/${TASK}_*.tar" -P "$OUTPUT_DIR/"
        tar -xf "$OUTPUT_DIR/${TASK}_*.tar" -C "$OUTPUT_DIR/"
    done
fi

echo ""
echo "✅ Download Complete!"
echo ""
echo "📊 Dataset Structure:"
ls -lh "$OUTPUT_DIR"

echo ""
echo "📈 Dataset Info:"
echo "  • Each task has imagesTr/ (training) and labelsTr/ (ground truth)"
echo "  • Use labels to validate your segmentation quality"
echo "  • Compare your output with ground truth to calculate accuracy"
echo ""
echo "💡 Usage:"
echo "  python batch_cloud_segmentation.py --local-dir $OUTPUT_DIR/Task03_Liver"
echo "  python compare_with_ground_truth.py --pred output/ --gt $OUTPUT_DIR/Task03_Liver/labelsTr/"
echo ""
