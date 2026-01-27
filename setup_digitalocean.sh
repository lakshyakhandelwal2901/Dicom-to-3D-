#!/bin/bash
# DigitalOcean Spaces Quick Setup for GitHub Students

echo "🚀 DigitalOcean Spaces Setup (GitHub Student Pack)"
echo "=================================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "📦 Installing AWS CLI..."
    pip install awscli
fi

echo "✓ AWS CLI ready"
echo ""

echo "📝 Next steps:"
echo ""
echo "1. Create Spaces bucket:"
echo "   → https://cloud.digitalocean.com/spaces"
echo "   → Click 'Create a Spaces Bucket'"
echo "   → Choose region (nyc3 recommended)"
echo "   → Name: my-medical-imaging (globally unique)"
echo ""

echo "2. Get API credentials:"
echo "   → https://cloud.digitalocean.com/account/api/tokens"
echo "   → 'Spaces Keys' tab"
echo "   → 'Generate New Key'"
echo "   → Copy Access Key and Secret Key"
echo ""

echo "3. Configure AWS CLI:"
read -p "Press Enter to configure AWS CLI for DigitalOcean..."
echo ""

aws configure --profile digitalocean
# User will be prompted for:
# - Access Key ID
# - Secret Access Key
# - Region (should match Spaces bucket region, e.g., nyc3)
# - Output format (json)

echo ""
echo "4. Create cloud_config.json:"
read -p "Enter your Spaces bucket name: " bucket_name
read -p "Enter your Spaces region (e.g., nyc3, sfo3, ams3): " region

cat > medical_imaging_platform/cloud_config.json << EOF
{
  "s3": {
    "bucket": "$bucket_name",
    "region": "$region",
    "endpoint_url": "https://${region}.digitaloceanspaces.com",
    "profile": "digitalocean"
  }
}
EOF

echo "✓ Created cloud_config.json"
echo ""

echo "5. Test upload:"
echo ""
echo "   python3 medical_imaging_platform/core/cloud_storage.py upload \\"
echo "     --provider s3 \\"
echo "     --local README.md \\"
echo "     --remote s3://$bucket_name/test/README.md"
echo ""

echo "✅ Setup complete! You have:"
echo "   - 250 GB storage"
echo "   - 1 TB monthly transfer"
echo "   - \$200 credit = 40 months free"
echo ""
echo "📚 See CLOUD_STORAGE_SETUP.md for usage examples"
