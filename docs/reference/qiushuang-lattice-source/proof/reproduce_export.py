import bpy,sys,hashlib,runpy,json
from pathlib import Path
repo=Path('/Users/auchan/projects/garden-of-dreams');r=Path('/tmp/garden-qiushuang-lattice-20261010')
sys.path.insert(0,str(repo/'scripts'))
from moon_paint_contract import snapshot
before=snapshot();source=Path(bpy.data.filepath);source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
mode=sys.argv[sys.argv.index('--')+1]
reference=repo if mode=='baseline' else r
exporter=repo/'scripts/export_garden.py' if mode=='red' else r/'canonical_export_garden.py'
out=r/('canonical-replay-'+mode)
sys.argv=['export_garden.py','--','--output-root',str(out)]
runpy.run_path(str(exporter),run_name='__main__')
after=snapshot()
for name,record in before['objects'].items():assert after['objects'][name]==record,name
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
files=['export/garden-of-dreams.glb']+[str(p.relative_to(reference)) for p in (reference/'export/sites').glob('*.glb')]
changed=[name for name in files if (reference/name).read_bytes()!=(out/name).read_bytes()]
report={'status':'passed' if not changed else 'canonical_source_reexport_mismatch','mode':mode,'saved_source_sha256':source_sha,'exporter_sha256':hashlib.sha256(exporter.read_bytes()).hexdigest(),'compared_files':len(files),'changed_files':changed,'source_objects_preserved':len(before['objects'])}
(r/('canonical-replay-'+mode+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print('QIUSHUANG_CANONICAL_REPLAY',report,flush=True)
assert not changed,changed
