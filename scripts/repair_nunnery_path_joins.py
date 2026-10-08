"""Repair two saved render slabs in a separate Blender candidate tree.

Collision proxies, walkable footprint, all other objects and materials are
preserved. No production file is saved by this script.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Vector

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from nunnery_path_layout import RENDER_SLABS, COLLISION_SLABS

parser = argparse.ArgumentParser()
parser.add_argument('--output-root', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = args.output_root.resolve()
repo = SCRIPTS.parent.resolve()
assert root != repo and repo not in root.parents, 'Use a separate candidate tree'
source = Path(bpy.data.filepath).resolve()
original_author = hashlib.sha256(source.read_bytes()).hexdigest()
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
stage = bpy.data.collections['SITE_stage']


def snapshot(o):
    row = {'name': o.name, 'type': o.type,
           'matrix': [list(r) for r in o.matrix_world],
           'hide_render': o.hide_render, 'properties': dict(o.items()),
           'collections': sorted(c.name for c in o.users_collection)}
    if o.type == 'MESH':
        row.update(vertices=[list(v.co) for v in o.data.vertices],
                   polygons=[list(p.vertices) for p in o.data.polygons],
                   materials=[m.name if m else None for m in o.data.materials],
                   uv_layers={u.name: [list(v.uv) for v in u.data]
                              for u in o.data.uv_layers})
    return hashlib.sha256(json.dumps(row, sort_keys=True, default=lambda value: value.to_list() if hasattr(value, 'to_list') else value.to_dict() if hasattr(value, 'to_dict') else value.name_full).encode()).hexdigest()


def bounds(o):
    points = [o.matrix_world @ v.co for v in o.data.vertices]
    return [min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]


def rectangles(objects):
    result = []
    for o in objects:
        lo, hi = bounds(o)
        result.append([lo[0], hi[0], -hi[1], -lo[1]])
    return result


def overlap(rects):
    return [max(0, min(a[1], b[1]) - max(a[0], b[0])) *
            max(0, min(a[3], b[3]) - max(a[2], b[2]))
            for i, a in enumerate(rects) for b in rects[i + 1:]]


objects = sorted((o for o in stage.objects if o.name.startswith('LONGCUI_approach')), key=lambda o: o.name)
colliders = sorted((o for o in stage.objects if o.name.startswith('COL_longcui_approach')), key=lambda o: o.name)
assert len(objects) == len(colliders) == 3
before = {o.name: snapshot(o) for o in scene.objects}
old_rects = rectangles(objects)
assert sum(overlap(old_rects)) > 4.85, 'Expected baseline overlapping corner geometry'
for i, o in enumerate(objects):
    assert o.type == 'MESH' and len(o.data.vertices) == 8 and len(o.data.polygons) == 6
    assert [m.name for m in o.data.materials] == ['MAT_plaster_rock']
    lo, hi = bounds(o)
    p, size = COLLISION_SLABS[i]
    assert all(abs(lo[k] - (p[k] - size[k]/2)) < 1e-5 and
               abs(hi[k] - (p[k] + size[k]/2)) < 1e-5 for k in range(3))
    if i == 1:
        continue
    p, size = RENDER_SLABS[i]
    for vertex in o.data.vertices:
        world = o.matrix_world @ vertex.co
        if i == 0 and abs(world.y - lo[1]) < 1e-5:
            world.y = p[1] - size[1]/2
        elif i == 2 and abs(world.y - hi[1]) < 1e-5:
            world.y = p[1] + size[1]/2
        vertex.co = o.matrix_world.inverted() @ world
    o.data.update()
bpy.context.view_layer.update()
new_rects = rectangles(objects)
assert max(overlap(new_rects)) < 1e-5, overlap(new_rects)
# Source float coordinates are snapped only for this membership proof. Actual
# saved bounds are separately constrained within 1e-5m of constructor values.
old = [[round(v, 4) for v in rect] for rect in old_rects]
new = [[round(v, 4) for v in rect] for rect in new_rects]
xs = sorted({v for rect in old + new for v in rect[:2]})
zs = sorted({v for rect in old + new for v in rect[2:]})
xs += [(a+b)/2 for a,b in zip(xs, xs[1:])]
zs += [(a+b)/2 for a,b in zip(zs, zs[1:])]
def member(rects, x, z):
    return any(a <= x <= b and c <= z <= d for a,b,c,d in rects)
assert all(member(old,x,z) == member(new,x,z) for x in xs for z in zs), 'Path footprint changed'
for i, o in enumerate(objects):
    lo, hi = bounds(o);p,size=RENDER_SLABS[i]
    assert all(abs(lo[k] - (p[k] - size[k]/2)) < 1e-5 and
               abs(hi[k] - (p[k] + size[k]/2)) < 1e-5 for k in range(3))
after = {o.name: snapshot(o) for o in scene.objects}
changed = sorted(k for k in before if before[k] != after[k])
assert set(before) == set(after) and changed == ['LONGCUI_approach', 'LONGCUI_approach.002'], changed
(root/'blender').mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/authoring.blend'), compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == original_author
report = {'status': 'native_candidate_path_repaired_not_adopted',
          'source_authoring_sha256': original_author,
          'candidate_authoring_sha256': hashlib.sha256((root/'blender/authoring.blend').read_bytes()).hexdigest(),
          'changed_objects': changed, 'unchanged_objects': len(before)-2,
          'old_rectangles_xz': old_rects, 'new_rectangles_xz': new_rects,
          'old_pairwise_overlap_m2': overlap(old_rects), 'new_pairwise_overlap_m2': overlap(new_rects),
          'footprint_membership_classes': len(xs)*len(zs),
          'coordinate_tolerance_m': 1e-5, 'collision_snapshot_sha256': {o.name: after[o.name] for o in colliders},
          'scope': 'Separate saved source candidate. Only two render slab meshes trimmed; source/colliders/all other object geometry unchanged. Fresh source-matched lighting and native visual validation still required.'}
(root/'path-repair.json').write_text(json.dumps(report, indent=2)+'\n')
sys.argv = ['export_garden.py', '--', '--output-root', str(root)]
runpy.run_path(str(SCRIPTS/'export_garden.py'), run_name='__main__')
print('NUNNERY_PATH_CANDIDATE_REPAIR_PASS', changed, len(before)-2, 'objects unchanged')
