from pathlib import Path
import json
import numpy as np
import torch

base = Path(__file__).resolve().parent
case = base / 'data' / 'Case_10'
out = base / 'outputs' / 'atrium_demo_t60'
web = base / 'web' / 'data'
web.mkdir(parents=True, exist_ok=True)

# load points
with open(case / 'Case_10.pts', 'r') as f:
    n = int(f.readline().strip())
    pts = np.loadtxt(f, dtype=np.float32)
assert pts.shape[0] == n

# load triangles from .elem lines like: Tr i j k tag
tris = []
with open(case / 'Case_10.elem', 'r') as f:
    _ = int(f.readline().strip())
    for line in f:
        sp = line.split()
        if not sp or sp[0] != 'Tr' or len(sp) < 4:
            continue
        i, j, k = int(sp[1]), int(sp[2]), int(sp[3])
        tris.append((i, j, k))
tris = np.asarray(tris, dtype=np.int32)

vm = torch.load(out / 'Vm.pt', map_location='cpu').numpy().astype(np.float32)  # [frames, nodes]


def build_decimated(face_target: int, seed: int, name: str):
    rng = np.random.default_rng(seed)
    m = tris.shape[0]
    if face_target >= m:
        face_idx = np.arange(m)
    else:
        face_idx = np.sort(rng.choice(m, size=face_target, replace=False))
    fsel = tris[face_idx]  # [F,3]

    used = np.unique(fsel.reshape(-1))
    remap = np.full(n, -1, dtype=np.int32)
    remap[used] = np.arange(used.size, dtype=np.int32)
    faces = remap[fsel]
    verts = pts[used]
    vm_s = vm[:, used]

    payload = {
        'meta': {
            'type': 'triangular_shell',
            'source': 'TorchCor Case_10 (decimated faces)',
            'frames': int(vm_s.shape[0]),
            'nodes_total': int(n),
            'nodes_used': int(used.size),
            'faces_total': int(tris.shape[0]),
            'faces_used': int(faces.shape[0]),
            'vm_min': float(vm_s.min()),
            'vm_max': float(vm_s.max()),
            'preset': name,
        },
        'vertices': verts.round(4).tolist(),
        'faces': faces.astype(np.int32).tolist(),
        'frames': [fr.round(4).tolist() for fr in vm_s],
    }
    outp = web / f'atrium_mesh_{name}.json'
    outp.write_text(json.dumps(payload))
    return outp

files = [
    build_decimated(500, 1, '500f'),
    build_decimated(5000, 2, '5kf'),
    build_decimated(20000, 3, '20kf'),
]
for p in files:
    print(p.name, round(p.stat().st_size / 1024 / 1024, 2), 'MB')
