from pathlib import Path
import json,hashlib,sys,itertools,numpy as np
from scipy.spatial import ConvexHull
r=Path('/Users/auchan/projects/garden-of-dreams');out=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-desktop-framing';assert not out.exists();out.mkdir();sys.path.insert(0,str(r/'scripts'))
from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();glb=Glb(r/'export/garden-of-dreams.glb');lower=Glb(r/'export/kits/flora/KIT_flora_reed_LOD1.glb')
def local(g,node):return np.concatenate([g.accessor(p['attributes']['POSITION']) for p in g.doc['meshes'][node['mesh']]['primitives']])
def world(n,ps):
 assert 'matrix' not in n
 x,y,z,w=n.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 return (ps*np.array(n.get('scale',[1,1,1])))@rot.T+np.array(n.get('translation',[0,0,0]))
subjects={};names={'island':'SITE_ziling-zhou_MAT_plaster_rock','bridge':'SITE_ziling-zhou_MAT_pavilion_atlas','pavilion_roof':'SITE_ouxiang-xie_MAT_rooftile'}
for name,node_name in names.items():
 n=next(n for n in glb.doc['nodes'] if n.get('name')==node_name);subjects[name]=world(n,local(glb,n))
reeds=[]
for n in glb.doc['nodes']:
 if n.get('name','').startswith('HERO_flora_ziling_zhou_'):
  reeds.append(world(n,local(glb,n)));reeds.append(world(n,local(lower,next(n for n in lower.doc['nodes'] if 'mesh' in n))))
subjects['reeds']=np.concatenate(reeds);hulls={name:ps[ConvexHull(ps).vertices] for name,ps in subjects.items()}
def measure(pos,target,fov):
 forward=np.array(target)-pos;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward);focal=600/(2*np.tan(np.radians(fov)/2));result={}
 for name,ps in hulls.items():
  diff=ps-pos;depth=diff@forward;pixels=np.column_stack([705+(diff@right)*focal/depth,300-(diff@up)*focal/depth]);lo=pixels.min(axis=0);hi=pixels.max(axis=0)
  result[name]={'low':lo.tolist(),'high':hi.tolist(),'front':bool((depth>.06).all()),'width_fraction':float((hi[0]-lo[0])/1410),'fits':bool((depth>.06).all() and lo[0]>=12 and hi[0]<=1398 and lo[1]>=50 and hi[1]<=391)}
 return result
baseline=measure(np.array([-40.,3,6]),[-34,.6,0],55)
native=json.loads((r/'docs/reference/ziling-source-art/installed/installed-ziling/report.json').read_text());row=next(x for x in native['rows'] if x['phase']=='arrival-desktop')
for name in subjects:
 for bound in ['low','high']:assert np.max(np.abs(np.array(baseline[name][bound])-np.array(row['measurements'][name][bound])))<.002,(name,bound)
passing=[]
for x,y,z,tx,ty,tz,fov in itertools.product([-44,-43,-42,-41,-40],[2.6,3,3.2,3.3],[6,7,8,9,10],[-34,-33],[-4,-3,-2,-1,0,.6],[0,1],[55,60,65,70,75]):
 pos=np.array([float(x),y,z]);target=[tx,ty,tz];m=measure(pos,target,fov)
 if not all(q['fits'] for q in m.values()):continue
 if m['island']['width_fraction']<.23 or m['bridge']['width_fraction']<.12:continue
 # Prefer a readable island and modest lens change; all subjects fit actual UI bounds.
 score=m['island']['width_fraction']-.002*abs(fov-55)-.001*np.linalg.norm(pos-np.array([-40,3,6]))
 passing.append({'position':pos.tolist(),'target':target,'fov':fov,'keep_aspect':'KEEP_HEIGHT','measurements':m,'score':float(score)})
passing.sort(key=lambda d:d['score'],reverse=True)
report={'status':'cpu_desktop_proposals_native_review_pending','source_glb_sha256':sha(glb.path),'route_sha256':sha(r/'godot/runtime/entry_route.gd'),'baseline_native_projection_max_error_px':.002,'actual_header_bottom':38,'actual_panel_top':405,'reserved_subject_bounds_y':[50,391],'baseline':baseline,'passing_count':len(passing),'top_proposals':passing[:12],'scope':'Actual current exported island/bridge/roof and full+lower reed geometry, with convex hull projection extrema checked against native baseline under0.002px. Includes submerged island sides. CPU projections cannot prove occlusion, terrain closure, appearance, resizing, interaction or device acceptance. No production files or HEAD changed; native comparison required.'}
(out/'cpu-proposals.json').write_text(json.dumps(report,indent=2)+'\n');(out/'executed-measure.py').write_text(Path(__file__).read_text());print('ZILING_DESKTOP_CPU_BASELINE_MATCH_AND_PROPOSALS',len(passing));print(json.dumps(passing[0],indent=2) if passing else 'none')
