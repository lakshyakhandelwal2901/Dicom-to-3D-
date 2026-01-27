# Medical Imaging Platform - Phase 1 Complete ✅

**Production-ready organ segmentation system for CT imaging**

## 📋 Overview

This is a modular, config-driven medical imaging platform for automated organ segmentation from DICOM CT scans. All segmentation logic is driven by YAML configuration files — no code changes needed to add new organs.

## 🗂️ Project Structure

```
medical_imaging_platform/
├── core/
│   ├── dicom_loader.py          # Load DICOM series → 3D volume
│   └── segmentation_engine.py   # Generic segmentation (config-driven)
├── profiles/                     # Organ configuration files
│   ├── brain.yaml               # Brain + skull
│   ├── liver.yaml               # Liver + vasculature
│   ├── lungs.yaml               # Lungs + airways
│   ├── heart.yaml               # Heart tissue
│   ├── kidneys.yaml             # Kidneys anatomy
│   ├── bones.yaml               # Skeletal system
│   ├── pancreas.yaml            # Pancreatic tissue
│   └── config_loader.py         # YAML loader & validator
├── main.py                       # CLI entry point
└── requirements.txt
```

## 🚀 Quick Start

### Installation

```bash
cd medical_imaging_platform
pip install -r requirements.txt
```

### List Available Organs

```bash
python main.py --list-profiles
```

### Segment an Organ

```bash
# Segment brain from DICOM folder
python main.py --organ brain --input /path/to/dicom/folder --output /output/path

# Segment liver
python main.py --organ liver --input /path/to/liver_ct --output output/liver

# Segment lungs
python main.py --organ lungs --input /path/to/chest_ct --output output/lungs
```

### Outputs

Each organ generates:
- `{organ}_{tissue}.stl` — 3D mesh for printing/CAD (binary format)
- `{organ}_{tissue}_colored.ply` — Colored mesh for visualization (Blender, MeshLab)

Example output for brain:
```
output/brain_segmentation/
├── brain_shell.stl              (skull/skin)
├── brain_shell_colored.ply
├── brain_brain.stl              (brain tissue)
└── brain_brain_colored.ply
```

## 📊 Available Organs (Phase 1)

| Organ | Tissues | Use Case |
|-------|---------|----------|
| **Brain** | Shell, Brain tissue | Neuro surgery planning |
| **Liver** | Liver, Vasculature | Hepatic tumor analysis |
| **Lungs** | Lung tissue, Airways | Pulmonary disease detection |
| **Heart** | Myocardium, Chambers | Cardiac pathology |
| **Kidneys** | Cortex, Medulla | Renal assessment |
| **Bones** | Cortical, Trabecular | Fracture analysis, orthopedics |
| **Pancreas** | Tissue, Ducts | Pancreatic tumor detection |

## ⚙️ How It Works

### 1. **Configuration-Driven**
Each organ has a YAML file defining:
- **Tissues**: HU ranges, colors, names
- **Preprocessing**: Resampling, denoising
- **Morphology**: Closing radius, dilation, erosion
- **Mesh**: Smoothing, decimation parameters

### 2. **Processing Pipeline**

```
DICOM Files
    ↓
Load 3D Volume
    ↓
Preprocess (resample to 1mm isotropic, denoise)
    ↓
Create Body Mask (remove air)
    ↓
For each Tissue:
  - Threshold by HU range
  - Apply morphological operations
  - Extract largest component
  - Create mesh via marching cubes
    ↓
Smooth (Laplacian filter)
    ↓
Decimate (reduce faces for performance)
    ↓
Export STL + PLY
```

### 3. **Extensible**
To add new organ:
1. Create `profiles/organ_name.yaml`
2. Define tissues with HU ranges
3. Run: `python main.py --organ organ_name --input DICOM_folder --output output`

## 🎨 Tissue Colors

Colors are automatically applied to tissues based on profile:
- **Brain**: Brown (tissue), light gray (skull)
- **Liver**: Brown (tissue), crimson (blood vessels)
- **Lungs**: Red (tissue), blue (airways)
- **Heart**: Pink (muscle), crimson (chambers)
- **Kidneys**: Red (cortex), orange (medulla)
- **Bones**: Gray (cortical), beige (trabecular)
- **Pancreas**: Orange (tissue), gold (ducts)

## 📈 Next Phases

### Phase 2: AI/ML Segmentation
- Replace HU thresholding with neural networks
- Use pre-trained models (MONAI, nnU-Net)
- Support MRI in addition to CT

### Phase 3: 3D Slicer Integration
- Reverse-engineer Segment Editor effects
- Full effect library as Python module
- Interactive UI

### Phase 4: AR/VR Interface
- Real-time 3D manipulation
- Interactive annotation tools
- Cloud-based processing

## 🔧 Technical Details

### Hounsfield Unit (HU) Ranges

| Tissue | HU Range | Notes |
|--------|----------|-------|
| Air | -1000 | Outside body |
| Lungs | -500 to -100 | Very low density |
| Fat | -100 to -50 | Soft tissue |
| Brain/Organs | 30-100 | Main soft tissue |
| Blood | 100-200 | Vessels, chambers |
| Cortical Bone | 300-2000+ | Dense |
| Metal | >3000 | Artifact region |

### Parameters (Customizable)

- **target_spacing_mm**: Resample volume to isotropic voxels
- **closing_radius**: Voxels for morphological closing (connectivity)
- **dilation_iterations**: Fill gaps before closing
- **laplacian_smoothing_iterations**: Mesh smoothness
- **decimation_target**: Fraction of faces to keep (0.7 = 30% reduction)

## 📚 Example Workflows

### 1. Prepare Brain for 3D Printing

```bash
python main.py --organ brain --input ct_data/brain --output 3d_print/brain
# Open output/brain_brain.stl in Cura
```

### 2. Visualize Tumor Location

```bash
python main.py --organ liver --input ct_data/liver --output analysis/liver
# Open output/liver_liver_colored.ply in Blender
```

### 3. Analyze Bone Fracture

```bash
python main.py --organ bones --input ct_data/leg --output orthopedic/leg
# Examine both cortical and trabecular bone
```

## 🐛 Troubleshooting

**Issue**: No tissues extracted
- **Solution**: Verify DICOM files are valid CT scans

**Issue**: Mesh has holes
- **Solution**: Increase `closing_radius` in YAML

**Issue**: Surface is noisy
- **Solution**: Increase `laplacian_smoothing_iterations`

**Issue**: Very large output files
- **Solution**: Decrease `decimation_target` (e.g., 0.5 instead of 0.8)

## 📄 License

[Your License Here]

## 🤝 Contributing

To add a new organ:
1. Research typical HU ranges for tissues
2. Create new YAML in `profiles/`
3. Test with sample DICOM
4. Submit PR with documentation

---

**Status**: Phase 1 Complete ✅
**Next**: Phase 2 - AI/ML Integration
