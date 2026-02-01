#!/bin/bash
# Universal setup - works from any directory/location
# Initializes project regardless of current working directory

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "📍 Project Root: $PROJECT_ROOT"
echo "🔧 Setting up adaptive project paths..."
echo ""

# Navigate to project root
cd "$PROJECT_ROOT"

# Create necessary directories
mkdir -p output data src logs

echo "✅ Directories created"
echo ""

# Check Python version
python3 --version
echo ""

# Install dependencies if needed
echo "📦 Checking Python dependencies..."
python3 -c "import google.auth" 2>/dev/null || {
    echo "⚠️  Installing Google Drive dependencies..."
    pip install -q google-auth-oauthlib google-auth-httplib2 google-api-python-client
}

echo "✅ Dependencies ready"
echo ""

# Verify credentials
if [ ! -f "$PROJECT_ROOT/credentials.json" ]; then
    echo "⚠️  credentials.json not found"
    echo "   Run: python3 setup_google_drive.py authenticate"
else
    echo "✅ Google Drive credentials found"
fi

if [ ! -f "$PROJECT_ROOT/token.pickle" ]; then
    echo "⚠️  token.pickle not found (not yet authenticated)"
    echo "   Run: python3 setup_google_drive.py authenticate"
else
    echo "✅ Google Drive token found"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ Project is ready to clone and use from any location!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📁 Project structure:"
echo "   $PROJECT_ROOT/"
echo "   ├── gdrive_*.py         (Google Drive utilities)"
echo "   ├── batch_cloud_segmentation.py"
echo "   ├── path_utils.py       (Adaptive path handling)"
echo "   ├── lean_gdrive_download.sh"
echo "   ├── output/             (Results)"
echo "   ├── data/               (Input datasets)"
echo "   └── src/                (Source code)"
echo ""
echo "Next steps:"
echo "  1. Run this script from project root: bash setup_project.sh"
echo "  2. Or just start using: python3 gdrive_list.py"
echo ""
