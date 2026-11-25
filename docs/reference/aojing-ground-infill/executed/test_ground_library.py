"""Check that the actual linked candidate master contains the saved ground patch."""
from pathlib import Path
import bpy, hashlib, json
from mathutils import Vector

r = Path(__file__).resolve().parent
source = r/'blender/authoring.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '9b6c83259f79aeb56bbdc67b1fd939b2e9ff69977bcb941cb8141b2ce329b66e'
scene = next(s for s in bpy.data.scenes if s.name == 'Garden of Dreams | master')
stage = next(c for c in scene.collection.children if c.name == 'SITE_stage')
patch = next(o for o in stage.objects if o.name == 'AOJING_ground_west_infill')
assert patch.library and Path(bpy.path.abspath(patch.library.filepath)).resolve() == (r/'blender/sites/SITE_stage.blend').resolve()
assert len(patch.data.vertices) == 8 and len(patch.data.polygons) == 6 and len(patch.data.uv_layers) == 0
assert [m.name for m in patch.data.materials] == ['MAT_stage_canvas']
points = [patch.matrix_world @ Vector(v) for v in patch.bound_box]
lo = [min(v[i] for v in points) for i in range(3)]
hi = [max(v[i] for v in points) for i in range(3)]
assert all(abs(a-b) < 1e-5 for a,b in zip(lo,[18,-21,-.63]))
assert all(abs(a-b) < 1e-5 for a,b in zip(hi,[20.2,-14,-.13]))
direct = [library for library in bpy.data.libraries if library.parent is None]
assert len(direct) == 15 and all(library.filepath.startswith('//sites/') for library in direct)
report = {'status':'linked_candidate_ground_patch_passed', 'authoring_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'master_sha256':hashlib.sha256((r/'blender/master.blend').read_bytes()).hexdigest(),
          'stage_library_sha256':hashlib.sha256((r/'blender/sites/SITE_stage.blend').read_bytes()).hexdigest(),
          'bounds_min':lo, 'bounds_max':hi, 'relative_direct_libraries':len(direct),
          'scope':'Saved linked-library source packaging only; no fresh bake, native collision or visual acceptance.'}
(r/'export/ground-linked-library.json').write_text(json.dumps(report,indent=2)+'\n')
print('AOJING_LINKED_GROUND_LIBRARY_PASS',len(direct))
