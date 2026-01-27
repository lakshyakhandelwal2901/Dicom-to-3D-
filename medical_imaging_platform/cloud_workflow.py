#!/usr/bin/env python3
"""
Cloud-Enabled Segmentation Workflow
Automatically downloads DICOM from cloud, processes, uploads results
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.cloud_storage import CloudStorage


class CloudWorkflow:
    def __init__(self, provider='s3', cleanup_input=False, cleanup_output=True):
        self.storage = CloudStorage(provider=provider)
        self.cleanup_input = cleanup_input
        self.cleanup_output = cleanup_output
        self.temp_dir = Path('/tmp/dicom_processing')
        self.temp_dir.mkdir(exist_ok=True)
    
    def download_dicom(self, remote_path: str) -> str:
        """
        Download DICOM from cloud to temporary local directory
        
        Args:
            remote_path: Cloud path (e.g., s3://bucket/datasets/lidc_sample)
        
        Returns:
            Local path where DICOM was downloaded
        """
        # Extract dataset name from remote path
        dataset_name = remote_path.rstrip('/').split('/')[-1]
        local_path = self.temp_dir / dataset_name
        
        # Skip download if already exists locally
        if local_path.exists():
            dcm_files = list(local_path.glob('*.dcm'))
            if dcm_files:
                print(f"✓ DICOM already exists locally: {local_path} ({len(dcm_files)} files)")
                return str(local_path)
        
        print(f"📥 Downloading DICOM from cloud: {remote_path}")
        local_path.mkdir(parents=True, exist_ok=True)
        
        success = self.storage.download(remote_path, str(local_path), recursive=True)
        
        if not success:
            raise Exception(f"Failed to download DICOM from {remote_path}")
        
        # Count downloaded files
        dcm_files = list(local_path.glob('*.dcm'))
        print(f"✓ Downloaded {len(dcm_files)} DICOM files to {local_path}")
        
        return str(local_path)
    
    def run_segmentation(self, input_path: str, organ: str, model: str = 'hu_based') -> str:
        """
        Run segmentation on local DICOM
        
        Args:
            input_path: Local path to DICOM files
            organ: Organ to segment (lungs, brain, etc.)
            model: Model type (hu_based, totalSegmentator, etc.)
        
        Returns:
            Output directory path
        """
        output_dir = self.temp_dir / f'{organ}_segmentation_{Path(input_path).name}'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔬 Running segmentation: {organ} (model: {model})")
        
        cmd = [
            sys.executable,
            'main.py',
            '--organ', organ,
            '--input', input_path,
            '--output', str(output_dir),
            '--model', model
        ]
        
        result = subprocess.run(cmd, cwd=Path(__file__).parent, capture_output=False, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Segmentation failed with exit code {result.returncode}")
        
        # Verify outputs exist
        output_files = list(output_dir.glob('*'))
        if not output_files:
            raise Exception(f"No output files generated in {output_dir}")
        
        print(f"✓ Segmentation complete: {len(output_files)} files in {output_dir}")
        
        return str(output_dir)
    
    def upload_results(self, local_path: str, remote_base: str) -> str:
        """
        Upload segmentation results to cloud
        
        Args:
            local_path: Local output directory
            remote_base: Base cloud path (e.g., s3://bucket/outputs/)
        
        Returns:
            Remote path where results were uploaded
        """
        output_name = Path(local_path).name
        remote_path = f"{remote_base.rstrip('/')}/{output_name}"
        
        print(f"📤 Uploading results to cloud: {remote_path}")
        
        success = self.storage.upload(local_path, remote_path, recursive=True)
        
        if not success:
            raise Exception(f"Failed to upload results to {remote_path}")
        
        # Count uploaded files
        output_files = list(Path(local_path).glob('*'))
        print(f"✓ Uploaded {len(output_files)} files to {remote_path}")
        
        return remote_path
    
    def cleanup(self, *paths):
        """Clean up local temporary files"""
        for path in paths:
            if path and os.path.exists(path):
                print(f"🧹 Cleaning up: {path}")
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
    
    def run(self, cloud_input: str, organ: str, cloud_output_base: str, 
            model: str = 'hu_based', keep_local: bool = False):
        """
        Complete cloud workflow: download → process → upload → cleanup
        
        Args:
            cloud_input: Cloud path to DICOM (e.g., s3://bucket/datasets/lidc_sample)
            organ: Organ to segment
            cloud_output_base: Base cloud path for outputs (e.g., s3://bucket/outputs/)
            model: Segmentation model
            keep_local: Keep local files after upload (default: False)
        """
        local_input = None
        local_output = None
        
        try:
            # Step 1: Download DICOM from cloud
            local_input = self.download_dicom(cloud_input)
            
            # Step 2: Run segmentation
            local_output = self.run_segmentation(local_input, organ, model)
            
            # Step 3: Upload results to cloud
            remote_output = self.upload_results(local_output, cloud_output_base)
            
            print("\n" + "="*70)
            print("✅ CLOUD WORKFLOW COMPLETE")
            print("="*70)
            print(f"Input (cloud):  {cloud_input}")
            print(f"Output (cloud): {remote_output}")
            
            if keep_local:
                print(f"Local input:    {local_input}")
                print(f"Local output:   {local_output}")
            else:
                print("Local files:    Cleaned up")
            
            print("="*70)
            
            # Step 4: Cleanup local files (optional)
            if not keep_local:
                if self.cleanup_input:
                    self.cleanup(local_input)
                if self.cleanup_output:
                    self.cleanup(local_output)
            
            return remote_output
            
        except Exception as e:
            print(f"\n❌ Workflow failed: {e}")
            
            # Cleanup on failure
            if not keep_local:
                if local_input and self.cleanup_input:
                    self.cleanup(local_input)
                if local_output and self.cleanup_output:
                    self.cleanup(local_output)
            
            raise


def main():
    parser = argparse.ArgumentParser(
        description='Cloud-enabled DICOM segmentation workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process DICOM from cloud, upload results
  python3 cloud_workflow.py \\
    --cloud-input s3://my-medical-imaging/datasets/lidc_sample \\
    --organ lungs \\
    --cloud-output s3://my-medical-imaging/outputs/
  
  # Keep local files after processing
  python3 cloud_workflow.py \\
    --cloud-input s3://my-medical-imaging/datasets/brain_ct \\
    --organ brain \\
    --cloud-output s3://my-medical-imaging/outputs/ \\
    --keep-local
  
  # Use different model
  python3 cloud_workflow.py \\
    --cloud-input s3://my-medical-imaging/datasets/chest_ct \\
    --organ lungs \\
    --cloud-output s3://my-medical-imaging/outputs/ \\
    --model totalSegmentator
        """
    )
    
    parser.add_argument('--cloud-input', required=True,
                       help='Cloud path to DICOM dataset (e.g., s3://bucket/datasets/scan)')
    parser.add_argument('--organ', required=True,
                       choices=['lungs', 'brain', 'liver', 'kidney', 'pancreas', 'heart', 'spleen'],
                       help='Organ to segment')
    parser.add_argument('--cloud-output', required=True,
                       help='Base cloud path for outputs (e.g., s3://bucket/outputs/)')
    parser.add_argument('--model', default='hu_based',
                       choices=['hu_based', 'totalSegmentator', 'monai', 'nnunet'],
                       help='Segmentation model (default: hu_based)')
    parser.add_argument('--provider', default='s3',
                       choices=['s3', 'gcs', 'azure'],
                       help='Cloud provider (default: s3 for DigitalOcean Spaces)')
    parser.add_argument('--keep-local', action='store_true',
                       help='Keep local files after upload (default: cleanup)')
    parser.add_argument('--cleanup-input', action='store_true',
                       help='Clean up input DICOM after processing (default: keep for reuse)')
    
    args = parser.parse_args()
    
    workflow = CloudWorkflow(
        provider=args.provider,
        cleanup_input=args.cleanup_input,
        cleanup_output=not args.keep_local
    )
    
    workflow.run(
        cloud_input=args.cloud_input,
        organ=args.organ,
        cloud_output_base=args.cloud_output,
        model=args.model,
        keep_local=args.keep_local
    )


if __name__ == '__main__':
    main()
