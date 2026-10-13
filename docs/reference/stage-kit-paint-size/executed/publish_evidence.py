from pathlib import Path
import json,hashlib,shutil
r=Path(__file__).resolve().parent;repo=Path('/Users/auchan/projects/garden-of-dreams');dst=repo/'docs/reference/stage-kit-paint-size';dst.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for folder in ['native-sv-baseline','native-sv-candidate','native-installed','native-raw']:
 shutil.copytree(r/folder,dst/folder,dirs_exist_ok=True)
proof=['baseline-reproduction.json','canonical-replay.json','source-preservation.json','export-preservation.json','texture-size-red.json','texture-size-green.json','native-fixed-comparison.json','raw-native-textures.json','direct-review.json','installed-validation.json','adoption.json','initial-native-decoded-comparison.json','initial-native-image-comparison.json']
(dst/'proof').mkdir(exist_ok=True)
for name in proof:shutil.copy2(r/name,dst/'proof'/name)
for name in ['report.json','inventory.json','inputs.json']:shutil.copy2(Path('/tmp/garden-kit-acceptance-v2-20261011')/name,dst/'proof'/('current-nine-kits-'+name))
(dst/'executed').mkdir(exist_ok=True)
for p in r.glob('*'):
 if p.is_file() and p.suffix in ['.py','.log']:shutil.copy2(p,dst/'executed'/p.name)
for name in ['check_paints.gd','render_paints.gd']:shutil.copy2(r/'raw-godot/tests'/name,dst/'executed'/name)
for mode in ['baseline','candidate']:
 shutil.copy2(r/f'godot-{mode}/tests/render_stage_kit_offscreen.gd',dst/'executed'/f'render-stage-{mode}.gd')
for name in ['native-baseline-live-fog','native-candidate-live-fog','native-baseline-fixed-timeout30','native-candidate-fixed-timeout30','native-baseline','native-candidate']:
 shutil.copytree(r/name,dst/'retained-window-runs'/name,dirs_exist_ok=True)
source_sizes={n:sum(p.stat().st_size for p in (r/n/'export/kits').rglob('*.glb')) for n in ['baseline','candidate']}
readme=f'''# Standalone stage paint export size

The seven stage modules retain their existing geometry and editable paintings. Their delivered GLBs now embed 2048 px cyclorama paint, matching the kit texture target. The three original 4096 px paintings and editable Blender library remain unchanged in production.

![Current stage modules](native-installed/stage-kit.png)

![Moonlit paint in the raw candidate](native-raw/candidate-moonlit.png)

The current export recipe reproduces all fourteen preceding GLBs exactly. Its corrected recipe reproduces all sixteen new GLBs, including two legacy aliases, exactly. Expanded indices, vertex attributes, UVs, normals, nodes, material settings, scenes and nonpaint image bytes are preserved. Six variant GLBs and two aliases change only their paint payload and corresponding buffer layout. The fourteen variant files shrink from48,311,736 to21,993,976bytes; all sixteen delivered files shrink from{source_sizes['baseline']} to{source_sizes['candidate']}bytes. This is an asset-size reduction, not measured phone performance.

The actual source inspection checks140 objects,68 meshes and all three packed4096 paintings across installed, baseline and candidate source files. An injected export failure restores the original image links and bytes and removes temporary copies. The production source library is retained byte for byte. The assembled garden source/engine remain7fb3bbc1 and runtimeec42ec55; source lighting is unchanged.

Actual raw native imports verify4096paint bindings before and2048after, with one image shared by base color and emission. All six raw before/after originals were directly inspected for colors, contours, moon and brushwork. Existing Godot material overrides still use1024px paint. Both native resource/collision checks pass14 models/22 shared surfaces/54 colliders. All eight fixed-clock native gallery images match byte for byte, and eight installed originals match the candidate. These eight originals were directly inspected.

The first gallery comparison had two small animated-fog differences; the other six views matched. The fixed-clock root-window runs then timed out with partial images, including one90-second run. Those runs and original files remain retained and unaccepted. The complete comparison uses the same geometry, cameras and materials in an always-updating native SubViewport with an explicit draw, independent of the root-window draw signal. Each complete gallery finishes in about ten seconds. This establishes standalone render equality; it does not resolve or claim root-window timing or target-device performance.

All nine current kit verifiers pass. The inventory independently checks60 named variants/120 LOD exports and byte-identical Godot copies. Every actual material-bound kit atlas and paint image decodes at2048; the special fog mask remains512. This establishes the delivered inventory and texture dimensions, not source reproduction for all nine kits, final site art, texture allocation or device acceptance. The26 Python tests pass.

The initial independent inventory check incorrectly treated the512fog mask as a2048atlas; the corrected role-aware check retains the fog mask and fixes the actual oversized paint exports. An export comparison initially expected renamed image records; the exporter retains their original names. The stricter successful comparison preserves all JSON except buffer lengths/offsets. Both failed controls are retained.

Final fourteen-site art, five missing references, Aojing ground adoption, current phone/2020 Adreno/sustained budgets, release and authenticated services remain open. The current offline APK predates this kit input change and must be rebuilt before claiming current provenance. User editor sessions were not reloaded.

Run `python3 scripts/verify_stage_kit.py` for the complete source export checks. Run `res://tests/test_stage_kit.gd` for native resources/collisions and `res://tests/render_stage_kit_offscreen.gd -- --output=<directory>` for the fixed native gallery. All published files except this manifest are hashed in `files.json`.
'''
(dst/'README.md').write_text(readme)
def manifest(folder):
 files={str(p.relative_to(folder)):sha(p) for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'files.json'};(folder/'files.json').write_text(json.dumps({'files':files},indent=2)+'\n');return len(files)
