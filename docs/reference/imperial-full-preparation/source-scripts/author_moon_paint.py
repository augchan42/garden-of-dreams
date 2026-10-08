"""Add calibrated painting to the saved moon without changing its physical scene.

Default writes a separate scratch .blend. --apply saves authoring and stage library;
canonical exports and genuinely fresh lighting must follow before engine adoption.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from moon_paint_contract import ROOT,FOLDER,OBJECT,MATERIAL,snapshot,check
parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--output-blend',type=Path);parser.add_argument('--report',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert args.apply != bool(args.output_blend),'Select a scratch output or canonical application'
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene;bpy.context.view_layer.update()
obj=bpy.data.objects[OBJECT];mat=bpy.data.materials[MATERIAL];assert len(obj.data.uv_layers)==0,'Apply only to the preceding bare moon source'
input_path=Path(bpy.data.filepath);before_digest=hashlib.sha256(input_path.read_bytes()).hexdigest();before=snapshot()
atlas=json.loads((FOLDER/'atlas.json').read_text());assert hashlib.sha256((FOLDER/'moon-paint.png').read_bytes()).hexdigest()==atlas['png_sha256']
image=bpy.data.images.load(str(FOLDER/'moon-paint.png'),check_existing=True);image.colorspace_settings.name='sRGB';image.pack()
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
for key,factor in [('Base Color',atlas['base_factor']),('Emission Color',atlas['emission_factor'])]:
 for link in list(bsdf.inputs[key].links):mat.node_tree.links.remove(link)
 multiply=mat.node_tree.nodes.new('ShaderNodeMix');multiply.data_type='RGBA';multiply.blend_type='MULTIPLY'
 fac=next(s for s in multiply.inputs if s.name=='Factor' and s.type=='VALUE');a=next(s for s in multiply.inputs if s.name=='A' and s.type=='RGBA');b=next(s for s in multiply.inputs if s.name=='B' and s.type=='RGBA')
 fac.default_value=1.;b.default_value=(factor,factor,factor,1)
 mat.node_tree.links.new(texture.outputs['Color'],a);mat.node_tree.links.new(next(s for s in multiply.outputs if s.type=='RGBA'),bsdf.inputs[key])
bsdf.inputs['Emission Strength'].default_value=.8
mat.diffuse_color=tuple(v*atlas['base_factor'] for v in atlas['mean_linear_rgb'])+(1,)
uv=obj.data.uv_layers.new(name='PaintUV')
for loop in obj.data.loops:
 point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(.5+point.x/5.4,.5+point.y/5.4)
obj['paint_source']='textures/backdrops/moon-paint/atlas.json';mat['paint_source']=obj['paint_source']
bpy.context.view_layer.update();assert before==snapshot(),'Unrelated geometry/UV/material/collision/camera/light source changed'
report=check();report.update(status='saved' if args.apply else 'scratch_only',source_before_sha256=before_digest,unchanged_objects_checked=len(before['objects']),unchanged_materials_checked=len(before['materials']),scope='Only moon primary UVs/material/paint metadata change. Canonical export and all fresh lighting required before Godot adoption.')
output=ROOT/'blender/authoring.blend' if args.apply else args.output_blend
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
report['saved_blend']=str(output);report['saved_blend_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
if args.apply:
 library=ROOT/'blender/sites/SITE_stage.blend';bpy.data.libraries.write(str(library),{bpy.data.collections['SITE_stage']},fake_user=True,compress=True)
 report['stage_library_sha256']=hashlib.sha256(library.read_bytes()).hexdigest()
args.report.write_text(json.dumps(report,indent=2)+'\n');print('MOON_PAINT_AUTHORING_PASS',report['status'],report['unchanged_objects_checked'],'objects preserved')
