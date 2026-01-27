#!/usr/bin/env python3
"""
Organize existing datasets and upload to DigitalOcean Spaces
"""

import os
import subprocess
import shutil
from pathlib import Path

def upload_to_cloud(local_path, remote_path):
    """Upload dataset to DigitalOcean Spaces"""
    print(f"\n📤 Uploading: {local_path}")
    print(f"   → {remote_path}")
    
    try:
        cmd = f"./do_spaces.sh upload {local_path} {remote_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/workspaces/Dicom-to-3D-")
        
        if result.returncode == 0:
            print(f"✓ Uploaded successfully")
            return True
        else:
            print(f"✗ Upload failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_dataset(path):
    """Check dataset size and file count"""
    path = Path(path)
    if not path.exists():
        return 0, 0
    
    dcm_files = list(path.rglob("*.dcm"))
    total_size = sum(f.stat().st_size for f in dcm_files)
    size_mb = total_size / (1024 * 1024)
    
    return len(dcm_files), size_mb

def main():
    """Upload existing datasets to cloud"""
    
    print("📦 Dataset Cloud Upload Manager")
    print("=" * 70)
    
    # Define datasets to upload
    datasets = [
        {
            "local": "data/lidc_sample_ct",
            "remote": "s3://my-medical-imaging/datasets/lidc_sample_ct",
            "description": "LIDC-IDRI Chest CT (already in cloud, re-upload)"
        },
        {
            "local": "data/sample_brain_ct",
            "remote": "s3://my-medical-imaging/datasets/sample_brain_ct",
            "description": "Sample Brain CT (Head)"
        },
        {
            "local": "data/sample_chest_ct",
            "remote": "s3://my-medical-imaging/datasets/sample_chest_ct",
            "description": "Sample Chest CT"
        }
    ]
    
    results = []
    
    for dataset in datasets:
        print(f"\n{'='*70}")
        print(f"Dataset: {dataset['description']}")
        print(f"Local: {dataset['local']}")
        print(f"{'='*70}")
        
        # Check if dataset exists
        file_count, size_mb = check_dataset(dataset['local'])
        
        if file_count == 0:
            print(f"⚠ Dataset not found or empty - skipping")
            results.append({
                "name": dataset['local'],
                "files": 0,
                "size_mb": 0,
                "status": "⊘ Not found"
            })
            continue
        
        print(f"📊 Files: {file_count}, Size: {size_mb:.1f} MB")
        
        # Upload
        success = upload_to_cloud(dataset['local'], dataset['remote'])
        
        results.append({
            "name": Path(dataset['local']).name,
            "files": file_count,
            "size_mb": size_mb,
            "status": "✓ Uploaded" if success else "✗ Failed"
        })
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 UPLOAD SUMMARY")
    print(f"{'='*70}")
    
    for r in results:
        print(f"{r['name']:30} | Files: {r['files']:4} | Size: {r['size_mb']:7.1f} MB | {r['status']}")
    
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if '✓' in r['status'])
    total_files = sum(r['files'] for r in results)
    total_size = sum(r['size_mb'] for r in results)
    
    print(f"\n✓ Successfully uploaded: {successful}/{len(datasets)}")
    print(f"📁 Total files uploaded: {total_files}")
    print(f"💾 Total size uploaded: {total_size:.1f} MB")
    
    if successful > 0:
        print(f"\n{'='*70}")
        print("✅ NEXT STEPS")
        print(f"{'='*70}")
        print("\n1. Verify cloud storage:")
        print("   ./do_spaces.sh usage")
        print("   ./do_spaces.sh list s3://my-medical-imaging/datasets/")
        print("\n2. Run segmentation from cloud (example):")
        print("   python3 cloud_workflow.py \\")
        print("     --cloud-input s3://my-medical-imaging/datasets/sample_brain_ct \\")
        print("     --organ brain \\")
        print("     --cloud-output s3://my-medical-imaging/outputs/")
        print("\n3. Process all datasets:")
        print("   for dataset in lidc_sample_ct sample_brain_ct sample_chest_ct; do")
        print("     python3 cloud_workflow.py \\")
        print("       --cloud-input s3://my-medical-imaging/datasets/$dataset \\")
        print("       --organ lungs \\")
        print("       --cloud-output s3://my-medical-imaging/outputs/")
        print("   done")

if __name__ == "__main__":
    main()
