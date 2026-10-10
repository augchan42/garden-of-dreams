from pathlib import Path
import argparse,hashlib,json,math
from PIL import Image
VARIANTS=['disabled','enabled','disabled_repeat']
def images(directory,name,records=None):
 result=[]
 for variant in VARIANTS:
  path=directory/f'{name}-{variant}.png'
  with Image.open(path) as im:
   assert im.mode=='RGBA' and im.size==(1410,600)
   data=im.tobytes()
  if records:
   r=records[variant]
   assert hashlib.sha256(path.read_bytes()).hexdigest()==r['file_sha256']
   assert hashlib.sha256(data).hexdigest()==r['pixel_sha256']
   assert r['automatic_frames_elapsed']>=20 and r['draws']>0 and r['primitives']>0
  result.append(data)
 assert result[0]==result[2],name+': off-repeat baseline differs'
 return result
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--cpu',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
partial=args.root/'occlusion-scoped-path-desktop';j=json.loads((partial/'report.json').read_text());assert len(j['cases'])==63
assert j['source_glb_sha256']=='faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f'
assert j['route_sha256']=='bee7c9f810641f8b3c5f223d8ec9571e641e8fe21f55969d274254822f7e7d3b'
for name,row in j['cases'].items():
 data=images(partial,name,row['comparisons']);assert data[0]==data[1]
 assert row['comparisons']['enabled']['draws']<=150 and row['comparisons']['enabled']['primitives']<=300000
bad=images(partial,'leg-2-frame-150')
differences=[i//4 for i in range(0,len(bad[0]),4) if bad[0][i:i+4]!=bad[1][i:i+4]]
assert differences==[259*1410+779]
assert list(bad[0][differences[0]*4:differences[0]*4+4])==[54,35,18,255]
assert list(bad[1][differences[0]*4:differences[0]*4+4])==[54,35,17,255]
focused=args.root/'occlusion-focused-path-desktop';f=json.loads((focused/'report.json').read_text());assert len(f['cases'])==21
for name,row in f['cases'].items():
 data=images(focused,name,row['comparisons']);assert data[0]==data[1]
producer=json.loads((partial/'actual-producer-roundtrip.json').read_text());s=producer['samples']['public_roundtrip'];b=producer['budget_results']['public_roundtrip']
assert producer['render_budget_scope']=='engine_global_all_viewports' and s['frames']>3000
assert s['global_draw_calls_max']==139 and s['global_primitives_max']==163083
assert b['draw_calls'] and b['primitives'] and not b['p95_60fps']
cpu=json.loads(args.cpu.read_text());assert cpu['exit_code']==0 and len(cpu['phases'])==9
for room in ['terminal_room','rockery_gate','qinfang_ting']:
 phases=[cpu['phases'][room+'-'+v] for v in VARIANTS]
 for phase in phases:assert phase['native']['automatic_render_frames']>=460 and phase['native']['sample_frames']==480
 baseline=sum(phase['cpu_seconds_per_wall_second'] for phase in [phases[0],phases[2]])/2
 assert math.isclose(phases[1]['cpu_seconds_per_wall_second']/baseline,cpu['pairs'][room]['candidate_over_baseline'])
 if room=='qinfang_ting':assert all(not phase['native']['occlusion_active'] for phase in phases)
report={'status':'verified_evidence_of_scoped_replay_failure_and_CPU_tradeoff','scope':'63 passing scoped cases before one failed pixel;21 fresh nearby poses do not replay the unrecorded original failed pose. No adoption/continuous-image/frame-rate/device acceptance.','partial_passing_cases':63,'partial_decoded_images':189,'failed_pixel':[779,259],'failed_blue_values':[18,17],'failed_case_decoded_images':3,'focused_cases':21,'focused_decoded_images':63,'public_roundtrip_draws_max':s['global_draw_calls_max'],'public_roundtrip_primitives_max':s['global_primitives_max'],'public_roundtrip_p95_ms':s['frame_interval_p95_ms'],'actual_controller_CPU_pairs':cpu['pairs']}
args.output.write_text(json.dumps(report,indent=2)+'\n');print('SCOPED_DIAGNOSTIC_EVIDENCE_VERIFIED; candidate remains unadopted',json.dumps({k:v for k,v in report.items() if k!='actual_controller_CPU_pairs'}))
