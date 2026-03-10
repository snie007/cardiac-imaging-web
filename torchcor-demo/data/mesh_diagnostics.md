# Mesh QA Diagnostics

Run: `atrium_demo_t60`

Smoothing: Taubin (iters=8, lambda=0.5, mu=-0.53, boundary_protect=True)

| Preset | Method | Faces before | Faces after | Regularity mean (pre→post-smooth) | Regularity q10 (pre→post-smooth) | Degenerate (before→after) | Non-manifold edges (before→after) | SI heuristic hits (before→after) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| low | pyvista_decimate_pro | 49994 | 49992 | 0.4948→0.6156 | 0.1063→0.2318 | 0→0 | 2→0 | 0→0 |
| med | pymeshlab_qem | 99999 | 99970 | 0.6580→0.6647 | 0.2308→0.2421 | 0→0 | 5→0 | 0→0 |
| high | pyvista_decimate_pro | 199997 | 199991 | 0.6292→0.7198 | 0.1871→0.3759 | 0→0 | 0→0 | 0→0 |
