#!/usr/bin/env python3
"""
Cloud Storage Manager
Supports AWS S3, Google Cloud Storage, Azure Blob Storage
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict
import subprocess
import sys


class CloudStorage:
    """Unified cloud storage interface for medical imaging data"""
    
    def __init__(self, provider: str = 's3', config_path: Optional[str] = None):
        """
        Initialize cloud storage
        
        Args:
            provider: 's3', 'gcs', or 'azure'
            config_path: Path to cloud_config.json
        """
        self.provider = provider.lower()
        self.config = self._load_config(config_path)
        self._validate_dependencies()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load cloud configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'cloud_config.json'
        
        if not os.path.exists(config_path):
            return {}
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config.get(self.provider, {})
    
    def _validate_dependencies(self):
        """Check if cloud CLI tools are installed"""
        cli_tools = {
            's3': 'aws',
            'gcs': 'gsutil',
            'azure': 'az'
        }
        
        tool = cli_tools.get(self.provider)
        if tool:
            try:
                subprocess.run([tool, '--version'], 
                             capture_output=True, 
                             check=True,
                             timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                print(f"⚠️  Warning: {tool} CLI not found. Install it for {self.provider} support.")
                print(f"   Install: pip install awscli (S3) | pip install google-cloud-storage (GCS) | pip install azure-cli (Azure)")
    
    def upload(self, local_path: str, remote_path: str, recursive: bool = False) -> bool:
        """
        Upload file or directory to cloud storage
        
        Args:
            local_path: Local file/directory path
            remote_path: Remote destination (e.g., 's3://bucket/path', 'gs://bucket/path')
            recursive: Upload directory recursively
        
        Returns:
            Success status
        """
        if not os.path.exists(local_path):
            print(f"❌ Local path not found: {local_path}")
            return False
        
        try:
            if self.provider == 's3':
                return self._upload_s3(local_path, remote_path, recursive)
            elif self.provider == 'gcs':
                return self._upload_gcs(local_path, remote_path, recursive)
            elif self.provider == 'azure':
                return self._upload_azure(local_path, remote_path, recursive)
            else:
                print(f"❌ Unsupported provider: {self.provider}")
                return False
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def download(self, remote_path: str, local_path: str, recursive: bool = False) -> bool:
        """
        Download file or directory from cloud storage
        
        Args:
            remote_path: Remote source path
            local_path: Local destination path
            recursive: Download directory recursively
        
        Returns:
            Success status
        """
        try:
            os.makedirs(os.path.dirname(local_path) or '.', exist_ok=True)
            
            if self.provider == 's3':
                return self._download_s3(remote_path, local_path, recursive)
            elif self.provider == 'gcs':
                return self._download_gcs(remote_path, local_path, recursive)
            elif self.provider == 'azure':
                return self._download_azure(remote_path, local_path, recursive)
            else:
                print(f"❌ Unsupported provider: {self.provider}")
                return False
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def list_files(self, remote_path: str) -> List[str]:
        """List files in cloud storage location"""
        try:
            if self.provider == 's3':
                return self._list_s3(remote_path)
            elif self.provider == 'gcs':
                return self._list_gcs(remote_path)
            elif self.provider == 'azure':
                return self._list_azure(remote_path)
            else:
                return []
        except Exception as e:
            print(f"❌ List failed: {e}")
            return []
    
    def delete(self, remote_path: str, recursive: bool = False) -> bool:
        """Delete file or directory from cloud storage"""
        try:
            if self.provider == 's3':
                return self._delete_s3(remote_path, recursive)
            elif self.provider == 'gcs':
                return self._delete_gcs(remote_path, recursive)
            elif self.provider == 'azure':
                return self._delete_azure(remote_path, recursive)
            else:
                return False
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return False
    
    # S3 implementations
    def _upload_s3(self, local_path: str, remote_path: str, recursive: bool) -> bool:
        cmd = ['aws', 's3', 'cp', local_path, remote_path]
        if recursive:
            cmd.append('--recursive')
        
        # Add endpoint URL for DigitalOcean Spaces or other S3-compatible
        if self.config.get('endpoint_url'):
            cmd.extend(['--endpoint-url', self.config['endpoint_url']])
        
        # Add profile if specified
        if self.config.get('profile'):
            env = os.environ.copy()
            env['AWS_PROFILE'] = self.config['profile']
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Uploaded to {remote_path}")
            return True
        else:
            print(f"❌ S3 upload failed: {result.stderr}")
            return False
    
    def _download_s3(self, remote_path: str, local_path: str, recursive: bool) -> bool:
        cmd = ['aws', 's3', 'cp', remote_path, local_path]
        if recursive:
            cmd.append('--recursive')
        
        # Add endpoint URL for DigitalOcean Spaces or other S3-compatible
        if self.config.get('endpoint_url'):
            cmd.extend(['--endpoint-url', self.config['endpoint_url']])
        
        # Add profile if specified
        if self.config.get('profile'):
            env = os.environ.copy()
            env['AWS_PROFILE'] = self.config['profile']
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Downloaded to {local_path}")
            return True
        else:
            print(f"❌ S3 download failed: {result.stderr}")
            return False
    
    def _list_s3(self, remote_path: str) -> List[str]:
        cmd = ['aws', 's3', 'ls', remote_path, '--recursive']
        
        # Add endpoint URL for DigitalOcean Spaces
        if self.config.get('endpoint_url'):
            cmd.extend(['--endpoint-url', self.config['endpoint_url']])
        
        # Add profile if specified
        if self.config.get('profile'):
            env = os.environ.copy()
            env['AWS_PROFILE'] = self.config['profile']
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            files = [line.split()[-1] for line in result.stdout.strip().split('\n') if line]
            return files
        return []
    
    def _delete_s3(self, remote_path: str, recursive: bool) -> bool:
        cmd = ['aws', 's3', 'rm', remote_path]
        if recursive:
            cmd.append('--recursive')
        
        # Add endpoint URL for DigitalOcean Spaces
        if self.config.get('endpoint_url'):
            cmd.extend(['--endpoint-url', self.config['endpoint_url']])
        
        # Add profile if specified
        if self.config.get('profile'):
            env = os.environ.copy()
            env['AWS_PROFILE'] = self.config['profile']
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0
    
    # GCS implementations
    def _upload_gcs(self, local_path: str, remote_path: str, recursive: bool) -> bool:
        cmd = ['gsutil', 'cp']
        if recursive:
            cmd.append('-r')
        cmd.extend([local_path, remote_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Uploaded to {remote_path}")
            return True
        else:
            print(f"❌ GCS upload failed: {result.stderr}")
            return False
    
    def _download_gcs(self, remote_path: str, local_path: str, recursive: bool) -> bool:
        cmd = ['gsutil', 'cp']
        if recursive:
            cmd.append('-r')
        cmd.extend([remote_path, local_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Downloaded to {local_path}")
            return True
        else:
            print(f"❌ GCS download failed: {result.stderr}")
            return False
    
    def _list_gcs(self, remote_path: str) -> List[str]:
        cmd = ['gsutil', 'ls', '-r', remote_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            files = [line.strip() for line in result.stdout.split('\n') if line and not line.endswith(':')]
            return files
        return []
    
    def _delete_gcs(self, remote_path: str, recursive: bool) -> bool:
        cmd = ['gsutil', 'rm']
        if recursive:
            cmd.append('-r')
        cmd.append(remote_path)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    # Azure implementations
    def _upload_azure(self, local_path: str, remote_path: str, recursive: bool) -> bool:
        # Azure Blob Storage format: https://account.blob.core.windows.net/container/path
        # Parse container and blob path
        container, blob_path = self._parse_azure_path(remote_path)
        
        cmd = ['az', 'storage', 'blob', 'upload', '--file', local_path, 
               '--container-name', container, '--name', blob_path]
        
        if self.config.get('account_name'):
            cmd.extend(['--account-name', self.config['account_name']])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Uploaded to {remote_path}")
            return True
        else:
            print(f"❌ Azure upload failed: {result.stderr}")
            return False
    
    def _download_azure(self, remote_path: str, local_path: str, recursive: bool) -> bool:
        container, blob_path = self._parse_azure_path(remote_path)
        
        cmd = ['az', 'storage', 'blob', 'download', '--file', local_path,
               '--container-name', container, '--name', blob_path]
        
        if self.config.get('account_name'):
            cmd.extend(['--account-name', self.config['account_name']])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Downloaded to {local_path}")
            return True
        else:
            print(f"❌ Azure download failed: {result.stderr}")
            return False
    
    def _list_azure(self, remote_path: str) -> List[str]:
        container, prefix = self._parse_azure_path(remote_path)
        
        cmd = ['az', 'storage', 'blob', 'list', '--container-name', container,
               '--prefix', prefix, '--output', 'json']
        
        if self.config.get('account_name'):
            cmd.extend(['--account-name', self.config['account_name']])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            blobs = json.loads(result.stdout)
            return [blob['name'] for blob in blobs]
        return []
    
    def _delete_azure(self, remote_path: str, recursive: bool) -> bool:
        container, blob_path = self._parse_azure_path(remote_path)
        
        cmd = ['az', 'storage', 'blob', 'delete', '--container-name', container,
               '--name', blob_path]
        
        if self.config.get('account_name'):
            cmd.extend(['--account-name', self.config['account_name']])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _parse_azure_path(self, path: str) -> tuple:
        """Parse Azure Blob Storage path into container and blob"""
        # Format: https://account.blob.core.windows.net/container/blob/path
        # Or: container/blob/path
        if path.startswith('https://'):
            parts = path.split('/', 4)
            container = parts[3]
            blob = parts[4] if len(parts) > 4 else ''
        else:
            parts = path.split('/', 1)
            container = parts[0]
            blob = parts[1] if len(parts) > 1 else ''
        
        return container, blob


def main():
    """CLI for cloud storage operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cloud Storage Manager for Medical Imaging')
    parser.add_argument('action', choices=['upload', 'download', 'list', 'delete'],
                       help='Action to perform')
    parser.add_argument('--provider', default='s3', choices=['s3', 'gcs', 'azure'],
                       help='Cloud provider')
    parser.add_argument('--local', help='Local path')
    parser.add_argument('--remote', required=True, help='Remote path (s3://bucket/key, gs://bucket/key)')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursive operation')
    parser.add_argument('--config', help='Path to cloud_config.json')
    
    args = parser.parse_args()
    
    storage = CloudStorage(provider=args.provider, config_path=args.config)
    
    if args.action == 'upload':
        if not args.local:
            print("❌ --local required for upload")
            sys.exit(1)
        success = storage.upload(args.local, args.remote, args.recursive)
        sys.exit(0 if success else 1)
    
    elif args.action == 'download':
        if not args.local:
            print("❌ --local required for download")
            sys.exit(1)
        success = storage.download(args.remote, args.local, args.recursive)
        sys.exit(0 if success else 1)
    
    elif args.action == 'list':
        files = storage.list_files(args.remote)
        for f in files:
            print(f)
        sys.exit(0)
    
    elif args.action == 'delete':
        confirm = input(f"Delete {args.remote}? (yes/no): ")
        if confirm.lower() == 'yes':
            success = storage.delete(args.remote, args.recursive)
            sys.exit(0 if success else 1)
        else:
            print("Cancelled")
            sys.exit(1)


if __name__ == '__main__':
    main()
