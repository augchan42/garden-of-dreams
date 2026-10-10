#!/usr/bin/env python3
"""Validate the isolated fixed-clock arrival evidence; never grants phone/FPS acceptance."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOMS={'terminal_room','rockery_gate','qinfang_ting','ouxiang_xie','ziling_zhou','qiushuang_zhai','tubi_tang','hengwu_yuan','daoxiang_cun','aojing_guan','longcui_an','xiaoxiang_guan','yihong_yuan','daguan_lou'}
VARIANTS={'disabled','enabled','disabled_repeat'}
def sha(data):return hashlib.sha256(data).hexdigest()
def verify(directory,shape):
 report=json.loads((directory/'report.json').read_text())
 assert report['source_glb_sha256']=='faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f'
 assert set(report['rooms'])==ROOMS
 assert len(report['occluders'])==5
 rows={}
 for room,records in report['rooms'].items():
  assert set(records)==VARIANTS
  pixels=[]
  for variant,record in records.items():
   path=directory/f'{room}-{variant}.png'
   assert sha(path.read_bytes())==record['file_sha256']
   with Image.open(path) as image:
    assert image.mode=='RGBA'
    assert image.size==((390,844) if shape=='portrait' else (1410,600))
    data=image.tobytes()
   assert sha(data)==record['pixel_sha256']
   pixels.append(data)
   assert type(record['automatic_frames_elapsed']) is int and record['automatic_frames_elapsed']>=20
   assert type(record['draws']) is int and record['draws']>0
   assert type(record['primitives']) is int and record['primitives']>0
  assert pixels[0]==pixels[1]==pixels[2],f'{shape}/{room}: pixels differ'
  baseline=records['disabled'];candidate=records['enabled'];repeat=records['disabled_repeat']
  assert baseline['draws']==repeat['draws'] and baseline['primitives']==repeat['primitives']
  assert candidate['draws']<=baseline['draws']
  assert candidate['primitives']<=baseline['primitives']
  assert candidate['draws']<=150 and candidate['primitives']<=300000
  rows[room]={'baseline_draws':baseline['draws'],'candidate_draws':candidate['draws'],'candidate_primitives':candidate['primitives'],'pixels_identical':True}
 return rows
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args()
 summary={'scope':'Isolated fixed-clock stationary native arrivals only. No production adoption, moving-camera, CPU/FPS, phone, sustained or final-art acceptance.','shapes':{}}
 for shape in ('desktop','portrait'):summary['shapes'][shape]=verify(args.root/f'occlusion-{shape}-validated',shape)
 args.output.write_text(json.dumps(summary,indent=2)+'\n')
 print('OCCLUSION_ARRIVAL_EVIDENCE_PASS: 28 cases, 84 decoded PNGs; identical pixels; actual frames; global draw/primitive counts within limits')
