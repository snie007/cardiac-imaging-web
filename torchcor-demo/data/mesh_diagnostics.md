# Mesh QA Diagnostics

Run: `atrium_demo_t60`

Smoothing: Taubin (iters=8, lambda=0.5, mu=-0.53, boundary_protect=True)

| Preset | Method | Faces before | Faces after | Regularity mean (pre→post-smooth) | Degenerate (before→after) | Non-manifold edges (before→after) | Boundary edges (before→after) | Watertight after | SI hits (before→after) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| low | pyvista_decimate_pro | 49994 | 49992 | 0.4948→0.6156 | 0→0 | 2→0 | 3422→3418 | False | 0→0 |
| med | pymeshlab_qem | 99999 | 99970 | 0.6580→0.6647 | 0→0 | 5→0 | 28749→28722 | False | 0→0 |
| high | pyvista_decimate_pro | 199997 | 199991 | 0.6292→0.7198 | 0→0 | 0→0 | 11883→11877 | False | 0→0 |

## LOD transition proximity (proxy for crack/pop risk)

- high↔med p95 distance: 704.8934 (relative radius 0.012409)
- med↔low p95 distance: 1004.0307 (relative radius 0.017675)
- high↔low p95 distance: 997.3501 (relative radius 0.017557)
