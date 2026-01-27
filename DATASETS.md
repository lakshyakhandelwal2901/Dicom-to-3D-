# Datasets Guide: Finding, Downloading & Organizing Medical Imaging Data

**Purpose**: Comprehensive guide for Phase 2B data collection (Week 2-8)  
**Status**: Ready to implement  
**Last Updated**: Jan 2026

---

## 🗂️ Available Datasets Overview

### Summary Table

| Dataset | Size | Format | Organs | QA Level | License | Download Time | Storage |
|---------|------|--------|--------|----------|---------|---|---|
| **Medical Segmentation Decathlon** | 1K scans | NIfTI | 10 organs | ⭐⭐⭐⭐⭐ | CC BY-NC 4.0 | 1 hour | 50 GB |
| **TCIA (Cancer Imaging Archive)** | 30K+ scans | DICOM | Multi | ⭐⭐⭐⭐⭐ | Various | 1-2 days | 500+ GB |
| **LiTS (Liver Tumor)** | 201 scans | NIfTI | Liver+tumor | ⭐⭐⭐⭐⭐ | CC0 | 30 min | 30 GB |
| **CHAOS (CT-MR Challenge)** | 120 scans | DICOM | 4 organs | ⭐⭐⭐⭐ | Research | 1 hour | 10 GB |
| **KITS (Kidney Tumor)** | 300 scans | DICOM | Kidney+tumor | ⭐⭐⭐⭐⭐ | CC BY-NC 4.0 | 2 hours | 50 GB |
| **BraTS (Brain Tumor)** | 500 scans | NIfTI | Brain+tumor | ⭐⭐⭐⭐⭐ | CC BY-NC 4.0 | 4 hours | 150 GB |
| **Synapse** | 30 scans | NIfTI | Multi-organ | ⭐⭐⭐⭐⭐ | CC BY-NC 4.0 | 30 min | 10 GB |
| **LIDC-IDRI (Lung)** | 1K+ scans | DICOM | Lung nodules | ⭐⭐⭐⭐ | TCIA/NIH | 1 day | 150 GB |
| **Pancreas CT** | 82 scans | NIfTI | Pancreas | ⭐⭐⭐⭐ | CC0 | 1 hour | 15 GB |
| **Heart (MICCAI)** | 20 scans | NIfTI | Heart | ⭐⭐⭐⭐ | Research | 30 min | 5 GB |

**Total Dataset Pool**: 32K+ labeled scans  
**Total Storage**: ~1 TB (if download all)  
**For Phase 2C Minimum**: 300-500 scans (100-200 GB recommended start)

---

## 📥 Dataset Details & Download Instructions

### 1. Medical Segmentation Decathlon ⭐ START HERE

**URL**: http://medicaldecathlon.com/  
**Size**: 1K scans (1.3 GB compressed, 50 GB extracted)  
**Format**: NIfTI (.nii.gz)  
**Organs**: 10 (brain, heart, liver, hippocampus, pancreas, prostate, lungs, spleen, colon, kidney)  
**Annotation Quality**: Expert (5 raters, consensus)  
**License**: CC BY-NC 4.0 (Academic use allowed)  
**Time to Download**: 1 hour

**Download Instructions:**
```bash
cd /workspaces/Dicom-to-3D-/data/datasets

# Download script (make it)
cat > download_decathlon.sh << 'EOF'
#!/bin/bash
# Download all 10 tasks
for task in 01_brain 02_heart 03_liver 04_hippocampus 05_pancreas \
             06_prostate 07_lungs 08_spleen 09_colon 10_kidney; do
    echo "Downloading Task $task..."
    wget -q https://msd-for-upload.s3-us-west-2.amazonaws.com/Task${task}.tar \
         && tar -xf Task${task}.tar \
         && rm Task${task}.tar
done
EOF

chmod +x download_decathlon.sh
./download_decathlon.sh  # Takes ~1 hour

# Result: TaskXX/ folders with train/ and test/ splits
```

**What You Get:**
```
Task01_Brain/
├── imagesTr/          (484 CT scans)
├── labelsTr/          (484 segmentation masks)
├── imagesTs/          (100 test scans)
└── dataset.json       (metadata)

Task03_Liver/
├── imagesTr/          (131 scans)
├── labelsTr/          (131 masks)
└── ...

...10 tasks total
```

