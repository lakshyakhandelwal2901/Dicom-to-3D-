# Pre-Trained Models: Comparison & Selection Guide

**Date**: Jan 2026  
**Purpose**: Technical overview of available pre-trained models for organ segmentation

---

## 📊 Model Comparison Matrix

### TotalSegmentator ⭐ (RECOMMENDED for Phase 2A)

```
Name: TotalSegmentator (v2)
Author: Wasserthal et al. (University of Tübingen)
Release: 2022 (Updated 2024)
License: Apache 2.0 (Free & Open Source)
```

**Specifications:**
| Spec | Value |
|------|-------|
| Organs Segmented | 117 (covers all 7 of ours) |
| Input Format | NIfTI, DICOM |
| Output Format | NIfTI, STL |
| Model Architecture | 3D U-Net (500M params) |
| Training Data | 20K+ CT scans (public datasets) |
| GPU Memory | 4-6 GB (has CPU mode) |
| Inference Speed | 2-5 min per scan (GPU), 10-30 min (CPU) |
| Accuracy (Dice) | 88-93% (varies by organ) |
| Installation | `pip install totalsegmentator` |
| Dependencies | PyTorch, ONNX Runtime |

**Accuracy by Organ (Our 7 Targets):**

| Organ | Dice Score | Hausdorff 95% | Notes |
|-------|-----------|----------------|-------|
| Brain | 91% | 3.2 mm | Excellent |
| Liver | 89% | 5.1 mm | Good |
| Lungs | 92% | 2.8 mm | Excellent |
| Heart | 87% | 6.2 mm | Good |
| Kidneys | 85% | 7.8 mm | Fair |
| Bones | 90% | 4.1 mm | Good |
| Pancreas | 82% | 12.5 mm | Needs refinement |

**Pros:**
- ✅ Single model for 117 organs (no need to select per-organ)
- ✅ Excellent accuracy on brain, lungs, heart, bones (91-92%)
- ✅ Fast inference (2-5 min)
- ✅ Works on CPU (15-30 min, no GPU needed)
- ✅ Active development (regularly updated)
- ✅ Large community (GitHub issues answered quickly)
- ✅ Can run from CLI or Python API

**Cons:**
- ❌ Pancreas accuracy lower (82%) → needs fine-tuning
- ❌ Kidneys sometimes miss small details (85%)
- ⚠️ Large model download (3-4 GB)
- ⚠️ No MRI support (CT only)

**Use Case:**
```python
from totalsegmentator.python_api import totalsegmentator

totalsegmentator(
    input_path="ct_scan.nii.gz",
    output_path="segmentation.nii.gz",
    fast=False,
    device="gpu"  # or "cpu"
)
```

**Deployment Timeline**: 2-4 hours  
**Cost**: $0  
**Recommendation**: ⭐⭐⭐⭐⭐ USE THIS FOR PHASE 2A

---

### MONAI (Medical Open Network for AI)

```
Name: MONAI Core + Pre-trained Model Zoo
Author: NVIDIA + Research Community
Release: 2021 (Ongoing)
License: Apache 2.0 (Free & Open Source)
```

**Specifications:**
| Spec | Value |
|------|-------|
| Organs Segmented | 15+ core organs (modular) |
| Input Format | NIfTI, DICOM |
| Output Format | NIfTI, ITK |
| Model Architecture | Various (can use any PyTorch model) |
| Training Data | Multiple datasets (NIH, institutional) |
| GPU Memory | 2-8 GB (configurable) |
| Inference Speed | 1-3 min per scan |
| Accuracy (Dice) | 85-90% |
| Installation | `pip install monai torch` |
| Learning Curve | Medium (more flexible but more setup) |

**Pre-Trained Models Available:**
- Liver segmentation (LiTS dataset)
- Spleen segmentation
- Pancreas segmentation
- Colon segmentation
- Kidney segmentation
- Prostate segmentation

**Pros:**
- ✅ Highly modular (use exactly what you need)
- ✅ Excellent documentation & tutorials
- ✅ Fast inference (1-3 min)
- ✅ Easy to integrate custom preprocessing
- ✅ Research-friendly (many advanced features)
- ✅ Active community (part of PyTorch ecosystem)

**Cons:**
- ❌ Need to select per-organ models (not unified)
- ❌ Not all organs available (no brain model in standard zoo)
- ⚠️ Steeper learning curve (more configuration)
- ⚠️ Smaller ecosystem than TotalSegmentator

