"""
main.py
-------
Phase 1 Entry Point - Config-driven organ segmentation
"""

import argparse
import os
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from profiles.config_loader import OrgalProfileLoader
from core.segmentation_engine import SegmentationEngine


def main():
    parser = argparse.ArgumentParser(
        description='Medical Imaging Platform - Organ Segmentation (Phase 1-2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Phase 1 (HU-based, fast)
  python main.py --organ brain --input data/brain_ct --output output/brain
  
  # Phase 2A (TotalSegmentator, better accuracy)
  python main.py --organ brain --input data/brain_ct --output output/brain --model totalSegmentator
  
  # List available profiles
  python main.py --list-profiles
  
MODELS:
  hu_based          - HU thresholding (Phase 1, default, fastest)
  totalSegmentator  - Pre-trained on 20K scans (Phase 2A, better accuracy)
"""
    )
    
    parser.add_argument(
        '--organ',
        type=str,
        help='Organ name (brain, liver, lungs, heart, kidneys, bones, pancreas)'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Input DICOM folder'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Output folder for STL/PLY files (default: output/)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='hu_based',
        choices=['hu_based', 'totalSegmentator', 'monai', 'nnunet'],
        help='Segmentation model to use (default: hu_based)'
    )
    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='List available organ profiles and exit'
    )
    
    args = parser.parse_args()
    
    # List profiles
    if args.list_profiles:
        profiles = OrgalProfileLoader.list_available()
        print("\n" + "="*70)
        print("Available Organ Profiles:")
        print("="*70)
        for profile in profiles:
            config = OrgalProfileLoader.load(profile)
            print(f"\n✓ {profile.upper()}")
            print(f"  Description: {config['description']}")
            print(f"  Tissues: {', '.join(config['tissues'].keys())}")
            print(f"  Modalities: {', '.join(config['modality'])}")
        print("\n")
        return
    
    # Validate inputs
    if not args.organ:
        print("ERROR: --organ required (use --list-profiles to see options)")
        sys.exit(1)
    
    if not args.input or not os.path.exists(args.input):
        print(f"ERROR: Input folder not found: {args.input}")
        sys.exit(1)
    
    # Load profile
    print("\n" + "="*70)
    print(f"ORGAN SEGMENTATION: {args.organ.upper()}")
    print("="*70)
    
    try:
        config = OrgalProfileLoader.load(args.organ)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    print(f"\n✓ Profile: {config['description']}")
    print(f"✓ Tissues: {list(config['tissues'].keys())}")
    print(f"✓ Model: {args.model}")
    
    # Create engine & process
    engine = SegmentationEngine(config, model_type=args.model)
    
    print(f"\nProcessing: {args.input}")
    outputs = engine.process(args.input, args.output)
    
    # Summary
    print("\n" + "="*70)
    print("✅ SEGMENTATION COMPLETE")
    print("="*70)
    for tissue_type, file_path in outputs.items():
        size_mb = os.path.getsize(file_path) / (1024*1024)
        print(f"\n✓ {tissue_type}")
        print(f"  Path: {file_path}")
        print(f"  Size: {size_mb:.1f} MB")
    
    print("\n" + "="*70)
    print("Next: Open .ply files in Blender or .stl in Cura/MeshLab")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
