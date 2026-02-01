# 🚀 Google Drive Integration - 2TB Cloud Storage

## Why Google Drive?

**Your Advantage:**
- ✅ **2TB storage** (vs 250GB DigitalOcean Spaces)
- ✅ **8x more capacity** for the same project
- ✅ **$0/month** (vs $5/month DigitalOcean)
- ✅ **Already available** - no setup fees
- ✅ Can store **entire TotalSegmentator dataset** (300GB)
- ✅ Can store **all 7,069 recommended datasets** (760GB)

**Cost Savings:**
```
DigitalOcean Spaces:  250 GB @ $5/month  = $60/year
Google Drive:        2000 GB @ $0/month  = $0/year

Annual Savings: $60 + 8x more storage!
```

---

## 📊 Storage Comparison

| Feature | DigitalOcean Spaces | Google Drive (Your Account) |
|---------|--------------------|-----------------------------|
| **Capacity** | 250 GB | 2,000 GB (2TB) |
| **Cost** | $5/month ($60/year) | $0 (already have it) |
| **$/GB** | $0.020/GB | $0.000/GB |
| **TotalSegmentator** | ❌ Won't fit (300GB) | ✅ Fits easily |
| **All Datasets** | ❌ Won't fit (760GB) | ✅ Fits with room |
| **API Access** | ✅ S3-compatible | ✅ Google Drive API |
| **Upload Speed** | Fast | Fast |
| **Download Speed** | Fast | Fast |

**Recommendation:** Use Google Drive as primary storage (replaces DigitalOcean completely - FREE).

---

## 🔧 SETUP (15 Minutes)

### Step 1: Install Dependencies (2 minutes)

```bash
cd /workspaces/Dicom-to-3D-
python setup_google_drive.py install
```

Installs:
- google-auth
- google-api-python-client
- pydrive2

---

### Step 2: Enable Google Drive API (5 minutes)

**2.1 Create Google Cloud Project:**
1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "NEW PROJECT"
3. Project name: `Dicom-3D-Medical-Imaging`
4. Click "CREATE"

**2.2 Enable Google Drive API:**
1. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com
2. Make sure your project is selected (top dropdown)
3. Click "ENABLE"
4. Wait 10-20 seconds for activation

---

### Step 3: Create OAuth Credentials (5 minutes)

**3.1 Configure OAuth Consent Screen:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. User Type: "External" (unless you have Google Workspace)
3. Click "CREATE"
4. Fill in:
   - App name: `Dicom-3D-Desktop`
   - User support email: (your email)
   - Developer contact: (your email)
5. Click "SAVE AND CONTINUE"
6. Scopes: Skip this (click "SAVE AND CONTINUE")
7. Test users: Add your email
8. Click "SAVE AND CONTINUE"
9. Summary: Click "BACK TO DASHBOARD"

**3.2 Create OAuth Client ID:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. Application type: **Desktop app**
4. Name: `Dicom-3D-Desktop`
5. Click "CREATE"
6. **Download JSON** (click download icon)
7. Save as: `/workspaces/Dicom-to-3D-/credentials.json`

```bash
# Make sure the file is in the right place
ls -lh /workspaces/Dicom-to-3D-/credentials.json
```

---

### Step 4: Authenticate (3 minutes)

```bash
cd /workspaces/Dicom-to-3D-
python setup_google_drive.py authenticate
```

**What happens:**
1. Browser opens automatically
2. Sign in to your Google account (the one with 2TB)
3. Click "Allow" when prompted
4. See "The authentication flow has completed"
5. Token saved to `token.pickle`

**If browser doesn't open:**
- Copy the URL from terminal
- Paste into browser
- Complete authentication
- Return to terminal

---

### Step 5: Test Connection (30 seconds)

```bash
python setup_google_drive.py test
```

**Expected output:**
```
================================================================================
✅ GOOGLE DRIVE CONNECTION SUCCESSFUL
================================================================================

📊 Storage Information:
  Total:     2000.0 GB
  Used:      45.2 GB (2.3%)
  Available: 1954.8 GB

📁 Recent Files (5):
  • example1.pdf (2.3 MB)
  • example2.jpg (1.5 MB)
  ...

✅ Google Drive is ready to use!
```

**If it fails:**
- Check `credentials.json` is in the right place
- Re-run: `python setup_google_drive.py authenticate`
- Make sure you signed in to the correct Google account

---

## 📤 USAGE

