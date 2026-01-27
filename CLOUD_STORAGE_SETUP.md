# Cloud Storage Setup Guide

Store DICOM datasets and 3D outputs in the cloud to save local disk space.

## Providers Supported
- **DigitalOcean Spaces** (250 GB with GitHub Student Pack - BEST for students!)
- **AWS S3** (recommended for non-students, 5 GB free tier)
- **Google Cloud Storage** (5 GB free tier)
- **Azure Blob Storage** (5 GB free tier)

---

## Quick Setup

### 1. DigitalOcean Spaces (RECOMMENDED for GitHub Students)

**GitHub Student Pack**: $200 credit = **40 months of 250 GB storage** (BEST DEAL!)

**Setup:**
```bash
# Install AWS CLI (DO Spaces uses S3-compatible API)
pip install awscli

# Create Spaces bucket via web UI
# 1. Go to https://cloud.digitalocean.com/spaces
# 2. Click "Create a Spaces Bucket"
# 3. Choose region: nyc3, sfo3, ams3, sgp1, fra1
# 4. Name: my-medical-imaging (must be globally unique)
# 5. Enable CDN (optional, for faster downloads)
# 6. Create

# Get API credentials
# 1. https://cloud.digitalocean.com/account/api/tokens
# 2. "Spaces Keys" tab → "Generate New Key"
# 3. Copy Access Key and Secret Key

# Configure AWS CLI for DigitalOcean
aws configure --profile digitalocean
# Access Key ID: DO00Q7YAUR2E2U8YAQLB
# Secret Access Key: XtaKjWILUKtkrYjSL8yJxj8yamQ8LMBzHYYxBMAAHdw
# Region: SGP1 (match your bucket region)
# Output: json
```

**Update cloud_config.json:**
```json
{
  "s3": {
    "bucket": "my-medical-imaging",
    "region": "nyc3",
    "profile": "digitalocean"
  }
}
```

**Usage (same S3 commands with endpoint override):**
```bash
# Upload outputs
AWS_PROFILE=digitalocean aws s3 cp output/lidc_phase1_lungs \
  s3://my-medical-imaging/outputs/lidc_phase1_lungs \
  --recursive \
  --endpoint-url https://nyc3.digitaloceanspaces.com

# Or use our script (modify to add --endpoint-url)
python3 medical_imaging_platform/core/cloud_storage.py upload \
  --provider s3 \
  --local output/lidc_phase1_lungs \
  --remote s3://my-medical-imaging/outputs/lidc_phase1_lungs \
  --recursive
```

**Capacity with $200 credit:**
- 250 GB storage × 40 months = **10 TB-months total**
- **4,000+ lung segmentation outputs** (61 MB each)
- **900+ brain segmentation outputs** (280 MB each)
- **14,000+ raw CT series** (17 MB each)

**After credit expires:** $5/month for 250 GB storage + 1 TB transfer (still cheaper than AWS)

---

### 2. AWS S3 (Recommended for non-students)

**Free Tier**: 5 GB storage, 20K GET requests, 2K PUT requests/month (12 months)

**Setup:**
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)

# Create bucket
aws s3 mb s3://my-medical-imaging-data --region us-east-1

# Update cloud_config.json
cp medical_imaging_platform/cloud_config.json.example medical_imaging_platform/cloud_config.json
# Edit bucket name in cloud_config.json
```

**Get AWS Credentials:**
1. Go to https://console.aws.amazon.com/
2. IAM → Users → Create User → Attach Policy: `AmazonS3FullAccess`
3. Security Credentials → Create Access Key
4. Copy Access Key ID and Secret Access Key

---

### 2. Google Cloud Storage

**Free Tier**: 5 GB storage, 5K Class A operations, 50K Class B operations/month

**Setup:**
```bash
# Install gsutil
pip install google-cloud-storage

# Authenticate
gcloud auth login

# Create bucket
gsutil mb gs://my-medical-imaging-data

# Update cloud_config.json with bucket and project_id
```

**Get GCS Credentials:**
1. Go to https://console.cloud.google.com/
2. Create project → Enable Cloud Storage API
3. IAM → Service Account → Create → Grant Storage Admin role
4. Create JSON key → Download
5. Export: `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`

---

### 3. Azure Blob Storage

**Free Tier**: 5 GB LRS storage, 20K read operations, 10K write operations/month (12 months)

**Setup:**
```bash
# Install Azure CLI
pip install azure-cli

# Login
az login

# Create storage account
az storage account create --name mymedicalimaging --resource-group myResourceGroup --location eastus

# Get connection string
az storage account show-connection-string --name mymedicalimaging

