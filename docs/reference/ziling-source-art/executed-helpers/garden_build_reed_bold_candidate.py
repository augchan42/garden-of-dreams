import ast,bpy,bmesh,hashlib,json,math,random,runpy,shutil,sys
from pathlib import Path
from mathutils import Vector
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);out=w/'reeds-bold';assert not out.exists();(out/'blender/kits').mkdir(parents=True);(out/'export/kits').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.path.insert(0,str(r/'scripts'));from make_flora_atlas import CELLS
source_class=next(n for n in ast.parse((r/'scripts/complete_flora_kit.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='Geometry');exec(compile(ast.Module(body=[source_class],type_ignores=[]),str(r/'scripts/complete_flora_kit.py'),'exec'))
def signature(o):
 d={'type':o.type,'matrix':[[*row] for row in o.matrix_world],'extras':{k:str(v) for k,v in o.items()},'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []}
 if o.type=='MESH':d.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],indices=[p.material_index for p in o.data.polygons],uvs={l.name:[list(x.uv) for x in l.data] for l in o.data.uv_layers})
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
def build(quality):
 rng=random.Random(89);g=Geometry(quality);details=[]
 for j in range(8):
  angle=j*2.399+.23;r0=.28*math.sqrt((j+1)/8);base=Vector((r0*math.cos(angle),r0*math.sin(angle),0));direction=Vector((math.cos(angle+.35),math.sin(angle+.35),0));height=.98+rng.random()*.57;plume=.27+rng.random()*.07;culm=height-plume
  def center(t):return base+direction*(.11*t*t)+Vector((0,0,culm*t))
  for k in range(3):g.stem(center(k/3),center((k+1)/3),.0075-k*.001,'reed_stem',4,.0065-k*.001)
  leaf_data=[]
  for k,t in enumerate([.32,.55,.78]):
   a=angle+k*2.1;leafdir=Vector((math.cos(a),math.sin(a),0));length=.36+rng.random()*.20;root=center(t);tip=root+leafdir*length+Vector((0,0,.03-k*.10));width=.095+rng.random()*.045
   g.leaf(root,tip,width,'reed',4,angle=.24*(k-1),bend=.10);leaf_data.append({'root':list(root),'tip':list(tip),'width':width})
  def head(t):return center(1)+direction*(.15*t*t)+Vector((0,0,plume*t))
  for k in range(2):g.stem(head(k/2),head((k+1)/2),.0024-k*.0006,'reed_stem',3,.0017-k*.0006)
  levels=5 if quality==1 else 2;branch_data=[]
  for k in range(levels):
   t=(k+.55)/levels;side=direction.cross(Vector((0,0,1)))*(-1 if k%2 else 1);start=head(t);span=.025+.10*math.sin(math.pi*t);tip=start+side*span+direction*.025+Vector((0,0,.025));g.stem(start,tip,.0013,'reed_stem',3,.0003)
   axis=(tip-start).normalized();ribbons=2 if quality==1 else 1
   for n in range(ribbons):
    p=start.lerp(tip,.52+n*.24);cross=axis.cross(Vector((0,0,1))).normalized()*.004
    g.face([p-cross,p+cross,p+axis*.043+Vector((0,0,.009))],'reed_stem',[(.3,.4),(.7,.4),(.5,.8)])
   branch_data.append({'root':list(start),'tip':list(tip)})
  # Broad card silhouettes preserve feathery plume masses at mobile size.
  outline=[(0,-.5),(-.35,-.35),(-.60,-.20),(-.40,-.10),(-.65,.08),(-.45,.18),(-.30,.30),(0,.5),(.28,.30),(.46,.12),(.62,-.05),(.35,-.15),(.55,-.30),(.20,-.40)] if quality==1 else [(0,-.5),(-.55,-.25),(-.65,.10),(-.30,.32),(0,.5),(.30,.32),(.65,.10),(.55,-.25)]
  axis=(head(1)-head(.1)).normalized();center_head=head(.6)
  for card in range(2 if quality==1 else 1):
   side=direction.cross(Vector((0,0,1))) if card==0 else direction
   points=[center_head+side*(x*.17)+axis*(y*plume*.85) for x,y in outline]
   g.face(points,'reed_stem',[(.5+x*.4,.5+y*.8) for x,y in outline])
  details.append({'stem':j,'height':height,'culm_sections':3,'leaves':leaf_data,'panicle_branches':branch_data,'plume_length':plume})
 return g,details
bpy.ops.wm.open_mainfile(filepath=str(r/'blender/kits/KIT_flora.blend'));mat=bpy.data.materials['MAT_flora_atlas'];before={o.name:signature(o) for o in bpy.data.objects};models={};counts={};details={}
for suffix,quality,scene_name,col_name in [('',1,'Flora reed','KIT_flora_reed'),('_LOD1',.4,'Flora reed LOD1','KIT_flora_reed_LOD1')]:
 scene=bpy.data.scenes[scene_name];bpy.context.window.scene=scene;col=bpy.data.collections[col_name];old=next(o for o in col.objects if o.type=='MESH' and not o.name.startswith('COL_'));g,desc=build(quality);temp=g.object('TEMP_reed_geometry'+suffix,col);old.data=temp.data;bpy.data.objects.remove(temp,do_unlink=True);models[suffix]=old.data;counts[suffix]=sum(len(p.vertices)-2 for p in old.data.polygons);details[suffix]=desc
 bpy.ops.export_scene.gltf(filepath=str(out/'export/kits'/('KIT_flora_reed'+suffix+'.glb')),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
after={o.name:signature(o) for o in bpy.data.objects};assert before.keys()==after.keys();changed={n for n in before if before[n]!=after[n]};assert changed=={'KIT_flora_reed_render','KIT_flora_reed_render_LOD1'},changed
assert 200<=counts['']<=2000 and .32<=counts['_LOD1']/counts['']<=.48,counts
bpy.ops.wm.save_as_mainfile(filepath=str(out/'blender/kits/KIT_flora.blend'),compress=True)
# Write the two authored mesh datablocks into a portable library for controlled placement.
bpy.data.libraries.write(str(out/'blender/kits/reed-meshes.blend'),set(models.values())|{mat},fake_user=True,compress=True)
manifest=json.loads((r/'export/kits/flora/manifest.json').read_text());item=manifest['variants']['reed'];item.update(triangles_lod0=counts[''],triangles_lod1=counts['_LOD1'],ratio=counts['_LOD1']/counts[''])
shutil.copytree(r/'export/kits/flora',out/'export/kits/flora');
for suffix in ['', '_LOD1']:shutil.copyfile(out/'export/kits'/('KIT_flora_reed'+suffix+'.glb'),out/'export/kits/flora'/('KIT_flora_reed'+suffix+'.glb'))
(out/'export/kits/flora/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Reopen the actual waterline source, then change only the ten existing reed meshes.
bpy.ops.wm.open_mainfile(filepath=str(w/'waterline/blender/authoring.blend'));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene;before_source={o.name:signature(o) for o in scene.objects}
with bpy.data.libraries.load(str(out/'blender/kits/reed-meshes.blend'),link=False) as (src,dst):dst.meshes=[n for n in src.meshes if n.startswith('TEMP_reed_geometry') and not n.endswith('_LOD1')]
assert len(dst.meshes)==1;mesh=dst.meshes[0];mesh.materials.clear();mesh.materials.append(bpy.data.materials['MAT_flora_atlas'])
placed=[]
for o in scene.objects:
 if o.get('flora_variant')=='reed' and o.get('flora_placement'):
  assert any(c.name=='SITE_ziling-zhou' for c in o.users_collection);o.data=mesh;placed.append(o.name)
assert len(placed)==10
after_source={o.name:signature(o) for o in scene.objects};assert before_source.keys()==after_source.keys();assert {n for n in before_source if before_source[n]!=after_source[n]}==set(placed)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'blender/authoring.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'blender/authoring.blend'));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene;assert {o.name:signature(o) for o in scene.objects}==after_source
(out/'reed-source-review.json').write_text(json.dumps({'status':'isolated_reed_models_and_source_saved_reopened_preserved','baseline_waterline_authoring_sha256':sha(w/'waterline/blender/authoring.blend'),'candidate_authoring_sha256':sha(out/'blender/authoring.blend'),'geometry_class_source_sha256':sha(r/'scripts/complete_flora_kit.py'),'changed_kit_objects':sorted(changed),'changed_scene_objects':placed,'triangles':counts,'ratio':counts['_LOD1']/counts[''],'botanical_structure':details,'before_source_fingerprints':before_source,'after_source_fingerprints':after_source,'scope':'Eight jointed/curved culms per clump, three narrow arching leaves per culm and branching tawny plumes with broad crossed silhouette cards; authored from observed botanical features, not copied photo pixels. Both LODs retain all culms/leaves. Original atlas and alpha material retained. Other seven flora variants and all scene object transforms/lighting/cameras/colliders/markers unchanged from separate waterline candidate. Fresh lighting/native model/physics review and adoption pending.'},indent=2)+'\n')
sys.argv=['export_garden.py','--','--output-root',str(out)];runpy.run_path(str(r/'scripts/export_garden.py'),run_name='__main__');print('REED_CANDIDATE_SAVED_EXPORTED',counts,out)