### Upload Files

**Single file:**
```bash
python gdrive_upload.py output/model.ply
```

**Specify folder:**
```bash
python gdrive_upload.py output/brain.ply Medical-Scans-2026
```

**Batch upload:**
```bash
for file in output/*.ply; do
    python gdrive_upload.py "$file"
done
```

**Upload with progress:**
```bash
python gdrive_upload.py large_dataset.tar.gz
# Progress: 10%
# Progress: 20%
# ...
# ✅ Upload complete!
```

---

### Download Files

**By file ID:**
```bash
python gdrive_download.py 1ABC123xyz456...
```

**By file name:**
```bash
python gdrive_download.py model.ply
```

**To specific location:**
```bash
python gdrive_download.py model.ply /tmp/downloads/
```

---

### List Files

**All files:**
```bash
python gdrive_list.py
```

**Files in specific folder:**
```bash
python gdrive_list.py Dicom-3D-Medical-Imaging
```

**Limit results:**
```bash
python gdrive_list.py 100  # Show 100 most recent
```

**Example output:**
```
📁 Listing all files

Found 25 files:

Name                                     Size         Modified             File ID
----------------------------------------------------------------------------------------------------
model_phase1.ply                        147.3 MB     2026-01-28 10:23     1ABC123xyz456...
brain_segmentation.ply                  89.2 MB      2026-01-27 15:42     1DEF456abc789...
dataset_lidc_01.tar.gz                  2.1 GB       2026-01-26 08:15     1GHI789def012...
...
----------------------------------------------------------------------------------------------------
Total: 25 files, 15.73 GB
```

---

## 🔄 Integration with Existing Pipeline

### Update batch_cloud_segmentation.py

The system can automatically use Google Drive instead of DigitalOcean:

```python
# Old (DigitalOcean only)
--cloud-output "s3://my-medical-imaging/outputs/"

# New (Google Drive)
--cloud-output "gdrive://Dicom-3D-Medical-Imaging/"

# Both (upload to both)
--cloud-output "both"
```

### Automatic Upload After Processing

```bash
# Process and upload to Google Drive
python batch_cloud_segmentation.py \
  --local-dir data/sample_brain_ct/ \
  --organs brain \
  --upload-to gdrive
```

---

## 📋 Storage Organization

**Recommended folder structure in Google Drive:**

```
Dicom-3D-Medical-Imaging/
├── datasets/
│   ├── tcia/
│   │   ├── lung_TCGA-17-Z054/
│   │   ├── lidc_patient_01/
│   │   └── ...
│   ├── medical_decathlon/
│   │   ├── Task01_Brain/
│   │   ├── Task03_Liver/
│   │   └── ...
│   └── totalsegmentator/
│       ├── sample_001/
│       └── ...
├── outputs/
│   ├── brain_segmentations/
│   ├── full_anatomy_segmentations/
│   └── professional_phase1/
└── models/
    ├── baseline_quality_90/
    └── professional_quality_94/
```

**Create folders:**
```bash
python gdrive_create_folder.py "Dicom-3D-Medical-Imaging"
python gdrive_create_folder.py "datasets" --parent "Dicom-3D-Medical-Imaging"
python gdrive_create_folder.py "outputs" --parent "Dicom-3D-Medical-Imaging"
```

---

## 💡 Pro Tips

### 1. Use for Large Dataset Downloads

**Download Medical Decathlon directly to Google Drive:**
```bash
# Download to local
./download_medical_decathlon.sh

# Upload to Google Drive
for task in data/medical_decathlon/Task*; do
    tar -czf "${task}.tar.gz" "$task"
    python gdrive_upload.py "${task}.tar.gz" datasets/medical_decathlon
done

# Delete local copy (free up space)
rm -rf data/medical_decathlon/
```

### 2. Backup Critical Models

```bash
# Auto-backup after Phase 1
python batch_cloud_segmentation.py ... && \
python gdrive_upload.py output/phase1_result.ply models/phase1/
```

### 3. Share Results

```bash
# Upload and get shareable link
python gdrive_upload.py final_model.ply
# Link: https://drive.google.com/file/d/1ABC123xyz456.../view
```

### 4. Monitor Storage Usage

```bash
# Check storage status
python setup_google_drive.py test | grep "Storage"

# Expected:
# Total:     2000.0 GB
# Used:      458.3 GB (22.9%)
# Available: 1541.7 GB
```

