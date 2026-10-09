from pathlib import Path
import hashlib, json, shutil, struct

repo=Path('/Users/auchan/projects/garden-of-dreams')
ledger=repo/'.superpowers/sdd/2026-09-23-garden-completion'
work=ledger/'tubi-runtime'
live=Path(json.loads(Path('/tmp/garden-tubi-framing.json').read_text())['folder'])
archive=repo/'docs/reference/tubi-portrait-framing'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
focused=json.loads((work/'accepted-focused-pipeline.json').read_text())
regressions=json.loads((work/'regression-pipeline.json').read_text())
assert focused['status']==regressions['status']=='passed'
assert len(focused['phases'])==3 and len(regressions['phases'])==13
assert focused['route_sha256']==regressions['route_sha256']==sha(repo/'godot/runtime/entry_route.gd')
assert focused['test_sha256']==sha(repo/'godot/tests/test_tubi_framing.gd')
for phase in focused['phases']+regressions['phases']:
    assert phase['exit_code']==0 and sha(phase['log'])==phase['log_sha256']
assert not archive.exists(), 'Never replace an existing evidence archive'
archive.mkdir()
files,locations,pngs={},{},[]
def copy(source,relative):
    target=archive/relative;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target);digest=sha(source);assert sha(target)==digest
    name=str(target.relative_to(repo));files[name]=digest;locations[str(source)]=name
    if target.suffix=='.png':
        b=target.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
        pngs.append({'path':name,'sha256':digest,'pixels':list(struct.unpack('>II',b[16:24]))})
for source in sorted((ledger/'tubi-framing-comparison').rglob('*')):
    if source.is_file():copy(source,Path('first-comparisons')/source.relative_to(ledger/'tubi-framing-comparison'))
for name in ['options-first','options','options-command.json','options.log']:
    source=live/name
    if source.is_file():copy(source,Path('layout-options')/name)
    else:
        for child in sorted(source.rglob('*')):
            if child.is_file():copy(child,Path('layout-options')/name/child.relative_to(source))
copy(live/'godot/tests/tubi_framing_options.gd',Path('layout-options/executed-probe.gd'))
for source in sorted(work.rglob('*')):
    if source.is_file():copy(source,Path('runtime')/source.relative_to(work))
for source in [Path('/tmp/garden_compare_tubi_framing.gd'),Path('/tmp/garden_prepare_tubi_framing.py'),Path('/tmp/garden_tubi_framing_options.gd'),Path('/tmp/garden_diagnose_tubi_resize.gd'),Path('/tmp/garden_review_tubi_framing.py'),Path(__file__)]:copy(source,Path('helpers')/source.name)
for name in ['godot/runtime/entry_route.gd','godot/runtime/entry_route.tscn','godot/tests/test_tubi_framing.gd','godot/tests/source-contract.json','godot/tests/test_import_source_contract.gd','godot/tests/test_hilltop_route.gd','godot/tests/test_study_route.gd','godot/tests/test_courtyard_route.gd','godot/tests/test_farmhouse_route.gd','godot/tests/test_mobile_ui_scaling.gd','godot/tests/test_gate_reveal.gd','godot/tests/test_first_reading_demo.gd','godot/tests/test_pond_view.gd','godot/tests/test_portrait_architecture.gd','godot/tests/test_hengwu_detail_framing.gd','godot/tests/test_oux_portrait_framing.gd']:copy(repo/name,Path('installed-code')/name)
assert len(pngs)==215, len(pngs)
for mode in ['normal','touch','density']:
    report=json.loads((work/('accepted-'+mode)/'report.json').read_text())
    assert not report['errors'] and len(report['rows'])==10
    for row in report['rows']:
        path=Path(row['capture']);assert sha(path)==row['sha256'];assert list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels']
preserved=json.loads((work/'source-preservation.json').read_text())
assert sha(repo/'blender/authoring.blend')==preserved['source']['authoring']
assert sha(repo/'godot/assets/garden-of-dreams.glb')==focused['source_glb_sha256']
for name,digest in preserved['source']['lighting_pngs'].items():assert sha(repo/name)==digest
readme='''# Hilltop portrait arrival and garden overlook

The portrait arrival keeps the complete painted moon, hall/title and staircase above the controls. A lower fixed camera has four bounded portrait framing variants for narrower and shorter layouts. Desktop arrival retains its original transform and projection. The garden overlook uses a higher camera so the central bridge pavilion is visible over the nearer roof. Resizing preserves the selected overlook and text; Look restores the arrival view. The portrait action list consistently reserves 128 logical units, with 48-unit touch targets and scrolling to the final action.

The actual public-action baseline failed 29 assertions. A first installed candidate passed normal and touch modes but failed two density return/Look stair-clearance checks. The diagnostic confirmed that scrollbar wrapping increased the list from 100 to 128 units after rotation while the description height stayed at 75. A stable reserve and revised short-view aim/FOV fix this. Three final graphical modes pass with thirty original PNGs. Thirteen adjacent import/source, hilltop climb/descent/study, courtyard/farmhouse, mobile UI, gate/demo and pond/architecture/Hengwu/Ouxiang camera regressions pass.

All 215 original PNGs are retained, including rejected earlier camera ranges, 39 first layout options, 40 lower-camera options, actual failing actions, resize diagnostics, final actions and 28 neighboring camera regression originals. Early layout probes measured the whole pavilion atlas, which also contains distant corridor roofs; those broad measurements are not central-roof acceptance. The public-action test selects actual imported roof vertices in the central pavilion region and checks them against the measured UI. Projection alone does not establish visibility. Seven final originals were directly inspected across normal, narrow touch, both density widths and desktop overlook: the hall/moon/stairs clear the controls, and the central pavilion appears beyond the near roof.

The saved Blender authoring 19eb386d, complete/exported/engine GLB 26033c99 and all 282 source/engine lighting PNGs were rechecked unchanged. This update does not alter geometry, source cameras, lighting or collision paths. No new full fourteen-room walk was run for this camera-only change; the actual hilltop climb and descent were checked on the current runtime.

Desktop density portrait windows are host-clamped to 1080×1978 and 944×1978; they are not physical-phone evidence. Small ceiling strips, backdrop/ground edges, exposed stage backs, coarse surfaces and final site art still need work. Five references, other sites, current physical-phone/2020 Adreno and sustained budgets, release and authenticated services remain required. The full goal stays active.
'''
(archive/'README.md').write_text(readme);files[str((archive/'README.md').relative_to(repo))]=sha(archive/'README.md')
index={'status':'installed_hilltop_camera_actions_and_adjacent_regressions_passed','scope':'Portrait hall/moon/stair composition, public overlook/Look and rotation/resize/touch behavior; source preserved. Desktop-native evidence, not final all-site art or phone/sustained acceptance.','source_glb_sha256':focused['source_glb_sha256'],'route_sha256':focused['route_sha256'],'test_sha256':focused['test_sha256'],'focused_modes':3,'adjacent_regressions':13,'original_png_count':len(pngs),'checked_file_count':len(files),'files':files,'artifact_locations':locations,'original_pngs':pngs}
(repo/'export/tubi-portrait-framing-evidence.json').write_text(json.dumps(index,indent=2)+'\n')
print('TUBI_ARCHIVE_CHECKED',len(files),'files',len(pngs),'originals',focused['route_sha256'])
