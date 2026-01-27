# TCIA Datasets in Cloud Storage

## Current Status
**Date**: January 23, 2026  
**Cloud Provider**: DigitalOcean Spaces (SGP1 region)  
**Bucket**: my-medical-imaging  
**Total Storage Used**: 526.5 MB / 250 GB (0.2%)  
**Total Objects**: 142 files

---

## Uploaded Datasets

### 1. LIDC-IDRI Chest CT (lidc_sample_ct)
- **Location**: `s3://my-medical-imaging/datasets/lidc_sample_ct/`
- **Files**: 133 DICOM files
- **Size**: 66.8 MB
- **Description**: Lung Image Database Consortium (LIDC) chest CT scan
- **Body Part**: Chest/Thorax
- **Useful For**: Lung segmentation, airway detection, chest anatomy
- **Status**: ✅ Uploaded and validated

**Run Segmentation**:
```bash
python3 cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/lidc_sample_ct \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/
```

---

## Segmentation Results in Cloud

### 1. Brain Segmentation Results
- **Location**: `s3://my-medical-imaging/outputs/brain_segmentation/`
- **Files**: 4 outputs (399 MB)
- **Outputs**:
  - `brain_brain.stl` - 3D mesh
  - `brain_brain_colored.ply` - Colored point cloud
  - Additional files

### 2. Lung Segmentation Results  
- **Location**: `s3://my-medical-imaging/outputs/lungs_segmentation_lidc_sample_ct/`
- **Files**: 4 outputs (61 MB)
- **Outputs**:
  - `lungs_lung_tissue.stl` (33.9 MB) - Lung tissue mesh
  - `lungs_lung_tissue_colored.ply` (14.3 MB) - Colored lung mesh
  - `lungs_airways.stl` (8.8 MB) - Airways mesh
  - `lungs_airways_colored.ply` (3.7 MB) - Colored airways mesh

---

## Available TCIA Collections

### Recommended for Download

1. **LIDC-IDRI** (Lung)
   - 1,018 chest CT series
   - Lung cancer screening
   - ~17 MB per series
   - Already have 1 sample ✓

2. **COVID-19-CT-Scans**
   - Chest CT with COVID-19
   - Various severity levels
   - Good for lung pathology

3. **CT-ORG**
   - Multi-organ CT dataset
   - Annotated organs
   - Chest, abdomen, pelvis

4. **TCGA-GBM** (Brain)
   - Brain tumor MRI/CT
   - Glioblastoma cases
   - Good for brain segmentation

5. **LiTS** (Liver)
   - Liver tumor segmentation
   - Challenge dataset
   - Abdominal CT

---

## How to Add More Datasets

### Method 1: Manual Download + Upload
```bash
# 1. Download from TCIA website (https://www.cancerimagingarchive.net/)
# 2. Save to data/new_dataset/
# 3. Upload to cloud:
./do_spaces.sh upload data/new_dataset s3://my-medical-imaging/datasets/new_dataset
```

### Method 2: Use TCIA Notebook
```bash
# 1. Open notebooks/TCIA_API_Download.ipynb
# 2. Install: pip install tcia_utils
# 3. Run cells to download dataset
# 4. Upload to cloud:
./do_spaces.sh upload data/tcia_downloads/dataset_name s3://my-medical-imaging/datasets/
```

### Method 3: Use Upload Script
```bash
# Place DICOM in data/ directory, then:
python3 scripts/upload_datasets_to_cloud.py
```

---

## Processing Pipeline

### Standard Workflow
1. **Upload dataset to cloud** (once)
   ```bash
   ./do_spaces.sh upload data/my_ct s3://my-medical-imaging/datasets/my_ct
   ```

2. **Run automated cloud workflow**
   ```bash
   python3 cloud_workflow.py \
     --cloud-input s3://my-medical-imaging/datasets/my_ct \
     --organ lungs \
     --cloud-output s3://my-medical-imaging/outputs/
   ```

