# Data Collection & Annotation Workflow

**Phase**: 2B (Weeks 2-8)  
**Purpose**: Systematic guide for collecting, annotating, and managing medical imaging data  
**Status**: Ready to implement

---

## 📋 Overview

This workflow guides you through:
1. **Downloading** free medical imaging datasets
2. **Collecting** custom institutional data
3. **Annotating** unlabeled scans
4. **Quality assurance** of annotations
5. **Organizing** for Phase 2C fine-tuning

---

## 📥 Part 1: Download Free Datasets (Week 1-2)

### Step 1.1: Create Dataset Directory

```bash
cd /workspaces/Dicom-to-3D-/data/datasets
mkdir -p medical_segmentation_decathlon lits_liver kits_kidney chaos_multimodal synapse_validation custom_institutional/{unlabeled,annotated}

# Create tracking file
cat > dataset_inventory.csv << 'EOF'
dataset_name,organ,total_scans,labeled_scans,format,size_gb,download_date,source_url,notes
EOF
```

### Step 1.2: Medical Segmentation Decathlon (Priority 1 - START HERE)

**Time**: 1 hour  
**Storage**: 50 GB  
**Organs Covered**: 10 (including all 7 of ours)

```bash
cd /workspaces/Dicom-to-3D-/data/datasets/medical_segmentation_decathlon

# Download all 10 tasks
for TASK in 01 02 03 04 05 06 07 08 09 10; do
    echo "Downloading Task $TASK..."
    wget -q https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Brain.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Heart.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Liver.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Hippocampus.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Pancreas.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Prostate.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Lungs.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Spleen.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Colon.tar \
         https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${TASK}_Kidney.tar 2>/dev/null
         
    for f in Task${TASK}*.tar; do
        if [ -f "$f" ]; then
            tar -xf "$f" && rm "$f"
        fi
    done
done

# Verify download
echo "Downloaded tasks:"
ls -d Task* | wc -l
# Expected: 10 tasks
```

**What You Get**:
```
Task01_Brain/
├── imagesTr/          (484 training CT scans)
├── labelsTr/          (484 segmentation masks)
└── imagesTs/          (100 test scans, no labels)

Task03_Liver/
├── imagesTr/          (131 scans)
├── labelsTr/          (131 masks)
└── ...

... (10 tasks total)
```

**Next**: Update inventory file
```bash
cat >> dataset_inventory.csv << 'EOF'
Medical Segmentation Decathlon,Multi,1000,1000,NIfTI,50,$(date +%Y-%m-%d),http://medicaldecathlon.com/,"All 10 tasks, expert annotated"
EOF
```

### Step 1.3: LiTS - Liver Tumor (Priority 2)

**Time**: 30 min  
**Storage**: 30 GB  
**Organs**: Liver + tumor

```bash
cd /workspaces/Dicom-to-3D-/data/datasets/lits_liver

# Register & download from https://www.lits-challenge.com/data
# Then extract:
unzip -q LiTS.zip
cd LiTS

# Verify structure
ls training/ | head
# Expected: volume-0.nii, segmentation-0.nii, etc. (200 pairs)

# Update inventory
cd ../..
cat >> dataset_inventory.csv << 'EOF'
LiTS,Liver,201,201,NIfTI,30,$(date +%Y-%m-%d),https://www.lits-challenge.com/,"Expert annotated, includes tumors"
EOF
```

### Step 1.4: KITS - Kidney Tumor (Priority 3)

**Time**: 2 hours  
**Storage**: 50 GB  
**Organs**: Kidney + tumor

```bash
cd /workspaces/Dicom-to-3D-/data/datasets/kits_kidney

# Download from https://kits-challenge.org/ (manual link)
unzip -q kits21_release.zip

# Verify structure
ls data/ | head -5
# Expected: case_00000/, case_00001/, etc. (300 cases)

# Update inventory
cd ../..
cat >> dataset_inventory.csv << 'EOF'
KITS,Kidney,300,300,DICOM,50,$(date +%Y-%m-%d),https://kits-challenge.org/,"Expert annotated, includes pathology"
EOF
```

### Step 1.5: Additional Datasets (Optional)

