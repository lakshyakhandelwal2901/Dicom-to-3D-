#!/usr/bin/env python3
"""
Generate a 3D Model - Standalone Demo
Creates a realistic 3D medical model without requiring external datasets
"""

import numpy as np
from pathlib import Path
import sys

def create_synthetic_brain_volume():
    """Create a synthetic brain CT volume"""
    print("🧠 Creating synthetic brain CT volume...")
    
    # Create 3D volume (simplified brain-like structure)
    shape = (64, 64, 64)
    volume = np.zeros(shape, dtype=np.float32)
    
    # Create brain outline (ellipsoid)
    center = np.array(shape) / 2
    for x in range(shape[0]):
        for y in range(shape[1]):
            for z in range(shape[2]):
                dx = (x - center[0]) / (shape[0] / 2.5)
                dy = (y - center[1]) / (shape[1] / 2.5)
                dz = (z - center[2]) / (shape[2] / 2.5)
                distance = np.sqrt(dx**2 + dy**2 + dz**2)
                
                # Brain tissue (HU ~40)
                if distance < 0.9:
                    volume[x, y, z] = np.random.normal(40, 5)
                # CSF in ventricles (HU ~15)
                elif distance < 0.6:
                    volume[x, y, z] = np.random.normal(15, 3)
    
    # Add some lesion (tumor-like)
    lesion_center = center + np.array([10, 5, -5])
    for x in range(shape[0]):
        for y in range(shape[1]):
            for z in range(shape[2]):
                dx = (x - lesion_center[0]) / 5
                dy = (y - lesion_center[1]) / 5
                dz = (z - lesion_center[2]) / 5
                distance = np.sqrt(dx**2 + dy**2 + dz**2)
                if distance < 3:
                    volume[x, y, z] = max(60, volume[x, y, z] + 30)  # Darker lesion
    
    return volume

def volume_to_mesh(volume, threshold=30, smooth=True):
    """Convert volume to mesh vertices and faces"""
    print(f"🔄 Converting volume to mesh (threshold={threshold})...")
    
    try:
        from skimage import measure
    except ImportError:
        print("⚠️ Installing scikit-image...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "scikit-image"], check=True)
        from skimage import measure
    
    # Create binary mask
    mask = volume > threshold
    
    # Extract surface
    verts, faces, _, _ = measure.marching_cubes(mask, level=0.5)
    
    # Normalize vertices
    verts = verts / np.array(volume.shape) * 100  # Scale to reasonable size
    
    if smooth and len(verts) > 0:
        # Simple smoothing by averaging with neighbors
        from scipy.spatial import cKDTree
        tree = cKDTree(verts)
        
        smoothed_verts = verts.copy()
        for i, vert in enumerate(verts):
            distances, indices = tree.query(vert, k=5)
            smoothed_verts[i] = verts[indices].mean(axis=0)
        
        verts = smoothed_verts
    
    return verts, faces

def save_ply(verts, faces, output_path, colors=None):
    """Save mesh as PLY file"""
    print(f"💾 Saving PLY: {output_path}")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        # PLY header
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(verts)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        
        if colors is not None:
            f.write("property uchar red\n")
            f.write("property uchar green\n")
            f.write("property uchar blue\n")
        
        f.write(f"element face {len(faces)}\n")
        f.write("property list uchar int vertex_indices\n")
        f.write("end_header\n")
        
        # Vertices
        for i, v in enumerate(verts):
            if colors is not None:
                r, g, b = colors[i] if i < len(colors) else (180, 100, 100)
                f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f} {r} {g} {b}\n")
            else:
                f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        
        # Faces
        for face in faces:
            f.write(f"3 {face[0]} {face[1]} {face[2]}\n")
    
    print(f"✅ Saved: {output_path}")
    print(f"   Vertices: {len(verts)}")
    print(f"   Faces: {len(faces)}")

def generate_colored_model(volume, output_path):
    """Generate model with colors based on intensity"""
    print("🎨 Creating colored model...")
    
    # Get vertices and faces
    verts, faces = volume_to_mesh(volume, threshold=20)
    
    # Assign colors based on position/intensity
    colors = np.zeros((len(verts), 3), dtype=np.uint8)
    
    # Map vertex positions to colors
    for i, v in enumerate(verts):
        # X-axis: Red
        # Y-axis: Green
        # Z-axis: Blue
        r = int(np.clip((v[0] / 100) * 255, 0, 255))
        g = int(np.clip((v[1] / 100) * 255, 0, 255))
        b = int(np.clip((v[2] / 100) * 255, 0, 255))
        colors[i] = [r, g, b]
    
    save_ply(verts, faces, output_path, colors)

def main():
    print("\n" + "="*70)
    print("🚀 3D Medical Model Generator")
    print("="*70 + "\n")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Generate synthetic volume
        volume = create_synthetic_brain_volume()
        print(f"✅ Volume created: shape={volume.shape}, HU range=[{volume.min():.1f}, {volume.max():.1f}]")
        
        # Generate basic model
        print("\n📦 Generating basic model...")
        verts, faces = volume_to_mesh(volume, threshold=30)
        
        if len(verts) > 0:
            save_ply(verts, faces, "output/brain_model_basic.ply")
            
            # Generate colored model
            print("\n🎨 Generating colored model...")
            generate_colored_model(volume, "output/brain_model_colored.ply")
            
            print("\n" + "="*70)
            print("✅ SUCCESS: 3D Models Generated!")
            print("="*70)
            print("\n📍 Output Files:")
            print("   ✓ output/brain_model_basic.ply")
            print("   ✓ output/brain_model_colored.ply")
            print("\n📊 Model Statistics:")
            print(f"   • Vertices: {len(verts):,}")
            print(f"   • Faces: {len(faces):,}")
            print(f"   • Volume bounds: {verts.min():.1f} to {verts.max():.1f}")
            print("\n💡 Tip: Open PLY files in:")
            print("   • Blender (Free, powerful)")
            print("   • MeshLab (Free, lightweight)")
            print("   • CloudCompare (Free, point cloud focus)")
            print("   • Any STL viewer")
            print("\n")
        else:
            print("❌ No mesh generated. Try adjusting threshold.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
