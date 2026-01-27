"""
model_loader.py
---------------
Wrapper for pre-trained model APIs (TotalSegmentator, MONAI, nnU-Net)
Abstracts model inference behind unified interface
"""

import os
import tempfile
import numpy as np
from typing import Dict, Tuple, Any

try:
    from totalsegmentator.python_api import totalsegmentator
    TOTALSEG_AVAILABLE = True
except ImportError:
    TOTALSEG_AVAILABLE = False

try:
    import nibabel as nib
    NIBABEL_AVAILABLE = True
except ImportError:
    NIBABEL_AVAILABLE = False


class PreTrainedModelLoader:
    """Load and use pre-trained segmentation models"""
    
    def __init__(self, model_type: str = "totalSegmentator"):
        """
        Initialize model loader
        
        Args:
            model_type: "totalSegmentator", "monai", or "nnunet"
        """
        self.model_type = model_type
        self._validate_availability()
    
    def _validate_availability(self):
        """Check if required model is available"""
        if self.model_type == "totalSegmentator":
            if not TOTALSEG_AVAILABLE:
                raise ImportError(
                    "TotalSegmentator not installed. "
                    "Run: pip install totalsegmentator"
                )
        elif self.model_type == "monai":
            raise NotImplementedError("MONAI integration coming in Phase 2B")
        elif self.model_type == "nnunet":
            raise NotImplementedError("nnU-Net integration coming in Phase 2C")
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def segment(
        self,
        volume: np.ndarray,
        spacing: Tuple[float, float, float],
        organ_name: str
    ) -> Dict[str, np.ndarray]:
        """
        Segment organ using pre-trained model
        
        Args:
            volume: 3D numpy array (HU values)
            spacing: (x, y, z) spacing in mm
            organ_name: Name of organ to segment
        
        Returns:
            Dict of {organ_tissue: binary_mask}
        """
        if self.model_type == "totalSegmentator":
            return self._segment_totalSegmentator(volume, spacing, organ_name)
        else:
            raise NotImplementedError(f"{self.model_type} not implemented yet")
    
    def _segment_totalSegmentator(
        self,
        volume: np.ndarray,
        spacing: Tuple[float, float, float],
        organ_name: str
    ) -> Dict[str, np.ndarray]:
        """
        Segment using TotalSegmentator
        
        TotalSegmentator predicts 104+ organs/tissues simultaneously.
        We extract the relevant ones based on organ_name.
        
        Note: TotalSegmentator outputs individual NIfTI files per organ,
        not a single multi-label segmentation.
        """
        if not NIBABEL_AVAILABLE:
            raise ImportError(
                "nibabel required for TotalSegmentator. "
                "Run: pip install nibabel"
            )
        
        print(f"  📊 TotalSegmentator: Analyzing {organ_name}...")
        print(f"     (This may take 2-10 minutes depending on CPU/GPU)")
        
        # Save volume as temporary NIfTI file
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.nii.gz")
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Create NIfTI with proper spacing
            affine = np.diag(list(spacing) + [1])
            img = nib.Nifti1Image(volume.astype(np.int16), affine)
            nib.save(img, input_path)
            
            # Run TotalSegmentator
            try:
                print(f"     Device: {'GPU' if self._has_gpu() else 'CPU'}")
                totalsegmentator(
                    input=input_path,
                    output=output_dir,
                    fast=False,  # Use full model for best accuracy
                    ml=True,     # Use multi-label output
                    device="gpu" if self._has_gpu() else "cpu",
                    quiet=False
                )
                print(f"  ✅ TotalSegmentator completed")
            except Exception as e:
                print(f"  ⚠️  TotalSegmentator failed: {e}")
                print(f"  → Falling back to HU-based segmentation")
                return None
            
            # TotalSegmentator outputs individual organ files
            # Find the output file (it's in the output directory)
            output_files = os.listdir(output_dir)
            if not output_files:
                print(f"  ⚠️  No segmentation files generated")
                return None
            
            # Load the segmentation (TotalSegmentator creates combined.nii.gz or individual organs)
            # Try to load the main segmentation file
            seg_file = None
            for filename in ['combined.nii.gz', 'segmentations.nii.gz']:
                potential_path = os.path.join(output_dir, filename)
                if os.path.exists(potential_path):
                    seg_file = potential_path
                    break
            
            if seg_file is None:
                # Try loading individual organ files
                print(f"  ℹ️  Loading individual organ segmentations...")
                label_mapping = self._get_totalseg_filenames(organ_name)
                results = {}
                
                for tissue_name, filename in label_mapping.items():
                    filepath = os.path.join(output_dir, filename)
                    if os.path.exists(filepath):
                        seg_img = nib.load(filepath)
                        mask = np.array(seg_img.dataobj).astype(np.uint8)
                        if np.sum(mask) > 100:  # Min voxels check
                            results[tissue_name] = mask
                            print(f"     ✓ {tissue_name}: {np.sum(mask):,} voxels")
                
                return results if results else None
            
            # Load combined segmentation
            seg_img = nib.load(seg_file)
            seg_array = np.array(seg_img.dataobj)
            
            # Extract organ-specific tissues by label values
            label_mapping = self._get_label_mapping(organ_name)
            
            results = {}
            for tissue_name, label_value in label_mapping.items():
                mask = (seg_array == label_value).astype(np.uint8)
                if np.sum(mask) > 100:  # Min voxels check
                    results[tissue_name] = mask
                    print(f"     ✓ {tissue_name}: {np.sum(mask):,} voxels")
            
            return results if results else None
    
    def _get_totalseg_filenames(self, organ_name: str) -> Dict[str, str]:
        """
        Get TotalSegmentator output filenames for organ
        
        TotalSegmentator outputs individual NIfTI files like:
        - brain.nii.gz
        - skull.nii.gz
        - liver.nii.gz
        etc.
        """
        mapping = {
            "brain": {
                "brain": "brain.nii.gz",
                "shell": "skull.nii.gz",
            },
            "liver": {
                "liver": "liver.nii.gz",
                "vasculature": "portal_vein_and_splenic_vein.nii.gz",
            },
            "lungs": {
                "lung_tissue": "lung_upper_lobe_left.nii.gz",  # Combine multiple
                "airways": "trachea.nii.gz",
            },
            "heart": {
                "cardiac_muscle": "heart.nii.gz",
                "cardiac_chambers": "heart_myocardium.nii.gz",
            },
            "kidneys": {
                "renal_cortex": "kidney_left.nii.gz",  # TotalSeg doesn't split cortex/medulla
                "renal_medulla": "kidney_right.nii.gz",
            },
            "bones": {
                "cortical_bone": "vertebrae_L5.nii.gz",  # Example
                "trabecular_bone": "rib_left_1.nii.gz",
            },
            "pancreas": {
                "pancreatic_tissue": "pancreas.nii.gz",
                "pancreatic_ducts": "duodenum.nii.gz",  # Approximation
            },
        }
        return mapping.get(organ_name.lower(), {})
    
    def _get_label_mapping(self, organ_name: str) -> Dict[str, int]:
        """
        Get TotalSegmentator label mapping for organ
        
        Simplified mapping - TotalSegmentator actually has 104 labels.
        This is a sample for demonstration.
        """
        mapping = {
            "brain": {
                "brain": 1,  # Brain parenchyma (simplified)
                "shell": 2,  # Skull (simplified)
            },
            "liver": {
                "liver": 3,
                "vasculature": 4,
            },
            "lungs": {
                "lung_tissue": 5,
                "airways": 6,
            },
            "heart": {
                "cardiac_muscle": 7,
                "cardiac_chambers": 8,
            },
            "kidneys": {
                "renal_cortex": 9,
                "renal_medulla": 10,
            },
            "bones": {
                "cortical_bone": 11,
                "trabecular_bone": 12,
            },
            "pancreas": {
                "pancreatic_tissue": 13,
                "pancreatic_ducts": 14,
            },
        }
        return mapping.get(organ_name.lower(), {})
    
    def _has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False


class ModelFactory:
    """Factory for creating model loaders"""
    
    @staticmethod
    def create(model_type: str) -> PreTrainedModelLoader:
        """Create appropriate model loader"""
        if model_type == "hu_based":
            # HU-based doesn't use PreTrainedModelLoader
            return None
        elif model_type in ["totalSegmentator", "monai", "nnunet"]:
            return PreTrainedModelLoader(model_type)
        else:
            raise ValueError(f"Unknown model type: {model_type}")


# Example usage:
if __name__ == "__main__":
    # This is a usage example
    try:
        loader = PreTrainedModelLoader("totalSegmentator")
        print("✓ TotalSegmentator available")
    except ImportError as e:
        print(f"✗ {e}")
