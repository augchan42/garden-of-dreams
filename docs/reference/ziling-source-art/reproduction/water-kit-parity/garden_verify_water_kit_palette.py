from pathlib import Path
import json,sys,hashlib,numpy as np
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root'])/'water-kit-parity';sys.path.insert(0,str(r/'scripts'));from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert json.loads((w/'source-review.json').read_text())['status']=='saved_water_source_palette_reopened_exported';source=Glb(w.parent/'reeds-volume/export/garden-of-dreams.glb');expected=next(m for m in source.doc['materials'] if m['name']=='MAT_water');changed=[];identical=[]
for p in sorted((w/'baseline').glob('*.glb')):
 a=Glb(p);b=Glb(w/'candidate'/p.name);assert a.doc['nodes']==b.doc['nodes'] and a.doc['meshes']==b.doc['meshes'];assert a.doc.get('cameras')==b.doc.get('cameras') and a.doc.get('extensions')==b.doc.get('extensions')
 for key in ['accessors','images','textures','samplers','scene','scenes']:assert a.doc.get(key)==b.doc.get(key),key
 for i in range(len(a.doc['accessors'])):assert np.array_equal(a.accessor(i),b.accessor(i)),(p.name,i)
 assert len(a.doc.get('materials',[]))==len(b.doc.get('materials',[]))
 for m,n in zip(a.doc.get('materials',[]),b.doc.get('materials',[])):
  old=a.material(m);new=b.material(n)
  if m['name']=='MAT_water':
   assert new==source.material(expected);old['pbrMetallicRoughness']['baseColorFactor']=new['pbrMetallicRoughness']['baseColorFactor'];assert old==new
  elif m['name']=='MAT_pavilion_atlas':
   target=next(m for m in source.doc['materials'] if m['name']=='MAT_pavilion_atlas');assert new==source.material(target)
   old['pbrMetallicRoughness']['baseColorTexture']['index']['source']=new['pbrMetallicRoughness']['baseColorTexture']['index']['source'];assert old==new
  else:assert old==new,(p.name,m['name'])
 for m,n in zip(a.doc.get('images',[]),b.doc.get('images',[])):
  ah,bh=a.image_hash(m),b.image_hash(n)
  if ah!=bh:assert ah=='8bb9434918c056be06886377de89e71ba721cf2b0e84dd3ce060137a693bbc5c' and bh==sha(r/'textures/atlases/pavilion/pavilion_basecolor.png')
 if p.read_bytes()==(w/'candidate'/p.name).read_bytes():identical.append(p.name)
 else:assert any(m['name'] in ['MAT_water','MAT_pavilion_atlas'] for m in a.doc['materials']);changed.append(p.name)
assert len(changed)==10 and len(identical)==2 and len(list((w/'candidate').glob('*.glb')))==12
(w/'export-preservation.json').write_text(json.dumps({'status':'controlled_water_kit_palette_passed','changed_palette_exports':changed,'unchanged_byte_identical_exports':identical,'expected_assembly_water_material':source.material(expected),'source_assembly_sha256':sha(w.parent/'reeds-volume/export/garden-of-dreams.glb'),'scope':'All12 saved/reopened-source exports checked; exact node/camera/collision/ports, every decoded accessor, all other PBR/images/textures and UV channels unchanged. Four stream/pond base colors and six embedded architectural color images change to exact source palette; the two lotus exports stay byte-identical. Native kit import/adoption still pending.'},indent=2)+'\n');print('WATER_KIT_COLOR_PRESERVATION_PASS')
