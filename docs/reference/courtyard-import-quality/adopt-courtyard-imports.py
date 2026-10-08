import hashlib,json,pathlib,shutil,subprocess
root=pathlib.Path('/Users/auchan/projects/garden-of-dreams')
ptr=json.load(open('/tmp/garden-roof-detail.json')); work=pathlib.Path(ptr['folder']); fixture=pathlib.Path(ptr['fixture'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(base):return {p.relative_to(base).as_posix():sha(p) for p in sorted(base.rglob('*')) if p.is_file() and '.godot' not in p.parts and 'android' not in p.parts}
assert sha(root/'blender/authoring.blend')==ptr['source_blend_sha256']
assert sha(root/'export/garden-of-dreams.glb')==sha(root/'godot/assets/garden-of-dreams.glb')==sha(fixture/'assets/garden-of-dreams.glb')==ptr['source_glb_sha256']
expected={'lightmaps/SITE_xiaoxiang-guan_MAT_whitewash.png.import','lightmaps/SITE_xiaoxiang-guan_MAT_lattice_wood.png.import'}
before=json.loads((work/'before-wall-imports.json').read_text()); assert len(before)==141
assert set(before)=={p.relative_to(root/'godot').as_posix() for p in (root/'godot/lightmaps').rglob('*.png.import')}
assert all(sha(root/'godot'/p)==h for p,h in before.items()),'Production imports drifted'
changed={p for p,h in before.items() if sha(fixture/p)!=h}; assert changed==expected,changed
pngs=sorted((root/'godot/lightmaps').rglob('*.png')); assert len(pngs)==141
assert all(sha(p)==sha(fixture/p.relative_to(root/'godot')) for p in pngs),'Source maps drifted'
candidate={p:sha(fixture/p) for p in expected}
(work/'scripts').mkdir(exist_ok=True); shutil.copy2(root/'scripts/configure_lightmap_imports.py',work/'scripts/configure_lightmap_imports.py')
run=subprocess.run(['python3',str(work/'scripts/configure_lightmap_imports.py'),'--size-limit','256'],capture_output=True,text=True)
(work/'configure-rule.log').write_text(run.stdout+run.stderr); assert run.returncode==0,run.stderr
assert {p for p,h in before.items() if sha(fixture/p)!=h}==expected
assert all(sha(fixture/p)==candidate[p] for p in expected),'Persistent rule differs from tested candidate'
pre=snapshot(root/'godot'); backups=work/'production-import-backups';backups.mkdir(exist_ok=True)
for p in sorted(expected):
 shutil.copy2(root/'godot'/p,backups/pathlib.Path(p).name)
 shutil.copy2(fixture/p,root/'godot'/p)
post=snapshot(root/'godot');assert set(pre)==set(post)
assert {p for p in pre if pre[p]!=post[p]}==expected
report={'status':'applied_pending_production_import','source_glb_sha256':ptr['source_glb_sha256'],'authoring_sha256':ptr['source_blend_sha256'],'source_maps_unchanged':{p.relative_to(root/'godot').as_posix():sha(p) for p in pngs},'before_import_sha256':before,'after_import_sha256':{p:sha(root/'godot'/p) for p in before},'changed_files':sorted(expected),'unchanged_godot_files_count':len(pre)-2,'configuration_command':run.args,'configuration_output':run.stdout,'scope':'Two runtime GPU imports only; source PNGs, GLB, Blender source, shaders, cameras, collision and runtime remain unchanged. Roof art and complete goal acceptance remain open.'}
(work/'production-adoption.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','changed_files','unchanged_godot_files_count']}))