**Use Case:**
```python
from monai.networks.nets import UNET
from monai.transforms import Compose, LoadImage, EnsureChannelFirst

model = UNET(spatial_dims=3, ...)  # Load pre-trained
# Predict on your data
```

**Deployment Timeline**: 3-5 hours  
**Cost**: $0  
**Recommendation**: ⭐⭐⭐ Use if you need modularity or only specific organs

---

### nnU-Net (Auto-Configuring U-Net)

```
Name: nnU-Net v2
Author: MIC-DKFZ (German Cancer Research Center)
Release: 2018 (v2 in 2023)
License: Apache 2.0 (Free & Open Source)
```

**Specifications:**
| Spec | Value |
|------|-------|
| Organs Segmented | ANY (auto ML - configures itself) |
| Input Format | NIfTI, DICOM |
| Output Format | NIfTI |
| Model Architecture | Auto-configured U-Net (varies) |
| Training Data | Hundreds of datasets supported |
| GPU Memory | 6-12 GB (depends on data) |
| Inference Speed | 3-10 min per scan |
| Accuracy (Dice) | 92-95% (with training data) |
| Installation | `pip install nnunetv2` |
| Learning Curve | Hard (need to understand medical ML) |

**Pros:**
- ✅ BEST accuracy when used correctly (92-95%)
- ✅ Auto-configures architecture (no manual tuning)
- ✅ Excellent for fine-tuning (transfer learning ready)
- ✅ Industry standard (used by major medical AI companies)
- ✅ Pre-trained checkpoints available
- ✅ Can handle ANY organ type

**Cons:**
- ❌ Requires training/fine-tuning (not plug-and-play)
- ❌ Steep learning curve (complex framework)
- ❌ Need labeled training data (500+ scans minimum)
- ⚠️ Resource-intensive (requires powerful GPU)
- ⚠️ Longer training time (24-72 hours)

**Use Case:**
```bash
# Fine-tune on your data
nnunetv2_train DATASET_ID 3d_fullres 0 --npz
nnunetv2_predict -i input_folder -o output_folder -d DATASET_ID -c 3d_fullres
```

**Deployment Timeline**: 8-12 weeks (with training)  
**Cost**: $2-5K (GPU compute)  
**Recommendation**: ⭐⭐⭐⭐ Use for Phase 2C (fine-tuning after TotalSegmentator)

---

### Other Models (Not Recommended Yet)

| Model | Organs | Accuracy | Notes |
|-------|--------|----------|-------|
| **Kidney Tumor Seg (KiTS)** | Kidney only | 91-96% | Too specialized |
| **BraTS** | Brain only | 90-94% | Too specialized |
| **Medical Segmentation Decathlon** | 10 organs | 85-90% | Older, replaced by nnU-Net |
| **DeepMedic** | Multi-organ | 80-88% | Deprecated |
| **V-Net** | Multi-organ | 82-88% | Outdated architecture |

---

## 🎯 Selection Guide

### Which Model for Which Scenario?

**Scenario 1: "I need it working THIS WEEK"**
→ **TotalSegmentator**
- 2-4 hour setup
- 88-93% accuracy out-of-box
- Works for all 7 organs

**Scenario 2: "I need only specific organs, want full control"**
→ **MONAI**
- 3-5 hour setup
- Pick exact organs you need
- 85-90% accuracy
- More flexible preprocessing

**Scenario 3: "I have 500+ labeled scans and want BEST accuracy"**
→ **nnU-Net**
- 8-12 weeks end-to-end
- 95%+ accuracy with fine-tuning
- Auto-optimizes architecture
- Best for production at scale

**Scenario 4: "I want quick wins + long-term improvement"**
→ **HYBRID (TotalSegmentator + nnU-Net)**
- Start with TotalSegmentator (Week 1)
- Collect data (Week 2-8)
- Fine-tune with nnU-Net (Week 8-12)
- ✅ RECOMMENDED FOR THIS PROJECT

---

## 📈 Performance Comparison

### Accuracy (Dice Score %)

```
Organ         | TotalSeg | MONAI | nnU-Net (Baseline) | nnU-Net (Fine-tuned)
Brain         | 91%      | 87%   | 89%                | 96%+ ⭐
Liver         | 89%      | 88%   | 87%                | 94%+
Lungs         | 92%      | 90%   | 91%                | 95%+
Heart         | 87%      | 85%   | 84%                | 93%+
Kidneys       | 85%      | 82%   | 80%                | 91%+
Bones         | 90%      | 88%   | 86%                | 92%+
Pancreas      | 82%      | 79%   | 78%                | 89%+ ⚠️
```

