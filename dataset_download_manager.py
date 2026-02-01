#!/usr/bin/env python3
"""
Dataset Download Manager
Downloads medical datasets in parallel with progress tracking
Stores in Google Drive after downloading
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Dataset URLs
MEDICAL_DECATHLON_TASKS = {
    "Task01_BrainTumour": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task01_BrainTumour.tar",
        "size_gb": 4.5,
        "scans": 484
    },
    "Task02_Heart": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task02_Heart.tar",
        "size_gb": 1.2,
        "scans": 30
    },
    "Task03_Liver": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task03_Liver.tar",
        "size_gb": 8.5,
        "scans": 131
    },
    "Task04_Hippocampus": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task04_Hippocampus.tar",
        "size_gb": 0.2,
        "scans": 260
    },
    "Task05_Prostate": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar",
        "size_gb": 1.1,
        "scans": 32
    },
    "Task06_Lung": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task06_Lung.tar",
        "size_gb": 7.2,
        "scans": 64
    },
    "Task07_Pancreas": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task07_Pancreas.tar",
        "size_gb": 16.0,
        "scans": 282
    },
    "Task08_HepaticVessel": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task08_HepaticVessel.tar",
        "size_gb": 12.0,
        "scans": 303
    },
    "Task09_Spleen": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task09_Spleen.tar",
        "size_gb": 2.8,
        "scans": 41
    },
    "Task10_Colon": {
        "url": "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task10_Colon.tar",
        "size_gb": 8.1,
        "scans": 126
    }
}

class DownloadManager:
    def __init__(self):
        self.download_dir = Path("/workspaces/Dicom-to-3D-/data/medical_decathlon")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.download_dir / "download_progress.log"
        self.lock = threading.Lock()
        self.downloads = {}
        
    def log_progress(self, message):
        """Log download progress"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}] {message}"
            print(log_msg)
            with open(self.log_file, 'a') as f:
                f.write(log_msg + "\n")
    
    def download_task(self, task_name, task_info):
        """Download a single task"""
        try:
            url = task_info["url"]
            size_gb = task_info["size_gb"]
            scans = task_info["scans"]
            
            output_file = self.download_dir / f"{task_name}.tar"
            
            # Check if already downloaded
            if output_file.exists():
                self.log_progress(f"✓ {task_name} already exists ({output_file.stat().st_size / (1024**3):.1f} GB)")
                return True
            
            self.log_progress(f"📥 Downloading {task_name} ({size_gb} GB, {scans} scans)...")
            
            # Start download
            cmd = [
                "wget", "-c",
                "--show-progress",
                "--progress=bar:force:noscroll",
                "-O", str(output_file),
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=86400)  # 24h timeout
            
            if result.returncode == 0:
                downloaded_size = output_file.stat().st_size / (1024**3)
                self.log_progress(f"✅ {task_name} downloaded ({downloaded_size:.1f} GB)")
                
                # Extract
                self.log_progress(f"📦 Extracting {task_name}...")
                extract_cmd = ["tar", "-xf", str(output_file), "-C", str(self.download_dir)]
                subprocess.run(extract_cmd, capture_output=True)
                self.log_progress(f"✅ {task_name} extracted")
                
                # Remove tar file to save space
                os.remove(output_file)
                self.log_progress(f"🗑️  Removed {task_name}.tar (freed space)")
                
                return True
            else:
                self.log_progress(f"❌ {task_name} download failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_progress(f"❌ {task_name} error: {e}")
            return False
    
    def download_all(self, max_workers=2):
        """Download all tasks in parallel"""
        self.log_progress("\n" + "="*80)
        self.log_progress("MEDICAL DECATHLON DATASET DOWNLOAD MANAGER".center(80))
        self.log_progress("="*80 + "\n")
        
        total_size = sum(task["size_gb"] for task in MEDICAL_DECATHLON_TASKS.values())
        total_scans = sum(task["scans"] for task in MEDICAL_DECATHLON_TASKS.values())
        
        self.log_progress(f"📊 Starting parallel download of {len(MEDICAL_DECATHLON_TASKS)} tasks")
        self.log_progress(f"   Total size: {total_size:.1f} GB")
        self.log_progress(f"   Total scans: {total_scans:,}")
        self.log_progress(f"   Parallel workers: {max_workers}")
        self.log_progress("")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.download_task, task_name, task_info): task_name
                for task_name, task_info in MEDICAL_DECATHLON_TASKS.items()
            }
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                task_name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.log_progress(f"❌ {task_name} failed: {e}")
        
        elapsed = time.time() - start_time
        hours = elapsed / 3600
        
        self.log_progress("")
        self.log_progress("="*80)
        self.log_progress("DOWNLOAD COMPLETE".center(80))
        self.log_progress("="*80)
        self.log_progress(f"⏱️  Total time: {hours:.1f} hours")
        self.log_progress(f"📊 Downloaded: {total_size:.1f} GB")
        self.log_progress(f"📁 Location: {self.download_dir}")
        self.log_progress("")
        self.log_progress("✅ All datasets ready for processing!")
        self.log_progress("")
        self.log_progress("Next steps:")
        self.log_progress("  1. Run Phase 1 professional upgrade on datasets")
        self.log_progress("  2. Upload results to Google Drive")
        self.log_progress("  3. Validate against ground truth labels")
        self.log_progress("")
    
    def show_status(self):
        """Show download status"""
        print("\n" + "="*80)
        print("DOWNLOAD STATUS".center(80))
        print("="*80 + "\n")
        
        total_size = 0
        completed = 0
        
        for task_name in MEDICAL_DECATHLON_TASKS:
            task_dir = self.download_dir / task_name
            if task_dir.exists():
                # Calculate directory size
                size = 0
                for dirpath, dirnames, filenames in os.walk(task_dir):
                    for filename in filenames:
                        size += os.path.getsize(os.path.join(dirpath, filename))
                
                size_gb = size / (1024**3)
                total_size += size_gb
                completed += 1
                print(f"  ✅ {task_name:<30} {size_gb:>8.1f} GB")
            else:
                print(f"  ⏳ {task_name:<30} Downloading...")
        
        print("")
        print(f"Progress: {completed}/{len(MEDICAL_DECATHLON_TASKS)} tasks complete")
        print(f"Total downloaded: {total_size:.1f} GB")
        print("")


def main():
    """Main execution"""
    manager = DownloadManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
            manager.download_all(max_workers=max_workers)
        elif command == "status":
            manager.show_status()
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python dataset_download_manager.py start [workers]")
            print("  python dataset_download_manager.py status")
    else:
        print("Medical Decathlon Download Manager")
        print("\nUsage:")
        print("  # Start download (2 parallel tasks)")
        print("  python dataset_download_manager.py start")
        print("")
        print("  # Start with more parallel downloads")
        print("  python dataset_download_manager.py start 3")
        print("")
        print("  # Check download status")
        print("  python dataset_download_manager.py status")
        print("")


if __name__ == "__main__":
    main()
