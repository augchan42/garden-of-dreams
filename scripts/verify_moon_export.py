"""Verify a moon-paint export preserves every other physical/render contract."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_mountain_export import Glb
ROOT=Path(__file__).resolve().parents[1]
NAME='SITE_stage_MAT_painted_moon'

def compare(old_path,new_path):
 old,new=Glb(old_path),Glb(new_path);atlas=json.loads((ROOT/'textures/backdrops/moon-paint/atlas.json').read_text())
 for key in ('asset','extensionsUsed','extensionsRequired','extensions','scene','scenes','cameras'):
  assert old.doc.get(key)==new.doc.get(key),('Changed scene/camera/light contract',key)
 assert len(old.doc['nodes'])==len(new.doc['nodes'])
 triangles=0;found=0
 for a,b in zip(old.doc['nodes'],new.doc['nodes']):
  adjusted=copy.deepcopy(b)
  if a.get('name')==NAME:
   assert adjusted.pop('extras')=={'paint_source':'textures/backdrops/moon-paint/atlas.json'};found+=1
  assert a==adjusted,('Changed node/transform/collision/metadata',a.get('name'))
  if 'mesh' not in a:continue
  ma,mb=old.doc['meshes'][a['mesh']],new.doc['meshes'][b['mesh']]
  assert {k:v for k,v in ma.items() if k!='primitives'}=={k:v for k,v in mb.items() if k!='primitives'}
  assert len(ma['primitives'])==len(mb['primitives'])
  for pa,pb in zip(ma['primitives'],mb['primitives']):
   assert {k:v for k,v in pa.items() if k not in ('attributes','indices')}=={k:v for k,v in pb.items() if k not in ('attributes','indices')}
   assert set(pa['attributes'])==set(pb['attributes'])
   ia,ib=old.accessor(pa['indices']).ravel(),new.accessor(pb['indices']).ravel()
   assert len(ia)==len(ib) and len(ia)%3==0;triangles+=len(ia)//3
   for key in pa['attributes']:
    va,vb=old.accessor(pa['attributes'][key])[ia],new.accessor(pb['attributes'][key])[ib]
    if a.get('name')==NAME and key=='TEXCOORD_0':
     pos=new.accessor(pb['attributes']['POSITION'])[ib]
     # Node-local glTF Y-up maps source local Y to negative glTF Z; image V also flips.
     expected=np.column_stack([.5+pos[:,0]/5.4,.5+pos[:,2]/5.4])
     assert np.isfinite(vb).all() and np.max(np.abs(vb-expected))<1e-6,('Moon paint UV mismatch',np.max(np.abs(vb-expected)))
     assert np.ptp(vb[:,0])>.99 and np.ptp(vb[:,1])>.99
    else:assert np.array_equal(va,vb),('Changed physical/normal/lightmap UV attribute',a.get('name'),key)
 old_mats={m['name']:m for m in old.doc['materials']};new_mats={m['name']:m for m in new.doc['materials']}
 assert old_mats.keys()==new_mats.keys()
 for name,mat in new_mats.items():
  if name!='MAT_painted_moon':assert old.material(old_mats[name])==new.material(mat),('Changed unrelated material',name)
 moon=new_mats['MAT_painted_moon'];pbr=moon['pbrMetallicRoughness'];base=moon['pbrMetallicRoughness']['baseColorTexture'];emit=moon['emissiveTexture']
 assert base['index']==emit['index'], 'Export must share the base/emission painting'
 assert new.texture(base['index'])['source']==atlas['png_sha256'],'Embedded paint differs from native packed PNG'
 assert np.max(np.abs(np.array(pbr['baseColorFactor'][:3])-atlas['base_factor']))<1e-6
 strength=moon.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1)
 assert np.max(np.abs(np.array(moon['emissiveFactor'])*strength-atlas['emission_factor']*.8))<1e-6
 previous=old_mats['MAT_painted_moon'];unchanged=copy.deepcopy(moon)
 for key in ('emissiveTexture','emissiveFactor','extras'):unchanged.pop(key,None)
 unchanged['pbrMetallicRoughness'].pop('baseColorTexture',None);unchanged['pbrMetallicRoughness']['baseColorFactor']=previous['pbrMetallicRoughness']['baseColorFactor']
 assert unchanged=={k:v for k,v in previous.items() if k!='emissiveFactor'},'Changed moon roughness/metallic/alpha/double-sided settings'
 assert found==1
 return {'status':'passed','source_before_sha256':hashlib.sha256(Path(old_path).read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(Path(new_path).read_bytes()).hexdigest(),'triangles_checked':triangles,'nodes_checked':len(old.doc['nodes']),'unchanged_materials':len(new_mats)-1,'paint_sha256':atlas['png_sha256'],'scope':'Only moon primary UV/material/extras differ; expanded physical, normal and lightmap UV attributes and all other camera/collision/material/light contracts preserved.'}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('before',type=Path);parser.add_argument('candidate',type=Path);parser.add_argument('--report',type=Path,required=True);args=parser.parse_args()
 report=compare(args.before,args.candidate);args.report.write_text(json.dumps(report,indent=2)+'\n');print('MOON_EXPORT_PRESERVATION_PASS',report)
