# Project Architecture & Technical Overview

**Phase**: 1 Complete, Phase 2 Starting  
**Date**: Jan 2026  
**Status**: Production-Ready Foundation + AI Integration Planned

---

## 🏗️ Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  main.py (CLI) with flags: --organ, --input, --output, --model  │
└────────────────────────┬────────────────────────────────────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
┌─────────────┐   ┌──────────────┐   ┌────────────────────┐
│Config Loader│   │DICOM Loader  │   │Model Selector      │
│(YAML parse) │   │(HU convert)  │   │(HU vs TotalSeg)    │
└──────┬──────┘   └──────┬───────┘   └────────┬───────────┘
       │                 │                    │
       └─────────────────┼────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │ Segmentation Engine          │
          │ (Config-Driven)              │
          │                              │
          │ ├─ HU-based path (Phase 1)   │
          │ ├─ TotalSegmentator (Phase2A)│
          │ ├─ MONAI (Phase 2B)          │
          │ └─ nnU-Net (Phase 2C)        │
          └──────────────┬───────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌────────────┐   ┌──────────────┐   ┌──────────────┐
│Thresholding│   │Morphological │   │Mesh Gen      │
│(HU-based)  │   │Ops           │   │(Marching Cubes)
└────────────┘   ├─ Dilation   │   └──────┬───────┘
                 ├─ Erosion    │          │
                 ├─ Closing    │          ▼
                 ├─ Fill Holes │   ┌───────────────┐
                 └─ Median     │   │Mesh Processing│
                               │   │├─ Laplacian   │
                               │   │└─ Decimate    │
                               │   └───────┬───────┘
                               │           │
                               └───────────┼───────────┐
                                           │           │
                                           ▼           ▼
                                       ┌─────────┐ ┌──────────┐
                                       │STL File │ │PLY File  │
                                       │(Binary) │ │(Colored) │
                                       └─────────┘ └──────────┘
```

---

## 📁 Phase 1 - Current Production Structure

### Directory Layout

```
medical_imaging_platform/
│
├── core/
│   ├── __init__.py
│   ├── dicom_loader.py          ✅ COMPLETE - Load DICOM → 3D volume
│   │   ├── load_dicom_series()
│   │   ├── normalize_to_hu()
│   │   └── resample_volume()
│   │
│   ├── segmentation_engine.py   ✅ COMPLETE - Generic config-driven engine
│   │   ├── __init__(config)
│   │   ├── process()            Main entry point
│   │   └── segment_tissue()
│   │
│   └── [NEW - Phase 2] model_loader.py
│       ├── load_model()
│       ├── segment_with_totalseg()
│       └── segment_with_monai()
│
├── profiles/
│   ├── __init__.py
│   ├── config_loader.py         ✅ COMPLETE - Parse YAML configs
│   │   ├── load(organ_name)
│   │   ├── list_available()
│   │   └── validate_config()
│   │
│   ├── brain.yaml               ✅ (HU: shell 120-3000, brain 0-150)
│   ├── liver.yaml               ✅ (HU: tissue 40-100, vessels 100-200)
│   ├── lungs.yaml               ✅ (HU: tissue -500 to -100, airways -1000 to -600)
│   ├── heart.yaml               ✅ (HU: myocardium 40-120, chambers 100-200)
│   ├── kidneys.yaml             ✅ (HU: cortex 40-80, medulla 30-50)
│   ├── bones.yaml               ✅ (HU: cortical 300-1500, trabecular 100-400)
│   ├── pancreas.yaml            ✅ (HU: tissue 35-90, ducts -10 to 30)
│   │
│   └── [NEW - Phase 2] 
│       ├── brain_totalseg.yaml  (model_type: totalSegmentator)
│       └── pancreas_nnunet.yaml (model_type: nnunet with fine-tuning)
│
├── main.py                      ✅ COMPLETE - CLI entry point
│   ├── --organ ORGAN_NAME
│   ├── --input DICOM_FOLDER
│   ├── --output OUTPUT_FOLDER
│   ├── --list-profiles
│   └── [NEW] --model hu_based|totalSegmentator|monai|nnunet
│
├── requirements.txt             ✅ COMPLETE
│   └── [NEW] + totalsegmentator, torch, nnunet
│
└── output/                      (Generated outputs)
    └── brain_segmentation/
        ├── brain_shell.stl
        ├── brain_shell_colored.ply
        ├── brain_brain.stl
        └── brain_brain_colored.ply
