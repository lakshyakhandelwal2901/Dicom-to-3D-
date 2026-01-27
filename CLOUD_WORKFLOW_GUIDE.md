# Automated Cloud Workflow - Quick Reference

## ✅ Status
**WORKING**: Automated DICOM storage/retrieval integrated with segmentation

## What It Does
1. **Auto-downloads** DICOM from cloud if not local
2. **Processes** locally (fast GPU/CPU)
3. **Auto-uploads** results to cloud
4. **Auto-cleanup** local files (saves space)
5. **Reuses** cached DICOM (skips re-download)

---

## Storage Structure

```
my-medical-imaging/ (DigitalOcean Spaces)
├── datasets/               # Raw DICOM files
│   ├── lidc_sample_ct/    # 133 DICOM files (17 MB)
│   └── your_scan/         # Your datasets here
│
└── outputs/               # Segmentation results
    ├── brain_segmentation/         # 4 files (399 MB)
    └── lungs_segmentation_*/       # 4 files (61 MB)
```

**Current Usage**: 526 MB / 250 GB (0.2%)

---

## Quick Commands

### Run Segmentation from Cloud
```bash
cd medical_imaging_platform

# Basic: Download → Process → Upload → Cleanup
python3 cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/lidc_sample_ct \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/

# Keep local files (for inspection)
python3 cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/your_scan \
  --organ brain \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --keep-local

# Different model
python3 cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/chest_ct \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --model totalSegmentator
```

### Upload New Dataset
```bash
# Upload your DICOM folder to cloud
./do_spaces.sh upload data/my_scan s3://my-medical-imaging/datasets/my_scan

# Then run workflow
python3 medical_imaging_platform/cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/my_scan \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/
```

### Download Results for Visualization
```bash
# Download specific output
./do_spaces.sh download \
  s3://my-medical-imaging/outputs/lungs_segmentation_lidc_sample_ct/lungs_lung_tissue.stl \
  output/lung.stl

# Download entire result folder
./do_spaces.sh download \
  s3://my-medical-imaging/outputs/lungs_segmentation_lidc_sample_ct \
  output/lungs_results
```

---

## Workflow Details

### Standard Workflow (Recommended)
```bash
python3 cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/scan_name \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/
```

**What happens:**
1. Downloads DICOM to `/tmp/dicom_processing/scan_name`
2. Runs segmentation (outputs to `/tmp/dicom_processing/lungs_segmentation_scan_name`)
3. Uploads results to `s3://my-medical-imaging/outputs/lungs_segmentation_scan_name`
4. Cleans up local output files (saves ~61 MB)
5. **Keeps DICOM cached** for next run (skips re-download)

### Development Workflow (Keep Local)
```bash
python3 cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/scan_name \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --keep-local
```

**What happens:**
- Same as above, but keeps local files for inspection
- Local files: `/tmp/dicom_processing/`

### Aggressive Cleanup (Save Max Space)
```bash
python3 cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/scan_name \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --cleanup-input
```

**What happens:**
- Same as standard, but **also deletes DICOM** after processing
- Next run will re-download DICOM
- Use if processing many scans sequentially

---

## Typical Workflows

### 1. Process Multiple Scans
```bash
# Upload all scans first
for scan in data/scan_*; do
  ./do_spaces.sh upload "$scan" s3://my-medical-imaging/datasets/$(basename "$scan")
done

# Process each from cloud
for scan in scan_001 scan_002 scan_003; do
  python3 medical_imaging_platform/cloud_workflow.py \
    --cloud-input s3://my-medical-imaging/datasets/$scan \
    --organ lungs \
    --cloud-output s3://my-medical-imaging/outputs/ \
    --cleanup-input  # Free space after each
done
```

### 2. Development/Testing
```bash
# Keep everything local for debugging
python3 medical_imaging_platform/cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/test_scan \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/ \
  --keep-local

# Inspect outputs
ls -lh /tmp/dicom_processing/lungs_segmentation_test_scan/
```

