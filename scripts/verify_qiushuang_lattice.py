"""Check saved screen openings and restore an obstructed layout as a control.

Run in a separate Blender background process. No source files are saved.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from qiushuang_lattice_contract import inspect
from moon_paint_contract import snapshot

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=ROOT/'export/qiushuang-lattice-rays.json')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert bpy.app.background,'Use a separate background Blender process'
source=Path(bpy.data.filepath)
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
before=snapshot();clear=inspect()
assert clear['status']=='passed',('Lattice blocks CRT screen samples',clear['blocked_samples'])
site=bpy.data.collections['SITE_qiushuang-zhai']
bars=[o for o in site.objects if o.type=='MESH' and 'lattice' in o.name.lower()]
locations={o.name:o.location.copy() for o in bars}
def center(o):return sum((o.matrix_world@Vector(p) for p in o.bound_box),Vector())/8
centers={o.name:center(o) for o in bars}
for x in [18.85,22.,25.15]:
 bank=[o for o in bars if abs(centers[o.name].x-x)<1]
 vertical=sorted([o for o in bank if 'vertical' in o.name],key=lambda o:centers[o.name].x)
 horizontal=sorted([o for o in bank if 'horizontal' in o.name],key=lambda o:centers[o.name].z)
 assert len(vertical)==len(horizontal)==7
 for k,o in enumerate(vertical):o.location.x+=x-.75+k*.25-centers[o.name].x
 for k,o in enumerate(horizontal):o.location.z+=.75+k*.25-centers[o.name].z
bpy.context.view_layer.update();obstructed=inspect()
assert obstructed['status']=='failed_lattice_crosses_screen' and obstructed['blocked_samples']==180,obstructed['blocked_samples']
for o in bars:o.location=locations[o.name]
bpy.context.view_layer.update()
assert inspect()==clear and snapshot()==before,'In-memory control did not restore the saved scene'
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report={'status':'passed','source_authoring_sha256':source_hash,'clear':clear,'negative_control_blocked_samples':obstructed['blocked_samples'],'source_file_and_scene_preserved':True,'scope':clear['scope']}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('QIUSHUANG_LATTICE_PASS',clear['total_samples'],'clear; negative control',obstructed['blocked_samples'],flush=True)
