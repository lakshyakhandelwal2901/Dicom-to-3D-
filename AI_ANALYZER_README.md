# 🤖 AI-Powered 3D Model Quality Analyzer

Automated analysis tool that uses AI to evaluate the quality, accuracy, and anatomical correctness of your 3D medical models.

## 🎯 What It Does

1. **Downloads models** from cloud storage automatically
2. **Analyzes mesh quality**: vertices, faces, topology, watertightness
3. **Detects anatomical structures** by vertex colors
4. **Calculates statistics**: surface area, volume, dimensions
5. **Identifies issues**: degenerate faces, artifacts, holes
6. **Provides recommendations** for improvement
7. **Generates quality score** (0-100)

## 🚀 Quick Start

### Analyze Latest Full Anatomy Model
```bash
./analyze_model.sh
```

### Analyze Specific Cloud Model
```bash
./analyze_model.sh --cloud s3://my-medical-imaging/outputs/lung_TCGA-17-Z054_full_anatomy/full_anatomy_combined_colored.ply
```

### Analyze Local File
```bash
./analyze_model.sh --local ./output/my_model.ply
```

### With Visual Renders (requires pyrender)
```bash
./analyze_model.sh --local ./output/model.ply --render
```

## 📊 Output Files

After analysis, you'll find:

```
analysis_output/
├── quality_report.txt          # Detailed statistical report
├── AI_ANALYSIS_SUMMARY.md      # Human-readable analysis with recommendations
├── view_front.png              # Front view render (if --render used)
├── view_back.png               # Back view render
├── view_oblique_1.png          # Oblique view
├── ...                         # More views
└── analysis_grid.png           # Grid of all views
```

## 📈 Quality Metrics

### What Gets Analyzed

#### Mesh Quality (40 points)
- ✅ Watertight (no holes): 20 points
- ✅ Low degenerate faces (<1%): 15 points  
- ✅ Standard topology: 10 points
- ✅ No isolated vertices: 5 points

#### Visual Quality (30 points)
- ✅ Has vertex colors: 10 points
- ✅ Multiple distinct colors: 10 points
- ✅ Balanced color distribution: 10 points

#### Processing Quality (30 points)
- ✅ Optimized poly count: 10 points
- ✅ Clean geometry: 10 points
- ✅ Proper dimensions: 10 points

### Quality Score Ranges

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Production-ready |
| 75-89 | ⭐⭐⭐⭐ Good | Minor improvements needed |
| 60-74 | ⭐⭐⭐ Fair | Some issues to address |
| 40-59 | ⭐⭐ Poor | Significant problems |
| 0-39 | ⭐ Failed | Major reconstruction needed |

## 🎨 Full Anatomy Model Analysis

The analyzer provides special insights for multi-organ models:

### Detected Structures
- 🦴 **Bones** (bone white)
- 🫁 **Lungs** (pink)
- 🫀 **Heart** (crimson)
- 🩸 **Vessels** (bright red)
- 🤎 **Muscle** (saddle brown)
- 🟤 **Liver** (brown)
- 🔴 **Kidneys** (firebrick)
- 🟣 **Spleen** (purple)
- 🟠 **Pancreas** (orange)

### Anatomical Accuracy

The AI compares vertex distribution against expected anatomical proportions:

| Organ | Expected % | Threshold |
|-------|-----------|-----------|
| Bones | 5-10% | Alert if < 3% or > 15% |
| Lungs | 15-25% | Alert if < 10% or > 30% |
| Heart | 8-12% | Alert if < 5% or > 18% |
| Liver | 10-15% | Alert if < 8% or > 20% |

## 🔍 Interpreting Results

### Example Output

```
Overall Quality Score: 90.0/100

MESH STATISTICS
--------------------------------------------------------------------------------
Vertices:              506,900
Faces:                 1,013,800
Watertight:            ✓ Yes
Unique Colors:         9

ANATOMICAL STRUCTURES (9 organs)
--------------------------------------------------------------------------------
RGB(178,34,34) - Kidneys    : 65,898 vertices (13.00%)
RGB(255,140,0) - Pancreas   : 65,774 vertices (12.98%)
...
```

### What to Look For

#### ✅ Good Signs
- Score above 85
- Watertight: Yes
- Degenerate faces < 1%
- All expected organs present
- Balanced vertex distribution

#### ⚠️ Warning Signs
- Score 60-85
- Non-watertight mesh
- One organ dominates (>40%)
- Missing expected structures

#### ❌ Problems
- Score below 60
- Many degenerate faces (>5%)
- Wrong topology
- No vertex colors
- Extreme imbalance

## 🛠️ Advanced Usage

### Python API