**CHAOS** (Multi-organ):
```bash
cd /workspaces/Dicom-to-3D-/data/datasets/chaos_multimodal
# Download from https://chaos.grand-challenge.org/
# Extract: Train_Sets/CT/ (60 CT scans + masks)
```

**Synapse** (High-quality validation set):
```bash
cd /workspaces/Dicom-to-3D-/data/datasets/synapse_validation
# Download from https://www.synapse.org/#!Synapse:syn3193805
# 30 high-quality multi-organ scans (perfect for validation)
```

---

## 🏷️ Part 2: Collect Custom Institutional Data (Week 3-4)

### Step 2.1: Identify & Gather Scans

```bash
# Create folder structure
mkdir -p /workspaces/Dicom-to-3D-/data/datasets/custom_institutional/{raw_dicom,converted_nifti,annotated}

# Collect your unlabeled scans:
# 1. Get access to your institution's PACS (Picture Archive System)
# 2. Export DICOM files for desired cases
# 3. Place in raw_dicom/

# Example structure:
data/datasets/custom_institutional/raw_dicom/
├── case_001/
│   ├── image.dcm
│   ├── image_001.dcm
│   └── ...
├── case_002/
│   └── ...
└── case_100/
```

### Step 2.2: Get Ethics Approval (CRITICAL)

**Required for using patient data**:

```
☐ IRB/Ethics Committee Approval
  - HIPAA compliance review
  - Patient consent forms
  - De-identification protocol
  
☐ De-identification
  - Remove patient names, MRN, DoB
  - Anonymize in DICOM headers
  - Can use dcmtk tool:
    dcmodify -e --no-backup -m PatientName="ANON" *.dcm
    
☐ Data Security
  - Encrypted storage
  - Access logs
  - Secure backup
```

**Timeline**: 2-4 weeks (start this BEFORE collection!)

### Step 2.3: Convert DICOM to NIfTI (Optional)

```bash
# Install converter
pip install dcm2niix

# Convert each case
for case_dir in raw_dicom/case_*; do
    case_name=$(basename $case_dir)
    dcm2niix -o converted_nifti/ -f $case_name "$case_dir"
done

# Result:
# converted_nifti/case_001.nii.gz
# converted_nifti/case_001.json  (metadata)
```

---

## ✏️ Part 3: Annotation Workflow (Week 4-8)

### Step 3.1: Setup Annotation Tool

**Option 1: 3D Slicer (Recommended - Professional)**

```bash
# Download & install from https://download.slicer.org/
# ~600 MB download

# Training: https://www.slicer.org/wiki/Documentation
# Features:
#   ✓ 3D visualization
#   ✓ Brush, Threshold, Draw tools
#   ✓ Multi-label support
#   ✓ Keyboard shortcuts
#   ✓ Label statistics
```

**Option 2: ITK-SNAP (Lightweight - Fast)**

```bash
# Download from http://www.itksnap.org/
# ~100 MB download

# Good for:
#   ✓ Quick segmentations
#   ✓ Polygon/snake tools
#   ✓ Low resource usage
```

**Option 3: Napari (Python - Scriptable)**

```bash
pip install napari napari-3d-popup

# Use for:
#   ✓ Automated + manual annotation
#   ✓ Custom plugins
#   ✓ Batch processing
```

### Step 3.2: Annotation Guidelines

Create standardized guidelines for consistency:

```yaml
# annotation_guidelines.yaml
brain:
  brain_tissue:
    description: "Gray and white matter within the skull"
    hu_range: [0, 150]
    color_rgb: [139, 69, 19]
    how_to_draw: |
      1. Use threshold tool (HU 0-150)
      2. Exclude ventricular CSF
      3. Exclude skull and meninges
      4. Fill any internal holes
    quality_checks:
      - "Volume > 500 mL"
      - "Smooth surface (no fragmentation)"
      - "Symmetrical hemispheres"
      
  skull:
    description: "Cranial bone and scalp"
    hu_range: [120, 3000]
    color_rgb: [211, 211, 211]
    how_to_draw: |
      1. Use threshold tool (HU 120+)
      2. Include calvarium and base
      3. Include scalp soft tissue
      4. Check for artifact metal removal
    quality_checks:
      - "Continuous bone structure"
      - "No internal brain voxels included"
```