```

---

## 🧮 Phase 2A - TotalSegmentator Integration

### Implementation Plan

**File**: `core/model_loader.py` (NEW)

```python
from totalsegmentator.python_api import totalsegmentator
from trimesh import Trimesh

class PreTrainedModelLoader:
    def __init__(self, model_type="totalSegmentator"):
        self.model_type = model_type
        
    def segment(self, volume, config):
        """
        Args:
            volume: 3D numpy array (HU values)
            config: Organ config dict from YAML
        
        Returns:
            segmentations: dict of {tissue_name: binary_mask}
        """
        if self.model_type == "totalSegmentator":
            return self._segment_totalSegmentator(volume, config)
        elif self.model_type == "monai":
            return self._segment_monai(volume, config)
        # ... etc
    
    def _segment_totalSegmentator(self, volume, config):
        # Call TotalSegmentator API
        # Return dict of tissue masks
        pass
```

**Config Example** (`profiles/brain.yaml`):
```yaml
organ: Brain
model_type: totalSegmentator      # ← NEW FIELD

tissues:
  - name: brain
    description: Brain tissue
    color: [139, 69, 19]
    # No HU range needed (model handles it)
    
  - name: shell
    description: Skull
    color: [211, 211, 211]
```

**Integration in segmentation_engine.py**:
```python
def __init__(self, config):
    self.config = config
    self.model_type = config.get("model_type", "hu_based")
    
    if self.model_type == "hu_based":
        self.segmentation_fn = self._segment_hu_based
    elif self.model_type == "totalSegmentator":
        self.model_loader = PreTrainedModelLoader("totalSegmentator")
        self.segmentation_fn = self.model_loader.segment
```

---

## 📊 Phase 2B - Data Collection & Organization

### Data Directory Structure

```
data/datasets/
├── medical_segmentation_decathlon/
│   ├── Task01_Brain/
│   │   ├── imagesTr/
│   │   │   ├── br_000.nii.gz
│   │   │   └── ... (484 training scans)
│   │   ├── labelsTr/
│   │   │   ├── br_000.nii.gz
│   │   │   └── ... (484 masks)
│   │   └── imagesTs/ (100 test scans)
│   │
│   ├── Task03_Liver/
│   ├── Task05_Pancreas/
│   ├── Task07_Lungs/
│   └── Task10_Kidney/
│
├── lits_liver/
│   ├── training/
│   │   ├── volume-*.nii
│   │   └── segmentation-*.nii
│   └── testing/
│
├── kits_kidney/
│   ├── data/
│   │   ├── case_00000/
│   │   │   ├── imaging.nii.gz
│   │   │   └── segmentation.nii.gz
│   │   └── ... (300 cases)
│
├── chaos_multimodal/
├── synapse_validation/
│
├── custom_institutional/
│   ├── unlabeled/
│   │   └── scan_*/  (DICOM folders)
│   └── annotated/
│       └── scan_*/  (With manual annotations)
│
└── dataset_inventory.csv
    (Track all sources, sizes, quality metrics)
```

---

## 🧠 Phase 2C - Fine-Tuning Architecture

### nnU-Net Integration Path

```python
# core/nnunet_wrapper.py

from nnunetv2.paths import nnUNet_raw, nnUNet_preprocessed

class nnUNetFinetuner:
    def __init__(self, config):
        self.config = config
        self.dataset_id = "Dataset100_YourOrgan"
    
    def prepare_dataset(self, train_images, train_labels):
        """Convert medical images to nnU-Net format"""
        # Copy to nnUNet_raw/dataset_id/imagesTs/, labelsTs/
        # Create dataset.json with metadata
        pass
    
    def finetune(self, gpu_id=0):
        """Train on custom data"""
        # nnunetv2_train Dataset100 3d_fullres 0 --npz
        pass
    
    def predict(self, test_image):
        """Use fine-tuned model"""
        # nnunetv2_predict -i input -o output -d Dataset100
        pass
```

### Training Configuration

```yaml
# profiles/pancreas_finetuned.yaml
organ: Pancreas
model_type: nnunet
model_checkpoint: nnUNet_v2_dataset100

training:
  dataset_id: "Dataset100_Pancreas"
  base_model: "nnUNet_v2"  # Start from this
  epochs: 100
  batch_size: 4
  learning_rate: 0.001
  
