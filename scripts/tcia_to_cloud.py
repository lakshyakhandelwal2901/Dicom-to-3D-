#!/usr/bin/env python3
"""
Download diverse CT datasets from TCIA and upload to DigitalOcean Spaces
Simple and robust approach
"""

import os
import subprocess
from pathlib import Path
from tcia_utils import nbia

def download_by_patient(collection, patient_id, output_dir, name):
    """Download all series for a patient"""
    print(f"\n{'='*70}")
    print(f"📥 Downloading: {name}")
    print(f"Collection: {collection}")
    print(f"Patient ID: {patient_id}")
    print(f"Output: {output_dir}")
    print(f"{'='*70}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Get series for this patient
        series = nbia.getSeries(collection=collection, patientId=patient_id, modality='CT')
        
        if not series:
            print("✗ No series found for this patient")
            return False, 0, 0
        
        print(f"Found {len(series)} series for patient {patient_id}")
        
        # Download all series using list input
        series_uids = [s['SeriesInstanceUID'] for s in series]
        nbia.downloadSeries(series_uids, input_type="list", path=str(output_path))
        
        # Count files and size
        dcm_files = list(output_path.rglob("*.dcm"))
        total_size = sum(f.stat().st_size for f in dcm_files)
        size_mb = total_size / (1024 * 1024)
        
        print(f"✓ Downloaded {len(dcm_files)} DICOM files ({size_mb:.1f} MB)")
        return True, len(dcm_files), size_mb
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, 0, 0

def upload_to_cloud(local_path, remote_path):
    """Upload dataset to DigitalOcean Spaces"""
    print(f"\n📤 Uploading to cloud: {remote_path}")
    
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

def main():
    """Download and upload diverse CT datasets"""
    
    base_dir = "/workspaces/Dicom-to-3D-/data/tcia_downloads"
    
    # Get some patient IDs from LIDC-IDRI
    print("🔍 Finding available patients in LIDC-IDRI...")
    try:
        all_series = nbia.getSeries(collection='LIDC-IDRI', modality='CT')
        patient_ids = list(set([s['PatientID'] for s in all_series[:10]]))[:3]  # Get 3 different patients
        print(f"✓ Selected {len(patient_ids)} patients")
    except Exception as e:
        print(f"✗ Error getting patients: {e}")
        return
    
    datasets = [
        {
            "collection": "LIDC-IDRI",
            "patient_id": patient_ids[0],
            "name": "lidc_patient_01",
            "description": f"LIDC-IDRI Patient {patient_ids[0]}"
        },
        {
            "collection": "LIDC-IDRI",
            "patient_id": patient_ids[1],
            "name": "lidc_patient_02",
            "description": f"LIDC-IDRI Patient {patient_ids[1]}"
        },
        {
            "collection": "LIDC-IDRI",
            "patient_id": patient_ids[2],
            "name": "lidc_patient_03",
            "description": f"LIDC-IDRI Patient {patient_ids[2]}"
        }
    ]
    
    print("🌐 TCIA Dataset Download & Cloud Upload Pipeline")
    print("=" * 70)
    print(f"Datasets: {len(datasets)} chest CT series from LIDC-IDRI")
    print("=" * 70)
    
    results = []
    
    for dataset in datasets:
        # Download
        local_path = os.path.join(base_dir, dataset["name"])
        success, file_count, size_mb = download_by_patient(
            dataset["collection"],
            dataset["patient_id"],
            local_path,
            dataset["description"]
        )
        
        if success and file_count > 0:
            # Upload to cloud
            remote_path = f"s3://my-medical-imaging/datasets/tcia/{dataset['name']}"
            upload_success = upload_to_cloud(local_path, remote_path)
            
            results.append({
                "name": dataset["name"],
                "patient_id": dataset["patient_id"],
                "files": file_count,
                "size_mb": size_mb,
                "download": "✓",
                "upload": "✓" if upload_success else "✗"
            })
        else:
            results.append({
                "name": dataset["name"],
                "patient_id": dataset.get("patient_id", "N/A"),
                "files": 0,
                "size_mb": 0,
                "download": "✗",
                "upload": "-"
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 PIPELINE SUMMARY")
    print("=" * 70)
    for r in results:
        print(f"{r['name']:25} | Patient: {r['patient_id']:15} | Files: {r['files']:4} | Size: {r['size_mb']:6.1f} MB | DL: {r['download']} | UP: {r['upload']}")
    
    total_files = sum(r['files'] for r in results)
    total_size = sum(r['size_mb'] for r in results)
    
    print("=" * 70)
    print(f"Total: {total_files} files, {total_size:.1f} MB")
    print("=" * 70)
    
    successful_downloads = sum(1 for r in results if r['download'] == '✓')
    successful_uploads = sum(1 for r in results if r['upload'] == '✓')
    
    print(f"\n✓ Downloaded: {successful_downloads}/{len(datasets)}")
    print(f"✓ Uploaded to cloud: {successful_uploads}/{len(datasets)}")
    
    if successful_uploads > 0:
        print("\n✅ NEXT STEPS:")
        print("\n1. Check cloud storage:")
        print("   ./do_spaces.sh list s3://my-medical-imaging/datasets/tcia/")
        print("\n2. Run segmentation from cloud:")
        print("   python3 cloud_workflow.py \\")
        print(f"     --cloud-input s3://my-medical-imaging/datasets/tcia/{results[0]['name']} \\")
        print("     --organ lungs \\")
        print("     --cloud-output s3://my-medical-imaging/outputs/")
        print("\n3. Check cloud usage:")
        print("   ./do_spaces.sh usage")

if __name__ == "__main__":
    main()