### Step 3.3: Annotation Process (Per Scan)

**Time per scan**: 30-60 minutes for expert, 2-3 hours for novice

```
WORKFLOW:
1. Open image in 3D Slicer/ITK-SNAP (5 min)
2. Threshold by HU range (5 min)
3. Manual refinement (20-30 min)
   ├─ Add missing voxels
   ├─ Remove false positives
   └─ Smooth boundaries
4. Export segmentation (2 min)
5. QA check (5-10 min)
```

**3D Slicer Quick Start**:

```
1. File → Add Volume → Select .nii.gz or DICOM
2. Segmentations → Create new segmentation
3. Editor → Threshold (set HU min/max from guidelines)
4. Refine with Brush, Eraser, Islands tools
5. File → Export Segmentation → NIfTI
```

### Step 3.4: QA/Quality Assurance (Critical)

```python
# qa_checker.py - Validate annotations

import nibabel as nib
import numpy as np

def check_annotation(image_path, seg_path, organ_name, guidelines):
    """Check if annotation meets quality criteria"""
    
    img = nib.load(image_path)
    seg = nib.load(seg_path)
    
    volume = np.array(img.dataobj)
    mask = np.array(seg.dataobj)
    
    # Checks
    checks = {}
    
    # 1. Min voxel count
    voxel_count = np.sum(mask)
    expected_min = guidelines[organ_name]['min_voxels']
    checks['voxel_count'] = voxel_count >= expected_min
    
    # 2. Connectivity (single component)
    from scipy import ndimage
    labeled, num_components = ndimage.label(mask)
    checks['connectivity'] = num_components == 1
    
    # 3. Surface smoothness (connected components at boundary)
    surface = mask - ndimage.binary_erosion(mask)
    surface_count = np.sum(surface)
    checks['smoothness'] = surface_count / voxel_count < 0.15  # <15% surface
    
    # 4. HU range check
    organ_hu = volume[mask > 0]
    hu_min = guidelines[organ_name]['hu_min']
    hu_max = guidelines[organ_name]['hu_max']
    checks['hu_range'] = np.sum((organ_hu >= hu_min) & (organ_hu <= hu_max)) / len(organ_hu) > 0.9
    
    return checks

# Run QA
for case in glob.glob('annotated/case_*_seg.nii.gz'):
    img_path = case.replace('_seg.nii.gz', '.nii.gz')
    result = check_annotation(img_path, case, 'brain', guidelines)
    if not all(result.values()):
        print(f"❌ {case}: {result}")
    else:
        print(f"✅ {case}")
```

**QA Threshold**: Pass if ≥90% of checks pass

### Step 3.5: Second Rater Validation (Recommended)

```bash
# Have 2nd expert annotate ~20% of scans independently
# Then compare using Dice coefficient

def dice_score(seg1, seg2):
    """Compute Dice overlap between two segmentations"""
    intersection = np.sum(seg1 * seg2)
    return 2.0 * intersection / (np.sum(seg1) + np.sum(seg2))

# Expected: Dice > 0.90 (>90% overlap)
```

---

## 🗂️ Part 4: Organize for Training (Week 8)

### Step 4.1: Create Training/Validation/Test Split