tissues:
  - name: pancreatic_tissue
    description: Pancreatic parenchyma
    color: [255, 165, 0]
  - name: pancreatic_ducts
    description: Pancreatic ducts
    color: [255, 215, 0]
```

---

## 🔄 Data Flow Comparison (Phase 1 vs 2 vs 3)

### Phase 1 - Current (HU-Based)

```
DICOM Files
    ↓
dicom_loader.py (convert to HU)
    ↓
segmentation_engine.py
    │
    ├─ Body mask (HU > -800)
    ├─ Thresholding by HU range (config driven)
    ├─ Morphological ops (closing, dilation, etc.)
    ├─ Marching cubes
    ├─ Laplacian smoothing
    └─ STL/PLY export
```

**Pros**: Fast (1 min/scan), interpretable, no training needed  
**Cons**: Limited accuracy (88%), organ-specific tuning needed

### Phase 2A - TotalSegmentator (AI, No Training)

```
DICOM Files
    ↓
Convert to NIfTI
    ↓
TotalSegmentator API
    ├─ Pre-trained 3D U-Net (20K scan training)
    ├─ Predicts 117 organs simultaneously
    └─ Returns segmentation mask
    ↓
segmentation_engine.py
    ├─ Extract specific tissues from mask
    ├─ Post-processing (morphology, smoothing)
    └─ STL/PLY export
```

**Pros**: Much better accuracy (91-92%), works for all organs, no data collection  
**Cons**: Fixed tissues, can't customize

### Phase 2C - Fine-Tuned nnU-Net (AI + Custom Training)

```
Training Phase:
  Your 500-1000 labeled scans
    ↓
  nnU-Net auto-configures architecture
    ↓
  Train on GPU (24-72 hours)
    ↓
  Fine-tuned checkpoint saved

Inference Phase:
  DICOM Files
    ↓
  Fine-tuned nnU-Net
    ├─ Transfer learning on your data
    ├─ Better accuracy for YOUR domain
    └─ Predicts custom tissue classes
    ↓
  segmentation_engine.py
    ├─ Post-processing
    └─ STL/PLY export
```

**Pros**: Best accuracy (95%+), customized to your domain, YOUR intellectual property  
**Cons**: Requires 500+ labeled scans, GPU compute ($2-5K), 8-12 week timeline

---

## 🎯 Tech Stack

### Current (Phase 1)

```
Core Dependencies:
├─ PyDICOM (read DICOM files)
├─ NumPy (array operations)
├─ SciPy (ndimage morphology)
├─ scikit-image (marching cubes)
├─ Trimesh (mesh generation)
├─ PyYAML (config parsing)
└─ Python 3.8+

Development:
├─ Git (version control)
├─ Docker (optional containerization)
└─ Jupyter (analysis notebooks)

File Formats:
├─ DICOM (.dcm)
├─ NIfTI (.nii.gz)
├─ STL (.stl binary/ASCII)
└─ PLY (.ply with vertex colors)
```

### New for Phase 2

```
Phase 2A:
├─ TotalSegmentator (pip install totalsegmentator)
├─ PyTorch (dependency of TotalSegmentator)
└─ ONNX Runtime (inference optimization)

Phase 2B/2C:
├─ MONAI (medical imaging toolkit)
├─ nnU-Net v2 (pip install nnunetv2)
├─ Torch Lightning (training framework)
├─ Hydra (config management)
└─ Optuna (hyperparameter tuning)

Data Handling:
├─ SimpleITK (DICOM/NIfTI I/O)
├─ nibabel (NIfTI I/O)
├─ h5py (HDF5 storage)
└─ Git LFS (large file storage)

Validation:
├─ Monai Metrics (Dice, Hausdorff)
├─ scikit-learn (classification metrics)
└─ Matplotlib (visualization)
```

---

## 🔐 Version Control Strategy

```
Workspace Structure:
├── src/
│   └── medical_imaging_platform/
│       ├── core/
│       ├── profiles/
│       └── main.py
│
├── data/
│   ├── sample_brain_ct/          (Small sample, in repo)
│   ├── datasets/                 (Large, in Git LFS)
│   │   ├── .gitattributes        (*.nii.gz filter=lfs)
│   │   └── [DICOM files]
│   └── output/
│
├── models/
│   ├── pretrained/               (Downloaded, not in repo)
│   │   └── totalsegmentator_*
│   └── finetuned/                (In Git LFS after training)
│       └── dataset100_nnunet_*
│
├── docs/
│   ├── HYBRID_APPROACH.md        (This doc)
│   ├── DATASETS.md
│   ├── MODELS.md
│   └── PROJECT_ARCHITECTURE.md   (This file)
│
├── notebooks/                    (Analysis & experimentation)
│   ├── phase2a_test_totalseg.ipynb
│   ├── phase2b_dataset_analysis.ipynb
│   └── phase2c_finetuning.ipynb
│
└── .gitignore
    /models/pretrained/          (Too large, auto-download)
    /data/datasets/raw/          (Or use Git LFS)
    __pycache__/
    *.egg-info/
