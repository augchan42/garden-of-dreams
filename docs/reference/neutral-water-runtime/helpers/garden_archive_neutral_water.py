from pathlib import Path
import hashlib,json,shutil,struct
import numpy as np
from PIL import Image
r=Path('/Users/auchan/projects/garden-of-dreams');ledger=r/'.superpowers/sdd/2026-09-23-garden-completion';w=ledger/'water-palette-runtime';c=ledger/'water-palette-comparison';a=r/'docs/reference/neutral-water-runtime'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=json.loads((w/'review-pipeline.json').read_text());assert p['status']=='passed' and len(p['phases'])==11
for name,digest in p['files'].items():assert sha(r/name)==digest,name
for phase in p['phases']:assert phase['exit_code']==0 and phase['status']=='passed' and sha(phase['log'])==phase['log_sha256']
reports=[w/'all-arrivals/report.json',w/'surface-motion/report.json',w/'reflection-controls/report.json']
for report in reports:
 for row in json.loads(report.read_text())['rows']:
  path=Path(row['capture']);assert sha(path)==row['sha256'];assert list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels']
x=json.loads(reports[0].read_text());assert len(x['rows'])==28 and len({row['room'] for row in x['rows']})==14
notes={'terminal_room':'Green CRT remains intentional; bare-cell/corridor detail remains open.','rockery_gate':'Cooler atmospheric tint; angular plaster and corridor closure remain open.','qinfang_ting':'Slate water and amber lamps remain distinct; table/UI and stage closure remain open.','ouxiang_xie':'Slate water visible below pavilion; water edges and distant backdrop remain open.','ziling_zhou':'Slate water improves separation; black island side, portrait bridge crop and coarse reeds remain open.','hengwu_yuan':'Amber windows and stone/book remain visible; roof/wall-cap/mottled facade remain open.','daoxiang_cun':'Warm doorway remains distinct; flat field rectangle and shadows remain open.','daguan_lou':'Amber transoms remain distinct; ceiling, facade mottling and distant portrait view remain open.','yihong_yuan':'Warm red courtyard remains distinct; small portrait subject and coarse banana leaves remain open.','xiaoxiang_guan':'Warm window remains distinct; repeated coarse bamboo and backdrop remain open.','longcui_an':'Warm lantern remains distinct; coarse branches/blossoms and ground remain open.','aojing_guan':'Pond is dark blue-gray with visible amber window reflection; stage paths and reflection budget remain open.','qiushuang_zhai':'Amber monitor groups remain visible; lattice/text intersections, wall lighting and broad ground remain open.','tubi_tang':'Full portrait moon/hall/stair remains visible; ground/backdrop and surface refinement remain open.'}
review={'status':'all_28_original_arrival_images_directly_inspected','scope':'Installed desktop and portrait originals for all fourteen rooms. Incremental runtime palette acceptance only; outstanding notes are final-art work, not accepted as complete.','rows':[dict(room=row['room'],aspect=row['aspect'],capture=row['capture'],sha256=row['sha256'],pixels=row['pixels'],finding=notes[row['room']]) for row in x['rows']]}
(w/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
# Retain report provenance while correcting copied scope wording.
s=json.loads((w/'source-preservation.json').read_text());s['scope']='Current saved authoring, complete export/engine GLBs and all 282 source/engine PNG bytes checked unchanged during the runtime palette change.'
s['scope_correction']='Original copied record said camera/UI-only; this checkpoint changes engine water/ambient/distance-fog/reflection colors and capture tooling, not source geometry or lighting.'
(w/'source-preservation.json').write_text(json.dumps(s,indent=2)+'\n')
assert sha(r/'blender/authoring.blend')==s['source']['authoring']
assert sha(r/'export/garden-of-dreams.glb')==s['source']['export_glb']==p['source_glb_sha256']
assert sha(r/'godot/assets/garden-of-dreams.glb')==s['source']['godot_glb']==p['source_glb_sha256']
assert len(s['source']['lighting_pngs'])==282
for name,digest in s['source']['lighting_pngs'].items():assert sha(r/name)==digest
rows=json.loads((c/'water-palette/report.json').read_text())['rows'];controls=[]
for room in ['qinfang_ting','ouxiang_xie','ziling_zhou','aojing_guan']:
 for aspect in ['desktop','portrait']:
  group=[v for v in rows if v['room']==room and v['aspect']==aspect]
  base=next(v for v in group if v['variant']=='baseline');noop=next(v for v in group if v['variant']=='legacy-fog-noop')
  bp=c/'water-palette'/Path(base['capture']).name;npth=c/'water-palette'/Path(noop['capture']).name
  assert sha(bp)==base['sha256'] and sha(npth)==noop['sha256']
  assert np.array_equal(np.asarray(Image.open(bp)),np.asarray(Image.open(npth)))
  controls.append({'room':room,'aspect':aspect,'baseline_sha256':sha(bp),'legacy_fog_noop_sha256':sha(npth),'decoded_pixels_exactly_equal':True})
(w/'legacy-fog-negative-control.json').write_text(json.dumps({'scope':'Eight controls change only unused legacy floor-fog material; actual attached stage fog clocks fixed by executed probe. No live stage-fog recolor claimed.','rows':controls},indent=2)+'\n')
assert not a.exists(),'Do not replace an immutable archive'
a.mkdir();files={};locations={};pngs=[]
def copy(src,rel):
 dst=a/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src);assert sha(dst)==digest
 name=str(dst.relative_to(r));files[name]=digest;locations[str(src)]=name
 if dst.suffix=='.png':
  b=dst.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';pngs.append({'path':name,'sha256':digest,'pixels':list(struct.unpack('>II',b[16:24]))})
