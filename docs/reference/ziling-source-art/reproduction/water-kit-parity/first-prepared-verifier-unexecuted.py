from pathlib import Path
import json,sys,hashlib,numpy as np
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root'])/'water-kit-parity';sys.path.insert(0,str(r/'scripts'));from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert json.loads((w/'source-review.json').read_text())['status']=='saved_water_source_color_only_reopened_exported';source=Glb(w.parent/'reeds-volume/export/garden-of-dreams.glb');expected=next(m for m in source.doc['materials'] if m['name']=='MAT_water');changed=[];identical=[]
for p in sorted((w/'baseline').glob('*.glb')):
 a=Glb(p);b=Glb(w/'candidate'/p.name);assert a.doc['nodes']==b.doc['nodes'] and a.doc['meshes']==b.doc['meshes'];assert a.doc.get('cameras')==b.doc.get('cameras') and a.doc.get('extensions')==b.doc.get('extensions')
 for key in ['accessors','bufferViews','images','textures','samplers','scene','scenes']:assert a.doc.get(key)==b.doc.get(key),key
 for i in range(len(a.doc['accessors'])):assert np.array_equal(a.accessor(i),b.accessor(i)),(p.name,i)
 assert len(a.doc.get('materials',[]))==len(b.doc.get('materials',[]))
 for m,n in zip(a.doc.get('materials',[]),b.doc.get('materials',[])):
  old=a.material(m);new=b.material(n)
  if m['name']=='MAT_water':
   assert new==source.material(expected);old['pbrMetallicRoughness']['baseColorFactor']=new['pbrMetallicRoughness']['baseColorFactor'];assert old==new
  else:assert old==new,(p.name,m['name'])
 for m,n in zip(a.doc.get('images',[]),b.doc.get('images',[])):assert a.image_hash(m)==b.image_hash(n)
 if p.read_bytes()==(w/'candidate'/p.name).read_bytes():identical.append(p.name)
 else:assert any(m['name']=='MAT_water' for m in a.doc['materials']);changed.append(p.name)
assert len(changed)==4 and len(identical)==8 and len(list((w/'candidate').glob('*.glb')))==12
(w/'export-preservation.json').write_text(json.dumps({'status':'controlled_water_kit_palette_passed','changed_color_only_exports':changed,'unchanged_byte_identical_exports':identical,'expected_assembly_water_material':source.material(expected),'source_assembly_sha256':sha(w.parent/'reeds-volume/export/garden-of-dreams.glb'),'scope':'All12 saved/reopened-source exports checked; exact node/camera/collision/ports, every decoded accessor, all other PBR/images/textures and UV channels unchanged. Only four stream/pond base colors change to exact source material. Native kit import/adoption still pending.'},indent=2)+'\n');print('WATER_KIT_COLOR_PRESERVATION_PASS')
