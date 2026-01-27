#!/usr/bin/env python3
"""
Download useful CT datasets from TCIA and upload to DigitalOcean Spaces
"""

import os
import sys
from pathlib import Path
from tcia_utils import nbia

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def download_dataset(collection, series_uid, output_dir, description):
    """Download a specific series from TCIA"""
    print(f"\n{'='*60}")
    print(f"📥 Downloading: {description}")
    print(f"Collection: {collection}")
    print(f"Series UID: {series_uid}")
    print(f"{'='*60}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download using series UID
        nbia.downloadSeries([series_uid], str(output_path))
        
        # Count downloaded files
        dcm_files = list(output_path.rglob("*.dcm"))
        print(f"✓ Downloaded {len(dcm_files)} DICOM files")
        
        # Calculate size
        total_size = sum(f.stat().st_size for f in dcm_files)
        size_mb = total_size / (1024 * 1024)
        print(f"✓ Total size: {size_mb:.1f} MB")
        
        return True
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return False

def main():
    """Download multiple useful datasets"""
    
    # Base output directory
    base_dir = "/workspaces/Dicom-to-3D-/data/tcia_downloads"
    
    datasets = [
        # Chest CT - COVID-19 (small, useful for lung segmentation)
        {
            "collection": "CT-ORG",
            "series_uid": "1.3.6.1.4.1.9328.50.4.0001",  # Sample chest CT
            "output": os.path.join(base_dir, "chest_ct_01"),
            "description": "Chest CT - Lung anatomy"
        },
        
        # Head CT - Brain (useful for brain segmentation)
        {
            "collection": "CT-ORG",
            "series_uid": "1.3.6.1.4.1.9328.50.4.0002",  # Sample head CT
            "output": os.path.join(base_dir, "head_ct_01"),
            "description": "Head CT - Brain anatomy"
        },
        
        # Abdomen CT - Liver (useful for organ segmentation)
        {
            "collection": "CT-ORG",
            "series_uid": "1.3.6.1.4.1.9328.50.4.0003",  # Sample abdomen CT
            "output": os.path.join(base_dir, "abdomen_ct_01"),
            "description": "Abdomen CT - Liver/organs"
        }
    ]
    
    print("🌐 TCIA Dataset Downloader")
    print("=" * 60)
    print(f"Downloading {len(datasets)} datasets from TCIA")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for dataset in datasets:
        success = download_dataset(
            dataset["collection"],
            dataset["series_uid"],
            dataset["output"],
            dataset["description"]
        )
        
        if success:
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print(f"📁 Output directory: {base_dir}")
    print("=" * 60)
    
    if successful > 0:
        print("\n📤 Next steps:")
        print("1. Validate datasets:")
        print(f"   python3 scripts/validate_dicom_series.py {base_dir}/chest_ct_01")
        print("\n2. Upload to DigitalOcean Spaces:")
        print(f"   ./do_spaces.sh upload {base_dir} s3://my-medical-imaging/datasets/tcia/")
        print("\n3. Run segmentation from cloud:")
        print("   python3 cloud_workflow.py \\")
        print("     --cloud-input s3://my-medical-imaging/datasets/tcia/chest_ct_01 \\")
        print("     --organ lungs \\")
        print("     --cloud-output s3://my-medical-imaging/outputs/")

if __name__ == "__main__":
    main()
