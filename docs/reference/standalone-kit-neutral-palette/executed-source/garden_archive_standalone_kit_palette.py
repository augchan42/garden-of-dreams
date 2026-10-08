import hashlib,json,shutil
from pathlib import Path
root=Path('/Users/auchan/projects/garden-of-dreams');c=json.loads(Path('/tmp/garden-kit-neutral-palette.json').read_text());work=Path(c['work']);archive=root/'docs/reference/standalone-kit-neutral-palette';archive.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={};locations={};seen={}
def save(key,source):
 source=Path(source);digest=sha(source)
 if digest in seen:rel=seen[digest]
 else:
  target=archive/key;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);rel=str(target.relative_to(root));seen[digest]=rel;files[rel]=digest
 locations[str(key)]={'path':rel,'sha256':digest}
for folder in ('baseline','candidate','baseline-reexports','native-checks','native-palettes','native-palettes-final'):
 for p in sorted((work/folder).rglob('*')):
  if p.is_file():save(str(p.relative_to(work)),p)
for name in ('checkpoint.json','source-update.json','export-preservation.json','baseline-metadata-restoration.json','palette-parse-rejected.gd','palette-parse-rejected.log','palette-initial-passed.gd','palette-initial-passed.log','missing-export-controls.json','original-empty.log','revised-empty.log'):
 save(name,work/name)
for p in sorted((work/'rejections').rglob('*')):
 if p.is_file():save(str(p.relative_to(work)),p)
for p in sorted((work/'adoption').rglob('*')):
 if p.is_file() and 'backup' not in p.relative_to(work/'adoption').parts:save(str(p.relative_to(work)),p)
for name in ('garden_prepare_kit_palette.py','garden_probe_saved_kit_export.py','garden_test_kit_palette_rejections.py','garden_review_standalone_kits.py','garden_adopt_kit_palette.py'):
 save('executed-source/'+name,Path('/tmp')/name)
for name in ('update_standalone_kit_palette.py','verify_pavilion_atlas.py','verify_garden_atlas_export.py','verify_mountain_export.py','test_garden_atlas_export_rejections.py'):
 save('executed-source/'+name,root/'scripts'/name)
for name in ('test_pavilion_atlas.gd','test_pavilion_kit.gd','test_corridor_kit.gd','test_wall_kit.gd','test_rockery_kit.gd','test_standalone_kit_palette.gd','garden-palette-contract.json'):
 save('executed-runtime/'+name,work/'godot/tests'/name)
save('executed-source/preceding-verify_pavilion_atlas.py',work/'missing-export/scripts/old.py')
for name in ('garden-kit-neutral-palette-native.log','garden-kit-neutral-palette-import.log','garden-kit-native-palettes-final.log','garden-saved-kit-export-probe.log'):
 save('native-logs/'+name,Path('/tmp')/name)
for kit in ('pavilion','corridor','wall','rockery'):
 for phase in ('red','green'):save('cpu-logs/'+kit+'-'+phase+'.log',Path('/tmp')/('garden-'+kit+'-palette-'+phase+'.log'))
save('saved-export-probe.json',Path('/tmp/garden-saved-kit-export-probe/report.json'))
readme='''# Standalone architectural kit palette installed

The pavilion, corridor, wall and rockery libraries now use the neutral palette installed in the assembled garden. Four packed color images were replaced in isolated saved Blender files; all other packed images, native geometry/UV/metadata/scene snapshots and exported contracts are preserved. Each saved source first reproduced its existing exports byte for byte. After saving and reopening the revised sources, all 48 variants/LODs preserve every expanded indexed attribute, node, material, sampler and unrelated image; only the exact base-color image changes. Eight legacy aliases match their intended modules. Total indexed triangles checked: 39,175.

All four atlas checks changed from actual pixel-mismatch failures to passes. The verifier also accepts an isolated asset root and now rejects missing exports: its preceding version falsely accepted an empty wall directory, while the revised version rejects it. Eleven unwanted-change controls reject old colors, moved connectors/collision, geometry/normals/both UVs, unrelated normal/ORM images, a green multiplier and changed sampler.

Ten isolated native phases pass: cold import, PBR import and actual physics for all four kits, plus deliberate wrong-color rejection. The headless physics tests use fixed 60fps simulation; they are not device performance measurements. The graphical test checks decoded swatch means, actual normal bindings, shared ORM binding and roughness-green/metallic-blue channels for all 48 modules. Four original neutral-lighting galleries were directly inspected. Their actual PNG size is 1600×680; logical viewport is 1600×900. The first passed reporter omitted that distinction; its originals are retained alongside the revised reporter and a passing rerun. The revised and installed galleries are byte-identical to the inspected originals. Rock silhouettes and LOD simplification still need final art review.

204 changed kit files were installed with exact before/after guards and recoverable local backups. Ten post-install checks pass: import, graphical kit palette, four PBR and four CPU atlas checks. The assembled authoring/master, complete GLBs, all site libraries/exports, runtime and lighting files are hash-unchanged. Normal/ORM engine images and their import settings are unchanged; extracted color-image settings change only their generator hash.

A GDScript type-inference failure occurred before the first successful graphical run; its exact script/log is retained. The initial minimal-project import reported a missing main scene while exiting zero; the project fixture was corrected and a clean cold import passed. Baseline atlas metadata was restored from ad01266 after preparation had copied current metadata beside old extracted PNGs; the comparisons used actual PNG bytes. All corrections and original logs are retained.

Artifact locations below reuse identical bytes by SHA256, including baseline reexports and aliases. Original reports retain their executed local paths. This completes the standalone palette synchronization; final site art/framing, six references, current device/sustained budgets, release and authenticated services remain open. The full goal is active.
'''
(archive/'README.md').write_text(readme);files[str((archive/'README.md').relative_to(root))]=sha(archive/'README.md')
manifest={'status':'four_standalone_kit_palettes_installed_verified','scope':'Four saved libraries, 48 modules at both LODs, eight aliases, native palette/PBR/physics and ten post-install checks. Main garden source and lighting unchanged. Remaining full-project requirements are open.','artifact_locations':locations}
(archive/'artifact-locations.json').write_text(json.dumps(manifest,indent=2)+'\n');files[str((archive/'artifact-locations.json').relative_to(root))]=sha(archive/'artifact-locations.json')
for rel,wanted in files.items():assert sha(root/rel)==wanted,rel
index={'status':manifest['status'],'scope':manifest['scope'],'files':files}
(root/'export/standalone-kit-neutral-palette-evidence.json').write_text(json.dumps(index,indent=2)+'\n')
print('STANDALONE_KIT_PALETTE_ARCHIVE_PASS',len(files),'unique immutable files',len(locations),'logical artifacts')