### 3. Production Pipeline
```bash
# Process with cleanup, download only final meshes
python3 medical_imaging_platform/cloud_workflow.py \
  --cloud-input s3://my-medical-imaging/datasets/patient_001 \
  --organ lungs \
  --cloud-output s3://my-medical-imaging/outputs/

# Download just the colored PLY for visualization
./do_spaces.sh download \
  s3://my-medical-imaging/outputs/lungs_segmentation_patient_001/lungs_lung_tissue_colored.ply \
  output/patient_001_lungs.ply
```

---

## Advantages

✅ **Zero local storage** - Process 1000+ scans without filling disk
✅ **Fast processing** - Download/upload in parallel, process locally on GPU
✅ **Automatic caching** - DICOM cached, skips re-download on subsequent runs
✅ **Flexible cleanup** - Keep or delete local files as needed
✅ **Cloud backup** - All results safely stored in DigitalOcean Spaces
✅ **Easy sharing** - Share cloud URLs instead of large files

---

## Space Savings Example

**Traditional (local-only):**
- 10 chest CT scans: ~170 MB
- 10 lung segmentations: ~610 MB
- **Total local**: ~780 MB

**Cloud workflow:**
- 10 scans in cloud: ~170 MB (cloud)
- Process one at a time, cleanup after: **~17 MB local peak**
- 10 results in cloud: ~610 MB (cloud)
- **Total local**: 17 MB (97% space saved!)

---

## Monitoring

### Check Cloud Usage
```bash
./do_spaces.sh usage
```

### List All Datasets
```bash
./do_spaces.sh list s3://my-medical-imaging/datasets/
```

### List All Results
```bash
./do_spaces.sh list s3://my-medical-imaging/outputs/
```

### Check Local Cache
```bash
ls -lh /tmp/dicom_processing/
du -sh /tmp/dicom_processing/*
```

---

## Troubleshooting

### "Download failed"
- Check credentials: `aws configure --profile digitalocean`
- Verify bucket: `./do_spaces.sh list`
- Check path exists: `./do_spaces.sh list s3://my-medical-imaging/datasets/`

### "Segmentation failed"
- Check DICOM validity: Run validator first
- Try with `--keep-local` to inspect files
- Check logs in terminal output

### "Out of space"
- Clean local cache: `rm -rf /tmp/dicom_processing/*`
- Use `--cleanup-input` flag
- Check local disk: `df -h /tmp`

### Slow downloads
- DigitalOcean SGP1 region (Singapore) - fast for Asia
- Switch to closer region if needed (nyc3, sfo3, ams3)
- Use `aws s3 sync` for faster parallel transfers

---

## Cost & Capacity

**DigitalOcean Spaces (GitHub Student Pack):**
- Storage: 250 GB
- Transfer: 1 TB/month
- Cost: $0 (with $200 credit = 40 months free)

**Capacity estimates:**
- ~14,000 raw CT scans (17 MB each)
- ~4,000 lung segmentations (61 MB each)
- ~900 brain segmentations (280 MB each)
- Mixed: 500 CTs + 1,000 lung results + 200 brain results

**Current usage**: 526 MB (0.2% of 250 GB)
**Remaining**: 249.5 GB

---

## Next Steps

1. **Upload your datasets**:
   ```bash
   ./do_spaces.sh upload data/your_scan s3://my-medical-imaging/datasets/your_scan
   ```

2. **Run automated workflow**:
   ```bash
   python3 medical_imaging_platform/cloud_workflow.py \
     --cloud-input s3://my-medical-imaging/datasets/your_scan \
     --organ lungs \
     --cloud-output s3://my-medical-imaging/outputs/
   ```

3. **Download results**:
   ```bash
   ./do_spaces.sh download \
     s3://my-medical-imaging/outputs/lungs_segmentation_your_scan/lungs_lung_tissue.stl \
     output/result.stl
   ```

4. **Visualize in Blender/MeshLab**

---

**Setup Date**: January 23, 2026  
**Files**: 142 objects, 526 MB  
**Status**: ✅ Fully operational
