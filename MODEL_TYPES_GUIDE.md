# 3D Model Output Types - Quick Reference

## 📦 Available Model Types Per DICOM Dataset

For each CT scan, you can now generate **3 different types** of 3D models:

---

### 1️⃣ **Organ-Specific Model**
**Example:** `lungs.yaml`, `liver.yaml`, `brain.yaml`

**What it shows:**
- Single organ segmentation
- Multiple tissue types within that organ
- Example: Lungs → lung_tissue + airways

**Use cases:**
- Medical education (isolated anatomy)
- 3D printing single organs
- Detailed analysis of one organ
- Surgical planning for specific organ

**File size:** 20-600 MB  
**Processing time:** 30-60 seconds

**Example output (lungs):**
```
outputs/lung_TCGA-17-Z054_lungs/
├── lungs_airways.stl               (9.2 MB)
├── lungs_airways_colored.ply       (3.9 MB)
├── lungs_lung_tissue.stl          (35.6 MB)
└── lungs_lung_tissue_colored.ply  (15.0 MB)
```

---

### 2️⃣ **Tissue-Specific Model**
**Example:** Within `brain.yaml` → `brain` + `shell`

**What it shows:**
- Same as organ-specific but focused on tissue layers
- Example: Brain → brain tissue + skull shell
- Example: Heart → myocardium + chambers

**Use cases:**
- Cross-sectional anatomy views
- Layer-by-layer analysis
- Educational models (peel-away views)
- Surgical approach visualization

**File size:** 50-400 MB  
**Processing time:** 30-90 seconds

**Example output (brain):**
```
outputs/brain_segmentation/
├── brain_brain.stl                (187.0 MB)
├── brain_brain_colored.ply         (78.6 MB)
├── brain_shell.stl                (107.6 MB)
└── brain_shell_colored.ply         (45.2 MB)
```

---

### 3️⃣ **Full Anatomy Model** ⭐ NEW!
**Profile:** `full_anatomy.yaml`

**What it shows:**
- ALL organs in one model
- Each structure colored differently
- Skin layer removed to expose internal anatomy
- 9 structures: bones, liver, kidneys, spleen, pancreas, heart, lungs, muscle, vessels

**Use cases:**
- Comprehensive anatomical overview
- Medical student training
- Patient education (show all affected areas)
- VR/AR visualization
- Research presentations
- Anatomical atlases

**File size:** 180-500 MB  
**Processing time:** 60-120 seconds

**Example output:**
```
outputs/lung_TCGA-17-Z054_full_anatomy/
├── full_anatomy_combined.stl           (72.8 MB)
├── full_anatomy_combined_colored.ply   (30.6 MB)  ← Best for viewing
└── full_anatomy_combined.obj           (85.7 MB)
```

**Color-coded structures:**
| Structure | Color | HU Range |
|-----------|-------|----------|
| Bones | Bone white (230,230,210) | 150-3000 |
| Liver | Liver brown (180,60,30) | 45-105 |
| Kidneys | Dark red (140,40,40) | 25-85 |
| Spleen | Purple-red (120,30,60) | 40-80 |
| Pancreas | Orange (255,165,0) | 30-95 |
| Heart | Bright red (200,40,40) | 20-70 |
| Lungs | Pink (255,200,200) | -530 to -50 |
| Muscle | Red-brown (150,80,80) | 10-60 |
| Vessels | Crimson (220,20,60) | 110-220 |

---

## 🎯 Usage Examples

### Generate All 3 Types
```bash
# 1. Organ-specific (lungs only)
.venv/bin/python batch_cloud_segmentation.py \
  --cloud-input s3://my-medical-imaging/datasets/tcia/lung_TCGA-17-Z054 \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --organs lungs

# 2. Tissue-specific (brain layers)
.venv/bin/python batch_cloud_segmentation.py \
  --cloud-input s3://my-medical-imaging/datasets/sample_brain_ct \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --organs brain

# 3. Full anatomy (all organs, skin removed)
.venv/bin/python batch_cloud_segmentation.py \
  --cloud-input s3://my-medical-imaging/datasets/tcia/lung_TCGA-17-Z054 \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --organs full_anatomy
```

---

## 📊 Comparison Table

| Feature | Organ-Specific | Tissue-Specific | Full Anatomy |
|---------|----------------|-----------------|--------------|
| **Structures** | 1 organ | 1 organ (layers) | 9+ organs |
| **Colors** | 2-3 per organ | 2-3 layers | 9 distinct |
| **Skin** | Included | Included | Removed ✅ |
| **File Size** | 20-600 MB | 50-400 MB | 180-500 MB |
| **Processing** | 30-60s | 30-90s | 60-120s |
| **Best For** | Single organ study | Layer analysis | Overview |
| **3D Printing** | ✅ Easy | ✅ Easy | ⚠️ Complex |
| **Education** | ✅ Good | ✅ Good | ✅✅ Excellent |
| **Patient Ed** | ✅ Good | ✅ Good | ✅✅ Best |
| **Research** | ✅ Good | ✅ Good | ✅✅ Best |

---

## 🎨 Viewing Recommendations

### For Colors (Full Anatomy)
- **Blender** - Best color support, powerful tools
- **MeshLab** - Inspect mesh quality, measurements
- **Sketchfab** - Upload and share online

### For STL (3D Printing)
- **Cura** - Slicing for FDM printers
- **PrusaSlicer** - Slicing for Prusa printers
- **Meshmixer** - Repair and prepare for printing

### For Medical Review
- **3D Slicer** - Full medical imaging suite
- **Horos** - Mac-based DICOM viewer
- **ParaView** - Scientific visualization

---

## 💾 Cloud Storage Summary

**Current Status (Jan 28, 2026):**
- Total Size: 2.8 GB / 250 GB (1.1% used)
- Total Objects: 2,220 files
- Datasets: 11 CT scans
- Models Generated: 32+ (organ + tissue + full anatomy)

**Model Breakdown:**
```
├── Organ-specific: 16 models (lungs, pancreas, kidneys, liver)
├── Tissue-specific: 8 models (brain layers, lung tissues)
└── Full anatomy: 1 model (all organs combined) ⭐ NEW
```

---

## 🚀 Next Steps

1. **Download and View:**
```bash
./do_spaces.sh download s3://my-medical-imaging/outputs/lung_TCGA-17-Z054_full_anatomy/ output/
blender output/full_anatomy_combined_colored.ply
```

2. **Generate More Full Anatomy Models:**
```bash
# Process all chest CTs
for dataset in lung_TCGA-17-Z054 lidc_patient_01 lidc_patient_02; do
  python batch_cloud_segmentation.py \
    --cloud-input s3://my-medical-imaging/datasets/tcia/$dataset \
    --cloud-output s3://my-medical-imaging/outputs/ \
    --organs full_anatomy
done
```

3. **Compare with 3D Slicer:**
- Import DICOM in 3D Slicer
- Use Segment Editor to manually segment
- Export as STL/PLY
- Compare with automated output

---

*Quick Reference Guide*  
*Last Updated: Jan 28, 2026*