print('published',manifest(dst))
archive=repo/'.superpowers/sdd/2026-09-23-garden-completion/stage-kit-paint-size-20261011';shutil.copytree(dst,archive,dirs_exist_ok=True)
for mode in ['baseline','candidate']:
 for folder in ['export/kits','blender/kits','textures/kits/stage','scripts']:
  shutil.copytree(r/mode/folder,archive/mode/folder,dirs_exist_ok=True)
print('durable',manifest(archive))
p=repo/'docs/kits/stage.md'
with p.open('a') as f:f.write('\n## Export texture size —2026-10-11\n\nThe original three4096px paintings and editable library are retained. Delivered variants/LODs and two aliases now embed2048px paint; the existing Godot1024px overrides remain. Geometry, UVs, materials and colliders are preserved. Eight installed native gallery images match the reviewed candidate byte for byte. [Source, native and failure evidence](../reference/stage-kit-paint-size/README.md). Final site/device acceptance remains open.\n')
p=repo/'docs/build-status.md'
with p.open('a') as f:f.write('\n### Current stock-kit inventory and stage paint exports —2026-10-11\n\nAll nine current kit checks pass:60 named variants,120 LOD exports and120 byte-identical Godot copies. Delivered stage paint is2048px while original4096px paintings remain editable. All sixteen stage GLBs reproduce canonically; all140 source objects/68 meshes are preserved. Eight installed native gallery originals match the reviewed candidate exactly. The26 Python tests pass. [Current evidence](reference/stage-kit-paint-size/README.md). Full-scene art, allocation/device/sustained budgets, references, release and services remain open; APK provenance is stale after the kit-input update.\n')
p=repo/'docs/superpowers/plans/2026-09-23-garden-completion.md';s=p.read_text();old='- [ ] Complete missing kit variants and distinctive later-site architecture.';assert old in s;s=s.replace(old,'- [x] Complete the named stock-kit variants and both LODs; current9-kit/60-variant/120-GLB evidence: `docs/reference/stage-kit-paint-size/README.md`.\n- [ ] Complete and accept distinctive later-site architecture against each site contract.');p.write_text(s)
