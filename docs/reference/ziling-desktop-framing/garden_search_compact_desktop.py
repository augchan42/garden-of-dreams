from pathlib import Path
import json,itertools,numpy as np
from scipy.spatial import ConvexHull
p=Path('/Users/auchan/projects/garden-of-dreams/.superpowers/sdd/2026-09-23-garden-completion/ziling-desktop-framing')
d=json.loads((p/'native-inputs.json').read_text());hulls={n:np.array(v)[ConvexHull(np.array(v)).vertices] for n,v in d['subjects'].items()}
def measure(pos,target,w,h,panel):
 forward=np.array(target)-pos;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward);f=h/(2*np.tan(np.radians(55)/2));result={}
 for n,ps in hulls.items():
  diff=ps-pos;depth=diff@forward;px=np.column_stack([w/2+(diff@right)*f/depth,h/2-(diff@up)*f/depth]);lo=px.min(axis=0);hi=px.max(axis=0)
  result[n]={'low':lo.tolist(),'high':hi.tolist(),'width_fraction':float((hi[0]-lo[0])/w),'fits':bool((depth>.06).all() and lo[0]>=12 and hi[0]<=w-12 and lo[1]>=50 and hi[1]<=panel-14)}
 return result
for label,w,h,panel in [('touch',1410,600,387),('compact',891.428588867188,411.428558349609,198.428558349609)]:
 passing=[]
 for x,y,z,tx,ty,tz in itertools.product(range(-48,-34,2),[1.4,1.8,2.2,2.6,3],range(6,17,2),[-34,-33,-32],np.arange(-6,1,.25),[0]):
  pos=np.array([float(x),y,float(z)]);target=[tx,float(ty),tz];m=measure(pos,target,w,h,panel)
  if not all(v['fits'] for v in m.values()) or m['bridge']['width_fraction']<.12:continue
  score=m['island']['width_fraction']-.0005*np.linalg.norm(pos-np.array([-40,2.6,10]))
  passing.append({'position':pos.tolist(),'target':target,'fov':55,'measurements':m,'score':float(score)})
 passing.sort(key=lambda d:d['score'],reverse=True);(p/(label+'-cpu-proposals.json')).write_text(json.dumps({'count':len(passing),'top':passing[:12],'scope':'Native-input CPU proposals only. Original minimum for newly added desktop width must be established by native composition; no prior accepted requirement changed.'},indent=2));print(label,len(passing),json.dumps(passing[:2]),flush=True)
