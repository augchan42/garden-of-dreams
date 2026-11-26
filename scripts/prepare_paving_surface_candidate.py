"""Prepare a separate paving-surface candidate; never overwrite canonical assets."""
import argparse, hashlib, json, runpy, sys
from pathlib import Path
import bpy

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo/'scripts'))
from moon_paint_contract import snapshot, check
from paving_surface_partition import partition, tops, signed_area

parser=argparse.ArgumentParser()
parser.add_argument('--output-root',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root=args.output_root.resolve()
assert root!=repo and repo not in root.parents, 'Use a separate source tree'
assert not root.exists(), 'Do not overwrite a prior candidate'
source=Path(bpy.data.filepath).resolve()
assert source==(repo/'blender/authoring.blend').resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before_hash=sha(source)
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene;bpy.context.view_layer.update()
before=snapshot();moon=check()
before_tops=tops(scene)
changes=partition(scene)
assert changes, 'No paving intersections repaired'
bpy.context.view_layer.update()
after=snapshot()
changed={r['object'] for r in changes}
assert before['objects'].keys()==after['objects'].keys()
for name, record in before['objects'].items():
    actual=dict(after['objects'][name])
    if name in changed:
        assert record['type']=='MESH' and not name.startswith(('COL_','HERO_','CAM_','TRG_','LGT_'))
        actual['mesh']=record['mesh']
    assert actual==record, ('Unrelated object contract changed', name)
assert before['materials']==after['materials']
assert check()==moon
(root/'blender').mkdir(parents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/authoring.blend'),compress=True)
assert sha(source)==before_hash
report={'status':'separate_partitioned_source_saved_export_pending',
        'baseline_authoring_sha256':before_hash,'candidate_authoring_sha256':sha(root/'blender/authoring.blend'),
        'changed_objects':changes,'preserved_object_count':len(before['objects'])-len(changed),
        'before_fingerprints':before,'after_fingerprints':after,
        'materials_preserved':True,'moon_preserved':moon,
        'original_top_face_count':len(before_tops),'candidate_top_face_count':len(tops(scene)),
        'scope':'Remove overlapping visible paving top faces, retaining timber/site ownership, transforms, collision proxies, cameras, lights, markers and all materials. Independent saved-footprint/overlap audit, exports and fresh lighting/native acceptance required. No canonical adoption.'}
(root/'source-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
sys.argv=['export_garden.py','--','--output-root',str(root)]
runpy.run_path(str(repo/'scripts/export_garden.py'),run_name='__main__')
report.update(status='separate_partitioned_source_exported_not_adopted',candidate_glb_sha256=sha(root/'export/garden-of-dreams.glb'))
(root/'source-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PAVING_SURFACE_CANDIDATE_EXPORTED',len(changed),report['candidate_glb_sha256'],flush=True)
