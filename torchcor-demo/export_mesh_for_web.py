from pathlib import Path
import argparse
import json
import numpy as np
import torch


base = Path(__file__).resolve().parent
case = base / "data" / "Case_10"
web = base / "web" / "data"
web.mkdir(parents=True, exist_ok=True)


parser = argparse.ArgumentParser(description="Export connected triangular shell remesh payloads for web viewer")
parser.add_argument("--run", default="atrium_demo_t60", help="Folder name under outputs/")
parser.add_argument("--duration-ms", type=float, default=None, help="Duration metadata for frame spacing")
args = parser.parse_args()
out = base / "outputs" / args.run


with open(case / "Case_10.pts", "r") as f:
    n = int(f.readline().strip())
    pts = np.loadtxt(f, dtype=np.float32)
assert pts.shape[0] == n

tris = []
with open(case / "Case_10.elem", "r") as f:
    _ = int(f.readline().strip())
    for line in f:
        sp = line.split()
        if not sp or sp[0] != "Tr" or len(sp) < 4:
            continue
        tris.append((int(sp[1]), int(sp[2]), int(sp[3])))
tris = np.asarray(tris, dtype=np.int32)

vm = torch.load(out / "Vm.pt", map_location="cpu").numpy().astype(np.float32)  # [frames, nodes]
frame_dt_ms = float(args.duration_ms / max(vm.shape[0] - 1, 1)) if args.duration_ms is not None else 1.0


def clustered_inverse(coords: np.ndarray, target_vertices: int, iters: int = 16):
    if target_vertices >= coords.shape[0]:
        inv = np.arange(coords.shape[0], dtype=np.int32)
        return inv, 0.0, np.arange(coords.shape[0], dtype=np.int32)

    mins = coords.min(axis=0)
    spans = np.maximum(coords.max(axis=0) - mins, 1e-6)
    max_span = float(np.max(spans))

    lo = max_span / 1024.0
    hi = max_span

    best_inv = None
    best_n = coords.shape[0]
    best_cell = hi

    for _ in range(iters):
        cell = 0.5 * (lo + hi)
        q = np.floor((coords - mins) / cell).astype(np.int32)
        _, inv = np.unique(q, axis=0, return_inverse=True)
        c = int(inv.max()) + 1

        if c >= target_vertices and c < best_n:
            best_n = c
            best_inv = inv.astype(np.int32)
            best_cell = cell

        if c > target_vertices:
            lo = cell
        else:
            hi = cell

    if best_inv is None:
        q = np.floor((coords - mins) / hi).astype(np.int32)
        _, inv = np.unique(q, axis=0, return_inverse=True)
        best_inv = inv.astype(np.int32)
        best_n = int(best_inv.max()) + 1
        best_cell = hi

    return best_inv, float(best_cell), np.arange(best_n, dtype=np.int32)


def cluster_reduce(coords: np.ndarray, triangles: np.ndarray, vm_all: np.ndarray, target_vertices: int):
    inv, cell_size, _ = clustered_inverse(coords, target_vertices)
    n_clusters = int(inv.max()) + 1

    counts = np.bincount(inv, minlength=n_clusters).astype(np.float32)

    verts = np.zeros((n_clusters, 3), dtype=np.float32)
    for d in range(3):
        np.add.at(verts[:, d], inv, coords[:, d])
    verts /= counts[:, None]

    vm_cluster = np.zeros((vm_all.shape[0], n_clusters), dtype=np.float32)
    for t in range(vm_all.shape[0]):
        np.add.at(vm_cluster[t], inv, vm_all[t])
    vm_cluster /= counts[None, :]

    faces = inv[triangles]
    keep = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    faces = faces[keep]

    sf = np.sort(faces, axis=1)
    _, unique_idx = np.unique(sf, axis=0, return_index=True)
    faces = faces[np.sort(unique_idx)]

    if faces.shape[0] == 0:
        raise RuntimeError("Remeshing collapsed all triangles; increase target vertices.")

    # Keep largest connected triangle component using shared-edge union-find.
    parent = np.arange(faces.shape[0], dtype=np.int32)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    edge_owner = {}
    for fi, (a, b, c) in enumerate(faces):
        edges = ((a, b), (b, c), (c, a))
        for u, v in edges:
            if u > v:
                u, v = v, u
            key = (int(u), int(v))
            if key in edge_owner:
                union(fi, edge_owner[key])
            else:
                edge_owner[key] = fi

    roots = np.array([find(i) for i in range(faces.shape[0])], dtype=np.int32)
    uniq_roots, root_counts = np.unique(roots, return_counts=True)
    main_root = int(uniq_roots[np.argmax(root_counts)])
    main_face_mask = roots == main_root
    faces_main = faces[main_face_mask]

    used = np.unique(faces_main.reshape(-1))
    remap = np.full(n_clusters, -1, dtype=np.int32)
    remap[used] = np.arange(used.size, dtype=np.int32)

    faces_out = remap[faces_main]
    verts_out = verts[used]
    vm_out = vm_cluster[:, used]

    return {
        "vertices": verts_out,
        "faces": faces_out,
        "vm": vm_out,
        "meta": {
            "cluster_cell_size": cell_size,
            "clusters_before_component_filter": n_clusters,
            "faces_after_cluster_collapse": int(faces.shape[0]),
            "faces_main_component": int(faces_main.shape[0]),
            "nodes_main_component": int(used.size),
        },
    }


def build_connected_preset(target_vertices: int, name: str):
    remesh = cluster_reduce(pts, tris, vm, target_vertices)
    verts = remesh["vertices"]
    faces = remesh["faces"]
    vm_s = remesh["vm"]

    payload = {
        "meta": {
            "type": "triangular_shell",
            "source": f"TorchCor Case_10 ({args.run}, connected clustered remesh)",
            "time_step_ms": frame_dt_ms,
            "frames": int(vm_s.shape[0]),
            "nodes_total": int(n),
            "nodes_used": int(verts.shape[0]),
            "faces_total": int(tris.shape[0]),
            "faces_used": int(faces.shape[0]),
            "vm_min": float(vm_s.min()),
            "vm_max": float(vm_s.max()),
            "preset": name,
            "remesh": {
                "method": "vertex_clustering_connected_component",
                "target_vertices": int(target_vertices),
                **remesh["meta"],
            },
        },
        "vertices": verts.round(4).tolist(),
        "faces": faces.astype(np.int32).tolist(),
        "frames": [fr.round(4).tolist() for fr in vm_s],
    }
    outp = web / f"atrium_mesh_{name}.json"
    outp.write_text(json.dumps(payload))
    return outp


files = [
    build_connected_preset(2500, "low"),
    build_connected_preset(7000, "med"),
    build_connected_preset(14000, "high"),
]
for p in files:
    print(p.name, round(p.stat().st_size / 1024 / 1024, 2), "MB")
