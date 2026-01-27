# ✅ DigitalOcean Spaces - Setup Complete

**Status**: ACTIVE and working!

## Your Configuration
- **Provider**: DigitalOcean Spaces
- **Region**: SGP1 (Singapore)
- **Bucket**: `my-medical-imaging`
- **Storage**: 250 GB
- **Credit**: $200 (40 months free)

## Current Usage
- **Files**: 5 objects
- **Size**: 399 MiB / 250 GB (0.15% used)
- **Remaining**: ~249.6 GB

## Uploaded Content
✓ Brain segmentation outputs (4 files, 399 MiB)
  - brain_brain.stl (178 MB)
  - brain_brain_colored.ply (75 MB)
  - brain_shell.stl (103 MB)
  - brain_shell_colored.ply (43 MB)

---

## Quick Commands

### Helper Script (Recommended)
```bash
# Show usage
./do_spaces.sh usage

# Upload outputs
./do_spaces.sh upload output/results s3://my-medical-imaging/outputs/results

# List files
./do_spaces.sh list s3://my-medical-imaging/outputs/

# Download file
./do_spaces.sh download s3://my-medical-imaging/outputs/lung.stl output/lung.stl
```

### Direct Commands
```bash
# Upload
python3 medical_imaging_platform/core/cloud_storage.py upload \
  --provider s3 \
  --local output/folder \
  --remote s3://my-medical-imaging/outputs/folder \
  --recursive

# Download
python3 medical_imaging_platform/core/cloud_storage.py download \
  --provider s3 \
  --remote s3://my-medical-imaging/outputs/folder \
  --local output/folder \
  --recursive

# List
python3 medical_imaging_platform/core/cloud_storage.py list \
  --provider s3 \
  --remote s3://my-medical-imaging/outputs/
```

### AWS CLI (Advanced)
```bash
# List all
AWS_PROFILE=digitalocean aws s3 ls s3://my-medical-imaging/ \
  --recursive --endpoint-url https://sgp1.digitaloceanspaces.com

# Upload single file
AWS_PROFILE=digitalocean aws s3 cp file.stl \
  s3://my-medical-imaging/outputs/file.stl \
  --endpoint-url https://sgp1.digitaloceanspaces.com

# Sync directory (faster for many files)
AWS_PROFILE=digitalocean aws s3 sync output/ \
  s3://my-medical-imaging/outputs/ \
  --endpoint-url https://sgp1.digitaloceanspaces.com
```

---

## 🔒 SECURITY REMINDER

**⚠️ YOUR CREDENTIALS WERE EXPOSED IN CHAT**

**Regenerate keys immediately:**
1. Go to: https://cloud.digitalocean.com/account/api/tokens
2. Click "Spaces Keys" tab
3. Delete the current key (DO00Q7YAUR2E2U8YAQLB)
4. Generate a new key
5. Update credentials:
   ```bash
   aws configure --profile digitalocean
   # Enter new Access Key and Secret Key
   ```

**Never share credentials in:**
- Chat messages
- Git commits
- Screenshots
- Public documentation

---

## Recommended Workflow

### 1. Process locally, upload, clean
```bash
# Process DICOM
cd medical_imaging_platform
python3 main.py --organ lungs --input ../data/ct_scan --output ../output/lungs

# Upload to cloud
./do_spaces.sh upload output/lungs s3://my-medical-imaging/outputs/lungs

# Free local space
rm -rf ../output/lungs
```

### 2. Download when needed
```bash
# Download specific file for visualization
./do_spaces.sh download \
  s3://my-medical-imaging/outputs/lungs/lung_tissue.stl \
  output/lung_tissue.stl

# Open in Blender/MeshLab
```

### 3. Monitor usage
```bash
# Check storage usage
./do_spaces.sh usage

# List all outputs
./do_spaces.sh list s3://my-medical-imaging/outputs/
```

---

## Capacity Planning

With 250 GB free storage, you can store:

| Content Type | Size | Capacity |
|--------------|------|----------|
| Lung segmentations | 61 MB | ~4,000 results |
| Brain segmentations | 280 MB | ~900 results |
| Raw CT series | 17 MB | ~14,000 scans |
| Mixed (50 lungs + 200 CTs) | - | Fits easily |

**Current usage**: 399 MB (0.15%)
**Remaining**: 249.6 GB (99.85%)

---

## Cost After Credit Expires

- **Monthly**: $5/month for 250 GB + 1 TB transfer
- **Annual**: $60/year
- **Credit lasts**: 40 months (~3+ years)

Still significantly cheaper than AWS/GCS/Azure beyond free tier!

---

## Access via Web UI

View/download files directly:
- URL: https://cloud.digitalocean.com/spaces/my-medical-imaging
- Browse folders, download individual files
- Share public links (if bucket is public)

---

## Troubleshooting

### "Access Denied"
```bash
# Verify credentials
AWS_PROFILE=digitalocean aws s3 ls --endpoint-url https://sgp1.digitaloceanspaces.com

# If fails, reconfigure
aws configure --profile digitalocean
```

### "Bucket not found"
- Check bucket name: `my-medical-imaging`
- Check region: SGP1
- Verify at: https://cloud.digitalocean.com/spaces

### Slow uploads
```bash
# Use sync instead of cp for large folders (parallel transfers)
AWS_PROFILE=digitalocean aws s3 sync output/ s3://my-medical-imaging/outputs/ \
  --endpoint-url https://sgp1.digitaloceanspaces.com
```

---

**Setup Date**: January 23, 2026
**Next Step**: Regenerate API keys for security!
