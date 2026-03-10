# TorchCor surface mesh decimation: external-solution benchmark + rebuild

Date: 2026-03-10  
Mesh: `Case_10` triangular shell (`385,698` verts, `760,625` tris)

## 1) Literature + repo scan (3–4 strong OSS options)

1. **fast-simplification** (repo: https://github.com/pyvista/fast-simplification)  
   - Method: Fast Quadric Error Metrics (QEM) simplification (wrapper around Fast-Quadric-Mesh-Simplification).  
   - License: **MIT** (repo LICENSE).  
   - Strengths: very fast; simple NumPy API; Python-friendly.  
   - Limits: in this case did **not** reach requested target face counts (stalled around 312k faces for all targets tested).

2. **PyMeshLab** (repo: https://github.com/cnr-isti-vclab/PyMeshLab)  
   - Method: MeshLab filters incl. `meshing_decimation_quadric_edge_collapse` (QEM family).  
   - License: **GPL** (stated in repo/docs).  
   - Strengths: mature mesh-processing stack, many cleanup/repair filters.  
   - Limits: slower here; topology fragmented at stronger decimation (many components/boundaries).

3. **VTK / PyVista** (repo: https://github.com/Kitware/VTK, PyVista front-end)  
   - Method: `vtkDecimatePro` via `pyvista.PolyData.decimate_pro(...)`.  
   - License: **BSD-3-Clause** (VTK).  
   - Strengths: fastest in this benchmark while hitting target face counts; robust Python workflow.  
   - Limits: some boundary edges/components remain; quality tuning is parameter-sensitive.

4. **Open3D** (repo: https://github.com/isl-org/Open3D)  
   - Method: quadric decimation (`simplify_quadric_decimation`) in C++/Python API.  
   - License: **MIT**.  
   - Strengths: modern 3D stack and good decimation implementation.  
   - Limits in this environment: package wheel unavailable on this host/python combo (see install failure below), so not benchmarked locally.

## 2) Local implementations completed

Implemented and benchmarked in `benchmarks/mesh_decimation_benchmark.py`:
- `pyvista_decimatepro` (selected)
- `pymeshlab_qem`
- `fast_simplification`
- `vertex_cluster_fallback` (robust fallback)

Install notes:
- Success: `trimesh`, `fast-simplification`, `pymeshlab`.
- Failure: `open3d` with exact error:  
  `ERROR: Could not find a version that satisfies the requirement open3d (from versions: none)`  
  `ERROR: No matching distribution found for open3d`

## 3) Quantitative benchmark summary

Full results: `benchmarks/results/benchmark_results.json` and `.md`.

| Method | Target faces | Runtime (s) | Output faces | Components | Area distortion |
|---|---:|---:|---:|---:|---:|
| pyvista_decimatepro | 200000 | 0.637 | 199997 | 2 | 0.002600 |
| pyvista_decimatepro | 100000 | 0.675 | 99997 | 1 | 0.005062 |
| pyvista_decimatepro | 50000 | 0.716 | 49994 | 1 | 0.009125 |
| pymeshlab_qem | 200000 | 6.474 | 199999 | 5 | 0.000351 |
| pymeshlab_qem | 100000 | 7.415 | 99999 | 5 | 0.000897 |
| pymeshlab_qem | 50000 | 7.974 | 49575 | 587 | 0.295165 |
| fast_simplification | 200000 | 1.206 | 312608 | 1 | 0.000045 |
| fast_simplification | 100000 | 1.076 | 312608 | 1 | 0.000045 |
| fast_simplification | 50000 | 1.079 | 312608 | 1 | 0.000045 |

Additional tracked metrics (in JSON/MD): Chamfer, Hausdorff approx, normal deviation, boundary edges, degenerate faces.

## 4) Selected method and rationale

**Selected:** `pyvista_decimatepro` (VTK DecimatePro).

Why:
- Best speed-quality tradeoff in this environment.
- Reliably meets requested target face counts for low/med/high presets.
- Much faster than PyMeshLab here, and unlike fast-simplification it actually reached target decimation levels.

## 5) Integration + rebuild

Updated exporter: `export_mesh_for_web.py`
- Default method now `pyvista` with automatic fallback to clustering.
- Presets rebuilt as face targets:
  - low: 50k faces
  - med: 100k faces
  - high: 200k faces

Updated viewer: `web/mesh.html`
- Preset labels now reflect face-based targets.

Rebuilt web payloads:
- `web/data/atrium_mesh_low.json`
- `web/data/atrium_mesh_med.json`
- `web/data/atrium_mesh_high.json`

## 6) Publish + GitHub Pages push

Synced to: `/tmp/cardiac-imaging-web/torchcor-demo`  
Committed and pushed to GitHub Pages repo:
- Repo: `https://github.com/snie007/cardiac-imaging-web`
- Commit: `3808e4f`

Published artifacts include benchmark files:
- `/tmp/cardiac-imaging-web/torchcor-demo/benchmarks/benchmark_results.json`
- `/tmp/cardiac-imaging-web/torchcor-demo/benchmarks/benchmark_results.md`
