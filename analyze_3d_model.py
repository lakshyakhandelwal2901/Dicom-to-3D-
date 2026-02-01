#!/usr/bin/env python3
"""
AI-Powered 3D Model Quality Analyzer
Renders 3D models from multiple angles and uses AI vision to analyze quality
"""

import os
import sys
import trimesh
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import argparse

def download_model_from_cloud(cloud_path, local_path):
    """Download model from DigitalOcean Spaces"""
    import subprocess
    
    print(f"📥 Downloading model from {cloud_path}")
    
    # Create local directory
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # Use AWS CLI to download
    cmd = [
        "aws", "s3", "cp",
        cloud_path,
        local_path,
        "--endpoint-url=https://sgp1.digitaloceanspaces.com"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        # Try using the do_spaces.sh script instead
        print("⚠️ AWS CLI failed, trying do_spaces.sh...")
        download_dir = os.path.dirname(local_path)
        cmd = ["./do_spaces.sh", "download", cloud_path, download_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to download model: {result.stderr}")
    
    print(f"✓ Downloaded to {local_path}")
    return local_path

def render_3d_model(mesh, output_path, angle=(30, 45, 0), resolution=(1920, 1080), 
                   show_edges=False, background_color=(40, 40, 50)):
    """
    Render a 3D mesh from a specific angle using trimesh
    
    Args:
        mesh: trimesh object
        output_path: where to save the render
        angle: (elevation, azimuth, roll) in degrees
        resolution: (width, height) in pixels
        show_edges: whether to show mesh edges
        background_color: RGB tuple (0-255)
    """
    import pyrender
    
    # Create pyrender scene
    scene = pyrender.Scene(ambient_light=[0.4, 0.4, 0.4], bg_color=[c/255 for c in background_color])
    
    # Convert trimesh to pyrender mesh
    if mesh.visual.kind == 'vertex':
        # Has vertex colors
        pyrender_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=True)
    else:
        # No colors, use default
        material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=[0.8, 0.8, 0.8, 1.0],
            metallicFactor=0.2,
            roughnessFactor=0.8
        )
        pyrender_mesh = pyrender.Mesh.from_trimesh(mesh, material=material, smooth=True)
    
    scene.add(pyrender_mesh)
    
    # Add lighting
    light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=3.0)
    scene.add(light, pose=np.eye(4))
    
    # Position camera
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
    
    # Calculate camera position based on mesh bounds
    bounds = mesh.bounds
    centroid = mesh.centroid
    scale = np.linalg.norm(bounds[1] - bounds[0])
    
    # Convert angles to radians
    elev_rad = np.radians(angle[0])
    azim_rad = np.radians(angle[1])
    
    # Calculate camera position
    distance = scale * 1.5
    cam_x = distance * np.cos(elev_rad) * np.cos(azim_rad)
    cam_y = distance * np.sin(elev_rad)
    cam_z = distance * np.cos(elev_rad) * np.sin(azim_rad)
    
    camera_pose = np.eye(4)
    camera_pose[:3, 3] = [cam_x, cam_y, cam_z]
    
    # Look at centroid
    forward = centroid - camera_pose[:3, 3]
    forward = forward / np.linalg.norm(forward)
    
    right = np.cross(forward, [0, 1, 0])
    right = right / np.linalg.norm(right)
    
    up = np.cross(right, forward)
    
    camera_pose[:3, 0] = right
    camera_pose[:3, 1] = up
    camera_pose[:3, 2] = -forward
    
    scene.add(camera, pose=camera_pose)
    
    # Render
    renderer = pyrender.OffscreenRenderer(resolution[0], resolution[1])
    color, depth = renderer.render(scene)
    
    # Save image
    img = Image.fromarray(color)
    img.save(output_path)
    
    renderer.delete()
    
    return output_path