3. **Download results when needed**
   ```bash
   ./do_spaces.sh download \
     s3://my-medical-imaging/outputs/lungs_segmentation_my_ct/lungs_lung_tissue.stl \
     output/result.stl
   ```

### Batch Processing Multiple Datasets
```bash
# Process all datasets
for dataset in $(./do_spaces.sh list s3://my-medical-imaging/datasets/ | grep "datasets/" | cut -d'/' -f2 | sort -u); do
  echo "Processing: $dataset"
  python3 cloud_workflow.py \
    --cloud-input s3://my-medical-imaging/datasets/$dataset \
    --organ lungs \
    --cloud-output s3://my-medical-imaging/outputs/ \
    --cleanup-input
done
```

---

## Storage Capacity Planning

**Current Usage**: 526.5 MB (0.2% of 250 GB)  
**Remaining**: 249.5 GB

### Capacity Estimates
- **Raw CT Scans**: 
  - Avg 17 MB per chest CT → ~14,700 scans
  - Avg 66 MB per brain CT → ~3,800 scans
  
- **Segmentation Outputs**:
  - Lung results: ~61 MB → ~4,000 results
  - Brain results: ~280 MB → ~900 results

- **Mixed Storage** (recommended):
  - 500 CT scans (raw): ~33.5 GB
  - 500 lung results: ~30 GB
  - 100 brain results: ~28 GB
  - **Total**: ~91.5 GB (still 158.5 GB free)

---

## Dataset Sources

### TCIA (The Cancer Imaging Archive)
- **Website**: https://www.cancerimagingarchive.net/
- **API**: tcia_utils Python library
- **Collections**: 30K+ datasets, 300+ studies
- **Access**: Free, registration required
- **Data Types**: CT, MRI, PET, X-ray, ultrasound

### Other Public Sources
1. **OpenNeuro** - Brain MRI
2. **MICCAI Grand Challenges** - Competition datasets
3. **NIH 3D Print Exchange** - Medical imaging
4. **Radiopaedia** - Teaching cases (with permission)

---

## Scripts Reference

### `upload_datasets_to_cloud.py`
Uploads local datasets to DigitalOcean Spaces
- Checks dataset existence and size
- Uploads to cloud
- Provides summary report

### `cloud_workflow.py`
Automated end-to-end processing
- Downloads DICOM from cloud
- Runs segmentation locally
- Uploads results to cloud
- Cleans up local files

### `do_spaces.sh`
DigitalOcean Spaces helper
- `upload` - Upload files/folders
- `download` - Download files/folders  
- `list` - List objects
- `usage` - Show storage usage
- `delete` - Delete objects

---

## Next Steps

### Immediate
1. ✅ LIDC chest CT uploaded and working
2. ⚠️ Regenerate API keys (exposed in chat - see DIGITALOCEAN_STATUS.md)
3. 📥 Download more datasets from TCIA
4. 🔬 Test automated workflow on multiple organs

### Short-term (This Week)
1. Add 3-5 diverse datasets (brain, liver, kidney)
2. Process all with automated workflow
3. Compare segmentation quality across datasets
4. Document any edge cases

### Medium-term (This Month)
1. Collect 20-50 diverse CT scans
2. Build dataset library in cloud
3. Test Phase 2A (TotalSegmentator) on cloud datasets
4. Create dataset catalog with metadata

---

## Troubleshooting

### "Download failed"
- Check credentials: `aws configure --profile digitalocean`
- Verify path exists: `./do_spaces.sh list s3://my-medical-imaging/datasets/`

### "Upload timeout"
- Large datasets may take time (17 MB = ~30 sec)
- Check internet: `ping digitaloceanspaces.com`
- Try smaller batches

### "Segmentation failed"
- Validate DICOM first: `python3 scripts/validate_dicom_series.py data/dataset/`
- Check modality (must be CT)
- Verify HU values present

---

**Last Updated**: January 23, 2026  
**Maintained By**: Medical Imaging Platform Team
