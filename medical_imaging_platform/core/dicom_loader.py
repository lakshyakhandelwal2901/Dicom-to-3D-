"""
dicom_loader.py
---------------
Load DICOM series into 3D volume
"""

import os
import numpy as np
import pydicom
from pathlib import Path


def load_dicom_series(folder_path: str) -> tuple:
    """
    Load DICOM series from folder
    Returns: (volume, spacing, origin)
      - volume: 3D numpy array (z, y, x)
      - spacing: tuple of voxel spacing (z_spacing, y_spacing, x_spacing)
      - origin: tuple of origin coordinates
    """
    dcm_files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith('.dcm')
    ])
    
    if not dcm_files:
        raise FileNotFoundError(f"No DICOM files found in {folder_path}")
    
    # Load first file to get metadata
    first_dcm = pydicom.dcmread(os.path.join(folder_path, dcm_files[0]))
    
    # Get pixel spacing (with fallback)
    if hasattr(first_dcm, 'PixelSpacing'):
        pixel_spacing = first_dcm.PixelSpacing
        x_spacing = float(pixel_spacing[0])
        y_spacing = float(pixel_spacing[1])
    else:
        x_spacing = y_spacing = 1.0
        print(f"  ⚠️  PixelSpacing not found, using default: 1.0 mm")
    
    # Get slice spacing
    z_spacing = 1.0
    if len(dcm_files) > 1:
        try:
            second_dcm = pydicom.dcmread(os.path.join(folder_path, dcm_files[1]))
            z_pos_1 = float(first_dcm.ImagePositionPatient[2])
            z_pos_2 = float(second_dcm.ImagePositionPatient[2])
            z_spacing = abs(z_pos_2 - z_pos_1)
        except (AttributeError, KeyError):
            if hasattr(first_dcm, 'SliceThickness'):
                z_spacing = float(first_dcm.SliceThickness)
                print(f"  ℹ️  Using SliceThickness: {z_spacing} mm")
            else:
                print(f"  ⚠️  Slice spacing not found, using default: 1.0 mm")
    
    spacing = (z_spacing, y_spacing, x_spacing)
    
    # Get origin (with fallback)
    if hasattr(first_dcm, 'ImagePositionPatient'):
        origin = tuple(float(x) for x in first_dcm.ImagePositionPatient)
    else:
        origin = (0.0, 0.0, 0.0)
        print(f"  ℹ️  ImagePositionPatient not found, using origin: (0, 0, 0)")
    
    # Load all slices
    volume_list = []
    for dcm_file in dcm_files:
        dcm = pydicom.dcmread(os.path.join(folder_path, dcm_file))
        slope = getattr(dcm, 'RescaleSlope', 1)
        intercept = getattr(dcm, 'RescaleIntercept', 0)
        hu = dcm.pixel_array * slope + intercept
        volume_list.append(hu)
    
    volume = np.stack(volume_list, axis=0).astype(np.float32)
    
    return volume, spacing, origin