**Best For**: Brain, liver, lungs, pancreas, kidney (all 7 of ours covered!)  
**Quality**: ⭐⭐⭐⭐⭐ Best annotated dataset  
**Recommendation**: Download immediately (only 1 hour, essential for Phase 2C)

---

### 2. TCIA - The Cancer Imaging Archive

**URL**: https://www.cancerimagingarchive.net/  
**Size**: 30K+ scans, 1TB+  
**Format**: DICOM (raw format)  
**Organs**: Multi-organ (many collections)  
**Annotation**: Varies (some with, some without)  
**License**: Various (check per collection)  
**Time to Download**: 1-2 days (massive)

**Key Collections for Your Organs:**

| Collection | Scans | Organs | Download | Notes |
|------------|-------|--------|----------|-------|
| **LPBA40** | 40 | Brain+structures | 5 GB | High-quality brain |
| **BraTS** | 500+ | Brain tumor | 150 GB | On TCIA mirror |
| **Pancreas-CT** | 82 | Pancreas | 15 GB | Great for pancreas |
| **LIDC-IDRI** | 1K+ | Lungs | 150 GB | Lung nodules with consensus |
| **CT Colonography** | 500+ | Colon | 50 GB | Optional |
| **Liver Tumor** | 200+ | Liver | 40 GB | Multi-phase CT |

**Download TCIA Data:**
```bash
# Install TCIA CLI
pip install tcia-utils

# Login to TCIA
tciactl auth

# Download specific collection
tciactl download --collection "LPBA40" --outputDir /data/datasets/tcia/

# Or download via web interface: https://www.cancerimagingarchive.net/
```

**Best For**: Brain, lungs, liver, pancreas  
**Quality**: ⭐⭐⭐⭐⭐ Excellent  
**Recommendation**: Download selectively (full TCIA is 1TB+, take collections one by one)

---

### 3. LiTS - Liver Tumor Segmentation

**URL**: https://www.lits-challenge.com/  
**Size**: 201 scans (30 GB)  
**Format**: NIfTI  
**Organs**: Liver + tumor  
**Annotation**: Expert radiologists  
**License**: CC0 (public domain)  
**Time to Download**: 30 min

**Download:**
```bash
# Register on LiTS website, then:
# https://www.lits-challenge.com/data

cd /data/datasets
wget https://www.lits-challenge.com/protected_data/LiTS.zip
unzip LiTS.zip
# Extracts: LiTS/training/ and LiTS/testing/
```

**What You Get:**
```
LiTS/
├── training/
│   ├── volume-00.nii    (liver CT scan)
│   ├── segmentation-00.nii  (binary mask: 0=background, 1=liver, 2=tumor)
│   └── ... (200 more)
└── testing/
    └── volume-XX.nii
```

**Best For**: Liver segmentation + tumor detection  
**Quality**: ⭐⭐⭐⭐⭐ Excellent  
**Recommendation**: Essential for Phase 2C liver fine-tuning

---

### 4. CHAOS - Multi-Organ CT/MRI

**URL**: https://chaos.grand-challenge.org/  
**Size**: 120 scans (CT: 60, MRI: 60)  
**Format**: DICOM (CT), NIfTI (MRI)  
**Organs**: Liver, kidney, spleen, pancreas  
**Annotation**: Expert consensus  
**License**: Research/Academic  
**Time to Download**: 1 hour

**Download:**
```bash
# Register on Grand Challenge platform
# Manual download: https://chaos.grand-challenge.org/Data/

# Extract:
cd /data/datasets
unzip CHAOS_train.zip
unzip CHAOS_test.zip
```

**What You Get:**
```
CHAOS/
├── Train_Sets/
│   ├── CT/              (60 CT scans + segmentations)
│   ├── MR/              (60 MRI scans + segmentations)
├── Test_Sets/
│   ├── CT/
│   └── MR/
```

**Best For**: Multi-organ (liver, kidney, spleen, pancreas)  
**Quality**: ⭐⭐⭐⭐  
**Recommendation**: Good for CT, skip MR for Phase 2A (CT only focus)

---

### 5. KITS - Kidney Tumor Segmentation

