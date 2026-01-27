#!/bin/bash
# Quick commands for DigitalOcean Spaces management

BUCKET="my-medical-imaging"
ENDPOINT="https://sgp1.digitaloceanspaces.com"

echo "DigitalOcean Spaces Manager"
echo "==========================="
echo "Bucket: $BUCKET (SGP1 region)"
echo ""

case "$1" in
  upload)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: ./do_spaces.sh upload <local_path> <remote_path>"
      echo "Example: ./do_spaces.sh upload output/results s3://$BUCKET/outputs/results"
      exit 1
    fi
    python3 medical_imaging_platform/core/cloud_storage.py upload \
      --provider s3 \
      --local "$2" \
      --remote "$3" \
      --recursive
    ;;
    
  download)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: ./do_spaces.sh download <remote_path> <local_path>"
      echo "Example: ./do_spaces.sh download s3://$BUCKET/outputs/results output/results"
      exit 1
    fi
    python3 medical_imaging_platform/core/cloud_storage.py download \
      --provider s3 \
      --remote "$2" \
      --local "$3" \
      --recursive
    ;;
    
  list)
    REMOTE_PATH="${2:-s3://$BUCKET/}"
    echo "Listing: $REMOTE_PATH"
    python3 medical_imaging_platform/core/cloud_storage.py list \
      --provider s3 \
      --remote "$REMOTE_PATH"
    ;;
    
  usage)
    echo "Storage usage:"
    AWS_PROFILE=digitalocean aws s3 ls s3://$BUCKET/ \
      --recursive --human-readable --summarize \
      --endpoint-url $ENDPOINT | tail -5
    echo ""
    echo "Remaining free space: $(echo "250*1024 - 399" | bc) MiB / 250 GiB"
    ;;
    
  delete)
    if [ -z "$2" ]; then
      echo "Usage: ./do_spaces.sh delete <remote_path>"
      echo "Example: ./do_spaces.sh delete s3://$BUCKET/outputs/old_results"
      exit 1
    fi
    python3 medical_imaging_platform/core/cloud_storage.py delete \
      --provider s3 \
      --remote "$2" \
      --recursive
    ;;
    
  *)
    echo "Usage: ./do_spaces.sh {upload|download|list|usage|delete} [args]"
    echo ""
    echo "Commands:"
    echo "  upload <local> <remote>   - Upload files/folders"
    echo "  download <remote> <local> - Download files/folders"
    echo "  list [path]               - List files (default: all)"
    echo "  usage                     - Show storage usage"
    echo "  delete <remote>           - Delete files/folders"
    echo ""
    echo "Examples:"
    echo "  ./do_spaces.sh upload output/lungs s3://$BUCKET/outputs/lungs"
    echo "  ./do_spaces.sh list s3://$BUCKET/outputs/"
    echo "  ./do_spaces.sh usage"
    echo "  ./do_spaces.sh download s3://$BUCKET/outputs/lungs/lung.stl output/lung.stl"
    exit 1
    ;;
esac
