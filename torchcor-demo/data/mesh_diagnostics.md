# Mesh QA Diagnostics

Run: `atrium_demo_t60`

| Preset | Method | Faces before | Faces after | Degenerate (before→after) | Duplicate (before→after) | Non-manifold edges (before→after) | Winding inconsistent pairs (before→after) | Small components (before→after) | SI heuristic hits (before→after) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| low | pyvista_decimate_pro | 49994 | 49992 | 0→0 | 0→0 | 2→0 | 0→0 | 0→0 | 1→1 |
| med | pymeshlab_qem | 99999 | 99970 | 0→0 | 0→0 | 5→0 | 0→0 | 4→0 | 0→0 |
| high | pyvista_decimate_pro | 199997 | 199991 | 0→0 | 0→0 | 0→0 | 1→0 | 1→0 | 0→0 |