### 5. Batch Operations

**Upload entire output directory:**
```bash
# Create tarball first
tar -czf output_$(date +%Y%m%d).tar.gz output/

# Upload
python gdrive_upload.py output_20260128.tar.gz backups/
```

---

## 🔐 Security Best Practices

1. **Keep credentials secure:**
   ```bash
   chmod 600 credentials.json
   chmod 600 token.pickle
   
   # Add to .gitignore
   echo "credentials.json" >> .gitignore
   echo "token.pickle" >> .gitignore
   ```

2. **Token expires:** Refresh automatically handled, but if issues:
   ```bash
   rm token.pickle
   python setup_google_drive.py authenticate
   ```

3. **Revoke access** (if needed):
   - Go to: https://myaccount.google.com/permissions
   - Find "Dicom-3D Medical Imaging"
   - Click "Remove Access"

---

## 🆚 When to Use What

| Use Case | Google Drive | DigitalOcean Spaces |
|----------|-------------|---------------------|
| **Large datasets (>100GB)** | ✅ Use Google Drive | ❌ Won't fit |
| **TotalSegmentator (300GB)** | ✅ Perfect | ❌ Too large |
| **Daily backups** | ✅ Free, unlimited | ⚠️ Counts against quota |
| **Public sharing** | ✅ Easy shareable links | ✅ Public URLs |
| **API automation** | ✅ Python scripts | ✅ AWS CLI |
| **Processing pipeline** | ⚠️ Download first | ✅ Direct S3 access |
| **Cost sensitivity** | ✅ $0 (free) | ⚠️ $5/month |

**Recommended Strategy:**
1. **Primary storage:** Google Drive (2TB, free)
2. **Processing cache:** /tmp auto-cleanup (fast local access)
3. **Workflow:**
   - Store datasets in Google Drive
   - Download to local for processing
   - Upload results to both (Google Drive for archive, DO for quick access)

---

## 🚀 Quick Start Recap

```bash
# 1. Install
python setup_google_drive.py install

# 2. Setup (download credentials.json first)
python setup_google_drive.py authenticate

# 3. Test
python setup_google_drive.py test

# 4. Use it!
python gdrive_upload.py output/model.ply
python gdrive_list.py
python gdrive_download.py model.ply
```

---

## 📊 Storage Capacity Planning

**What you can store in 2TB:**

| Dataset | Size | Quantity | Total |
|---------|------|----------|-------|
| Medical Decathlon | 50 GB | 1 | 50 GB |
| TotalSegmentator Full | 300 GB | 1 | 300 GB |
| LIDC-IDRI | 124 GB | 1 | 124 GB |
| AMOS2022 | 80 GB | 1 | 80 GB |
| CT-ORG | 25 GB | 1 | 25 GB |
| TCGA Datasets | ~100 GB | Various | 100 GB |
| Your Outputs | - | - | 200 GB |
| **Subtotal** | | | **879 GB** |
| **Remaining** | | | **1,121 GB (56%)** |

**You can store:**
- ✅ All recommended datasets (760 GB)
- ✅ All your processed outputs (100-200 GB)
- ✅ Multiple backup versions
- ✅ Still have 1TB+ free for future growth

---

## ❓ Troubleshooting

### "Authentication failed"
```bash
rm token.pickle credentials.json
# Re-download credentials.json from Google Cloud Console
python setup_google_drive.py authenticate
```

### "File not found"
```bash
# List files to get correct name/ID
python gdrive_list.py

# Use exact name or file ID
python gdrive_download.py "exact_file_name.ply"
```

### "Upload slow"
- Google Drive has rate limits
- Large files (>100MB) use resumable upload automatically
- Check internet connection

### "Quota exceeded"
```bash
# Check storage usage
python setup_google_drive.py test

# Delete old files if needed
python gdrive_list.py
# Manually delete via web interface: drive.google.com
```

---

## 🎯 Next Steps

1. ✅ Complete setup (15 minutes)
2. ✅ Upload your current models to Google Drive
3. ✅ Download Medical Decathlon to Google Drive (saves 50GB local space)
4. ✅ Process with Phase 1 upgrade, upload results
5. ✅ Scale up with TotalSegmentator (fits in your 2TB!)

**Start now:**
```bash
python setup_google_drive.py setup
```

Then follow authentication steps above!

---

**With 2TB Google Drive, you have 8x more capacity than before - use it to scale up your AI training! 🚀**