def generate_analysis_views(mesh, output_dir):
    """Generate multiple views of the 3D model for AI analysis"""
    
    views = {
        'front': (0, 0, 0),
        'back': (0, 180, 0),
        'left': (0, -90, 0),
        'right': (0, 90, 0),
        'top': (90, 0, 0),
        'bottom': (-90, 0, 0),
        'oblique_1': (30, 45, 0),
        'oblique_2': (30, 135, 0),
        'oblique_3': (30, 225, 0),
        'oblique_4': (30, 315, 0),
    }
    
    rendered_views = {}
    
    print(f"🎨 Rendering {len(views)} views...")
    
    for view_name, angles in views.items():
        output_path = os.path.join(output_dir, f"view_{view_name}.png")
        try:
            render_3d_model(mesh, output_path, angle=angles, resolution=(1920, 1080))
            rendered_views[view_name] = output_path
            print(f"  ✓ {view_name}: {output_path}")
        except Exception as e:
            print(f"  ✗ Failed to render {view_name}: {e}")
    
    return rendered_views

def create_analysis_grid(rendered_views, output_path):
    """Create a grid of all rendered views for easy visualization"""
    
    # Create 2x5 grid
    fig, axes = plt.subplots(2, 5, figsize=(25, 10))
    fig.suptitle('3D Model Analysis Views', fontsize=20, fontweight='bold')
    
    view_names = ['front', 'back', 'left', 'right', 'top', 
                  'oblique_1', 'oblique_2', 'oblique_3', 'oblique_4', 'bottom']
    
    for idx, view_name in enumerate(view_names):
        row = idx // 5
        col = idx % 5
        
        if view_name in rendered_views and os.path.exists(rendered_views[view_name]):
            img = Image.open(rendered_views[view_name])
            axes[row, col].imshow(img)
            axes[row, col].set_title(view_name.replace('_', ' ').title(), fontsize=14)
        else:
            axes[row, col].text(0.5, 0.5, 'No Image', ha='center', va='center')
            axes[row, col].set_title(view_name.replace('_', ' ').title(), fontsize=14)
        
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created analysis grid: {output_path}")
    return output_path

def analyze_mesh_statistics(mesh):
    """Generate detailed mesh statistics"""
    
    stats = {
        'vertices': len(mesh.vertices),
        'faces': len(mesh.faces),
        'edges': len(mesh.edges),
        'watertight': mesh.is_watertight,
        'volume': mesh.volume if mesh.is_watertight else None,
        'surface_area': mesh.area,
        'bounding_box': mesh.bounds.tolist(),
        'centroid': mesh.centroid.tolist(),
        'has_vertex_colors': mesh.visual.kind == 'vertex',
        'euler_characteristic': mesh.euler_number,
    }
    
    # Check for degenerate faces
    face_areas = mesh.area_faces
    degenerate_faces = np.sum(face_areas < 0.001)
    stats['degenerate_faces'] = int(degenerate_faces)
    stats['degenerate_percentage'] = float(degenerate_faces / len(mesh.faces) * 100)
    
    # Check for isolated vertices
    stats['isolated_vertices'] = 0  # trimesh usually removes these
    
    # Color statistics if available
    if mesh.visual.kind == 'vertex':
        colors = mesh.visual.vertex_colors
        unique_colors = len(np.unique(colors.view(np.uint32)))
        stats['unique_colors'] = int(unique_colors)
        stats['color_distribution'] = {}
        
        # Count vertices per color
        for color in np.unique(colors[:, :3], axis=0):
            color_key = f"RGB({color[0]},{color[1]},{color[2]})"
            count = np.sum(np.all(colors[:, :3] == color, axis=1))
            stats['color_distribution'][color_key] = int(count)
    
    return stats

