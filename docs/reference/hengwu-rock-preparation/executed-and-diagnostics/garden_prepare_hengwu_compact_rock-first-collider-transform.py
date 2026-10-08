import bpy,bmesh,hashlib,json,runpy,sys,math,tempfile
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
repo=Path('/Users/auchan/projects/garden-of-dreams');source=repo/'blender/authoring.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='3a3ae2536f17cf8f19b8e5c1c811b080fe05c25615297fa20cb24019c0709621'
work=Path(tempfile.mkdtemp(prefix='garden-hengwu-compact-rock-'));(work/'blender').mkdir();(work/'export').mkdir();Path('/tmp/garden-hengwu-compact-rock.json').write_text(json.dumps({'root':str(work)})+'\n')
bpy.ops.wm.open_mainfile(filepath=str(source));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
rock=bpy.data.objects['HENGWU_perforated_rock'];collider=bpy.data.objects['COL_hengwu_rock'];allowed={rock.name,collider.name}
def signature(o):
 info={'type':o.type,'matrix':[[*r] for r in o.matrix_world],'extras':{k:str(v) for k,v in o.items()},'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'data_name':o.data.name if o.data else None}
 if o.type=='MESH':
  info.update(vertices=[list(v.co) for v in o.data.vertices],edges=[list(e.vertices) for e in o.data.edges],faces=[{'v':list(f.vertices),'material':f.material_index,'smooth':f.use_smooth} for f in o.data.polygons],materials=[m.name if m else None for m in o.data.materials],uvs={l.name:[list(x.uv) for x in l.data] for l in o.data.uv_layers})
 return hashlib.sha256(json.dumps(info,sort_keys=True).encode()).hexdigest()
before={o.name:signature(o) for o in scene.objects};original_body=[list(v.co) for v in rock.data.vertices];first_materials=[m.name if m else None for m in rock.data.materials]
# Scale the nearest silhouette around its existing floor anchor, retaining the
# three authored perforations and the two other courtyard stones unchanged.
anchor=Vector((-15.4,12.5,0));factors=Vector((.8,1,.75))
for v in rock.data.vertices:
 world=rock.matrix_world@v.co;world=anchor+Vector(((world.x-anchor.x)*factors.x,(world.y-anchor.y)*factors.y,(world.z-anchor.z)*factors.z));v.co=rock.matrix_world.inverted()@world
for f in rock.data.polygons:f.material_index=0;f.use_smooth=True
while len(rock.data.materials)>1:rock.data.materials.pop(index=len(rock.data.materials)-1)
bpy.context.view_layer.objects.active=rock
bevel=rock.modifiers.new('Plaster edge softness','BEVEL');bevel.width=.018;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(35)
bpy.ops.object.modifier_apply(modifier=bevel.name)
# Collision retains the same horizontal anchor and shrinks with the dressing.
collider.location.z*=.75;collider.scale.x*=.8;collider.scale.z*=.75
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(rock,deps)
holes=[]
for fraction,offset in [(.3,-.12),(.57,.16),(.8,-.1)]:
 p=Vector((-15.4+offset*1.05*.8,12.5,2.8*fraction*.75));hit=tree.ray_cast(p-Vector((0,2,0)),Vector((0,1,0)),4)[0];assert hit is None,('Closed hole',list(p));holes.append(list(p))
after={o.name:signature(o) for o in scene.objects};assert before.keys()==after.keys();changed={n for n in before if before[n]!=after[n]};assert changed==allowed,changed
bpy.ops.wm.save_as_mainfile(filepath=str(work/'blender/authoring.blend'),compress=True)
# Reopen the actual saved candidate and verify every object fingerprint.
bpy.ops.wm.open_mainfile(filepath=str(work/'blender/authoring.blend'));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
assert {o.name:signature(o) for o in scene.objects}==after
report={'status':'isolated_compact_rock_saved_reopened_source_preserved','root':str(work),'source_authoring_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_authoring_sha256':hashlib.sha256((work/'blender/authoring.blend').read_bytes()).hexdigest(),'changed_objects':sorted(changed),'unchanged_objects':len(before)-2,'before_fingerprints':before,'after_fingerprints':after,'open_perforation_ray_centers_z_up':holes,'original_material_slots':first_materials,'scope':'Only nearest Hengwu plaster stone and its collider changed. Compact .8 X/.75 Z footprint, softened .018m bevel and smoothed plaster faces; default slot repaired on cutter interiors. Three holes remain open. Exports/lighting/native visual/physics acceptance and adoption pending.'}
(work/'source-review.json').write_text(json.dumps(report,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==report['source_authoring_sha256']
sys.argv=['export_garden.py','--','--output-root',str(work)];runpy.run_path(str(repo/'scripts/export_garden.py'),run_name='__main__')
print('HENGWU_COMPACT_ROCK_CANDIDATE_EXPORTED',work)
