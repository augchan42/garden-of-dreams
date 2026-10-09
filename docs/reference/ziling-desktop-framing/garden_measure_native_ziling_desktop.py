from pathlib import Path
import json,hashlib,itertools,numpy as np
from scipy.spatial import ConvexHull
r=Path('/Users/auchan/projects/garden-of-dreams');out=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-desktop-framing';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();data=json.loads((out/'native-inputs.json').read_text());assert data['status']=='actual_native_desktop_inputs_extracted';assert data['source_glb_sha256']==sha(r/'godot/assets/garden-of-dreams.glb');assert data['route_sha256']==sha(r/'godot/runtime/entry_route.gd');assert data['logical_viewport']==[1410,600] and data['header_bottom']==38 and data['panel_top']==405
hulls={name:np.array(ps)[ConvexHull(np.array(ps)).vertices] for name,ps in data['subjects'].items()}
def measure(pos,target,fov,basis=None):
 if basis is None:
  forward=np.array(target)-pos;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
 else:right=np.array(basis[0]);up=np.array(basis[1]);forward=-np.array(basis[2])
 focal=600/(2*np.tan(np.radians(fov)/2));result={}
 for name,ps in hulls.items():
  diff=ps-pos;depth=diff@forward;pixels=np.column_stack([705+(diff@right)*focal/depth,300-(diff@up)*focal/depth]);lo=pixels.min(axis=0);hi=pixels.max(axis=0)
  result[name]={'low':lo.tolist(),'high':hi.tolist(),'front':bool((depth>.06).all()),'width_fraction':float((hi[0]-lo[0])/1410),'fits':bool((depth>.06).all() and lo[0]>=12 and hi[0]<=1398 and lo[1]>=50 and hi[1]<=391)}
 return result
baseline=measure(np.array(data['camera_position']),None,data['fov'],data['camera_basis_columns']);errors={name:max(float(np.max(np.abs(np.array(baseline[name][key])-np.array(data['native_projected_bounds'][name][key])))) for key in ['low','high']) for name in hulls};assert max(errors.values())<.002,errors
prior=json.loads((r/'docs/reference/ziling-source-art/installed/installed-ziling/report.json').read_text());previous=next(x for x in prior['rows'] if x['phase']=='arrival-desktop')
assert max(np.max(np.abs(np.array(data['native_projected_bounds'][name][key])-np.array(previous['measurements'][name][key]))) for name in hulls for key in ['low','high'])<.002
passing=[]
for x,y,z,tx,ty,tz,fov in itertools.product([-44,-43,-42,-41,-40],[2.6,3,3.2,3.3],[6,7,8,9,10],[-34,-33],[-4,-3,-2,-1,0,.6],[0,1],[55,60,65,70,75]):
 pos=np.array([float(x),y,z]);target=[tx,ty,tz];m=measure(pos,target,fov)
 if not all(q['fits'] for q in m.values()):continue
 if m['island']['width_fraction']<.23 or m['bridge']['width_fraction']<.12:continue
 score=m['island']['width_fraction']-.002*abs(fov-55)-.001*np.linalg.norm(pos-np.array([-40,3,6]))
 passing.append({'position':pos.tolist(),'target':target,'fov':fov,'keep_aspect':'KEEP_HEIGHT','measurements':m,'score':float(score)})
passing.sort(key=lambda d:d['score'],reverse=True)
report={'status':'native_inputs_cpu_proposals_render_review_pending','source_glb_sha256':data['source_glb_sha256'],'route_sha256':data['route_sha256'],'native_inputs_sha256':sha(out/'native-inputs.json'),'baseline_projection_error_pixels':errors,'original_guard_pixels':.002,'actual_header_bottom':38,'actual_panel_top':405,'reserved_subject_bounds_y':[50,391],'baseline':baseline,'passing_count':len(passing),'top_proposals':passing[:16],'scope':'Actual current imported world vertices plus native camera basis; the original0.002px baseline guard passes without relaxation. Prior original native bounds also match. CPU candidates use full island/bridge/roof and both reed LODs, including submerged island sides. No native proposed-camera, occlusion, render quality, interaction/resizing or device acceptance yet.'}
(out/'native-input-cpu-proposals.json').write_text(json.dumps(report,indent=2)+'\n');(out/'executed-native-measure.py').write_text(Path(__file__).read_text());print('NATIVE_BASELINE_ORIGINAL_GUARD_PASS',errors);print('PASSING_PROPOSALS',len(passing));print(json.dumps(passing[:3],indent=2))
