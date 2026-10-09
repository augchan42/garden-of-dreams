"""Independently audit saved paving polygons and their complete footprint.

Input records come from a read-only Blender inspection of the saved source.
Intersection uses point/edge enumeration; footprint uses scanline unions.
Neither algorithm uses the partitioner's polygon-subtraction implementation.
"""
import argparse, json, math
from pathlib import Path


def area(p):
    return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1])))/2 if len(p)>2 else 0


def contains(p, polygon):
    sides=[(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]) for a,b in zip(polygon,polygon[1:]+polygon[:1])]
    return min(sides)>=-1e-8 or max(sides)<=1e-8


def crossing(a,b,c,d):
    u=[b[k]-a[k] for k in (0,1)];v=[d[k]-c[k] for k in (0,1)]
    denominator=u[0]*v[1]-u[1]*v[0]
    if abs(denominator)<1e-12:return None
    w=[c[k]-a[k] for k in (0,1)]
    t=(w[0]*v[1]-w[1]*v[0])/denominator;s=(w[0]*u[1]-w[1]*u[0])/denominator
    if -1e-9<=t<=1+1e-9 and -1e-9<=s<=1+1e-9:return [a[k]+t*u[k] for k in (0,1)]
    return None


def intersection(a,b):
    if max(p[0] for p in a)<min(p[0] for p in b) or max(p[0] for p in b)<min(p[0] for p in a) or max(p[1] for p in a)<min(p[1] for p in b) or max(p[1] for p in b)<min(p[1] for p in a):return []
    candidates=[p for p in a if contains(p,b)]+[p for p in b if contains(p,a)]
    for u,v in zip(a,a[1:]+a[:1]):
        for w,x in zip(b,b[1:]+b[:1]):
            hit=crossing(u,v,w,x)
            if hit is not None:candidates.append(hit)
    unique={tuple(round(v,9) for v in p) for p in candidates}
    if len(unique)<3:return []
    centre=[sum(p[k] for p in unique)/len(unique) for k in (0,1)]
    return [list(p) for p in sorted(unique,key=lambda p:math.atan2(p[1]-centre[1],p[0]-centre[0]))]


def faces(document):
    return [{'owner':o['name'],**f} for o in document['objects'] for f in o['top_faces']]


def overlaps(rows):
    result=[]
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            if abs(a['height']-b['height'])>1e-5:continue
            shape=intersection(a['xy'],b['xy']);size=area(shape)
            if size>1e-5:result.append({'owners':[a['owner'],b['owner']],'faces':[a['polygon'],b['polygon']],'area_m2':size,'height':a['height'],'xy':shape})
    return result


def intervals(rows,x):
    segments=[]
    for face in rows:
        points=face['xy'];hits=[]
        for a,b in zip(points,points[1:]+points[:1]):
            if min(a[0],b[0])<x<max(a[0],b[0]):hits.append(a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]))
        if hits:segments.append([min(hits),max(hits)])
    result=[]
    for low,high in sorted(segments):
        if result and low<=result[-1][1]+1e-8:result[-1][1]=max(result[-1][1],high)
        else:result.append([low,high])
    return result


def compare_footprint(before,after):
    heights=sorted({round(f['height'],5) for f in before+after});records=[]
    for height in heights:
        old=[f for f in before if round(f['height'],5)==height];new=[f for f in after if round(f['height'],5)==height]
        edges=[(a,b) for f in old+new for a,b in zip(f['xy'],f['xy'][1:]+f['xy'][:1])]
        breaks={p[0] for f in old+new for p in f['xy']}
        for i,(a,b) in enumerate(edges):
            for c,d in edges[i+1:]:
                hit=crossing(a,b,c,d)
                if hit is not None:breaks.add(hit[0])
        xs=sorted(breaks);old_area=new_area=0.;columns=0
        for a,b in zip(xs,xs[1:]):
            if b-a<1e-7:continue
            x=(a+b)/2;oi=intervals(old,x);ni=intervals(new,x)
            assert len(oi)==len(ni) and all(abs(u-v)<1e-5 for p,q in zip(oi,ni) for u,v in zip(p,q)),('Paving footprint changed',height,x,oi,ni)
            old_area+=(b-a)*sum(q-p for p,q in oi);new_area+=(b-a)*sum(q-p for p,q in ni);columns+=1
        assert abs(old_area-new_area)<1e-5
        records.append({'height':height,'old_union_m2':old_area,'new_union_m2':new_area,'partition_columns':columns})
    return records


def main():
    p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--require-disjoint',action='store_true');args=p.parse_args()
    # Analytic controls: overlapping rectangles, shared edges and a diagonal crossing.
    a=[[0,0],[2,0],[2,2],[0,2]];b=[[1,1],[3,1],[3,3],[1,3]]
    assert abs(area(intersection(a,b))-1)<1e-8
    assert area(intersection(a,[[2,0],[3,0],[3,2],[2,2]]))==0
    assert abs(area(intersection(a,[[1,-1],[3,1],[1,3],[-1,1]]))-4)<1e-8
    before=json.loads(args.before.read_text());after=json.loads(args.after.read_text()) if args.after else before
    old,new=faces(before),faces(after);bad=overlaps(new)
    footprint=compare_footprint(old,new) if args.after else []
    report={'status':'saved_paving_disjoint_and_footprint_preserved' if not bad else 'saved_paving_overlap_rejected','baseline_authoring_sha256':before['authoring_sha256'],'candidate_authoring_sha256':after['authoring_sha256'],'before_top_faces':len(old),'after_top_faces':len(new),'positive_coplanar_pairs':bad,'footprint':footprint,'analytic_controls_passed':3,'scope':'Independent actual saved top-polygon intersections and scanline union/height equality at every vertex/edge-crossing partition. No render or lighting acceptance.'}
    args.output.write_text(json.dumps(report,indent=2)+'\n');print('PAVING_AUDIT',len(bad),'overlap pairs;',len(footprint),'height groups',flush=True)
    if args.require_disjoint:assert not bad,'Positive-area duplicate paving surfaces remain'


if __name__=='__main__':main()