```

---

## 🚀 Deployment Roadmap

### Timeline

```
Week 1-2   [Phase 2A] Deploy TotalSegmentator
├─ Install totalsegmentator
├─ Create model_loader.py wrapper
├─ Test on sample_brain_ct
├─ Benchmark accuracy & speed
└─ Update main.py with --model flag
   Status: ✅ Ready to implement

Week 2-8   [Phase 2B] Collect & Organize Data
├─ Download Medical Decathlon
├─ Download LiTS, KITS, CHAOS, Synapse
├─ Collect custom institutional scans
├─ Annotate 100-200 custom scans
└─ Create combined training dataset
   Status: ✅ Ready to implement

Week 8-12  [Phase 2C] Fine-Tune Custom Model
├─ Install nnunetv2
├─ Prepare dataset in nnU-Net format
├─ Configure training parameters
├─ Train on GPU (50-100 hours)
├─ Validate on test set
└─ Deploy fine-tuned model
   Status: ✅ Ready to implement

Week 12+   [Phase 3] Slicer Integration (Optional)
└─ Reverse-engineer Segment Editor effects
```

---

## 📈 Success Metrics (Phase 1-3)

| Phase | Accuracy | Speed | Cost | Effort |
|-------|----------|-------|------|--------|
| **Phase 1 (Current)** | 88-92% | 1 min | $0 | Done |
| **Phase 2A** | 91-93% | 3 min | $0 | 2 weeks |
| **Phase 2B** | 91-93% | 3 min | $0-5K | 6 weeks |
| **Phase 2C** | 95%+ | 5 min | $2-5K | 4 weeks |
| **Phase 3** | 96%+ | 5 min | $1-2K | 8 weeks |

---

## 🎓 Key Design Decisions

1. **Config-Driven Over Hardcoding**
   - Each organ is a YAML file
   - No code changes needed to add organs
   - Easy to version and track changes

2. **Modular Segmentation Engine**
   - Same engine processes any organ
   - Pluggable backends (HU, TotalSeg, MONAI, nnU-Net)
   - Easy to swap algorithms

3. **Hybrid Approach Over Pure AI**
   - Phase 1 (HU) provides immediate value
   - Phase 2A (TotalSeg) improves accuracy
   - Phase 2C (fine-tuning) optimizes for your domain

4. **Open-Source Dependencies**
   - No proprietary licenses
   - Community-maintained
   - Can audit code

5. **Medical Imaging Standards**
   - DICOM input (medical standard)
   - NIfTI for datasets (research standard)
   - STL/PLY for 3D printing (industry standard)

---

## ❓ FAQ

**Q: Do I need to implement Phase 2A before 2C?**  
A: No. Phase 2A is independent. But Phase 2A → 2B → 2C is recommended (quick wins first).

**Q: Can I skip Phase 2B?**  
A: No. Phase 2C (nnU-Net) requires labeled training data.

**Q: Should I use TotalSegmentator results as ground truth?**  
A: Only if >90% accurate on your scans. Otherwise collect expert annotations.

**Q: How much GPU memory do I need for fine-tuning?**  
A: Minimum 8 GB. Recommended 16+ GB. RTX 3080/A100 optimal.

**Q: Can I use pre-trained models on MRI?**  
A: Not TotalSegmentator (CT-only). Some MONAI models support MRI.

---

## 🔗 Related Documentation

- [HYBRID_APPROACH.md](HYBRID_APPROACH.md) - Strategy & timeline
- [MODELS.md](MODELS.md) - Model comparison
- [DATASETS.md](DATASETS.md) - Data collection guide
- [DATA_COLLECTION_WORKFLOW.md](DATA_COLLECTION_WORKFLOW.md) - Annotation process

---

**Last Updated**: Jan 22, 2026  
**Next Review**: After Phase 2A completion