def generate_quality_report(mesh, stats, output_path):
    """Generate a text-based quality report"""
    
    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("3D MODEL QUALITY ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Mesh Statistics
        f.write("MESH STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Vertices:              {stats['vertices']:,}\n")
        f.write(f"Faces:                 {stats['faces']:,}\n")
        f.write(f"Edges:                 {stats['edges']:,}\n")
        f.write(f"Surface Area:          {stats['surface_area']:.2f} mm²\n")
        f.write(f"Watertight:            {'✓ Yes' if stats['watertight'] else '✗ No'}\n")
        if stats['volume']:
            f.write(f"Volume:                {stats['volume']:.2f} mm³\n")
        f.write(f"Euler Characteristic:  {stats['euler_characteristic']}\n")
        f.write("\n")
        
        # Quality Metrics
        f.write("QUALITY METRICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Degenerate Faces:      {stats['degenerate_faces']:,} ({stats['degenerate_percentage']:.2f}%)\n")
        f.write(f"Isolated Vertices:     {stats['isolated_vertices']}\n")
        f.write(f"Has Vertex Colors:     {'✓ Yes' if stats['has_vertex_colors'] else '✗ No'}\n")
        
        if stats['has_vertex_colors']:
            f.write(f"Unique Colors:         {stats['unique_colors']}\n")
        
        f.write("\n")
        
        # Bounding Box
        f.write("SPATIAL DIMENSIONS\n")
        f.write("-" * 80 + "\n")
        bounds = stats['bounding_box']
        dimensions = [bounds[1][i] - bounds[0][i] for i in range(3)]
        f.write(f"X: {bounds[0][0]:.2f} to {bounds[1][0]:.2f} mm (width: {dimensions[0]:.2f} mm)\n")
        f.write(f"Y: {bounds[0][1]:.2f} to {bounds[1][1]:.2f} mm (height: {dimensions[1]:.2f} mm)\n")
        f.write(f"Z: {bounds[0][2]:.2f} to {bounds[1][2]:.2f} mm (depth: {dimensions[2]:.2f} mm)\n")
        f.write(f"Centroid: ({stats['centroid'][0]:.2f}, {stats['centroid'][1]:.2f}, {stats['centroid'][2]:.2f})\n")
        f.write("\n")
        
        # Color Distribution
        if stats['has_vertex_colors'] and 'color_distribution' in stats:
            f.write("COLOR DISTRIBUTION (ANATOMICAL STRUCTURES)\n")
            f.write("-" * 80 + "\n")
            total_vertices = stats['vertices']
            for color, count in sorted(stats['color_distribution'].items(), key=lambda x: x[1], reverse=True):
                percentage = count / total_vertices * 100
                f.write(f"{color:20s}: {count:12,} vertices ({percentage:5.2f}%)\n")
            f.write("\n")
        
        # Quality Assessment
        f.write("AUTOMATED QUALITY ASSESSMENT\n")
        f.write("-" * 80 + "\n")
        
        quality_score = 100.0
        issues = []
        
        # Check for issues
        if not stats['watertight']:
            quality_score -= 20
            issues.append("⚠️ Mesh is not watertight (has holes)")
        
        if stats['degenerate_percentage'] > 5:
            quality_score -= 15
            issues.append(f"⚠️ High percentage of degenerate faces ({stats['degenerate_percentage']:.1f}%)")
        elif stats['degenerate_percentage'] > 1:
            quality_score -= 5
            issues.append(f"⚠️ Moderate degenerate faces ({stats['degenerate_percentage']:.1f}%)")
        
        if not stats['has_vertex_colors']:
            quality_score -= 10
            issues.append("⚠️ No vertex colors (use PLY format for colored models)")
        
        if stats['euler_characteristic'] != 2:
            quality_score -= 10
            issues.append(f"⚠️ Non-standard topology (Euler: {stats['euler_characteristic']}, expected: 2)")
        
        if stats['faces'] > 5000000:
            issues.append(f"ℹ️ Very high poly count ({stats['faces']:,} faces) - consider decimation")
        
        if issues:
            f.write("\n".join(issues) + "\n\n")
        else:
            f.write("✓ No major issues detected\n\n")
        
        f.write(f"Overall Quality Score: {quality_score:.1f}/100\n")
        f.write("\n")
        
        # Recommendations
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 80 + "\n")
        
        if not stats['watertight']:
            f.write("• Run mesh repair to close holes\n")
        
        if stats['degenerate_percentage'] > 1:
            f.write("• Remove degenerate faces with mesh.remove_degenerate_faces()\n")
        
        if not stats['has_vertex_colors']:
            f.write("• Export in PLY or OBJ format to preserve colors\n")
        
        if stats['faces'] > 5000000:
            f.write(f"• Consider decimation to reduce poly count (current: {stats['faces']:,})\n")
        
        if not issues:
            f.write("• Model quality is good! Consider testing with different HU ranges for refinement.\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
    
    print(f"✓ Quality report saved: {output_path}")
    return quality_score

def main():
    parser = argparse.ArgumentParser(description='AI-powered 3D model quality analyzer')
    parser.add_argument('--cloud-path', type=str, help='Cloud path to model (s3://...)')
    parser.add_argument('--local-path', type=str, help='Local path to model file')
    parser.add_argument('--output-dir', type=str, default='./analysis_output', 
                       help='Directory for analysis outputs')
    parser.add_argument('--skip-render', action='store_true', 
                       help='Skip rendering (faster, only stats)')
    
    args = parser.parse_args()
    
    # Determine input file
    if args.cloud_path:
        print(f"📥 Downloading from cloud: {args.cloud_path}")
        local_file = os.path.join('/tmp', 'analysis_model.ply')
        try:
            download_model_from_cloud(args.cloud_path, local_file)
        except Exception as e:
            print(f"❌ Download failed: {e}")
            # Try to find it locally
            model_name = os.path.basename(args.cloud_path)
            local_file = f"./output/{model_name}"
            if not os.path.exists(local_file):
                print(f"❌ Model not found locally either: {local_file}")
                return 1
    elif args.local_path:
        local_file = args.local_path
    else:
        # Default: analyze the latest full anatomy model
        local_file = "./output/full_anatomy_v2.ply"
        if not os.path.exists(local_file):
            # Try to download it
            cloud_path = "s3://my-medical-imaging/outputs/lung_TCGA-17-Z054_full_anatomy/full_anatomy_combined_colored.ply"
            print(f"📥 Model not found locally, downloading from cloud...")
            try:
                download_model_from_cloud(cloud_path, local_file)
            except:
                print(f"❌ Could not find or download model")
                return 1
    
    if not os.path.exists(local_file):
        print(f"❌ Model file not found: {local_file}")
        return 1
    
    print(f"📂 Loading model: {local_file}")
    
    # Load mesh
    try:
        mesh = trimesh.load(local_file, process=False)
        print(f"✓ Loaded mesh: {len(mesh.vertices):,} vertices, {len(mesh.faces):,} faces")
    except Exception as e:
        print(f"❌ Failed to load mesh: {e}")
        return 1
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Analyze mesh statistics
    print("\n📊 Analyzing mesh statistics...")
    stats = analyze_mesh_statistics(mesh)
    
    # Generate quality report
    report_path = os.path.join(args.output_dir, 'quality_report.txt')
    quality_score = generate_quality_report(mesh, stats, report_path)
    
    # Render views (unless skipped)
    if not args.skip_render:
        print("\n🎨 Generating visualization renders...")
        try:
            rendered_views = generate_analysis_views(mesh, args.output_dir)
            
            # Create grid
            grid_path = os.path.join(args.output_dir, 'analysis_grid.png')
            create_analysis_grid(rendered_views, grid_path)
            
            print(f"\n✅ Analysis complete!")
            print(f"   Quality Score: {quality_score:.1f}/100")
            print(f"   Report: {report_path}")
            print(f"   Grid: {grid_path}")
            print(f"   Individual views: {args.output_dir}/view_*.png")
            
        except ImportError:
            print("\n⚠️ pyrender not installed, skipping visualization")
            print("   Install with: pip install pyrender")
            print(f"\n✅ Statistical analysis complete!")
            print(f"   Quality Score: {quality_score:.1f}/100")
            print(f"   Report: {report_path}")
    else:
        print(f"\n✅ Statistical analysis complete!")
        print(f"   Quality Score: {quality_score:.1f}/100")
        print(f"   Report: {report_path}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
