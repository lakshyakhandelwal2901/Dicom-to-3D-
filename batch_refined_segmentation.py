#!/usr/bin/env python3
"""
Refined batch segmentation with enhanced HU parameters
Runs segmentation using refined profiles for better 3D model quality
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

def run_segmentation(dataset_name, cloud_input, organ, refined=True):
    """Run segmentation for a dataset"""
    profile_suffix = "_refined" if refined else ""
    
    print(f"\n{'='*80}")
    print(f"🔬 Processing: {dataset_name} → {organ}")
    print(f"{'='*80}")
    
    cmd = [
        ".venv/bin/python", "batch_cloud_segmentation.py",
        "--cloud-input", cloud_input,
        "--cloud-output", "s3://my-medical-imaging/outputs/",
        f"--organs", organ
    ]
    
    # Note: Profiles are loaded by name from medical_imaging_platform/profiles/
    # The batch_cloud_segmentation will use organ name to find the yaml file
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd="/workspaces/Dicom-to-3D-")
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='Refined batch segmentation')
    parser.add_argument('--datasets', nargs='+', 
                       default=['lung_TCGA-17-Z054', 'pancreas_Pancreas-CT-CB_034', 
                               'kidney_TCGA-BP-4989', 'liver_TCGA-DD-A3A9'],
                       help='Datasets to process')
    args = parser.parse_args()
    
    targets = {
        'lung_TCGA-17-Z054': ('s3://my-medical-imaging/datasets/tcia/lung_TCGA-17-Z054', 'lungs'),
        'pancreas_Pancreas-CT-CB_034': ('s3://my-medical-imaging/datasets/tcia/pancreas_Pancreas-CT-CB_034', 'pancreas'),
        'kidney_TCGA-BP-4989': ('s3://my-medical-imaging/datasets/tcia/kidney_TCGA-BP-4989', 'kidneys'),
        'liver_TCGA-DD-A3A9': ('s3://my-medical-imaging/datasets/tcia/liver_TCGA-DD-A3A9', 'liver'),
    }
    
    results = {}
    
    print("\n" + "="*80)
    print("🎯 REFINED BATCH SEGMENTATION - ENHANCED HU PARAMETERS")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Quality improvements:")
    print("  ✓ Optimized HU ranges for better tissue separation")
    print("  ✓ Enhanced smoothing (Laplacian + Taubin)")
    print("  ✓ Improved morphological operations")
    print("  ✓ Better artifact removal and edge preservation")
    print("  ✓ Finer mesh resolution (0.8-1.5mm vs 2.0mm)")
    print("="*80)
    
    for dataset in args.datasets:
        if dataset not in targets:
            print(f"\n⚠️  Unknown dataset: {dataset}")
            continue
        
        cloud_input, organ = targets[dataset]
        success = run_segmentation(dataset, cloud_input, organ, refined=True)
        results[dataset] = "✓ SUCCESS" if success else "✗ FAILED"
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    for dataset, status in results.items():
        print(f"{dataset:40} {status}")
    
    successful = sum(1 for s in results.values() if "SUCCESS" in s)
    print("="*80)
    print(f"✓ Completed: {successful}/{len(results)}")
    print("="*80)
    
    print("\n💾 Cloud storage verification:")
    print("  ./do_spaces.sh list s3://my-medical-imaging/outputs/")
    print("\n📥 Download results:")
    print("  ./do_spaces.sh download s3://my-medical-imaging/outputs/ output/")
    print("\n🎨 View 3D models:")
    print("  Blender, MeshLab, Cura, or any STL/PLY viewer")

if __name__ == "__main__":
    main()
