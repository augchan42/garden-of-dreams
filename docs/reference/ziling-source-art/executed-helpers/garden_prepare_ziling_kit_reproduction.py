from pathlib import Path
import json,shutil,ast
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);root=w/'flora-generator-reproduction';assert not root.exists();(root/'scripts').mkdir(parents=True);(root/'blender/kits').mkdir(parents=True);shutil.copytree(r/'textures/kits/flora',root/'textures/kits/flora');shutil.copyfile(w/'source-code-candidates/complete_flora_kit.py',root/'scripts/complete_flora_kit.py');shutil.copyfile(r/'scripts/make_flora_atlas.py',root/'scripts/make_flora_atlas.py')
s="""import bpy,json,hashlib
from pathlib import Path
w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);source=w/'reeds-volume/blender/kits/KIT_flora.blend';out=w/'flora-saved-source-reexports';assert not out.exists();out.mkdir();original=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source))
for variant in ['bamboo_small','bamboo_medium','bamboo_large','plum','willow','banana','reed','potted']:
 for suffix in ['', '_LOD1']:
  bpy.context.window.scene=bpy.data.scenes['Flora '+variant+(' LOD1' if suffix else '')]
  path=out/('KIT_flora_'+variant+suffix+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
  assert path.read_bytes()==(w/'reeds-volume/export/kits/flora'/path.name).read_bytes(),path.name
assert hashlib.sha256(source.read_bytes()).hexdigest()==original
(out/'report.json').write_text(json.dumps({'status':'all16saved_flora_exports_byte_exact','saved_source_sha256':original,'exports':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.glb'))}},indent=2)+'\\n');print('SAVED_FLORA_REEXPORT_PASS_16')
""";ast.parse(s);(w/'source-code-candidates/reexport_saved_flora.py').write_text(s)
verifier="""from pathlib import Path
import json,sys,hashlib,numpy as np
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);sys.path.insert(0,str(r/'scripts'));from verify_mountain_export import Glb
rows=[];changed_names=[]
for p in sorted((w/'reeds-volume/export/kits/flora').glob('*.glb')):
 a=Glb(p);b=Glb(w/'flora-generator-reproduction/export/kits/flora'/p.name);assert a.doc['nodes']==b.doc['nodes'],('Node/connector/collider metadata mismatch',p.name)
 for key in ['asset','scene','scenes','cameras','extensions','extensionsUsed','extensionsRequired','samplers']:assert a.doc.get(key)==b.doc.get(key),(p.name,key)
 assert {m['name']:a.material(m) for m in a.doc['materials']}=={m['name']:b.material(m) for m in b.doc['materials']},p.name
 assert {m['name']:a.image_hash(m) for m in a.doc['images']}=={m['name']:b.image_hash(m) for m in b.doc['images']},p.name
 assert len(a.doc['meshes'])==len(b.doc['meshes'])
 tris=0
 for mesh,newmesh in zip(a.doc['meshes'],b.doc['meshes']):
  if mesh.get('name')!=newmesh.get('name'):assert p.name.startswith('KIT_flora_reed');changed_names.append({'file':p.name,'old_name':mesh.get('name'),'generator_name':newmesh.get('name')})
  assert {k:v for k,v in mesh.items() if k not in ['name','primitives']}=={k:v for k,v in newmesh.items() if k not in ['name','primitives']}
  assert len(mesh['primitives'])==len(newmesh['primitives'])
  for x,y in zip(mesh['primitives'],newmesh['primitives']):
   assert {k:v for k,v in x.items() if k not in ['attributes','indices']}=={k:v for k,v in y.items() if k not in ['attributes','indices']};assert x['attributes'].keys()==y['attributes'].keys()
   ix=a.accessor(x['indices']).ravel();iy=b.accessor(y['indices']).ravel();assert len(ix)==len(iy);tris+=len(iy)//3
   for attr in x['attributes']:assert np.array_equal(a.accessor(x['attributes'][attr])[ix],b.accessor(y['attributes'][attr])[iy]),(p.name,attr)
 rows.append({'file':p.name,'expanded_indexed_triangles':tris,'saved_export_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generator_export_sha256':hashlib.sha256(b.bytes).hexdigest()})
assert len(rows)==16
(w/'flora-generator-reproduction/semantic-preservation.json').write_text(json.dumps({'status':'all16regenerated_flora_semantics_equal','rows':rows,'allowed_reed_mesh_datablock_name_changes':changed_names,'scope':'Fresh factory source generator recreates all16kit node/collider/port records, PBR/images and expanded positions/normals/allUVs exactly; only new reed mesh datablock labels may differ. Not authoring byte or native lighting acceptance.'},indent=2)+'\\n');print('REGENERATED_FLORA_SEMANTICS_PASS_16')
""";ast.parse(verifier);(w/'source-code-candidates/verify_flora_generator.py').write_text(verifier);print('KIT_REPRODUCTION_HELPERS_PREPARED')