**URL**: https://kits-challenge.org/kits21/  
**Size**: 300 scans (50 GB)  
**Format**: DICOM  
**Organs**: Kidney + tumor + cysts  
**Annotation**: Expert radiologists  
**License**: CC BY-NC 4.0  
**Time to Download**: 2 hours

**Download:**
```bash
# Via Google Drive link on https://kits-challenge.org/data
# Manual download recommended (faster than script)

cd /data/datasets
unzip kits21_release.zip
```

**What You Get:**
```
kits21/data/
├── case_00000/
│   ├── imaging.nii.gz          (CT volume)
│   ├── segmentation.nii.gz     (0=bg, 1=kidney, 2=tumor, 3=cyst)
│   └── ...
├── case_00001/
└── ... (300 cases)
```

**Best For**: Kidney segmentation with pathology  
**Quality**: ⭐⭐⭐⭐⭐ Excellent  
**Recommendation**: Essential for Phase 2C kidney fine-tuning

---

### 6. BraTS - Brain Tumor Segmentation

**URL**: https://www.med.upenn.edu/cbica/brats/  
**Size**: 500 scans (150 GB) - MRI based  
**Format**: NIfTI  
**Organs**: Brain + tumor (multi-modal MRI)  
**Annotation**: Expert neuroradiologists  
**License**: CC BY-NC 4.0  
**Time to Download**: 4 hours

**Note**: BraTS is MRI, not CT. Phase 2A focuses on CT.  
**Skip for Phase 2A, consider for Phase 3 (MRI support)**

---

### 7. Synapse Multi-Organ (High Quality, Small)

**URL**: https://www.synapse.org/#!Synapse:syn3193805  
**Size**: 30 scans (10 GB) - SMALL BUT HIGH QUALITY  
**Format**: NIfTI  
**Organs**: Liver, kidney, spleen, pancreas  
**Annotation**: Expert radiologists (5 raters)  
**License**: CC BY-NC 4.0  
**Time to Download**: 30 min

**Download:**
```bash
# Via Synapse web interface (need account)
# Or use Python API:
import synapseclient
syn = synapseclient.Synapse()
syn.login('username', 'password')

# Download dataset
entity = syn.get('syn3193805', downloadLocation='/data/datasets/')
```

**Best For**: Multi-organ high-quality benchmark  
**Quality**: ⭐⭐⭐⭐⭐ Best annotated (small dataset)  
**Recommendation**: Download for validation set (30 scans is perfect for test)

---

### 8. LIDC-IDRI - Lung Nodules

**URL**: https://wiki.cancerimagingarchive.net/display/Public/LIDC-IDRI  
**Size**: 1K+ scans (150 GB)  
**Format**: DICOM  
**Organs**: Lungs + nodules  
**Annotation**: 4 radiologists per scan (consensus)  
**License**: TCIA  
**Time to Download**: 1 day

**Best For**: Lung segmentation with nodule detection  
**Quality**: ⭐⭐⭐⭐  
**Recommendation**: Download if you need lung nodule expertise

---

## 📊 Recommended Download Strategy

### Phase 2B - Weeks 2-8 (Data Collection)

**Week 1 Priority (Download First):**
```
1. Medical Segmentation Decathlon  (1 hour, 50 GB) ← START NOW
2. LiTS (Liver)                    (30 min, 30 GB)
3. KITS (Kidney)                   (2 hours, 50 GB)
4. Synapse (Validation)            (30 min, 10 GB)

Total: 4 hours download, 140 GB storage
Organs covered: Brain, liver, kidney, pancreas, lungs, spleen, colon
```

**Week 2-3 (Parallel):**
```
5. CHAOS (Multi-organ)             (1 hour, 10 GB)
6. LIDC-IDRI (Lungs) - optional    (1 day, 150 GB) - skip if storage limited
```

**Week 4-8 (Collect Custom Data):**
```
- Download additional TCIA collections as needed
- Collect your own institutional scans (if available)
- Get consent/IRB approval for any proprietary data
```

---

## 🎯 Directory Organization