# Update cloud_config.json with account_name and container
```

---

## Usage Examples

### Upload Dataset
```bash
# Upload DICOM folder to S3
python3 medical_imaging_platform/core/cloud_storage.py upload \
  --provider s3 \
  --local data/lidc_sample_ct \
  --remote s3://my-medical-imaging-data/datasets/lidc_sample_ct \
  --recursive

# Upload outputs
python3 medical_imaging_platform/core/cloud_storage.py upload \
  --provider s3 \
  --local output/lidc_phase1_lungs \
  --remote s3://my-medical-imaging-data/outputs/lidc_phase1_lungs \
  --recursive
```

### Download Dataset
```bash
# Download from S3
python3 medical_imaging_platform/core/cloud_storage.py download \
  --provider s3 \
  --remote s3://my-medical-imaging-data/datasets/lidc_sample_ct \
  --local data/lidc_sample_ct \
  --recursive
```

### List Files
```bash
# List all datasets
python3 medical_imaging_platform/core/cloud_storage.py list \
  --provider s3 \
  --remote s3://my-medical-imaging-data/datasets/
```

### Delete (Free up cloud space)
```bash
# Delete old outputs
python3 medical_imaging_platform/core/cloud_storage.py delete \
  --provider s3 \
  --remote s3://my-medical-imaging-data/outputs/old_run \
  --recursive
```

---

## Integrated Workflow

### 1. Upload local data to cloud (after processing)
```bash
cd medical_imaging_platform

# Process locally
python3 main.py --organ lungs --input ../data/lidc_sample_ct --output ../output/lidc_lungs

# Upload outputs to cloud
python3 core/cloud_storage.py upload \
  --provider s3 \
  --local ../output/lidc_lungs \
  --remote s3://my-medical-imaging-data/outputs/lidc_lungs \
  --recursive

# Delete local outputs to save space
rm -rf ../output/lidc_lungs
```

### 2. Download when needed
```bash
# Download specific output for visualization
python3 core/cloud_storage.py download \
  --provider s3 \
  --remote s3://my-medical-imaging-data/outputs/lidc_lungs/lungs_lung_tissue.stl \
  --local ../output/lungs_lung_tissue.stl
```

---

## Cost Optimization

### Keep Local (Fast Access)
- Input DICOM during active processing
- Current working outputs

### Store in Cloud (Archive)
- Completed outputs (.stl, .ply files)
- Raw datasets not currently in use
- Backup of processed results

### Free Tier Limits (Monthly)
- **S3**: 5 GB storage, good for ~50-100 CT series outputs
- **GCS**: 5 GB storage, same capacity
- **Azure**: 5 GB storage, same capacity

### Example Storage Sizes
- LIDC chest CT (133 slices): ~17 MB raw DICOM
- Lung segmentation outputs: ~61 MB (4 files)
- Brain segmentation outputs: ~280 MB (4 files)

**Estimate**: With 5 GB free tier, you can store:
- ~80 lung segmentation results
- ~18 brain segmentation results
- Or mix: 50 lung + 200 CT series (raw DICOM)

---

## Security Best Practices

1. **Never commit credentials** to git
   - Add `cloud_config.json` to `.gitignore`
   - Use environment variables or IAM roles

2. **Use least-privilege access**
   - Create separate IAM users for upload/download
   - Restrict bucket access to specific IPs if possible

3. **Enable encryption**
   - S3: Enable SSE-S3 or SSE-KMS
   - GCS: Enabled by default
   - Azure: Enable encryption at rest

4. **Set lifecycle policies** (auto-delete old data)
   ```bash
   # S3 example: Delete objects older than 90 days
   aws s3api put-bucket-lifecycle-configuration \
     --bucket my-medical-imaging-data \
     --lifecycle-configuration file://lifecycle.json
   ```

---

## Troubleshooting

### "AccessDenied" or "Unauthorized"
- Check credentials: `aws s3 ls` (S3), `gsutil ls` (GCS), `az storage account list` (Azure)
- Verify IAM permissions: Storage Admin/Full Access role
- Check bucket region matches config

### "Bucket not found"
- Create bucket first: `aws s3 mb s3://bucket-name`
- Verify bucket name (must be globally unique)

### Slow uploads/downloads
- Use `--recursive` for directories (parallel transfers)
- Consider compressing large folders: `tar -czf data.tar.gz data/`
- Upgrade to paid tier for faster transfer speeds

---

## Next Steps

1. Choose provider (S3 recommended for simplicity)
2. Create account and get free tier
3. Configure credentials
4. Create bucket
5. Update `cloud_config.json`
6. Test with small file: `python3 core/cloud_storage.py upload --local README.md --remote s3://bucket/test.md`

---

**Recommended Workflow:**
- Process locally → Upload outputs to cloud → Delete local outputs → Keep cloud archive
- Download only when needed for visualization or further processing
