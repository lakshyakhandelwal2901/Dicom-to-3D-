#!/usr/bin/env python3
"""
Batch process DICOM datasets through ALL organ segmentation models
Automatically downloads from cloud, processes all organs, saves outputs locally with names
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# List of all available organs in profiles
ORGANS = ['lungs', 'brain', 'liver', 'kidneys', 'heart', 'pancreas', 'bones']

def download_from_cloud(cloud_path, local_dir):
    """Download DICOM dataset from cloud"""
    print(f"\n{'='*70}")
    print(f"📥 DOWNLOADING FROM CLOUD")
    print(f"{'='*70}")
    print(f"Cloud: {cloud_path}")
    print(f"Local: {local_dir}")
    
    local_path = Path(local_dir)
    local_path.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded (including nested structure)
    dcm_files = list(local_path.rglob("*.dcm"))
    if dcm_files:
        print(f"✓ Already cached: {len(dcm_files)} DICOM files")
        # Find the actual DICOM directory (might be nested)
        subdirs = [d for d in local_path.iterdir() if d.is_dir()]
        if subdirs:
            actual_dcm_dir = subdirs[0]
            subdir_dcms = list(actual_dcm_dir.rglob("*.dcm"))
            if subdir_dcms:
                return actual_dcm_dir
        return local_path
    
    try:
        cmd = f"./do_spaces.sh download {cloud_path} {local_dir}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/workspaces/Dicom-to-3D-")
        
        if result.returncode == 0:
            # Find actual DICOM directory (TCIA has nested structure with series UID)
            subdirs = [d for d in local_path.iterdir() if d.is_dir()]
            if subdirs:
                # Try first subdirectory
                actual_dcm_dir = subdirs[0]
                actual_dcm_files = list(actual_dcm_dir.rglob("*.dcm"))
                if actual_dcm_files:
                    print(f"✓ Downloaded {len(actual_dcm_files)} DICOM files")
                    return actual_dcm_dir
            
            # Fall back to local_path
            dcm_files = list(local_path.rglob("*.dcm"))
            print(f"✓ Downloaded {len(dcm_files)} DICOM files")
            return local_path
        else:
            print(f"✗ Download failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def process_organ(dcm_path, organ, output_dir):
    """Process a single organ segmentation"""
    print(f"\n📊 Processing: {organ.upper()}")
    
    try:
        # Build main.py command
        cmd = [
            'python3',
            'medical_imaging_platform/main.py',
            '--input', str(dcm_path),
            '--organ', organ,
            '--output', str(output_dir),
            '--model', 'hu_based'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/workspaces/Dicom-to-3D-", timeout=300)
        
        if result.returncode == 0:
            # Check for outputs
            stl_files = list(Path(output_dir).glob(f"{organ}_*.stl"))
            ply_files = list(Path(output_dir).glob(f"{organ}_*.ply"))
            
            if stl_files or ply_files:
                print(f"✓ {organ}: Generated {len(stl_files)} STL + {len(ply_files)} PLY files")
                return True, stl_files, ply_files
            else:
                print(f"⚠ {organ}: No output files generated")
                return False, [], []
        else:
            print(f"✗ {organ}: Failed")
            if "error" in result.stderr.lower():
                print(f"   Error: {result.stderr[:200]}")
            return False, [], []
            
    except subprocess.TimeoutExpired:
        print(f"✗ {organ}: Timeout (>5min)")
        return False, [], []
    except Exception as e:
        print(f"✗ {organ}: Exception - {e}")
        return False, [], []

def organize_outputs(output_dir, dataset_name, results):
    """Organize and rename output files by organ"""
    organized_dir = Path(output_dir) / f"segmentation_results_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    organized_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"📁 ORGANIZING OUTPUTS")
    print(f"{'='*70}")
    print(f"Output dir: {organized_dir}")
    
    summary = {}
    for organ, stl_files, ply_files in results:
        if stl_files or ply_files:
            for f in stl_files + ply_files:
                # Copy with naming: output_name_organ_type.ext
                new_name = f"{dataset_name}_{organ}{f.suffix}"
                dest = organized_dir / new_name
                shutil.copy2(f, dest)
                print(f"  ✓ {new_name}")
                
            summary[organ] = {
                'stl': len(stl_files),
                'ply': len(ply_files),
                'size_mb': sum(f.stat().st_size for f in stl_files + ply_files) / (1024*1024)
            }
    
    return organized_dir, summary

def upload_results_to_cloud(result_dir, dataset_name, cloud_base):
    """Upload all results back to cloud"""
    print(f"\n{'='*70}")
    print(f"📤 UPLOADING TO CLOUD")
    print(f"{'='*70}")
    
    remote_path = f"{cloud_base}/batch_segmentation_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        cmd = f"./do_spaces.sh upload {result_dir} {remote_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/workspaces/Dicom-to-3D-")
        
        if result.returncode == 0:
            print(f"✓ Uploaded to: {remote_path}")
            return True, remote_path
        else:
            print(f"✗ Upload failed: {result.stderr}")
            return False, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, None

def main():
    """Main batch processing pipeline"""
    
    print("\n" + "="*70)
    print("🔬 BATCH ORGAN SEGMENTATION PIPELINE")
    print("="*70)
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 batch_process_all_organs.py <cloud_dataset_path> [--no-upload] [--keep-local]")
        print("\nExample:")
        print("  python3 batch_process_all_organs.py s3://my-medical-imaging/datasets/tcia/lidc_patient_01")
        print("  python3 batch_process_all_organs.py s3://my-medical-imaging/datasets/tcia/colon_cmb_crc_01068 --no-upload")
        sys.exit(1)
    
    cloud_input = sys.argv[1]
    no_upload = '--no-upload' in sys.argv
    keep_local = '--keep-local' in sys.argv
    
    # Extract dataset name from cloud path
    dataset_name = cloud_input.rstrip('/').split('/')[-1]
    
    # Setup directories
    temp_dir = Path(f"/tmp/batch_segmentation_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    dcm_dir = temp_dir / "dicom"
    output_dir = temp_dir / "output"
    dcm_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📋 Configuration:")
    print(f"  Cloud input: {cloud_input}")
    print(f"  Dataset: {dataset_name}")
    print(f"  Temp dir: {temp_dir}")
    print(f"  Organs to process: {', '.join(ORGANS)}")
    print(f"  Upload to cloud: {'Yes' if not no_upload else 'No'}")
    
    # Step 1: Download
    actual_dcm_dir = download_from_cloud(cloud_input, dcm_dir)
    if not actual_dcm_dir:
        print("\n✗ Failed to download dataset")
        sys.exit(1)
    
    # Step 2: Process all organs
    print(f"\n{'='*70}")
    print(f"🔄 PROCESSING {len(ORGANS)} ORGANS")
    print(f"{'='*70}")
    
    results = []
    processed = 0
    failed = 0
    
    for organ in ORGANS:
        success, stl_files, ply_files = process_organ(actual_dcm_dir, organ, output_dir)
        results.append((organ, stl_files, ply_files))
        
        if success:
            processed += 1
        else:
            failed += 1
    
    # Step 3: Organize outputs
    result_dir, summary = organize_outputs("/workspaces/Dicom-to-3D-/output", dataset_name, results)
    
    # Step 4: Upload to cloud (optional)
    cloud_result_path = None
    if not no_upload:
        upload_success, cloud_result_path = upload_results_to_cloud(
            result_dir, 
            dataset_name,
            "s3://my-medical-imaging/outputs"
        )
    
    # Step 5: Summary
    print(f"\n{'='*70}")
    print(f"📊 BATCH PROCESSING COMPLETE")
    print(f"{'='*70}")
    
    print(f"\n✅ Results Summary:")
    print(f"  Total organs: {len(ORGANS)}")
    print(f"  Processed: {processed}")
    print(f"  Failed: {failed}")
    print(f"\n📁 Output location: {result_dir}")
    
    print(f"\n📦 Segmentation outputs by organ:")
    for organ, info in summary.items():
        print(f"  {organ:12} | STL: {info['stl']}  PLY: {info['ply']}  Size: {info['size_mb']:.1f} MB")
    
    total_files = sum(info['stl'] + info['ply'] for info in summary.values())
    total_size = sum(info['size_mb'] for info in summary.values())
    print(f"\n  TOTAL       | Files: {total_files}  Size: {total_size:.1f} MB")
    
    if cloud_result_path:
        print(f"\n☁️  Cloud storage: {cloud_result_path}")
    
    # Cleanup options
    if not keep_local:
        print(f"\n🧹 Cleaning up temp directory: {temp_dir}")
        shutil.rmtree(temp_dir)
        print(f"✓ Cleaned")
    else:
        print(f"\n📌 Keeping local files (temp dir): {temp_dir}")
    
    print(f"\n{'='*70}")
    print(f"✓ Pipeline complete!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
