# 🚀 Universal Project Setup Guide

## Clone & Setup (Any Location)

### Step 1: Clone the Repository
```bash
# Works from ANY directory
git clone https://github.com/lakshyakhandelwal2901/Dicom-to-3D-.git
cd Dicom-to-3D-
```

### Step 2: Run Universal Setup
```bash
# Works from project directory (or called from anywhere)
bash setup_project.sh
```

Or run from anywhere:
```bash
bash /path/to/Dicom-to-3D-/setup_project.sh
```

## Adaptive Path System

All scripts now use **automatic path detection**:

### How It Works

1. **Python Scripts** (`gdrive_*.py`, `batch_cloud_segmentation.py`):
   ```python
   from path_utils import ensure_in_project, get_project_root
   
   # Automatically detects project location
   ensure_in_project()  # Navigate to project root if needed
   root = get_project_root()  # Get absolute project path
   ```

2. **Shell Scripts** (`.sh` files):
   ```bash
   # Detects script location = project root
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   PROJECT_ROOT="$SCRIPT_DIR"
   cd "$PROJECT_ROOT"
   ```

### Why This Works

- ✅ No hardcoded `/workspaces/` paths
- ✅ No hardcoded absolute paths
- ✅ Works from any directory
- ✅ Works from any drive/mount point
- ✅ Works on Linux, macOS, Windows (WSL)

## Usage Examples

### Example 1: Run from Project Directory
```bash
cd ~/projects/Dicom-to-3D-
python3 gdrive_list.py datasets
```

### Example 2: Run from Anywhere (Python)
```bash
cd /home/user/something-else/
python3 ~/projects/Dicom-to-3D-/gdrive_list.py datasets
# Automatically navigates to project root
```

### Example 3: Run Shell Script from Anywhere
```bash
bash /full/path/to/Dicom-to-3D-/lean_gdrive_download.sh
# Automatically detects project root from script location
```

### Example 4: Nested Calls Work
```bash
cd /anywhere/
python3 /path/to/batch_cloud_segmentation.py \
  --cloud-input "datasets/medical_decathlon" \
  --organs "full_anatomy"
# Calls internal gdrive_upload.py with correct paths
```

## Available Paths (Adaptive)

All these are automatically detected and work from any location:

```python
from path_utils import *

get_project_root()        # /wherever/Dicom-to-3D-
get_token_path()          # /wherever/Dicom-to-3D-/token.pickle
get_credentials_path()    # /wherever/Dicom-to-3D-/credentials.json
get_src_dir()            # /wherever/Dicom-to-3D-/src (if exists)
get_data_dir()           # /wherever/Dicom-to-3D-/data
get_output_dir()         # /wherever/Dicom-to-3D-/output
```

## Installation on Different Systems

### Linux/macOS
```bash
# Clone
git clone https://github.com/lakshyakhandelwal2901/Dicom-to-3D-.git
cd Dicom-to-3D-

# Setup
bash setup_project.sh

# Use
python3 gdrive_list.py
python3 gdrive_upload.py /path/to/file results/
```

### Windows (WSL)
```bash
# Same as Linux
wsl
git clone https://github.com/lakshyakhandelwal2901/Dicom-to-3D-.git
cd Dicom-to-3D-
bash setup_project.sh
```

### Docker
```bash
docker run -v /path/to/Dicom-to-3D-:/project python:3.10
cd /project
bash setup_project.sh
python3 gdrive_list.py
```

## Directory Structure (Works from Anywhere)

```
/wherever/you/clone/Dicom-to-3D-/
├── path_utils.py              ← Magic happens here!
├── setup_project.sh           ← Universal setup
├── gdrive_list.py             ← Auto-detects project root
├── gdrive_upload.py           ← Auto-detects project root
├── gdrive_download.py         ← Auto-detects project root
├── lean_gdrive_download.sh    ← Auto-detects project root
├── batch_cloud_segmentation.py ← Auto-detects project root
├── output/                    ← Auto-created if missing
├── data/                      ← Auto-created if missing
└── src/                       ← Auto-added to Python path
```

## What Makes It Universal

### Before (Hardcoded Paths)
```bash
cd /workspaces/Dicom-to-3D-     # ❌ Only works from this exact location
python3 gdrive_upload.py ...    # ❌ Fails if run from elsewhere
```

### After (Adaptive Paths)
```bash
cd /anywhere/                   # ✅ Any location
python3 /path/to/gdrive_upload.py ...  # ✅ Auto-detects project
# Automatically:
# 1. Finds project root
# 2. Loads credentials from correct location
# 3. Sets working directory
# 4. Runs successfully
```

## Testing Adaptive Paths

```bash
# Test 1: Run from project directory
cd ~/Dicom-to-3D-
python3 gdrive_list.py
# ✅ Should work

# Test 2: Run from different directory
cd /tmp
python3 ~/Dicom-to-3D-/gdrive_list.py
# ✅ Should work (auto-navigates to project)

# Test 3: Run shell script from anywhere
bash ~/Dicom-to-3D-/lean_gdrive_download.sh
# ✅ Should work (script detects its own location)

# Test 4: Nested script calls
cd /var
python3 ~/Dicom-to-3D-/batch_cloud_segmentation.py \
  --cloud-input "datasets/medical_decathlon"
# ✅ Should work (calls other scripts correctly)
```

## Troubleshooting

### Issue: "token.pickle not found"
**Solution:** Run from project root or ensure credentials are set
```bash
cd /path/to/Dicom-to-3D-
python3 setup_google_drive.py authenticate
```

### Issue: "Module not found"
**Solution:** Ensure you're in project directory
```bash
cd /path/to/Dicom-to-3D-
python3 gdrive_list.py
```

### Issue: Permission denied on shell script
**Solution:** Make it executable
```bash
chmod +x /path/to/Dicom-to-3D-/*.sh
```

## Moving the Project

The project can be moved or relocated:

```bash
# No reconfiguration needed!
mv ~/Dicom-to-3D- ~/new/location/Dicom-to-3D-
cd ~/new/location/Dicom-to-3D-
python3 gdrive_list.py
# ✅ Works perfectly (paths auto-adapt)
```

## Summary

✅ Clone from anywhere  
✅ Run scripts from anywhere  
✅ Move project without reconfiguring  
✅ Works on any OS (Linux, macOS, Windows/WSL)  
✅ No hardcoded paths  
✅ Automatic credential loading  
✅ Auto-directory detection  

**The project is now truly universal!**
