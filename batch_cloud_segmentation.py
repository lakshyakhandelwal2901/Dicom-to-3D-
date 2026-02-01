#!/usr/bin/env python3
"""
Batch Cloud Segmentation
- Download DICOM from cloud (one dataset)
- Segment ALL organs (brain, lungs, liver, heart, kidneys, etc.)
- Upload results to cloud
- Delete local files (keep DICOM cache for reuse)
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import argparse
from datetime import datetime

def run_cmd(cmd, check=True):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        sys.exit(1)
    return result

def download_from_cloud(cloud_path, local_path):
    """Download DICOM from Google Drive to local /tmp"""
    print(f"\n📥 Downloading from Google Drive: {cloud_path}")
    cmd = f"python3 gdrive_download.py '{cloud_path}' {local_path}"
    result = run_cmd(cmd)
    
    # Count files
    dcm_files = list(Path(local_path).rglob("*.dcm"))
    if dcm_files:
        size_mb = sum(f.stat().st_size for f in dcm_files) / (1024*1024)
        print(f"✓ Downloaded {len(dcm_files)} DICOM files ({size_mb:.1f} MB)")
        return True
    return False

def get_available_organs():
    """Get list of available organ profiles"""
    result = run_cmd("python3 medical_imaging_platform/main.py --list-profiles", check=False)
    organs = []
    for line in result.stdout.split('\n'):
        if line.startswith('✓ '):
            organ = line.split('✓ ')[1].strip()
            organs.append(organ.lower())
    return organs

def segment_organ(dicom_path, organ, output_base):
    """Segment a single organ"""
    print(f"\n🔬 Segmenting: {organ.upper()}")
    
    output_path = Path(output_base) / f"{organ}_segmentation"
    output_path.mkdir(parents=True, exist_ok=True)
    
    cmd = f"python3 medical_imaging_platform/main.py --organ {organ} --input {dicom_path} --output {output_path}"
    result = run_cmd(cmd, check=False)
    
    if result.returncode == 0:
        print(f"✓ {organ.upper()} segmentation complete")
        return True, output_path
    else:
        print(f"✗ {organ.upper()} segmentation failed")
        print(result.stderr)
        return False, None

def upload_to_cloud(local_path, remote_base, dataset_name):
    """Upload results to Google Drive"""
    remote_path = f"{remote_base}/{dataset_name}"
    print(f"\n📤 Uploading results to Google Drive: {remote_path}")
    
    cmd = f"python3 gdrive_upload.py {local_path} results/{remote_base}"
    result = run_cmd(cmd, check=False)
    
    if result.returncode == 0:
        print(f"✓ Uploaded successfully")
        return True
    else:
        print(f"✗ Upload failed")
        return False

def cleanup(path):
    """Delete local files"""
    if Path(path).exists():
        shutil.rmtree(path)
        print(f"🧹 Cleaned up: {path}")

def main():
    parser = argparse.ArgumentParser(
        description='Batch Cloud Segmentation - Segment ALL organs from cloud DICOM'
    )
    parser.add_argument(
        '--cloud-input',
        required=True,
        help='Cloud path to DICOM dataset (e.g., s3://bucket/datasets/scan_name)'
    )
    parser.add_argument(
        '--cloud-output',
        required=True,
        help='Cloud base path for results (e.g., s3://bucket/outputs/)'
    )
    parser.add_argument(
        '--organs',
        default='lungs,brain,liver,heart,kidneys',
        help='Comma-separated organs to segment (default: lungs,brain,liver,heart,kidneys)'
    )
    parser.add_argument(
        '--keep-dicom',
        action='store_true',
        default=True,
        help='Keep DICOM in cache for reuse (default: True)'
    )
    parser.add_argument(
        '--keep-outputs',
        action='store_true',
        help='Keep local output files (default: False, upload to cloud only)'
    )
    
    args = parser.parse_args()
    
    # Parse inputs
    cloud_input = args.cloud_input
    cloud_output = args.cloud_output
    organs_to_segment = [o.strip() for o in args.organs.split(',')]
    
    # Extract dataset name from cloud path
    dataset_name = cloud_input.split('/')[-1]
    
    print("\n" + "="*70)
    print("🌐 BATCH CLOUD SEGMENTATION")
    print("="*70)
    print(f"Input (cloud):  {cloud_input}")
    print(f"Output (cloud): {cloud_output}")
    print(f"Dataset:        {dataset_name}")
    print(f"Organs:         {', '.join(organs_to_segment)}")
    print("="*70)
    
    # Setup temp directories
    tmp_base = Path("/tmp/batch_segmentation")
    tmp_base.mkdir(exist_ok=True)
    
    dicom_cache = tmp_base / "dicom_cache" / dataset_name
    outputs_base = tmp_base / "outputs" / dataset_name
    
    try:
        # Download DICOM from cloud
        if not dicom_cache.exists():
            download_from_cloud(cloud_input, str(dicom_cache))
        else:
            dcm_files = list(dicom_cache.rglob("*.dcm"))
            size_mb = sum(f.stat().st_size for f in dcm_files) / (1024*1024)
            print(f"\n✓ Using cached DICOM ({len(dcm_files)} files, {size_mb:.1f} MB)")
        
        # Find actual DICOM directory (nested under series UID)
        dicom_files = list(dicom_cache.rglob("*.dcm"))
        if not dicom_files:
            print("ERROR: No DICOM files found")
            sys.exit(1)
        
        # DICOM files are in: cache/dataset/SeriesUID/*.dcm
        # Get the directory containing the DICOM files
        dicom_path = dicom_files[0].parent
        
        print(f"✓ DICOM path: {dicom_path} ({len(dicom_files)} files)")
        
        # Segment organs
        results = []
        outputs_base.mkdir(parents=True, exist_ok=True)
        
        for organ in organs_to_segment:
            success, output_path = segment_organ(str(dicom_path), organ, str(outputs_base))
            if success:
                results.append((organ, output_path))
        
        # Summary
        print("\n" + "="*70)
        print("📊 SEGMENTATION RESULTS")
        print("="*70)
        print(f"Successful: {len(results)}/{len(organs_to_segment)}")
        for organ, path in results:
            files = list(path.glob("*"))
            size = sum(f.stat().st_size for f in files if f.is_file()) / (1024*1024)
            print(f"  ✓ {organ}: {len(files)} files ({size:.1f} MB) → uploading to cloud")
        
        # Upload ALL results to cloud immediately
        if results:
            print("\n" + "="*70)
            print("☁️  UPLOADING TO CLOUD (Cloud Storage Only - NO Local Storage)")
            print("="*70)
            
            for organ, output_path in results:
                upload_to_cloud(str(output_path), cloud_output, f"{dataset_name}_{organ}")
                # Delete after upload to save space
                cleanup(str(output_path))
            
            print("\n✅ All results uploaded to cloud and deleted locally")
            print(f"   Cloud path: {cloud_output}")
        
        # Final cleanup of outputs directory
        print("\n🧹 Final cleanup (temp files)")
        cleanup(str(outputs_base))
        
        print("\n" + "="*70)
        print("✅ BATCH SEGMENTATION COMPLETE")
        print("="*70)
        print(f"\nView results in cloud:")
        print(f"  python3 gdrive_list.py results")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