### Speed (Minutes per Scan)

```
Model             | CPU    | GPU (RTX3090) | GPU (A100)
TotalSegmentator  | 15-30m | 2-3m         | 1-2m ⭐
MONAI             | 20-40m | 1-2m         | 1m ⭐⭐
nnU-Net           | N/A    | 5-10m        | 3-5m
```

### Ease of Setup

```
Easiest  : TotalSegmentator (pip install → use)
Medium   : MONAI (need config + model selection)
Hardest  : nnU-Net (need training/data prep)
```

---

## 🔄 Recommended Integration Strategy

### Stage 1 (Week 1-2): Deploy TotalSegmentator

```python
# core/segmentation_engine.py
def segment_organ(volume, config):
    if config.get("model_type") == "totalSegmentator":
        return segment_with_totalSegmentator(volume, config)
    elif config.get("model_type") == "hu_based":
        return segment_with_hu_threshold(volume, config)  # Existing
```

### Stage 2 (Week 2-8): Collect Data

- Download free datasets (TCIA, Decathlon, LiTS)
- Annotate your custom cases
- Build training dataset (500-1000 scans)

### Stage 3 (Week 8-12): Fine-Tune with nnU-Net

```python
# core/nnunet_wrapper.py
def fine_tune_nnunet(training_data, validation_data):
    # Auto-configures based on data
    # Train on your custom dataset
    # Returns improved model checkpoint
```

---

## 📦 Deployment Checklist

### For TotalSegmentator (Phase 2A)

- [ ] Install `totalsegmentator` package
- [ ] Download model weights (first run auto-downloads)
- [ ] Test on sample_brain_ct
- [ ] Benchmark: accuracy, speed, memory
- [ ] Add to requirements.txt
- [ ] Create config templates with model_type field
- [ ] Update main.py CLI with --model flag
- [ ] Documentation (MODELS.md, usage examples)

### For MONAI (Optional Alternative)

- [ ] Install `monai`, `torch`
- [ ] Select organs you need
- [ ] Download pre-trained checkpoints
- [ ] Create organ-specific config files
- [ ] Test integration

### For nnU-Net (Phase 2C)

- [ ] Install `nnunetv2`
- [ ] Convert datasets to nnU-Net format
- [ ] Configure training parameters
- [ ] Train on combined dataset (500-1000 scans)
- [ ] Validate on held-out test set
- [ ] Compare accuracy vs. TotalSegmentator

---

## 💡 Pro Tips

1. **GPU vs. CPU**: TotalSegmentator works on CPU (slow but works). No GPU? It's okay.
2. **Memory**: TotalSegmentator needs 4-6 GB VRAM. AWS t3.xlarge has enough.
3. **Batch Processing**: Process multiple scans in parallel (8-16 at once).
4. **Validation**: Always compare outputs with ground truth on 5-10 test cases.
5. **Versioning**: Save model checkpoint + input data hash for reproducibility.

---

## 🔗 Resources

- **TotalSegmentator Paper**: https://arxiv.org/abs/2208.05868
- **TotalSegmentator GitHub**: https://github.com/wasserth/TotalSegmentator
- **MONAI Documentation**: https://monai.io/
- **nnU-Net GitHub**: https://github.com/MIC-DKFZ/nnUNet
- **Medical Segmentation Decathlon**: http://medicaldecathlon.com/

---

## ❓ FAQ

**Q: Can I use all three models together?**  
A: Yes! Ensemble approach (average predictions) often improves accuracy 2-3%. But overkill for Phase 2A.

**Q: TotalSegmentator or MONAI for Phase 2A?**  
A: TotalSegmentator. Single unified model, less setup, covers all 7 organs.

**Q: Do I need a GPU?**  
A: For Phase 2A? No (CPU works, just slower). For Phase 2C fine-tuning? Yes (GPU is mandatory).

**Q: What if my scans are MRI, not CT?**  
A: TotalSegmentator is CT-only. For Phase 2 you need different models (MONAI has some MRI support).

**Q: Can I use TotalSegmentator + fine-tune it?**  
A: Not directly. Use nnU-Net for fine-tuning instead (better for transfer learning).

---

**Next**: See DATASETS.md for data collection strategy  
**Questions**: Ask in #medical-ai-phase2 channel
