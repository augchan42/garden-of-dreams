import json, struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
report={}
for p in sorted((R/'export').rglob('*.glb')):
 b=p.read_bytes();magic,version,size=struct.unpack_from('<4sII',b);assert magic==b'glTF' and version==2 and size==len(b),p
 length,kind=struct.unpack_from('<II',b,12);assert kind==0x4E4F534A
 doc=json.loads(b[20:20+length]);assert doc.get('scenes'),p
 for n in doc.get('nodes',[]):
  if p.name=='garden-of-dreams.glb' and 'mesh' in n and not n.get('name','').startswith('COL_'):
   assert all('TEXCOORD_1' in primitive['attributes'] for primitive in doc['meshes'][n['mesh']]['primitives']),(p,n['name'],'missing UV2')
  if n.get('name','').startswith('TRG_'):assert 'room_id' in n.get('extras',{}),(p,n)
 assert 'KHR_draco_mesh_compression' not in doc.get('extensionsUsed',[])
 report[str(p.relative_to(R))]={'bytes':size,'nodes':len(doc.get('nodes',[])),'meshes':len(doc.get('meshes',[]))}
master=report['export/garden-of-dreams.glb'];assert master['nodes']>300
assert len(list((R/'blender/sites').glob('*.blend')))==15
assert len(list((R/'blender/kits').glob('*.blend')))==9
(R/'export/validation.json').write_text(json.dumps(report,indent=2))
print('Validated',len(report),'GLBs; 15 site files; 9 kit files; room metadata and no Draco')
