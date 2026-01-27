"""
segmentation_engine.py
----------------------
Generic segmentation engine that processes DICOM using organ profiles
"""

import os
import numpy as np
from scipy import ndimage
from skimage import measure
import trimesh
from typing import Dict, Tuple, Any, Optional

from .dicom_loader import load_dicom_series
from .model_loader import ModelFactory


class SegmentationEngine:
    """
    Config-driven segmentation for any organ
    Supports both HU-based (Phase 1) and pre-trained models (Phase 2A+)
    """
    
    def __init__(self, config: Dict[str, Any], model_type: str = "hu_based"):
        """
        Initialize with organ profile config
        
        Args:
            config: Organ configuration (from YAML)
            model_type: "hu_based" (default), "totalSegmentator", "monai", "nnunet"
        """
        self.config = config
        self.organ = config['organ']
        self.tissues = config['tissues']
        self.preprocessing = config['preprocessing']
        self.morphology = config['morphology']
        self.mesh_params = config['mesh']
        self.export_params = config['export']
        
        # Set segmentation method
        self.model_type = model_type
        self.model = None
        
        if model_type != "hu_based":
            try:
                self.model = ModelFactory.create(model_type)
                print(f"  Using {model_type} for segmentation")
            except (ImportError, ValueError) as e:
                print(f"  ⚠️  {model_type} unavailable: {e}")
                print(f"  Falling back to HU-based segmentation")
                self.model_type = "hu_based"
                self.model = None
    
    def process(self, dicom_folder: str, output_folder: str) -> Dict[str, str]:
        """
        Full pipeline: Load DICOM → Segment → Mesh → Export
        Returns: dict with output file paths
        """
        os.makedirs(output_folder, exist_ok=True)
        
        # Step 1: Load DICOM
        print(f"Loading DICOM from {dicom_folder}...")
        volume, spacing, origin = load_dicom_series(dicom_folder)
        print(f"  ✓ Volume: {volume.shape}, spacing: {spacing}")
        
        # Step 2: Preprocess
        volume_preprocessed, spacing_proc = self._preprocess(volume, spacing)
        print(f"  ✓ Preprocessed: {volume_preprocessed.shape}")
        
        # Step 3: Segment
        tissue_meshes = {}
        
        if self.model_type == "hu_based":
            tissue_meshes = self._segment_hu_based(
                volume_preprocessed, spacing_proc, output_folder
            )
        else:
            tissue_meshes = self._segment_model_based(
                volume_preprocessed, spacing_proc, output_folder
            )
        
        # Step 4: Export
        outputs = {}
        if tissue_meshes:
            outputs = self._export_meshes(tissue_meshes, output_folder)
        
        return outputs
    
    def _segment_hu_based(
        self, volume: np.ndarray, spacing: Tuple,
        output_folder: str
    ) -> Dict[str, trimesh.Trimesh]:
        """Phase 1: HU-based segmentation"""
        print("\n[HU-BASED SEGMENTATION - Phase 1]")
        
        # Create body mask (remove air)
        body_mask = self._make_body_mask(volume)
        print(f"  ✓ Body mask: {np.sum(body_mask):,} voxels")
        
        # Segment each tissue
        tissue_meshes = {}
        
        for tissue_name, tissue_config in self.tissues.items():
            print(f"\nSegmenting {tissue_config['name']}...")
            mask = self._segment_tissue(volume, tissue_config, body_mask)
            
            if mask is None or np.sum(mask) < self.config['quality']['min_voxels']:
                print(f"  ⚠️  Skipped (too small)")
                continue
            
            # Create mesh
            mesh = self._mask_to_mesh(mask, spacing, tissue_config['color'])
            if mesh:
                tissue_meshes[tissue_name] = mesh
                print(f"  ✓ Mesh: {len(mesh.vertices):,} vertices, {len(mesh.faces):,} faces")
        
        return tissue_meshes
    
    def _segment_model_based(
        self, volume: np.ndarray, spacing: Tuple,
        output_folder: str
    ) -> Dict[str, trimesh.Trimesh]:
        """Phase 2A+: Pre-trained model segmentation"""
        print(f"\n[{self.model_type.upper()} SEGMENTATION - Phase 2A+]")
        
        # Call pre-trained model
        tissue_masks = self.model.segment(volume, spacing, self.organ)
        
        if tissue_masks is None:
            print(f"  ⚠️  Model failed, falling back to HU-based")
            return self._segment_hu_based(volume, spacing, output_folder)
        
        # Convert masks to meshes
        tissue_meshes = {}
        
        for tissue_name, mask in tissue_masks.items():
            print(f"\nProcessing {tissue_name}...")
            
            if np.sum(mask) < self.config['quality']['min_voxels']:
                print(f"  ⚠️  Skipped (too small)")
                continue
            
            # Apply post-processing morphology
            mask = self._post_process_mask(mask)
            
            # Get color for tissue
            tissue_config = self.tissues.get(tissue_name, {})
            color = tissue_config.get('color', [128, 128, 128])
            
            # Create mesh
            mesh = self._mask_to_mesh(mask, spacing, color)
            if mesh:
                tissue_meshes[tissue_name] = mesh
                print(f"  ✓ Mesh: {len(mesh.vertices):,} vertices, {len(mesh.faces):,} faces")
        
        return tissue_meshes
    
    def _post_process_mask(self, mask: np.ndarray) -> np.ndarray:
        """Post-processing for model-based segmentation masks"""
        # Light morphology operations
        if self.morphology['fill_holes']:
            mask = ndimage.binary_fill_holes(mask)
        
        # Keep largest component
        if self.morphology['keep_largest_component']:
            mask = self._largest_component(mask)
        
        # Median denoise
        mask = ndimage.median_filter(mask.astype(np.uint8), size=3)
        
        return mask.astype(np.uint8)
    
    def _preprocess(self, volume: np.ndarray, spacing: Tuple) -> Tuple:
        """Resample and denoise volume"""
        # Gaussian blur
        volume = ndimage.gaussian_filter(
            volume.astype(np.float32),
            sigma=self.preprocessing['gaussian_sigma']
        )
        
        # Resample to isotropic
        target = self.preprocessing['target_spacing_mm']
        factors = (spacing[0]/target, spacing[1]/target, spacing[2]/target)
        volume = ndimage.zoom(volume, zoom=factors, order=1)
        new_spacing = (target, target, target)
        
        return volume, new_spacing
    
    def _make_body_mask(self, volume: np.ndarray) -> np.ndarray:
        """Create body mask to exclude air"""
        mask = (volume > -400).astype(np.uint8)
        mask = ndimage.binary_dilation(mask, iterations=2)
        mask = ndimage.binary_fill_holes(mask)
        mask = self._largest_component(mask)
        return mask
    
    def _segment_tissue(
        self, volume: np.ndarray,
        tissue_config: Dict,
        body_mask: np.ndarray
    ) -> np.ndarray:
        """Segment tissue using HU range + morphological ops"""
        hu_min = tissue_config['hu_min']
        hu_max = tissue_config['hu_max']
        
        # Threshold
        mask = (volume >= hu_min) & (volume <= hu_max)
        mask = mask.astype(np.uint8)
        mask = mask * body_mask.astype(np.uint8)
        
        # Morphological operations
        if self.morphology['dilation_iterations'] > 0:
            mask = ndimage.binary_dilation(
                mask, iterations=self.morphology['dilation_iterations']
            )
        
        if self.morphology['fill_holes']:
            mask = ndimage.binary_fill_holes(mask)
        
        # Closing
        if self.morphology['closing_radius'] > 0:
            struct = ndimage.generate_binary_structure(3, 2)
            mask = ndimage.binary_closing(
                mask, structure=struct,
                iterations=self.morphology['closing_radius']
            )
        
        # Keep largest component
        if self.morphology['keep_largest_component']:
            mask = self._largest_component(mask)
        
        # Erosion
        if self.morphology['erosion_iterations'] > 0:
            mask = ndimage.binary_erosion(
                mask, iterations=self.morphology['erosion_iterations']
            )
        
        # Median denoise
        mask = ndimage.median_filter(mask.astype(np.uint8), size=3)
        
        return mask.astype(np.uint8)
    
    def _largest_component(self, mask: np.ndarray) -> np.ndarray:
        """Keep only largest connected component"""
        labeled, num = ndimage.label(mask)
        if num <= 1:
            return mask.astype(np.uint8)
        sizes = ndimage.sum(mask, labeled, range(num + 1))
        largest = np.argmax(sizes)
        return (labeled == largest).astype(np.uint8)
    
    def _mask_to_mesh(
        self, mask: np.ndarray,
        spacing: Tuple,
        color_rgb: list
    ) -> trimesh.Trimesh:
        """Convert binary mask to colored mesh"""
        if np.sum(mask) < 100:
            return None
        
        verts, faces, _, _ = measure.marching_cubes(mask, level=0.5, spacing=spacing)
        if len(faces) == 0:
            return None
        
        mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
        mesh.visual.vertex_colors = np.tile(color_rgb, (len(verts), 1))
        
        # Smooth
        iters = self.mesh_params['laplacian_smoothing_iterations']
        if iters > 0:
            try:
                trimesh.smoothing.filter_laplacian(
                    mesh,
                    lamb=self.mesh_params['laplacian_smoothing_lambda'],
                    iterations=iters
                )
            except:
                pass
        
        # Decimate
        target_frac = self.mesh_params['decimation_target']
        if target_frac < 1.0:
            try:
                target_count = int(len(mesh.faces) * target_frac)
                if target_count > 1000:
                    mesh = mesh.simplify_quadratic_decimation(target_count)
            except:
                pass
        
        return mesh
    
    def _export_meshes(self, meshes: Dict, output_folder: str) -> Dict[str, str]:
        """Export all tissue meshes"""
        outputs = {}
        
        for tissue_name, mesh in meshes.items():
            # STL
            if 'stl' in self.export_params['formats']:
                stl_path = os.path.join(
                    output_folder, f"{self.organ}_{tissue_name}.stl"
                )
                mesh.export(stl_path)
                outputs[f"{tissue_name}_stl"] = stl_path
            
            # PLY
            if 'ply' in self.export_params['formats']:
                ply_path = os.path.join(
                    output_folder, f"{self.organ}_{tissue_name}_colored.ply"
                )
                mesh.export(ply_path)
                outputs[f"{tissue_name}_ply"] = ply_path
        
        return outputs
