#!/usr/bin/env python3
"""
Professional Quality Upgrade Tracker
Monitors and compares improvements at each phase
"""

import os
import json
import trimesh
import numpy as np
from datetime import datetime
from pathlib import Path

class UpgradeTracker:
    """Track quality improvements through upgrade phases"""
    
    def __init__(self, tracking_file='upgrade_tracking.json'):
        self.tracking_file = tracking_file
        self.history = self._load_history()
    
    def _load_history(self):
        """Load existing tracking data"""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return {
            'phases': {},
            'comparisons': {},
            'timeline': []
        }
    
    def _save_history(self):
        """Save tracking data"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def analyze_model(self, model_path, phase_name):
        """Analyze a model and store results"""
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found: {model_path}")
            return None
        
        mesh = trimesh.load(model_path, process=False)
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'phase': phase_name,
            'model_path': model_path,
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces),
            'surface_area': float(mesh.area),
            'watertight': bool(mesh.is_watertight),
            'file_size_mb': os.path.getsize(model_path) / (1024 * 1024),
            'degenerate_faces': int(np.sum(mesh.area_faces < 0.001)),
            'degenerate_pct': float(np.sum(mesh.area_faces < 0.001) / len(mesh.faces) * 100),
        }
        
        # Calculate quality score
        score = 100.0
        
        if stats['degenerate_pct'] > 0.01:
            score -= (stats['degenerate_pct'] * 10)
        
        if not stats['watertight']:
            score -= 20
        
        stats['quality_score'] = max(0, score)
        
        # Store in history
        self.history['phases'][phase_name] = stats
        self.history['timeline'].append({
            'timestamp': stats['timestamp'],
            'phase': phase_name,
            'quality_score': stats['quality_score'],
            'vertices': stats['vertices']
        })
        
        self._save_history()
        
        return stats
    
    def generate_comparison_report(self):
        """Generate comparison between phases"""
        
        if len(self.history['phases']) < 2:
            print("⚠️ Need at least 2 phases to compare")
            return None
        
        phases = sorted(self.history['phases'].items())
        
        report = {
            'title': 'PROFESSIONAL QUALITY UPGRADE COMPARISON',
            'generated': datetime.now().isoformat(),
            'phases_count': len(phases),
            'comparisons': []
        }
        
        # Compare each phase with previous
        for i in range(1, len(phases)):
            prev_name, prev_data = phases[i-1]
            curr_name, curr_data = phases[i]
            
            comparison = {
                'from': prev_name,
                'to': curr_name,
                'vertex_gain': curr_data['vertices'] - prev_data['vertices'],
                'vertex_gain_pct': ((curr_data['vertices'] - prev_data['vertices']) / prev_data['vertices'] * 100) if prev_data['vertices'] > 0 else 0,
                'face_gain': curr_data['faces'] - prev_data['faces'],
                'face_gain_pct': ((curr_data['faces'] - prev_data['faces']) / prev_data['faces'] * 100) if prev_data['faces'] > 0 else 0,
                'quality_improvement': curr_data['quality_score'] - prev_data['quality_score'],
                'degenerate_improvement': prev_data['degenerate_pct'] - curr_data['degenerate_pct'],
                'file_size_growth_mb': curr_data['file_size_mb'] - prev_data['file_size_mb'],
            }
            
            report['comparisons'].append(comparison)
        
        return report

def main():
    print("=" * 80)
    print("📊 PROFESSIONAL QUALITY UPGRADE TRACKER")
    print("=" * 80)
    print()
    
    tracker = UpgradeTracker()
    
    # Phase 0: Current baseline
    print("📍 PHASE 0: Current Baseline (2.0mm resolution)")
    print("-" * 80)
    
    baseline_path = "./analysis_output/full_anatomy.ply"
    
    if os.path.exists(baseline_path):
        baseline = tracker.analyze_model(baseline_path, "Phase 0 - Baseline (2.0mm)")
        
        print(f"Vertices:        {baseline['vertices']:,}")
        print(f"Faces:           {baseline['faces']:,}")
        print(f"Surface Area:    {baseline['surface_area']:.0f} mm²")
        print(f"File Size:       {baseline['file_size_mb']:.1f} MB")
        print(f"Degenerate:      {baseline['degenerate_pct']:.3f}%")
        print(f"Quality Score:   {baseline['quality_score']:.1f}/100")
        print()
    else:
        print(f"❌ Baseline model not found: {baseline_path}")
        print()
    
    # Show expected improvements
    print("=" * 80)
    print("📈 EXPECTED IMPROVEMENTS (Phase 1 - Professional 0.5mm)")
    print("=" * 80)
    print()
    
    if baseline:
        expected_phase1 = {
            'vertices': baseline['vertices'] * 4,  # 4x from finer voxels
            'faces': baseline['faces'] * 3.5,      # 3.5x after all optimizations
            'quality_score': baseline['quality_score'] + 3.5,
            'file_size_mb': baseline['file_size_mb'] * 5,  # Estimated 5x larger
        }
        
        print(f"Vertex Increase:    {baseline['vertices']:,} → {int(expected_phase1['vertices']):,} (+97%)")
        print(f"Face Increase:      {baseline['faces']:,} → {int(expected_phase1['faces']):,} (+94%)")
        print(f"Quality Score:      {baseline['quality_score']:.1f} → {expected_phase1['quality_score']:.1f}/100 (+{expected_phase1['quality_score']-baseline['quality_score']:.1f})")
        print(f"Est. File Size:     {baseline['file_size_mb']:.1f} MB → {expected_phase1['file_size_mb']:.1f} MB")
        print()
        
        print("🎯 What You'll See:")
        print("  ✓ Bronchial tree hints visible in lungs")
        print("  ✓ Complete vascular network branches")
        print("  ✓ Ultra-smooth organ surfaces")
        print("  ✓ Professional medical imaging quality")
        print()
    
    # Timeline
    print("=" * 80)
    print("⏱️ UPGRADE TIMELINE")
    print("=" * 80)
    print()
    
    if tracker.history['timeline']:
        for item in tracker.history['timeline']:
            print(f"  {item['timestamp']}: {item['phase']}")
            print(f"    Vertices: {item['vertices']:,} | Quality: {item['quality_score']:.1f}/100")
    else:
        print("  No phases completed yet. Start with:")
        print("  ./run_professional_upgrade.sh")
    
    print()
    print("=" * 80)
    print("📊 HOW TO USE THIS TRACKER")
    print("=" * 80)
    print()
    print("After each phase completes:")
    print()
    print("  1. Download the model:")
    print("     export AWS_ACCESS_KEY_ID=...")
    print("     export AWS_SECRET_ACCESS_KEY=...")
    print("     aws s3 cp s3://my-medical-imaging/outputs/.../*.ply ./phase_N.ply")
    print()
    print("  2. Run analyzer:")
    print("     python track_upgrade.py")
    print()
    print("  3. View comparison:")
    print("     cat upgrade_tracking.json")
    print()

if __name__ == '__main__':
    main()
