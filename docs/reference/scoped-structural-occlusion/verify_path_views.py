#!/usr/bin/env python3
"""Check actual four-leg state/floor evidence and recorded-pose comparisons, not all continuous rendered frames."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
DETAILS={'terminal_room':['look','terminal'],'rockery_gate':['look'],'qinfang_ting':['look','table','water'],'ouxiang_xie':['look','tea'],'ziling_zhou':['look','reeds'],'qiushuang_zhai':['look','left','centre','right'],'tubi_tang':['look','overlook'],'hengwu_yuan':['look','read','rocks'],'daoxiang_cun':['look','doors','tools','paddy'],'aojing_guan':['look','doors','reflection'],'longcui_an':['look','doors','incense'],'xiaoxiang_guan':['look','doors','stems'],'yihong_yuan':['look','doors','leaves'],'daguan_lou':['look','doors']}
def sha(data):return hashlib.sha256(data).hexdigest()
def verify(directory,shape):
 j=json.loads((directory/'report.json').read_text())
 assert j['shape']==shape and j['source_glb_sha256']=='faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f'
 assert j['route_sha256']=='ec42ec55bf382ec314b6da325da741d214d297d81418d4da38bdabe0d017ec87'
 assert len(j['occluders'])==5 and len(j['legs'])==4
 assert j['arrival_signals']==['rockery_gate','qinfang_ting','rockery_gate','terminal_room']
 assert [(r['command'],r['to']) for r in j['legs']]==[('exit','rockery_gate'),('enter','qinfang_ting'),('back','rockery_gate'),('back','terminal_room')]
 assert sum(r['grounded_rays'] for r in j['legs'])==j['grounded_rays']>3000
 assert j['reveal_frames']>100
 expected={room+'-'+command for room,commands in DETAILS.items() for command in commands}
 assert {name for name,row in j['cases'].items() if row['kind']=='public_detail'}==expected
 assert len(expected)==37
 kinds={};changed=0;maxdraw=0;maxprim=0
 for name,row in j['cases'].items():
  kinds[row['kind']]=kinds.get(row['kind'],0)+1
  variants=row['comparisons'];assert set(variants)=={'disabled','enabled','disabled_repeat'}
  images=[]
  for variant,record in variants.items():
   path=directory/f'{name}-{variant}.png'
   assert sha(path.read_bytes())==record['file_sha256']
   with Image.open(path) as image:
    assert image.mode=='RGBA' and image.size==((390,844) if shape=='portrait' else (1410,600))
    data=image.tobytes()
   assert sha(data)==record['pixel_sha256'];images.append(data)
   assert type(record['automatic_frames_elapsed']) is int and record['automatic_frames_elapsed']>=20
   assert type(record['draws']) is int and record['draws']>0
   assert type(record['primitives']) is int and record['primitives']>0
  assert images[0]==images[1]==images[2],f'{shape}/{name}: pixels differ'
  a=variants['disabled'];b=variants['enabled'];c=variants['disabled_repeat']
  assert a['draws']==c['draws'] and a['primitives']==c['primitives']
  assert b['draws']<=a['draws'] and b['primitives']<=a['primitives']
  assert b['draws']<=150 and b['primitives']<=300000
  changed+=int(b['draws']<a['draws']);maxdraw=max(maxdraw,b['draws']);maxprim=max(maxprim,b['primitives'])
 assert kinds['travel']>=90 and kinds['reveal']>=6 and kinds['settled_arrival']==4
 assert len(j['cases'])==147
 return {'cases':len(j['cases']),'decoded_images':len(j['cases'])*3,'kinds':kinds,'draw_saving_cases':changed,'candidate_global_draws_max':maxdraw,'candidate_global_primitives_max':maxprim,'grounded_rays':j['grounded_rays'],'reveal_frames':j['reveal_frames']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 summary={'scope':'Actual four-leg public cell/gate/pavilion normal-physics round trip; replayed recorded camera poses and37public detail endpoints per shape. Not continuous per-frame image equality, CPU/FPS, phone, sustained or final-art acceptance.','shapes':{shape:verify(a.root/f'occlusion-path-{shape}',shape) for shape in ('desktop','portrait')}}
 a.output.write_text(json.dumps(summary,indent=2)+'\n');print('OCCLUSION_PATH_EVIDENCE_PASS',json.dumps(summary['shapes']))
