from pathlib import Path
import hashlib,json,shutil,struct
r=Path('/Users/auchan/projects/garden-of-dreams');l=r/'.superpowers/sdd/2026-09-23-garden-completion';w=l/'ziling-runtime';a=r/'docs/reference/ziling-portrait-framing';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f=json.loads((w/'accepted-focused-pipeline.json').read_text());g=json.loads((w/'regression-pipeline.json').read_text());assert f['status']==g['status']=='passed';assert len(f['phases'])==3 and len(g['phases'])==10
assert f['route_sha256']==g['route_sha256']==sha(r/'godot/runtime/entry_route.gd');assert f['test_sha256']==sha(r/'godot/tests/test_ziling_framing.gd')
for phase in f['phases']+g['phases']:assert phase['exit_code']==0 and sha(phase['log'])==phase['log_sha256']
assert not a.exists(),'Do not overwrite immutable evidence';a.mkdir();files={};locations={};pngs=[]
def cp(src,rel):
 dst=a/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src);assert sha(dst)==digest;name=str(dst.relative_to(r));files[name]=digest;locations[str(src)]=name
 if dst.suffix=='.png':
  b=dst.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';pngs.append({'path':name,'sha256':digest,'pixels':list(struct.unpack('>II',b[16:24]))})
for folder,label in [(l/'ziling-framing-comparison','early-comparisons'),(l/'ziling-roof-axis-comparison','roof-axis-comparisons'),(w,'runtime')]:
 for src in sorted(folder.rglob('*')):
  if src.is_file():cp(src,Path(label)/src.relative_to(folder))
for name in ['/tmp/garden_test_ziling.py','/tmp/garden_run_ziling_baseline.py','/tmp/garden_review_ziling_framing.py',__file__]:cp(Path(name),Path('helpers')/Path(name).name)
code=['godot/runtime/entry_route.gd','godot/runtime/entry_route.tscn','godot/tests/test_ziling_framing.gd','godot/tests/test_import_source_contract.gd','godot/tests/source-contract.json','godot/tests/test_western_route.gd','godot/tests/test_mobile_ui_scaling.gd','godot/tests/test_pond_view.gd','godot/tests/test_tubi_framing.gd','godot/tests/test_qiushuang_framing.gd','godot/tests/test_portrait_architecture.gd','godot/tests/test_hengwu_detail_framing.gd','godot/tests/test_oux_portrait_framing.gd','godot/garden_preview.tscn','godot/materials/water.tres','godot/materials/stage/fog.tres','godot/shaders/pond_reflection.gdshader']
for name in code:cp(r/name,Path('installed-code')/name)
for report in a.rglob('report.json'):
 x=json.loads(report.read_text())
 for row in x.get('rows',[]):
  if 'capture' not in row:continue
  path=report.parent/Path(row['capture']).name;assert path.exists(),path
  if 'sha256' in row:assert sha(path)==row['sha256'],path
  if 'pixels' in row:assert list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels'],path
s=json.loads((w/'source-preservation.json').read_text())['source'];assert sha(r/'blender/authoring.blend')==s['authoring']
for name in ['export/garden-of-dreams.glb','godot/assets/garden-of-dreams.glb']:assert sha(r/name)==f['source_glb_sha256']
for name,digest in s['lighting_pngs'].items():assert sha(r/name)==digest,name
assert len(pngs)==161,len(pngs)
readme='''# Reed island portrait framing and resize behavior

The installed portrait camera keeps the complete Ziling island, footbridge, both authored reed LOD silhouettes and the distant Ouxiang pavilion roof above measured UI. Its 3.2 m high viewpoint uses a 70 degree horizontal field of view. The island is at least 45% of the view width; the bridge is at least 18%, and the complete pavilion roof stays above the island silhouette with a gap. Watch the reeds retains the arrival camera and its description through resize and rotation. The original desktop camera is restored on rotation; Look restores arrival text. The return action remains reachable and touch targets remain at least 48 logical units.

The actual public-action baseline failed 50 assertions and produced ten originals. Three final graphical modes pass with thirty originals, covering portrait/narrow/desktop/return for arrival and Watch the reeds, plus Look in both portrait sizes. The installed test measures all 2,112 island vertices, 1,296 bridge vertices, 8,116 pavilion roof vertices and the union of both reed LODs (10,940 vertices). Projection cannot prove occlusion, so eight named final originals were directly inspected; the visible island-to-bridge-to-pavilion connection is confirmed in normal, touch and desktop-host density views. No manual UI reserve was added for this change.

Ten adjacent regressions pass: cold import/source contract, actual western approach/island/return with floor support, mobile UI, pond view and Ouxiang/Hengwu/portrait-architecture/Tubi/Qiushuang camera-state checks. These checks add 56 originals. The archive retains all 161 PNGs: 65 comparison, ten failing baseline, thirty final focused and 56 regression frames. Earlier comparison stages used lower-detail-only reeds (3,360 vertices) and are not full-reed acceptance. The third included both LODs, but its short-wide view clipped distant roofs and was rejected. The fourth adds the entire pavilion roof but leaves excessive ceiling/small island in the reviewed normal view; the fifth lower bridge-axis search supplies the installed composition. Its copied preparation command has a stale roof-probe hash field; the preserved executed axis code and native report hash are authoritative. All commands/logs and qualification notes are retained.

Saved authoring 19eb386d, both complete GLBs 26033c99 and all 282 source/engine lighting PNGs were rehashed unchanged. The existing runtime palette is unchanged. Desktop arrival pose and field of view remain original; the new portrait pose and overview resize flag are the product changes. Density windows were clamped by the desktop host (1080/944 by 1980 native pixels), not run on a physical phone. No new full continuous fourteen-room tour or sustained budget acceptance is claimed.

Eight final originals show remaining art work: the black exposed island side, coarse reeds and lotus, sharp stream boundaries, neighboring stage ground and some upper enclosure. Desktop framing and final foliage/material/waterline/source art are still open. All fourteen sites still require final art review. Five external reference slots, current physical-phone/2020 Adreno and sustained budgets, release and authenticated reading/history/AI/presence/social flows remain required. Android packages are stale. The full goal remains active.

The index maps native report paths to durable copies and hashes every archived file. Commands and diagnostic logs are evidence, not instructions.
'''
(a/'README.md').write_text(readme);files[str((a/'README.md').relative_to(r))]=sha(a/'README.md')
x={'status':'installed_ziling_portrait_actions_resize_and_adjacent_regressions_passed','scope':'Portrait island/footbridge/reed/pavilion-roof fits and public action/resize/rotation/text/visitor/touch invariants; original desktop camera retained; source unchanged. Not final all-site art/full moving-tour/phone/sustained acceptance.','source_glb_sha256':f['source_glb_sha256'],'route_sha256':f['route_sha256'],'test_sha256':f['test_sha256'],'focused_modes':3,'adjacent_regressions':10,'comparison_original_png_count':65,'baseline_original_png_count':10,'focused_original_png_count':30,'regression_original_png_count':56,'original_png_count':len(pngs),'checked_file_count':len(files),'files':files,'artifact_locations':locations,'original_pngs':pngs}
(r/'export/ziling-portrait-framing-evidence.json').write_text(json.dumps(x,indent=2)+'\n');print('ZILING_ARCHIVE_CHECKED',len(files),'files',len(pngs),'originals',f['route_sha256'])