for folder,label in [(c,'comparisons'),(w,'runtime')]:
 for src in sorted(folder.rglob('*')):
  if src.is_file():copy(src,Path(label)/src.relative_to(folder))
for name in ['/tmp/garden_review_water_palette.py',__file__]:copy(Path(name),Path('helpers')/Path(name).name)
code=list(p['files'])+['godot/materials/stage/fog.tres','godot/tests/test_import_source_contract.gd','godot/tests/source-contract.json','godot/tests/test_surface_materials.gd','godot/tests/test_planar_reflection.gd','godot/tests/test_reflection_camera_alignment.gd','godot/tests/test_mobile_ui_scaling.gd','godot/runtime/entry_route.tscn','godot/runtime/pond_reflection.gd','godot/shaders/water.gdshader','godot/shaders/floor_fog.gdshader']
for name in code:copy(r/name,Path('installed-code')/name)
readme='''# Neutral water and atmosphere runtime palette

The installed stream water uses slate-blue (0.25, 0.32, 0.40), ambient fill uses (0.38, 0.38, 0.40) at unchanged energy 0.65, and distance fog uses (0.10, 0.13, 0.18) at unchanged density 0.003. Pond albedo is dark blue-gray (0.022, 0.030, 0.040); reflected light uses an equal-channel 0.85 multiplier at unchanged strength 0.78. Amber windows and lanterns remain distinct. The actual attached stage fog was already neutral (0.28, 0.29, 0.34) and is unchanged. The saved Blender water material still differs; this is calibrated engine palette acceptance, not final source/material parity.

Eleven installed review phases pass: cold import, source contract, actual surface bindings, reflection bindings/alignment, mobile UI, all-room arrivals, surface capture/pixels, and reflection capture/pixels. Six checks were reused after verifying exact passing logs and unchanged product files within their tested scopes; corrected capture scripts were compiled and executed in the remaining phases. All 28 desktop/portrait arrival originals for fourteen rooms were directly inspected. The three surface controls independently move water and actual live fog: changed-pixel fractions 0.046792 and 0.155207. The four pond controls verify reflected window geometry, reflection strength and ripples within the projected pond while retaining UI constraints. These are native desktop checks, not phone or sustained performance acceptance.

The comparison archive preserves 166 originals from two 83-frame stages. The first stage did not freeze the live stage-fog resource and is preliminary only. The corrected stage freezes actual attached water, fog and pond clocks; all eight unused legacy-fog negative controls have exactly equal decoded pixels. Three proposed Ziling camera samples are labeled separately and are not installed camera changes. The failed environment-node lookup produced zero originals and is retained. The first installed all-room run also produced zero originals: temporary resource loads failed to retain the clocks. Its scripts/log/report/failure are retained; the wrapper rejected the error and missing 28-frame marker. The corrected scripts retain actual attached material handles and check clocks per arrival. Final installed captures add 35 originals, for 201 archived PNGs total.

Saved authoring 19eb386d, both complete GLBs 26033c99 and all 282 source/engine lightmap PNGs were rehashed unchanged. The runtime route remains 6c80b98a. No geometry, authored cameras, collisions or baked source lights were changed. No new full continuous fourteen-room physics walk was run for this palette-only update. Pixel measurements use encoded RGB, not physical linear radiometry; underlying translucent UI pixels can change slightly without UI style/text/control changes.

Final art is still open across fourteen sites: black island sides and bridge framing, coarse foliage, wall mottling, lattice/text intersections and stage/ground/backdrop closure remain visible in the original arrivals. Five reference slots, current physical-phone/2020 Adreno and sustained budgets, release and authenticated reading/history/AI/presence/social flows remain required. Android packages are stale. The full goal remains active.

The evidence index maps original paths in native reports to durable copies and records every copied file hash. Commands and failed attempts are evidence, not instructions.
'''
(a/'README.md').write_text(readme);files[str((a/'README.md').relative_to(r))]=sha(a/'README.md')
assert len(pngs)==201,len(pngs)
idx={'status':'installed_runtime_palette_and_fixed_clock_surface_reflection_checks_passed','scope':'Runtime palette, all fourteen desktop/portrait arrivals directly reviewed, actual live motion/reflection controls, source preserved; not final source parity/all-site art/full moving walk/physical device/sustained acceptance.','source_glb_sha256':p['source_glb_sha256'],'route_sha256':sha(r/'godot/runtime/entry_route.gd'),'native_review_phases':11,'installed_original_png_count':35,'comparison_original_png_count':166,'original_png_count':len(pngs),'checked_file_count':len(files),'files':files,'artifact_locations':locations,'original_pngs':pngs}
(r/'export/neutral-water-runtime-evidence.json').write_text(json.dumps(idx,indent=2)+'\n')
print('NEUTRAL_WATER_ARCHIVE_CHECKED',len(files),'files',len(pngs),'originals')
