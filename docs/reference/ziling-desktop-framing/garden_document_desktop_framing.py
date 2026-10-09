from pathlib import Path
import hashlib,json,shutil
from PIL import Image
r=Path('/Users/auchan/projects/garden-of-dreams');p=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-desktop-framing';a=p/'archive-prepared';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(r/'blender/authoring.blend')=='0d3e84e3cb0aada4d7aafda8448f3ebb90bb39426eb18f24941a97c56977f400'
assert sha(r/'godot/assets/garden-of-dreams.glb')=='1380ceca14ee8bd79723c351a6084438eed4384416aee76a78222802550ca485'
(a/'README.md').write_text('''# Ziling desktop camera checkpoint — 2026-10-09

The desktop island and reeds previously extended behind the command panel. The new low view moves back smoothly as logical landscape height falls from 600 to 410. It retains the 55° lens and KEEP_HEIGHT projection. Portrait cameras and game actions are retained.

Native framing checks pass in normal, touch and phone-density layouts: 35 original captures include 1410×600, 1280×720, 1410×540, 1410×480, portrait resizing and actual 2340×1080 pixels / 891.43×411.43 logical landscape units. All imported island, bridge, distant pavilion roof and both reed LOD vertices fit above the measured controls. Tests also require silhouette separation, a low viewpoint, completed tweens, preserved description/visitor, public Look and Watch the reeds, touch48 and reachable return controls. Regular desktop minimum widths are 23% island / 12% bridge; short landscape minimums are 150 / 110 logical pixels, reviewed with the larger controls. These are added desktop checks; existing portrait requirements are retained.

The original stronger test fails four desktop fit assertions on the preceding game. The first candidate passes normal desktop but fails two touch assertions; a phone-density control fails six. Those reports and representative originals are retained in `rejected/`. Camera-only comparisons are proposals, not final public-action acceptance.

Two unchanged-deadline touch runs timed out during capture. Native controls confirm `force_draw()` emits its completed-frame signal synchronously: subscribing afterward can miss it. The final test subscribes first and requires the observed completion. The earlier normal control's eleven images are byte-identical before/after this capture fix. The 100-second deadline and camera assertions are retained. See `draw-wait-diagnosis.json` and [Godot's signal documentation](https://docs.godotengine.org/en/stable/classes/class_renderingserver.html#class-renderingserver-signal-frame-post-draw).

Thirteen installed normal originals reproduce the isolated fixture byte for byte. A headless western collision round trip passes; four installed native originals show settled arrivals after public typed commands in both directions. All four were directly reviewed. This focused check does not replace full moving-tour or physical-device acceptance.

The raw-GLB CPU projection first failed the original 0.002px guard. Its executed helper and rejection are preserved. Native imported vertices and camera basis resolve the discrepancy without changing that guard; largest baseline discrepancy is under 0.000055px. `native-inputs.json.gz` retains the complete original JSON bytes after decompression. Source geometry, saved Blender cameras, authoring and all lighting maps are retained. The current source is `1380ceca`; authoring is `0d3e84e3`.

The evidence index records every archived file and native image dimensions. Absolute capture paths inside original reports identify the retained scratch run; published copies keep the same bytes. The selected direct-review list is explicit: other captures were hashed and measured, not all visually inspected. Partial timeout originals and other superseded captures remain in the ignored work root.

This is an incremental camera checkpoint. Island sides, bank and lotus detail, foliage treatment, backdrop/material filtering and final site art remain open. Full goal scope includes all fourteen sites, five remaining reference slots (37/42 collected), current physical phone / 2020 Adreno / sustained budgets, release and authenticated services. Phone-density desktop rendering is not a phone performance result.
''')
for script in ['garden_archive_desktop_framing.py','garden_document_desktop_framing.py']:
 shutil.copy2(Path('/tmp')/script,a/script)
viewed=['green-touch/arrival-desktop-480.png','green-touch/arrival-desktop-540.png','green-density/arrival-desktop.png','green-normal/arrival-desktop.png']+[f'installed-western/{i}-{room}.png' for i,room in enumerate(['ouxiang_xie','ziling_zhou','ouxiang_xie','qinfang_ting'])]
files={str(f.relative_to(a)):sha(f) for f in sorted(a.rglob('*')) if f.is_file()}
images={str(f.relative_to(a)):list(Image.open(f).size) for f in sorted(a.rglob('*.png'))}
d={'status':'incremental_ziling_desktop_framing_verified','source_glb_sha256':sha(r/'godot/assets/garden-of-dreams.glb'),'authoring_sha256':sha(r/'blender/authoring.blend'),'route_sha256':sha(r/'godot/runtime/entry_route.gd'),'test_sha256':sha(r/'godot/tests/test_ziling_framing.gd'),'archive_root':'docs/reference/ziling-desktop-framing','archive_files_sha256':files,'original_png_dimensions':images,'selected_current_originals_directly_viewed':viewed,'isolated_framing_originals':35,'installed_framing_originals':13,'installed13_byte_equal_fixture':True,'rendered_western_arrivals':4,'scope':'Camera/UI fit and public actions/resizing plus focused supported western traversal. Source/bakes retained. Incremental visual review; not final all-site art, new bank/lotus meshes, physical phone, sustained/device budgets, release or authenticated services acceptance.'}
assert all(files[x]==sha(a/x) for x in files)
final=r/d['archive_root'];assert not final.exists();a.rename(final)
(r/'export/ziling-desktop-framing-evidence.json').write_text(json.dumps(d,indent=2)+'\n')
text='''\n\n## Ziling desktop framing checkpoint — 2026-10-09

The reed island now remains clear of the desktop controls. A low 55° view moves back smoothly with shorter landscape height; portrait framing is retained. Native normal/touch/density checks pass with 35 originals, including 480/540/600/720 desktop heights, public Look/Watch the reeds, resizing/rotation, description/visitor preservation and touch48/return access. Thirteen installed originals reproduce the fixture exactly, and the supported western round trip passes with four directly reviewed native arrivals. The capture test now subscribes before forcing a draw, retaining its 100-second deadline and assertions; rejected fit controls and two capture timeouts are retained.

Source `1380ceca`, authoring `0d3e84e3` and matching lightmaps are retained. This is camera progress; bank/lotus/foliage and final fourteen-site art, five references, physical devices/sustained budgets, release and authenticated services remain open. Evidence: [originals and reports](../reference/ziling-desktop-framing/README.md).
'''
for f in [r/'docs/sites/ziling-zhou.md',r/'docs/build-status.md',r/'docs/scene-work-plan.md',r/'docs/superpowers/plans/2026-09-23-garden-completion.md']:
 t=text
 if f.parent.name!='sites':t=t.replace('../reference/ziling-desktop-framing/README.md','reference/ziling-desktop-framing/README.md')
 if f.parent.name=='plans':t=t.replace('reference/ziling-desktop-framing/README.md','../../reference/ziling-desktop-framing/README.md')
 with f.open('a') as out:out.write(t)
print('ARCHIVE_FINAL',len(files),'files',len(images),'PNGs')
