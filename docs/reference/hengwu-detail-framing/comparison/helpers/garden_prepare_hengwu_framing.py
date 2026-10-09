from pathlib import Path
import json,hashlib,shutil,tempfile
repo=Path('/Users/auchan/projects/garden-of-dreams');work=Path(tempfile.mkdtemp(prefix='garden-hengwu-detail-framing-')).resolve()
source=Path(json.load(open('/tmp/garden-hengwu-full-review.json'))['folder']).resolve()/'godot'
shutil.copytree(source,work/'godot',ignore=shutil.ignore_patterns('acceptance-captures','captures','android','export','*.log'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(work/'godot/assets/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')=='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
contract=json.load(open(repo/'godot/tests/source-contract.json'));rock=contract['colliders']['COL_hengwu_rock']
assert rock['transform']==[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
low=[min(p[i] for p in rock['faces']) for i in range(3)];high=[max(p[i] for p in rock['faces']) for i in range(3)]
probe={'source_glb_sha256':contract['source_glb_sha256'],'rock_bounds':[low,high],'tabletop_bounds':[[-20.9,.71,-15.275],[-19.1,.925,-14.125]],'book_bounds':[[-20.325,.835,-14.93],[-19.675,.915,-14.47]],'scope':'Conservative stone collider bounds and source-preserved tabletop/book bounds. Candidate camera-only probe; not production acceptance.'}
(work/'godot/tests/hengwu-framing-probe.json').write_text(json.dumps(probe,indent=2)+'\n')
shutil.copy2('/tmp/garden_compare_hengwu_detail_framing.gd',work/'godot/tests/compare_hengwu_detail_framing.gd')
(work/'preparation.json').write_text(json.dumps({'status':'camera_probe_prepared','folder':str(work),'source_glb_sha256':probe['source_glb_sha256'],'route_sha256':sha(repo/'godot/runtime/entry_route.gd'),'probe':probe},indent=2)+'\n')
Path('/tmp/garden-hengwu-detail-framing.json').write_text(json.dumps({'folder':str(work)},indent=2)+'\n')
print('HENGWU_DETAIL_PROBE_PREPARED',work,flush=True)