```python
# prepare_training_data.py

import os
import shutil
import random
import nibabel as nib
from sklearn.model_selection import train_test_split

# Gather all annotated data
all_images = []
all_labels = []

for dataset in ['medical_decathlon', 'lits', 'kits', 'custom_annotated']:
    images = glob.glob(f'{dataset}/imagesTr/*.nii.gz')
    labels = glob.glob(f'{dataset}/labelsTr/*.nii.gz')
    all_images.extend(images)
    all_labels.extend(labels)

# Split: 80% train, 10% val, 10% test
train_i, test_i = train_test_split(range(len(all_images)), test_size=0.1, random_state=42)
train_i, val_i = train_test_split(train_i, test_size=0.1/(0.9), random_state=42)

# Create split folders for nnU-Net format
nnunet_dir = '/workspaces/Dicom-to-3D-/nnUNet_raw/Dataset100_YourOrgan'
os.makedirs(f'{nnunet_dir}/imagesTr', exist_ok=True)
os.makedirs(f'{nnunet_dir}/labelsTr', exist_ok=True)
os.makedirs(f'{nnunet_dir}/imagesVal', exist_ok=True)
os.makedirs(f'{nnunet_dir}/labelsVal', exist_ok=True)
os.makedirs(f'{nnunet_dir}/imagesTs', exist_ok=True)

# Copy files
for idx in train_i:
    shutil.copy(all_images[idx], f'{nnunet_dir}/imagesTr/{idx:03d}_0000.nii.gz')
    shutil.copy(all_labels[idx], f'{nnunet_dir}/labelsTr/{idx:03d}.nii.gz')

for idx in val_i:
    shutil.copy(all_images[idx], f'{nnunet_dir}/imagesVal/{idx:03d}_0000.nii.gz')
    shutil.copy(all_labels[idx], f'{nnunet_dir}/labelsVal/{idx:03d}.nii.gz')

for idx in test_i:
    shutil.copy(all_images[idx], f'{nnunet_dir}/imagesTs/{idx:03d}_0000.nii.gz')

print(f"Train: {len(train_i)}, Val: {len(val_i)}, Test: {len(test_i)}")
```

### Step 4.2: Create Dataset Metadata (nnU-Net Format)

```python
# Create dataset.json for nnU-Net
import json

dataset_json = {
    "channel_names": {
        "0": "CT"
    },
    "labels": {
        "background": 0,
        "brain": 1,
        "skull": 2
    },
    "numTraining": len(train_i),
    "numValidation": len(val_i),
    "description": "Custom Brain CT Segmentation",
    "reference": "Your Institution",
    "license": "Your License",
    "modality": {
        "0": "CT"
    },
    "tensorImageSize": "3D"
}

with open(f'{nnunet_dir}/dataset.json', 'w') as f:
    json.dump(dataset_json, f, indent=2)
```

### Step 4.3: Version & Backup

```bash
# Create manifest for reproducibility
cat > dataset_manifest.txt << 'EOF'
TRAINING DATA MANIFEST
======================
Date: $(date)
Total scans: $total
  - Training: $train_count
  - Validation: $val_count
  - Test: $test_count

Sources:
  - Medical Decathlon: $count scans
  - LiTS: $count scans
  - KITS: $count scans
  - Custom: $count scans

Quality: All scans passed QA
  - Min voxels: $min_voxels
  - Dice consistency: >0.90
  - HU range check: >90% pass

Backup location: [your backup path]
EOF

# Create backup
tar -czf ~/backups/training_data_$(date +%Y%m%d).tar.gz $nnunet_dir/
```

---

## 📊 Summary Checklist

- [ ] **Week 1-2**: Download Medical Decathlon + LiTS + KITS + Synapse (140 GB)
- [ ] **Week 2-3**: Collect custom institutional scans (100-200 scans)
- [ ] **Week 2**: Get IRB/ethics approval
- [ ] **Week 2-3**: De-identify all custom scans
- [ ] **Week 3**: Setup annotation tool (3D Slicer/ITK-SNAP)
- [ ] **Week 3-4**: Create annotation guidelines
- [ ] **Week 4-7**: Annotate 100-200 custom scans (30-60 min each)
- [ ] **Week 7**: Run QA checks (>90% pass rate)
- [ ] **Week 7**: Get 2nd rater validation (Dice > 0.90)
- [ ] **Week 8**: Organize for nnU-Net training
- [ ] **Week 8**: Create dataset metadata
- [ ] **Week 8**: Backup dataset

**Total Scans Ready for Phase 2C**: 300-500 labeled scans  
**Storage Required**: ~200-300 GB  
**Time Investment**: 200-300 hours  
**Cost**: $0-5K (if hiring annotators: $200-2000/scan × 50-100 scans)

---

## 🎓 Resources

- **3D Slicer Tutorials**: https://www.slicer.org/wiki/Documentation
- **ITK-SNAP Guide**: http://www.itksnap.org/
- **DICOM Standard**: https://www.dicomstandard.org/
- **Medical Imaging Ethics**: https://www.aamc.org/what-we-do/mission-areas/health-professions/privacy-security

---

**Next Step**: See HYBRID_APPROACH.md for Phase 2C (Fine-tuning with nnU-Net)