```
/workspaces/Dicom-to-3D-/data/datasets/
├── medical_segmentation_decathlon/
│   ├── Task01_Brain/
│   ├── Task03_Liver/
│   ├── Task05_Pancreas/
│   ├── Task07_Lungs/
│   ├── Task10_Kidney/
│   └── README.txt (download log)
│
├── lits_liver/
│   ├── training/
│   └── testing/
│
├── kits_kidney/
│   ├── data/
│   │   ├── case_00000/
│   │   └── ...
│   └── README.txt
│
├── chaos_multimodal/
│   ├── Train_Sets/CT/
│   └── Train_Sets/MR/
│
├── synapse_validation/
│   ├── volume_0/
│   └── ...
│
├── custom_institutional/
│   ├── unlabeled/
│   │   ├── scan_001/
│   │   └── ...
│   └── annotated/
│       ├── scan_001/
│       └── ...
│
└── dataset_inventory.csv  ← Track all downloaded data
```

**Create inventory:**
```bash
cat > /data/datasets/dataset_inventory.csv << 'EOF'
dataset_name,organ,total_scans,labeled_scans,format,size_gb,download_date,notes
Medical Segmentation Decathlon,Multi,1000,1000,NIfTI,50,2026-01-22,All 10 tasks
LiTS,Liver,201,201,NIfTI,30,2026-01-22,Including tumors
KITS,Kidney,300,300,DICOM,50,2026-01-22,With tumors
CHAOS,Multi,120,120,DICOM/NIfTI,10,2026-01-22,CT and MRI
Synapse,Multi,30,30,NIfTI,10,2026-01-22,High quality validation
EOF
```

---

## 🏷️ Annotation Guidelines (If Labeling Custom Scans)

### HU Range Reference for Manual Annotation

| Tissue | HU Range | Visual Appearance | How to Draw |
|--------|----------|------------------|------------|
| Brain Parenchyma | 0-150 | Gray soft tissue | Exclude ventricles, use brush tool |
| Skull/Bone | 120-3000 | White/bright | Follows outer edge, connects at base |
| Liver | 40-100 | Reddish-brown | Exclude hepatic veins (100-200 HU) |
| Kidneys | 30-80 | Slightly lighter brown | Oval shapes on lateral sides |
| Pancreas | 35-90 | Gray-brown, thin | Head/body/tail, between kidney & spleen |
| Lungs | -500 to -100 | Dark gray/black | Entire lung field, exclude airways |
| Heart | 40-120 | Medium gray | 4 chambers, exclude blood pools |

### Annotation Tool Setup

```bash
# Option 1: 3D Slicer (Professional, recommended)
# Download: https://download.slicer.org/
# Tutorials: https://www.slicer.org/wiki/Documentation

# Option 2: ITK-SNAP (Lightweight, fast)
# Download: http://www.itksnap.org/

# Option 3: Python-based (for automation)
pip install napari  # Lightweight viewer with annotation
```

### Quality Assurance

- Annotation time: 30-60 min per scan
- QA time: 5-10 min per scan (second rater)
- Target: >90% overlap (Dice score) between raters
- Flag edge cases for senior radiologist review

---

## 💾 Data Storage Tips

### Local Storage Strategy

```
If you have <500 GB storage:
  → Download only Phase 2A minimum (Medical Decathlon + LiTS + KITS + Synapse = 140 GB)
  → Keep others on cloud (AWS S3, Google Drive)
  
If you have 1 TB storage:
  → Download all Phase 2B datasets (500 GB)
  → Stream from cloud as needed
  
If you have 2 TB+ storage:
  → Download everything
  → Set up local Git LFS for versioning
```

### Cloud Storage (If Limited Local Space)

```bash
# AWS S3
aws s3 sync s3://tcia-public-bucket datasets/ --no-sign-request

# Google Cloud Storage
gsutil -m cp -r gs://open-medical-imaging/decathlon/** ./

# Free tier limits:
# AWS: 1 GB/month free download
# GCS: 5 GB/month free
```

---

## 📋 Data Preparation Checklist

- [ ] Week 1: Download Medical Segmentation Decathlon
- [ ] Week 1: Download LiTS + KITS + Synapse
- [ ] Week 2: Organize in /data/datasets/ with inventory
- [ ] Week 2: Sample 10 scans from each dataset
- [ ] Week 3: Validate format (NIfTI vs DICOM conversion if needed)
- [ ] Week 3: Create train/val/test splits
- [ ] Week 4-8: Collect your own custom scans (if available)
- [ ] Week 4-8: Annotate 100-200 custom scans
- [ ] Week 8: Create combined training dataset (500-1000 scans)
- [ ] Week 8: Validate ground truth (QA check)

