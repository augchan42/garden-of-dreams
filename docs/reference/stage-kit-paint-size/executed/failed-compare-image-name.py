from pathlib import Path
import copy,hashlib,json,sys
import numpy as np
sys.path.insert(0,'/Users/auchan/projects/garden-of-dreams/scripts')
from verify_mountain_export import Glb
r=Path(__file__).resolve().parent;rows=[]
for base in sorted((r/'baseline/export/kits/stage').glob('*.glb')):
 candidate=r/'candidate/export/kits/stage'/base.name;old,new=Glb(base),Glb(candidate)
 assert len(old.doc['accessors'])==len(new.doc['accessors'])
 for i in range(len(old.doc['accessors'])):assert np.array_equal(old.accessor(i),new.accessor(i)),(base.name,i)
 for key in ['nodes','meshes','materials','scenes','scene','samplers','extensionsUsed','extensionsRequired']:
  assert old.doc.get(key)==new.doc.get(key),(base.name,key)
 changes=[]
 assert len(old.doc.get('images',[]))==len(new.doc.get('images',[]))
 for a,b in zip(old.doc.get('images',[]),new.doc.get('images',[])):
  ah,bh=old.image_hash(a),new.image_hash(b)
  if ah!=bh:
   assert a['name'].startswith('cyclorama-') and b['name']==a['name']+'.export2048',(a,b)
   changes.append({'name':a['name'],'before_sha256':ah,'after_sha256':bh})
 assert len(changes)==(1 if base.name.startswith('KIT_stage_cyclorama_') else 0),(base.name,changes)
 if not changes:assert old.bytes==new.bytes,base.name
 rows.append({'file':base.name,'before_bytes':len(old.bytes),'after_bytes':len(new.bytes),'accessors_exact':len(old.doc['accessors']),'changes':changes})
report={'status':'passed','files':rows,'total_before_bytes':sum(x['before_bytes'] for x in rows),'total_after_bytes':sum(x['after_bytes'] for x in rows),'scope':'Actual expanded accessor arrays, nodes, meshes, material parameters, scenes, samplers and nonpaint image payloads preserved; six cyclorama GLBs change only paint payload/name and buffer layout.'};(r/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('STAGE_EXPORT_PRESERVATION_PASS',len(rows),report['total_before_bytes'],report['total_after_bytes'])
