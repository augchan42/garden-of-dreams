"""Check exported paving scope against the unchanged current production GLBs."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/paving-site-joins'
root=Path('/tmp/garden-paving-joins-20261010-v3')
sys.path.insert(0,str(repo/'scripts'))
from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline=json.loads((work/'saved-paving-baseline-all-polygons.json').read_text())
source=json.loads((root/'source-preservation.json').read_text())
names={r['object'] for r in source['changed_objects']}
allowed={c+'_'+('_'.join(o['materials']) or 'geometry') for o in baseline['objects'] if o['name'] in names for c in o['collections'] if c.startswith('SITE_')}
assert len(names)==26 and len(allowed)==8

def compare(oldpath,newpath):
    a,b=Glb(oldpath),Glb(newpath)
    for key in ['asset','scene','scenes','nodes','cameras','extensionsUsed','extensionsRequired','extensions']:
        assert a.doc.get(key)==b.doc.get(key),key
    assert {m['name']:a.material(m) for m in a.doc['materials']}=={m['name']:b.material(m) for m in b.doc['materials']}
    assert {i['name']:a.image_hash(i) for i in a.doc['images']}=={i['name']:b.image_hash(i) for i in b.doc['images']}
    changed=[];preserved=0;triangles=0
    for node,other in zip(a.doc['nodes'],b.doc['nodes']):
        if 'mesh' not in node:continue
        name=node['name'];ma=a.doc['meshes'][node['mesh']];mb=b.doc['meshes'][other['mesh']]
        assert {k:v for k,v in ma.items() if k!='primitives'}=={k:v for k,v in mb.items() if k!='primitives'}
        assert len(ma['primitives'])==len(mb['primitives'])
        differs=False
        for pa,pb in zip(ma['primitives'],mb['primitives']):
            assert {k:v for k,v in pa.items() if k not in ['attributes','indices']}=={k:v for k,v in pb.items() if k not in ['attributes','indices']}
            assert pa['attributes'].keys()==pb['attributes'].keys()
            ia,ib=a.accessor(pa['indices']).ravel(),b.accessor(pb['indices']).ravel()
            assert len(ib)%3==0
            if not name.startswith('COL_'):triangles+=len(ib)//3
            for attr in pa['attributes']:
                va,vb=a.accessor(pa['attributes'][attr])[ia],b.accessor(pb['attributes'][attr])[ib]
                assert np.isfinite(vb).all(),(name,attr)
                same=va.shape==vb.shape and np.array_equal(va,vb)
                if not same:differs=True
                if name not in allowed:assert same,('Unrelated expanded attribute changed',name,attr)
        if differs:changed.append(name)
        else:preserved+=1
    assert set(changed)<=allowed
    return {'before_sha256':sha(oldpath),'after_sha256':sha(newpath),'changed_batches':changed,'preserved_meshes':preserved,'render_triangles':triangles,'materials':len(b.doc['materials']),'images':len(b.doc['images'])}
master=compare(repo/'export/garden-of-dreams.glb',root/'export/garden-of-dreams.glb')
assert set(master['changed_batches'])==allowed
assert master['render_triangles']==266447<300000
sites={}
for old in sorted((repo/'export/sites').glob('*.glb')):
    new=root/'export/sites'/old.name
    if old.read_bytes()==new.read_bytes():sites[old.name]={'byte_identical':True,'sha256':sha(new)}
    else:sites[old.name]=compare(old,new)
assert len(sites)==15 and sum(r.get('byte_identical',False) for r in sites.values())==8
counts={'cameras':sum('camera' in n for n in Glb(root/'export/garden-of-dreams.glb').doc['nodes']),
        'colliders':sum(n['name'].startswith('COL_') for n in Glb(root/'export/garden-of-dreams.glb').doc['nodes']),
        'markers':sum(n['name'].startswith('TRG_') for n in Glb(root/'export/garden-of-dreams.glb').doc['nodes'])}
assert counts=={'cameras':42,'colliders':454,'markers':71}
report={'status':'paving_export_preservation_passed','candidate_authoring_sha256':sha(root/'blender/authoring.blend'),'master':master,'sites':sites,'counts':counts,'changed_source_objects':sorted(names),'scope':'Eight intended render batches change from26floor owners. All other expanded mesh attributes, node/camera/light/COL/marker hierarchy and all material/embedded image contents retained. Eight site GLBs byte exact. No source lighting or native appearance acceptance.'}
(root/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PAVING_EXPORT_PRESERVATION_PASS',len(allowed),'changed batches;',master['preserved_meshes'],'preserved;',master['render_triangles'],'render triangles')
