"""Reduce authored moon intensity in a separate complete candidate tree.

Keep original painting, physical scene and previous luminance metadata intact.
New metadata states the intended lower luminance rather than claiming equality
with the preceding bare moon. All fresh lighting and native art checks follow.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from moon_paint_contract import ROOT,FOLDER,OBJECT,MATERIAL,check,snapshot,fingerprint

parser=argparse.ArgumentParser()
parser.add_argument('--output-root',type=Path,required=True)
parser.add_argument('--multiplier',type=float,default=.45)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
output=args.output_root.resolve()
assert output!=ROOT and ROOT not in output.parents,'Use a separate candidate tree'
assert 0<args.multiplier<1
assert not (output/'blender/authoring.blend').exists(),'Do not overwrite a previous source candidate'
source=Path(bpy.data.filepath)
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
bpy.context.view_layer.update()
before=snapshot()
preceding=check()
moon=bpy.data.objects[OBJECT]
geometry=fingerprint(moon.data)
material=bpy.data.materials[MATERIAL]
bsdf=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
atlas=json.loads((FOLDER/'atlas.json').read_text())
old_atlas_hash=hashlib.sha256((FOLDER/'atlas.json').read_bytes()).hexdigest()
for key,field in [('Base Color','base_factor'),('Emission Color','emission_factor')]:
 node=bsdf.inputs[key].links[0].from_node
 factor=next(s for s in node.inputs if s.name=='B' and s.type=='RGBA')
 atlas[field]*=args.multiplier
 factor.default_value=(atlas[field],atlas[field],atlas[field],1)
material.diffuse_color=tuple(v*atlas['base_factor'] for v in atlas['mean_linear_rgb'])+(1,)
atlas['target_mean_luminance_ratio']=preceding['target_mean_luminance_ratio']*args.multiplier
for key in ['calibrated_base_luminance','calibrated_emission_luminance_at_strength']:atlas[key]*=args.multiplier
atlas['contrast_adjustment']={'multiplier_of_preceding_factors':args.multiplier,'preceding_atlas_sha256':old_atlas_hash,'preceding_authoring_sha256':source_hash,'reason':'Actual whole-garden moon clips to uniform white before grading. Reduced linear base/emission restores native brush contrast. Fresh final-source bakes and art checks still required.','evidence':'docs/reference/ceiling-lighting/moon-contrast/report.json'}
folder=output/'textures/backdrops/moon-paint'
folder.mkdir(parents=True,exist_ok=True)
shutil.copy2(FOLDER/'moon-paint.png',folder/'moon-paint.png')
(folder/'atlas.json').write_text(json.dumps(atlas,indent=2)+'\n')
assert fingerprint(moon.data)==geometry
assert snapshot()==before,'Unrelated object, material, camera, light or receiver contract changed'
report=check(folder/'atlas.json')
(output/'blender').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(output/'blender/authoring.blend'),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report.update(status='scratch_only',source_before_sha256=source_hash,unchanged_objects=len(before['objects']),unchanged_materials=len(before['materials']),unchanged_full_moon_geometry_uv_sha256=geometry,atlas_sha256=hashlib.sha256((folder/'atlas.json').read_bytes()).hexdigest(),authoring_sha256=hashlib.sha256((output/'blender/authoring.blend').read_bytes()).hexdigest(),scope='Only authored moon base/emission factors and diffuse preview color change. Original packed PNG, complete moon UVs/geometry and every other source object/material preserved. Not fresh lighting, adoption or final art acceptance.')
(output/'moon-contrast-authoring.json').write_text(json.dumps(report,indent=2)+'\n')
print('MOON_CONTRAST_AUTHORING_CANDIDATE_PASS',args.multiplier,len(before['objects']),'objects preserved')
