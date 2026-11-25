"""Align existing lattice objects with screen gaps in an isolated source file."""
import bpy,sys,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path('/tmp/garden-qiushuang-lattice-20261010')
sys.path[:0]=[str(repo/'scripts'),str(root)]
from moon_paint_contract import snapshot,fingerprint,check
from lattice_contract import inspect
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='0f93c42421a17b85b297fa0ff5447fad95cb7b98afeff183a2282ffe060492a4'
assert sha(repo/'blender/authoring.blend')==expected
assert not (root/'blender/authoring.blend').exists()
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
before=snapshot();moon_before=check();moon_mesh=fingerprint(bpy.data.objects['KIT_stage_painted_moon'].data)
images={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
baseline=inspect();assert baseline['status']=='failed_lattice_crosses_screen'
(root/'baseline-rays-both-poses.json').write_text(json.dumps(baseline,indent=2)+'\n')
site=bpy.data.collections['SITE_qiushuang-zhai'];bars=[o for o in site.objects if o.type=='MESH' and 'lattice' in o.name.lower()]
targets={o.name for o in bars};old_locations={o.name:o.location.copy() for o in bars};moves=[]
def centre(o):return sum((o.matrix_world@Vector(p) for p in o.bound_box),Vector())/8
centres={o.name:centre(o) for o in bars}
for center in [18.85,22.,25.15]:
 bank=[o for o in bars if abs(centres[o.name].x-center)<1.0];assert len(bank)==14
 vertical=sorted([o for o in bank if 'vertical' in o.name],key=lambda o:centres[o.name].x)
 horizontal=sorted([o for o in bank if 'horizontal' in o.name],key=lambda o:centres[o.name].z)
 assert len(vertical)==len(horizontal)==7
 for index,(o,offset) in enumerate(zip(vertical,[-.78,-.68,-.07,0,.07,.68,.78])):
  if index==3:continue
  delta=center+offset-centres[o.name].x
  if abs(delta)>1e-6:o.location.x+=delta
 for index,(o,height) in enumerate(zip(horizontal,[.75,.84,1.28,1.375,1.47,1.93,2.25])):
  if index in [0,6]:continue
  delta=height-centres[o.name].z
  if abs(delta)>1e-6:o.location.z+=delta
bpy.context.view_layer.update();candidate=inspect()
(root/'candidate-rays.json').write_text(json.dumps(candidate,indent=2)+'\n')
assert candidate['status']=='passed',candidate['blocked_samples']
after=snapshot();assert before['materials']==after['materials'];assert before['objects'].keys()==after['objects'].keys()
for name,old in before['objects'].items():
 new=after['objects'][name]
 if name in targets:
  assert {k:v for k,v in old.items() if k!='matrix'}=={k:v for k,v in new.items() if k!='matrix'},name
  # Only X translation of vertical bars and Z translation of horizontal bars.
  axis=0 if 'vertical' in name else 2
  for row in range(4):
   for col in range(4):
    if (row,col)!=(axis,3):assert old['matrix'][row][col]==new['matrix'][row][col],(name,row,col)
  if old['matrix']!=new['matrix']:moves.append({'object':name,'before':old['matrix'],'after':new['matrix']})
 else:assert old==new,name
assert len(moves)==33,len(moves)
assert moon_before==check() and moon_mesh==fingerprint(bpy.data.objects['KIT_stage_painted_moon'].data)
assert images=={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
# Negative control: the same saved layout test must fail with old positions restored.
candidate_locations={o.name:o.location.copy() for o in bars}
for o in bars:o.location=old_locations[o.name]
bpy.context.view_layer.update();assert inspect()==baseline
for o in bars:o.location=candidate_locations[o.name]
bpy.context.view_layer.update();assert inspect()==candidate
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/authoring.blend'),compress=True)
report={'status':'isolated_lattice_source_preservation_passed','baseline_authoring_sha256':expected,'candidate_authoring_sha256':sha(root/'blender/authoring.blend'),'moves':moves,'unchanged_objects':len(before['objects'])-len(moves),'unchanged_materials':len(before['materials'])+1,'unchanged_packed_images':len(images),'baseline_blocked_samples':baseline['blocked_samples'],'candidate_blocked_samples':candidate['blocked_samples'],'ray_samples':candidate['total_samples'],'negative_control':'restoring old locations reproduces baseline exactly'}
(root/'source-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
# Normalize only the disposable export representation. The batching exporter
# adopts the first object's origin; applying these translations avoids moving
# the whole wood batch origin and recomputing unrelated wood normals.
world_vertices={o.name:[list(o.matrix_world@v.co) for v in o.data.vertices] for o in bars}
bpy.ops.object.select_all(action='DESELECT')
for o in bars:o.select_set(True)
bpy.context.view_layer.objects.active=bars[0]
bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
bpy.context.view_layer.update()
assert world_vertices=={o.name:[list(o.matrix_world@v.co) for v in o.data.vertices] for o in bars}
assert inspect()==candidate
report['export_normalization']='Applied lattice location translations only in disposable export memory; every world-space vertex exact, saved authoring unchanged.'
sys.argv=['export_garden.py','--','--output-root',str(root)]
runpy.run_path(str(repo/'scripts/export_garden.py'),run_name='__main__')
assert sha(repo/'blender/authoring.blend')==expected
report.update(status='isolated_lattice_source_exported',candidate_glb_sha256=sha(root/'export/garden-of-dreams.glb'))
(root/'source-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print('QIUSHUANG_LATTICE_SOURCE_EXPORTED',len(moves),candidate['total_samples'],flush=True)
