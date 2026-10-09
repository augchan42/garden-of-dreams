from pathlib import Path
import hashlib,json,shutil,struct
r=Path('/Users/auchan/projects/garden-of-dreams');ledger=r/'.superpowers/sdd/2026-09-23-garden-completion';w=ledger/'qiushuang-runtime';archive=r/'docs/reference/qiushuang-screen-framing';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
focused=json.loads((w/'accepted-focused-pipeline.json').read_text());regressions=json.loads((w/'regression-pipeline.json').read_text())
assert focused['status']==regressions['status']=='passed'
assert len(focused['phases'])==3 and len(regressions['phases'])==14
assert focused['route_sha256']==regressions['route_sha256']==sha(r/'godot/runtime/entry_route.gd')
assert focused['test_sha256']==sha(r/'godot/tests/test_qiushuang_framing.gd')
for phase in focused['phases']+regressions['phases']:assert phase['exit_code']==0 and sha(phase['log'])==phase['log_sha256']
assert not archive.exists(),'Do not replace an evidence archive'
archive.mkdir();files={};locations={};pngs=[]
def copy(source,relative):
 target=archive/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);digest=sha(source);assert sha(target)==digest
 name=str(target.relative_to(r));files[name]=digest;locations[str(source)]=name
 if target.suffix=='.png':
  b=target.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';pngs.append({'path':name,'sha256':digest,'pixels':list(struct.unpack('>II',b[16:24]))})
for source in sorted((ledger/'qiushuang-framing-comparison').rglob('*')):
 if source.is_file():copy(source,Path('comparisons')/source.relative_to(ledger/'qiushuang-framing-comparison'))
for source in sorted(w.rglob('*')):
 if source.is_file():copy(source,Path('runtime')/source.relative_to(w))
for name in ['/tmp/garden_test_qiushuang.py','/tmp/garden_run_qiushuang_baseline.py','/tmp/garden_review_qiushuang_framing.py',__file__]:copy(Path(name),Path('helpers')/Path(name).name)
for name in ['godot/runtime/entry_route.gd','godot/runtime/entry_route.tscn','godot/tests/test_qiushuang_framing.gd','godot/tests/test_tubi_framing.gd','godot/tests/source-contract.json','godot/tests/test_import_source_contract.gd','godot/tests/test_hilltop_route.gd','godot/tests/test_study_route.gd','godot/tests/test_courtyard_route.gd','godot/tests/test_farmhouse_route.gd','godot/tests/test_mobile_ui_scaling.gd','godot/tests/test_gate_reveal.gd','godot/tests/test_first_reading_demo.gd','godot/tests/test_pond_view.gd','godot/tests/test_portrait_architecture.gd','godot/tests/test_hengwu_detail_framing.gd','godot/tests/test_oux_portrait_framing.gd']:copy(r/name,Path('installed-code')/name)
for mode in ['normal','touch','density']:
 report=json.loads((w/('accepted-'+mode)/'report.json').read_text());assert not report['errors'] and len(report['rows'])==18
 for row in report['rows']:
  path=Path(row['capture']);assert sha(path)==row['sha256'] and list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels']
preserved=json.loads((w/'source-preservation.json').read_text());assert sha(r/'blender/authoring.blend')==preserved['source']['authoring']
for n in ['export/garden-of-dreams.glb','godot/assets/garden-of-dreams.glb']:assert sha(r/n)==focused['source_glb_sha256']
for name,digest in preserved['source']['lighting_pngs'].items():assert sha(r/name)==digest
readme='''# Bulletin hall overview and screen banks

The portrait overview shows the complete Qiushuang roof and three groups of four amber monitors above the controls. Each public screen-bank action brings its four-monitor rack closer. Resizing preserves the selected bank and text; rotation restores the original desktop arrival or bank pose; Look restores the overview and clears the bank selection. A stable 128-unit portrait action area preserves 48-unit touch targets and scrolling to the last action.

The actual public-action baseline failed 22 assertions. Three final graphical modes pass with 54 original PNGs, covering normal and narrow portraits, desktop rotation, return, all three bank actions and Look. Fourteen adjacent import/source, actual bulletin/study and hilltop climb/descent, courtyard/farmhouse, mobile UI, gate/demo and pond/architecture/Hengwu/Tubi/Ouxiang camera regressions pass.

All comparison attempts are retained: the first produced 46 originals and failed to find six overview fits; the second produced 52 but showed too much ceiling and a small facade; the third produced 52 and supplied the chosen moderate lower view; the fourth produced 13 but tilted the building too much despite fitting projected bounds. The first probes used conservative whole-batch boxes. The third verifies 84 convex-hull points against all 30,987 imported facade vertices to within 0.009034 logical pixels. The final public-action test projects actual facade vertices rather than impossible whole-box roof corners. Its bank-region selection checks the imported four-monitor rack, not complete desk/lantern or lattice geometry. Lattice visibility and occlusion require the original rendered images.

Eight final originals were directly inspected: normal overview and all three bank close-ups, narrow touch Look, wide density return, narrow density centre bank and original desktop arrival. All three bank close-ups show four distinct screens behind their lattice. The lattice crosses some screen text, the central wall remains bright and mottled, and broad ceiling/ground areas and stage/background closure still need final art work. This is incremental camera/UI acceptance, not final site-art acceptance. Static screen artwork is not connected to live bulletins.

The saved Blender authoring 19eb386d, complete export/engine GLB 26033c99 and all 282 source/engine lighting PNGs were rechecked unchanged. No geometry, authored cameras, lights or collisions were changed. No new full fourteen-room walk was run for this camera update; current actual bulletin approach/return and hilltop climb/descent checks pass. Density windows are desktop-host-clamped, not physical-phone evidence. Android packages are stale. Final art across fourteen sites, five references, current physical-phone/2020 Adreno and sustained budgets, release and authenticated services remain required. The full goal stays active.
'''
(archive/'README.md').write_text(readme);files[str((archive/'README.md').relative_to(r))]=sha(archive/'README.md')
index={'status':'installed_bulletin_camera_actions_and_adjacent_regressions_passed','scope':'Portrait facade and all three public monitor-bank views, Look/resize/rotation/touch behavior; source preserved. Native desktop evidence, not final all-site art or physical-device/sustained acceptance.','source_glb_sha256':focused['source_glb_sha256'],'route_sha256':focused['route_sha256'],'test_sha256':focused['test_sha256'],'focused_modes':3,'adjacent_regressions':14,'original_png_count':len(pngs),'checked_file_count':len(files),'files':files,'artifact_locations':locations,'original_pngs':pngs}
(r/'export/qiushuang-screen-framing-evidence.json').write_text(json.dumps(index,indent=2)+'\n')
print('QIUSHUANG_ARCHIVE_CHECKED',len(files),'files',len(pngs),'originals',focused['route_sha256'])