---

## 🔗 Quick Download Links

```bash
# Automated download script (copy-paste)
mkdir -p /data/datasets && cd /data/datasets

# Medical Segmentation Decathlon
echo "Downloading Decathlon..."
for i in {1..10}; do
  wget -q https://msd-for-upload.s3-us-west-2.amazonaws.com/Task$(printf "%02d" $i)_*.tar \
    && tar -xf Task$(printf "%02d" $i)_*.tar \
    && rm Task$(printf "%02d" $i)_*.tar
done

# LiTS
echo "Downloading LiTS..."
wget -q https://www.lits-challenge.com/protected_data/LiTS.zip && unzip -q LiTS.zip

# KITS
echo "Downloading KITS..."
# Manual: https://kits-challenge.org/data/

echo "Dataset download complete!"
```

---

## ✅ CT Readiness Checklist

- Modality: CT only; exclude CR/X-ray projections (AP/PA views).
- HU availability: `RescaleSlope` and `RescaleIntercept` present; HU stats include air near −1000 and soft tissue near [−100, 100].
- Bit depth: `BitsStored` ≥ 12 (typically 16) with consistent `PixelRepresentation`.
- Spacing tags: `PixelSpacing` (XY) and `SliceThickness` (Z) present and consistent across slices.
- Slice count: ≥ 50 unique slice positions with near-uniform Z spacing.
- Ordering: `ImagePositionPatient` or `InstanceNumber` usable to sort slices.
- Integrity: One series per folder; avoid mixing modalities/series.
- Privacy: PHI removed or properly de-identified per dataset license.

## 🔎 Quick Validation Script

- Path: [medical_imaging_platform/scripts/validate_dicom_series.py](medical_imaging_platform/scripts/validate_dicom_series.py)
- Usage:

```bash
python3 medical_imaging_platform/scripts/validate_dicom_series.py /path/to/dicom_series
```

The script prints PASS/FAIL with specific reasons. Use it to pre-check datasets before running segmentation.

## 📚 Recommended Chest CT Sources

- TCIA – LIDC-IDRI: Large lung CT collection with annotations (registration required).
- TCIA – Lung-PET-CT-Dx: Diagnostic chest CTs paired with PET (CT usable for segmentation).
- MosMedData: COVID-19 chest CTs from multiple hospitals (diverse protocols).
- NSCLC Radiogenomics (TCIA): Thoracic CTs with clinical metadata.
- Medical Segmentation Decathlon – Task07 Lungs: NIfTI lungs subset for prototyping.

## 💻 TCIA API Notebook

- Use the ready notebook to list collections, filter series, and download one CT series via `tcia_utils`.
- Path: [notebooks/TCIA_API_Download.ipynb](notebooks/TCIA_API_Download.ipynb)
- Output: Downloads a series into `data/tcia_downloads/`.

## ❓ FAQ

**Q: How much storage do I need?**  
A: Minimum 200 GB (Medical Decathlon + LiTS + KITS + Synapse). Ideal 1 TB.

**Q: Can I use only free datasets?**  
A: Yes! All recommended datasets are free (CC0 or CC-BY-NC).

**Q: How do I convert DICOM to NIfTI?**  
A: Use `dcm2niix` → `dcm2niix input_folder -o output_folder`

**Q: Do I need all datasets?**  
A: No. Start with Medical Decathlon (covers all organs). Add others if you need specialization.

**Q: Can I use proprietary hospital data?**  
A: Yes, but need IRB/ethics approval + patient consent.

**Q: How long does annotation take?**  
A: 30-60 minutes per scan for expert. 2-3 hours for novice.

---

## 📞 Support

- **TCIA Help**: https://wiki.cancerimagingarchive.net/
- **Medical Decathlon**: http://medicaldecathlon.com/
- **LiTS Challenge**: https://www.lits-challenge.com/
- **KITS Challenge**: https://kits-challenge.org/

---

**Next Steps**: Download Medical Segmentation Decathlon today (1 hour setup)  
**Then**: See DATA_COLLECTION_WORKFLOW.md for annotation process
