# Crack/Gap Robustness Repo Scan (evidence-based)

## Shortlist (6)

1. **trimesh** — <https://github.com/mikedh/trimesh>
   - Evidence: README states emphasis on **watertight surfaces**.
   - Fit: python-native; can run in our exporter for manifold/winding checks and cleanup.

2. **PyMeshFix (MeshFix wrapper)** — <https://github.com/pyvista/pymeshfix>
   - Evidence: README says output is a **single watertight triangle mesh**, removing singularities/self-intersections/degenerates.
   - Fit: very strong for closed-solid cleanup; not installed in this env, so kept as fallback option.

3. **PyMeshLab / MeshLab** — <https://github.com/cnr-isti-vclab/PyMeshLab>
   - Evidence: Python interface to MeshLab filters; robust decimation/repair filters.
   - Fit: already installed and used in pipeline for QEM decimation.

4. **Manifold** — <https://github.com/elalish/manifold>
   - Evidence: explicitly targets and guarantees **manifold output**.
   - Fit: high reliability for CAD/solid workflows; heavier integration for current Python pipeline.

5. **meshoptimizer** — <https://github.com/zeux/meshoptimizer>
   - Evidence: includes simplification + `clusterlod` companion for continuous LOD.
   - Fit: strong for production LOD transition quality/crack/popping reduction; would require C++/WASM integration.

6. **point-cloud-utils** — <https://github.com/fwilliams/point-cloud-utils>
   - Evidence: docs include mesh processing utilities, incl. watertight-manifold routines.
   - Fit: useful fallback for manifold conversion experiments in Python.

## Why selected for immediate implementation

- We prioritized methods already available in this workspace (`trimesh`, `pymeshlab`, `pyvista`, `scipy`) to avoid dependency risk.
- `pymeshfix`/`manifold`/`meshoptimizer` are high-value next integrations but were not required to land immediate fixes.

## Implemented high-impact fixes in this pass

1. **Geometry fix #1 — quantized vertex welding stage**
   - Added `weld_vertices_quantized(...)` before topology repair to reduce near-duplicate seams/T-junction risks.

2. **Geometry fix #2 — trimesh winding/normal repair stage**
   - Added `trimesh_repair(...)` stage (`fix_winding`, `fix_normals`, merge vertices) integrated into `repair_mesh(...)`.

3. **Rendering/LOD robustness fix — auto-LOD hysteresis + depth stabilization**
   - Auto mode now uses hysteresis thresholds (prevents rapid LOD thrash/popping around boundary distances).
   - Added polygon offset in material setup to reduce crack-like depth artifacts in distance views.

4. **Viewer diagnostic mode**
   - New checkbox overlays suspect geometry:
     - boundary edges (amber)
     - non-manifold edges (red)
     - tiny/sliver faces (magenta)

## Validation summary (from `web/data/mesh_diagnostics.json`)

- **Non-manifold edges:**
  - low: `2 -> 0`
  - med: `5 -> 0`
  - high: `0 -> 0`
- **Winding inconsistent pairs:** high: `1 -> 0`
- **Self-intersection heuristic hits:** all presets `0`
- **Watertightness:** still `false` for all presets (expected open atrial shell with boundaries)
- **Boundary loops/holes:** measured and reported (`boundary_loops`, `small_hole_loops`)
- **LOD transition crack-risk proxy:** added nearest-surface metrics (`lod_transition` high↔med/med↔low/high↔low)

## Dependency notes

- `trimesh`: installed and used.
- `pymeshfix`: not installed in this environment; documented as recommended next upgrade path when full watertight closure is required.
