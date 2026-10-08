import hashlib,json,pathlib,sys
import numpy as np
from PIL import Image
sys.path.insert(0,'/Users/auchan/projects/garden-of-dreams/scripts')
from verify_mountain_export import Glb
R=pathlib.Path('/Users/auchan/projects/garden-of-dreams')
g=Glb(R/'godot/assets/garden-of-dreams.glb')
report=json.load(open('/tmp/garden-oux-visible-surface-probe-with-lightmap.json'))
candidate_path=pathlib.Path(json.load(open('/tmp/garden-oux-full-source.json'))['folder'])/'export/garden-of-dreams.glb'
candidate=Glb(candidate_path)
name='SITE_stage_MAT_plaster_rock'
n=next(x for x in g.doc['nodes'] if x.get('name')==name)
cn=next(x for x in candidate.doc['nodes'] if x.get('name')==name)
assert n==cn
assert n.get('translation')==[-18,0,-9] and not any(k in n for k in ('matrix','rotation','scale'))
parents={child:i for i,x in enumerate(g.doc['nodes']) for child in x.get('children',[])}
ni=g.doc['nodes'].index(n);assert ni not in parents
p=g.doc['meshes'][n['mesh']]['primitives'][0]
cp=candidate.doc['meshes'][cn['mesh']]['primitives'][0]
assert p.keys()==cp.keys()
for attr in p['attributes']:
 assert np.array_equal(g.accessor(p['attributes'][attr]),candidate.accessor(cp['attributes'][attr]))
assert np.array_equal(g.accessor(p['indices']),candidate.accessor(cp['indices']))
pos=g.accessor(p['attributes']['POSITION']).astype(float)+np.array(n['translation']);idx=g.accessor(p['indices']).ravel().reshape(-1,3)
boxes=[]
expected=[([-20.1,-.24,0],[-18.3,0,5]),([-25.9,-.24,4.1],[-18.3,0,5.9]),([-25.9,-.24,4.1],[-24.1,0,11.7])]
for start,(elo,ehi) in zip((156,168,180),expected):
 points=np.unique(np.round(pos[idx[start:start+12]].reshape(-1,3),6),axis=0)
 lo=points.min(axis=0);hi=points.max(axis=0)
 assert len(points)==8 and np.allclose(lo,elo,atol=1e-5,rtol=0) and np.allclose(hi,ehi,atol=1e-5,rtol=0)
 assert all(sum(abs(v[j]-lo[j])<1e-5 or abs(v[j]-hi[j])<1e-5 for j in range(3))==3 for v in points)
 boxes.append({'triangle_range':[start,start+11],'bounds_min_y_up':lo.tolist(),'bounds_max_y_up':hi.tolist(),
  'rect_xz':[elo[0],ehi[0],elo[2],ehi[2]],'saved_source_owner':'LONGCUI_approach'+('' if start==156 else '.001' if start==168 else '.002'),
  'owner_scope':'Name inferred from the checked construction script; native saved-object ownership still required before an edit.'})
old=[b['rect_xz'] for b in boxes]
new=[[-20.1,-18.3,0,4.1],old[1],[-25.9,-24.1,5.9,11.7]]
def inside(rect,x,z):return rect[0]<=x<=rect[1] and rect[2]<=z<=rect[3]
def covered(rects,x,z):return any(inside(r,x,z) for r in rects)
xs=sorted({r[i] for r in old+new for i in (0,1)})
zs=sorted({r[i] for r in old+new for i in (2,3)})
# Membership is constant on each open cell of this exact rectangular partition.
# Also test all edge and corner classes, including original/proposed seams.
x_samples=sorted(set(xs+[(a+b)/2 for a,b in zip(xs,xs[1:])]+[xs[0]-1,xs[-1]+1]))
z_samples=sorted(set(zs+[(a+b)/2 for a,b in zip(zs,zs[1:])]+[zs[0]-1,zs[-1]+1]))
for x in x_samples:
 for z in z_samples:assert covered(old,x,z)==covered(new,x,z),(x,z)
def overlaps(rects):
 return [{'a':i,'b':j,'area_m2':max(0,min(a[1],b[1])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[2],b[2]))}
  for i,a in enumerate(rects) for j,b in enumerate(rects) if i<j]
old_overlap=overlaps(old);new_overlap=overlaps(new);assert sum(x['area_m2'] for x in new_overlap)==0
def union_area(rects):
 return sum((x1-x0)*(z1-z0) for x0,x1 in zip(xs,xs[1:]) for z0,z1 in zip(zs,zs[1:]) if covered(rects,(x0+x1)/2,(z0+z1)/2))
assert abs(union_area(old)-union_area(new))<1e-10
image=np.asarray(Image.open(R/report['reference_png']).convert('RGB'))
for row in report['pixels']:x,y=row['pixel'];row['actual_native_capture_rgb8']=image[y,x].tolist()
proposal={'status':'geometry_proposal_only_not_applied','scope':'Trim only the two vertical render slabs at the crosspiece. The exact union of path surfaces/volume and all existing colliders must remain unchanged. Native saved-object inspection, a controlled source export, source-matched fresh lighting and native before/after surface views are still required.',
 'original_boxes':boxes,'proposed_render_rectangles_xz':new,
 'original_pairwise_overlap_areas_m2':old_overlap,'proposed_pairwise_overlap_areas_m2':new_overlap,
 'original_and_proposed_union_area_m2':union_area(old),
 'partition_membership_classes_checked':len(x_samples)*len(z_samples),
 'source_constructor':'scripts/refine_nunnery.py',
 'source_constructor_sha256':hashlib.sha256((R/'scripts/refine_nunnery.py').read_bytes()).hexdigest(),
 'saved_blender_native_check_pending':True,'collision_changes':False,'native_fix_render_pending':True}
report['join_repair_proposal']=proposal
report['matching_complete_bake_candidate_stage_primitive']={'path':str(candidate_path),'sha256':hashlib.sha256(candidate.bytes).hexdigest(),'all_indexed_and_unindexed_attributes_identical_to_installed_stage_path_mesh':True}
pathlib.Path('/tmp/garden-oux-nunnery-path-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n')
print('NUNNERY_PATH_PROPOSAL',sum(x['area_m2'] for x in old_overlap),'m2 overlap -> 0; exact31.5m2 footprint preserved across',len(x_samples)*len(z_samples),'partition classes')
print('NATIVE_CAPTURE_PIXEL_RGB',[(x['pixel'],x['actual_native_capture_rgb8']) for x in report['pixels']])