```python
import trimesh
from analyze_3d_model import analyze_mesh_statistics, generate_quality_report

# Load mesh
mesh = trimesh.load('model.ply')

# Analyze
stats = analyze_mesh_statistics(mesh)
score = generate_quality_report(mesh, stats, 'report.txt')

print(f"Quality Score: {score}/100")
```

### Batch Analysis

Analyze multiple models:

```bash
for model in $(aws s3 ls s3://my-bucket/outputs/ --recursive | grep ".ply" | awk '{print $4}'); do
    ./analyze_model.sh --cloud "s3://my-bucket/$model" --output "./analysis_$(basename $model .ply)"
done
```

### Custom Thresholds

Edit `analyze_3d_model.py` to adjust quality thresholds:

```python
# Line ~380
if stats['degenerate_percentage'] > 5:  # Change threshold
    quality_score -= 15
```

## 📚 Understanding Metrics

### Euler Characteristic
- **Expected**: 2 for a single closed surface (like a sphere)
- **Multi-organ**: 0 or negative (multiple disconnected components)
- **What it means**: Topology health indicator

### Watertight
- **Yes**: Mesh has no holes, can hold water
- **No**: Has gaps or holes
- **Impact**: Required for 3D printing, volume calculations

### Degenerate Faces
- Triangles with near-zero area
- Caused by: Duplicate vertices, zero-length edges
- **Fix**: `mesh.remove_degenerate_faces()`

### Vertex Colors
- RGB values stored per vertex
- Used for: Organ identification, visualization
- **Format**: PLY and OBJ support colors, STL does not

## 🐛 Troubleshooting

### "Model file not found"
```bash
# Check cloud path:
./do_spaces.sh list s3://my-medical-imaging/outputs/ | grep model_name

# Or use full path with double slashes if needed:
./analyze_model.sh --cloud "s3://bucket/outputs//folder/model.ply"
```

### "pyrender not installed"
```bash
# Skip rendering:
./analyze_model.sh --local model.ply  # (--skip-render is default)

# Or install pyrender:
.venv/bin/pip install pyrender
./analyze_model.sh --local model.ply --render
```

### "Unable to locate credentials"
```bash
# Set up AWS credentials:
aws configure
# Or source credentials:
source ~/.bashrc
```

## 🎓 Best Practices

1. **Always analyze PLY files** for colored models (not STL)
2. **Run after each profile change** to validate improvements
3. **Compare scores** before/after refinement
4. **Check anatomical proportions** for medical accuracy
5. **Use with other tools** (3D Slicer, MeshLab) for validation

## 📖 Related Tools

- **batch_cloud_segmentation.py** - Generate models
- **do_spaces.sh** - Cloud storage management
- **main.py** - Direct segmentation
- **analyze_model.sh** - This analyzer (wrapper script)
- **analyze_3d_model.py** - Core analysis engine

## 🤝 Contributing

To add new analysis features:

1. Edit `analyze_3d_model.py`
2. Add new metrics to `analyze_mesh_statistics()`
3. Update `generate_quality_report()` with new checks
4. Adjust quality score calculation
5. Test on sample models

## 📝 Examples

### Example 1: Validate Refinement

```bash
# Before refinement
./analyze_model.sh --local old_model.ply --output analysis_before

# After refinement  
./analyze_model.sh --local new_model.ply --output analysis_after

# Compare scores
grep "Overall Quality" analysis_before/quality_report.txt
grep "Overall Quality" analysis_after/quality_report.txt
```

### Example 2: Batch Quality Check

```bash
#!/bin/bash
for organ in lungs kidneys liver brain; do
    echo "Analyzing $organ..."
    ./analyze_model.sh \
        --cloud "s3://my-medical-imaging/outputs/lung_TCGA-17-Z054_${organ}/..." \
        --output "analysis_${organ}"
    
    score=$(grep "Overall Quality Score" "analysis_${organ}/quality_report.txt" | grep -oE '[0-9.]+')
    echo "$organ: $score/100"
done
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/model-quality.yml
name: Model Quality Check
on: [push]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Analyze Models
        run: |
          ./analyze_model.sh --local ./output/latest_model.ply
          score=$(grep "Overall Quality Score" ./analysis_output/quality_report.txt | grep -oE '[0-9.]+')
          if (( $(echo "$score < 75" | bc -l) )); then
            echo "Quality score too low: $score"
            exit 1
          fi
```

## 🎯 Roadmap

- [ ] Web UI for analysis visualization
- [ ] Real-time comparison with medical atlases
- [ ] Deep learning-based anatomical validation
- [ ] Automated HU range optimization suggestions
- [ ] Multi-model comparison reports
- [ ] Integration with DICOM metadata

---

**Version**: 1.0  
**Last Updated**: 2026-01-28  
**License**: MIT
