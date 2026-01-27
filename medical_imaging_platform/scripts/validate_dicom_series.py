#!/usr/bin/env python3
import os
import sys
import argparse
from typing import List, Tuple

import pydicom
import numpy as np

REQUIRED_MIN_SLICES = 50  # pragmatic minimum for usable 3D


def read_dicom(path: str):
    try:
        return pydicom.dcmread(path, stop_before_pixels=False)
    except Exception as e:
        return None


def get_slice_position(dcm) -> float:
    ipp = getattr(dcm, 'ImagePositionPatient', None)
    if ipp is not None and len(ipp) == 3:
        return float(ipp[2])
    # Fallback: InstanceNumber (not ideal but better than nothing)
    return float(getattr(dcm, 'InstanceNumber', 0))


def summarize_series(files: List[str]) -> Tuple[dict, List[str]]:
    issues = []
    summary = {
        'file_count': len(files),
        'modalities': set(),
        'bits_allocated': set(),
        'bits_stored': set(),
        'pixel_representation': set(),
        'slope_present': False,
        'intercept_present': False,
        'pixel_spacing_present': False,
        'slice_thickness_present': False,
        'rows_cols': set(),
        'slice_positions': [],
        'series_descriptions': set(),
        'image_types': set(),
        'hu_sample_stats': None,
    }

    if len(files) == 0:
        issues.append('No DICOM files found in directory.')
        return summary, issues

    # Read a small sample for header consistency
    sample_indices = [0, min(5, len(files)-1), len(files)//2, len(files)-1]
    sample_indices = sorted(set(sample_indices))
    dcms = []
    for idx in sample_indices:
        dcm = read_dicom(files[idx])
        if dcm is None:
            issues.append(f'Failed to read DICOM file: {os.path.basename(files[idx])}')
            continue
        dcms.append(dcm)

    if not dcms:
        issues.append('Failed to read any DICOM files.')
        return summary, issues

    # Series-level checks
    for dcm in dcms:
        summary['modalities'].add(getattr(dcm, 'Modality', 'N/A'))
        summary['bits_allocated'].add(getattr(dcm, 'BitsAllocated', 'N/A'))
        summary['bits_stored'].add(getattr(dcm, 'BitsStored', 'N/A'))
        summary['pixel_representation'].add(getattr(dcm, 'PixelRepresentation', 'N/A'))
        summary['series_descriptions'].add(getattr(dcm, 'SeriesDescription', 'N/A'))
        it = getattr(dcm, 'ImageType', None)
        if it is not None:
            try:
                summary['image_types'].add('|'.join(list(it)))
            except Exception:
                summary['image_types'].add(str(it))
        summary['rows_cols'].add((getattr(dcm, 'Rows', 'N/A'), getattr(dcm, 'Columns', 'N/A')))
        if hasattr(dcm, 'RescaleSlope'):
            summary['slope_present'] = True
        if hasattr(dcm, 'RescaleIntercept'):
            summary['intercept_present'] = True
        if hasattr(dcm, 'PixelSpacing'):
            summary['pixel_spacing_present'] = True
        if hasattr(dcm, 'SliceThickness'):
            summary['slice_thickness_present'] = True

    # Modality check
    if summary['modalities'] != {'CT'}:
        issues.append(f"Modality mismatch: expected 'CT', found {summary['modalities']}")

    # Bit depth check
    if not any((b is not None and isinstance(b, int) and b >= 12) for b in summary['bits_stored']):
        issues.append(f"Low bit depth: BitsStored values {summary['bits_stored']} (expected >= 12 for CT)")

    # Spacing presence
    if not summary['pixel_spacing_present']:
        issues.append('Missing PixelSpacing tag (required for physical spacing).')
    if not summary['slice_thickness_present']:
        issues.append('Missing SliceThickness tag (needed for Z spacing).')

    # Slice positions and spacing consistency
    # Read all files quickly for positions
    positions = []
    for f in files:
        dcm = read_dicom(f)
        if dcm is None:
            continue
        positions.append(get_slice_position(dcm))
    if positions:
        summary['slice_positions'] = positions
        unique_positions = sorted(set(positions))
        if len(unique_positions) < REQUIRED_MIN_SLICES:
            issues.append(f'Insufficient slices: {len(unique_positions)} (min recommended {REQUIRED_MIN_SLICES}).')
        # Check near-uniform spacing if we have > 2 slices
        if len(unique_positions) > 2:
            diffs = np.diff(sorted(unique_positions))
            if np.std(diffs) > 1e-2:  # 0.01 mm tolerance
                issues.append(f'Non-uniform slice spacing detected (std={np.std(diffs):.4f}).')
    else:
        issues.append('Could not determine slice positions; missing ImagePositionPatient or InstanceNumber.')

    # HU sample check from first readable sample
    first = dcms[0]
    try:
        slope = float(getattr(first, 'RescaleSlope', 1))
        intercept = float(getattr(first, 'RescaleIntercept', 0))
        arr = first.pixel_array.astype(np.float32)
        hu = arr * slope + intercept
        summary['hu_sample_stats'] = {
            'min': float(hu.min()), 'max': float(hu.max()), 'mean': float(hu.mean()),
            'p5': float(np.percentile(hu, 5)), 'p95': float(np.percentile(hu, 95)),
        }
        # Sanity check: HU should include air near -1000 and soft tissue around [-100, 100]
        if summary['hu_sample_stats']['min'] > -900:
            issues.append(f"HU min unusually high ({summary['hu_sample_stats']['min']:.1f}); data may not be in HU.")
        if summary['hu_sample_stats']['max'] < 200:
            issues.append(f"HU max unusually low ({summary['hu_sample_stats']['max']:.1f}); data may not be in HU.")
    except Exception:
        issues.append('Failed HU conversion; missing/invalid RescaleSlope/Intercept or pixel data.')

    return summary, issues


def print_summary(path: str, summary: dict, issues: List[str]) -> None:
    print(f"Series path: {path}")
    print(f"DICOM files: {summary['file_count']}")
    print(f"Modalities: {', '.join(summary['modalities']) or 'N/A'}")
    print(f"BitsAllocated: {', '.join(map(str, summary['bits_allocated'])) or 'N/A'}")
    print(f"BitsStored: {', '.join(map(str, summary['bits_stored'])) or 'N/A'}")
    print(f"PixelRepresentation: {', '.join(map(str, summary['pixel_representation'])) or 'N/A'}")
    print(f"SeriesDescription(s): {', '.join(summary['series_descriptions']) or 'N/A'}")
    print(f"ImageType(s): {', '.join(summary['image_types']) or 'N/A'}")
    print(f"Rows x Cols: {', '.join([f"{r}x{c}" for r,c in summary['rows_cols']]) or 'N/A'}")
    print(f"RescaleSlope present: {summary['slope_present']}")
    print(f"RescaleIntercept present: {summary['intercept_present']}")
    print(f"PixelSpacing present: {summary['pixel_spacing_present']}")
    print(f"SliceThickness present: {summary['slice_thickness_present']}")
    if summary['hu_sample_stats']:
        s = summary['hu_sample_stats']
        print(f"HU sample stats: min={s['min']:.1f}, max={s['max']:.1f}, mean={s['mean']:.1f}, p5={s['p5']:.1f}, p95={s['p95']:.1f}")
    if summary['slice_positions']:
        print(f"Unique slice positions: {len(set(summary['slice_positions']))}")
    print()

    if issues:
        print('FAIL: Series is not suitable for 3D CT segmentation.')
        for i in issues:
            print(f"- {i}")
    else:
        print('PASS: Series looks suitable for 3D CT segmentation.')


def main():
    parser = argparse.ArgumentParser(description='Validate a DICOM series for 3D CT segmentation readiness.')
    parser.add_argument('series_dir', help='Path to directory containing a single DICOM series')
    args = parser.parse_args()

    if not os.path.isdir(args.series_dir):
        print(f"Provided path is not a directory: {args.series_dir}")
        sys.exit(1)

    files = [os.path.join(args.series_dir, f) for f in os.listdir(args.series_dir) if f.lower().endswith('.dcm')]
    files.sort()

    summary, issues = summarize_series(files)
    print_summary(args.series_dir, summary, issues)

    # Exit code: 0 on pass, 2 on fail
    sys.exit(0 if not issues else 2)


if __name__ == '__main__':
    main()
