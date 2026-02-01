# 🎯 Quick Start - Clone & Run Anywhere

## Clone the Project
```bash
git clone https://github.com/lakshyakhandelwal2901/Dicom-to-3D-.git
cd Dicom-to-3D-
```

## Universal Setup (Any Location)
```bash
bash setup_project.sh
```

That's it! The project now:
- ✅ Auto-detects its location
- ✅ Loads credentials from correct path
- ✅ Works from any directory
- ✅ Works on any OS (Linux, macOS, WSL)
- ✅ No hardcoded paths

## Basic Commands (Work from Anywhere)

### List Google Drive Files
```bash
python3 gdrive_list.py datasets
python3 gdrive_list.py results
```

### Download from Google Drive
```bash
python3 gdrive_download.py "datasets/medical_decathlon/Task06_Lung" data/
```

### Upload to Google Drive
```bash
python3 gdrive_upload.py output/brain_model results/
```

### Batch Segmentation
```bash
python3 batch_cloud_segmentation.py \
  --cloud-input "datasets/medical_decathlon/Task06_Lung" \
  --organs "full_anatomy"
```

### Start Dataset Download
```bash
bash lean_gdrive_download.sh
```

## Run from Any Directory

Before:
```bash
cd /workspaces/Dicom-to-3D-  # ❌ Required exact path
python3 gdrive_list.py
```

After:
```bash
cd /anywhere/                 # ✅ Any directory
python3 ~/Dicom-to-3D-/gdrive_list.py
# Automatically navigates to project root!
```

## Project Structure

```
Dicom-to-3D-/
├── path_utils.py           ← Magic path detection
├── setup_project.sh        ← Universal setup
├── gdrive_*.py             ← Work from anywhere
├── batch_cloud_segmentation.py
├── lean_gdrive_download.sh
├── output/                 ← Results
├── data/                   ← Datasets
├── src/                    ← Source code
└── (all other files)
```

## Troubleshooting

**Q: Command not found**
```bash
# Solution: Add project to PATH or use full path
python3 /path/to/Dicom-to-3D-/gdrive_list.py
```

**Q: token.pickle not found**
```bash
# Solution: Authenticate first
cd /path/to/Dicom-to-3D-
python3 setup_google_drive.py authenticate
```

**Q: Permission denied on .sh files**
```bash
# Solution: Make executable
chmod +x /path/to/*.sh
bash /path/to/lean_gdrive_download.sh
```

## Moving the Project

No reconfiguration needed:
```bash
mv ~/Dicom-to-3D- /new/location/
cd /new/location/Dicom-to-3D-
python3 gdrive_list.py
# ✅ Works perfectly!
```

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Clone | ✅ Any location | ✅ Any location |
| Run | ❌ Specific dir only | ✅ Any directory |
| Move | ❌ Requires reconfigure | ✅ Just move & go |
| Paths | ❌ Hardcoded | ✅ Adaptive |
| Setup | ❌ Manual | ✅ Automatic |

**The project is now truly universal and portable!**

For detailed guide: See [UNIVERSAL_SETUP_GUIDE.md](UNIVERSAL_SETUP_GUIDE.md)
