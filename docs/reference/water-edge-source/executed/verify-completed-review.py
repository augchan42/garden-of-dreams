from pathlib import Path
import datetime, hashlib, json, struct

repo = Path('/Users/auchan/projects/garden-of-dreams')
w = repo / '.superpowers/sdd/2026-09-23-garden-completion/water-edge-source'
src = w / 'closed-leaf-candidate'
r = w / 'lit-native-review'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
def require(ok, message):
    if not ok: raise RuntimeError(message)
expected = '7a9fc523bc1517941cc248c040877b86f9cd00a11654c6c31e40f3acc089632f'
author = '074ab2014d9122e207783d9e7c7992f9dfc9197a6f380a2d6f5e8c0c05e31978'
d = load(r / 'review-pipeline-resume1.json')
require(d['status'] == 'technical_review_complete_original_lit_visual_review_pending' and 'finished_at' in d, 'Review incomplete')
require(d['source_glb_sha256'] == sha(src / 'export/garden-of-dreams.glb') == sha(r / 'godot/assets/garden-of-dreams.glb') == expected, 'Source mismatch')
require(d['authoring_sha256'] == sha(src / 'blender/authoring.blend') == author, 'Authoring mismatch')
phases = d['reused_checked_phases'] + d['phases']
require(len(phases) == len({p['name'] for p in phases}) == 36, 'Review phase count')
for p in phases:
    require(p['status'] == 'passed' and p['exit_code'] == 0 and sha(p['log']) == p['log_sha256'], 'Review evidence changed: ' + p['name'])
require(sha(r / 'review-pipeline.json') == d['prior_failed_report_sha256'], 'Initial failed report changed')
normal = next(p for p in phases if p['name'] == 'ziling-normal')
require(normal['original_runner_status'] == 'failed' and 'ZILING_FRAMING_RESULT 13 originals; 0 failures' in Path(normal['log']).read_text(), 'Initial marker failure qualification')
bake = load(src / 'export/full-lighting-refresh.json')
require(bake['status'] == 'source_complete' and len(bake['phases']) == 6 and all(p['status'] == 'passed' and p['exit_code'] == 0 for p in bake['phases']), 'Bake incomplete')
require(bake['coverage']['expected_meshes'] == bake['coverage']['baked_meshes'] == 124 and not bake['coverage']['missing'] and not bake['coverage']['unexpected'], 'Receiver coverage')
milestone = load(w / 'completed-source-milestone-verification.json')
require(sha(src / 'export/full-lighting-refresh.json') == milestone['bake_report_sha256'], 'Bake metadata changed')
for p, h in milestone['finished_source_log_sha256'].items(): require(sha(p) == h, 'Bake log changed: ' + p)
frozen = load(src / 'full-lighting-inputs.json')['files']
require(len(frozen) == 257, 'Frozen input coverage')
for rel, h in frozen.items(): require(sha(src / rel) == h, 'Frozen input changed: ' + rel)
maps = d['installed_source_png_sha256']
require(len(maps) == len(list((src / 'export/lightmaps').rglob('*.png'))) == 141, 'Source map count')
for rel, h in maps.items(): require(sha(src / 'export/lightmaps' / rel) == sha(r / 'godot/lightmaps' / rel) == h, 'Map mismatch: ' + rel)
saved = load(w / 'saved-source-reproduction/saved-source-verification.json')
require(saved['status'] == 'saved_candidate_and_default_exports_verified' and saved['authoring_sha256'] == author and len(saved['default_export_equality']) == 16, 'Default reexport coverage')
for rel, h in saved['default_export_equality'].items(): require(sha(src / 'export' / rel) == sha(w / 'saved-source-reproduction/export' / rel) == h, 'Default reexport changed: ' + rel)
contract = load(r / 'native-import-contract.json')
require(contract['passed'] and contract['cameras_checked'] == 42 and contract['colliders_checked'] == contract['physics_rays_passed'] == 454 and contract['marker_metadata_checked'] == 71 and contract['render_meshes_snapshotted'] == 167, 'Native contract')
kit = load(w / 'water-kit-preservation.json')
require(kit['status'] == 'ten_unchanged_water_exports_byte_exact' and sum(x['unchanged'] for x in kit['exports']) == 10, 'Water kit preservation')
for row in kit['exports']:
    require(sha(src / 'export/kits/water' / row['file']) == sha(r / 'godot/assets/kits/water' / row['file']) == row['sha256'], 'Water module mismatch: ' + row['file'])
    if row['unchanged']: require(sha(repo / 'export/kits/water' / row['file']) == row['sha256'], 'Unchanged water module mismatch')
factory = load(w / 'water-generator-reproduction/semantic-preservation.json')
require(factory['status'] == 'all12regenerated_water_semantics_equal' and len(factory['rows']) == 12, 'Canonical water reproduction')
for row in factory['rows']:
    require(sha(src / 'export/kits/water' / row['file']) == row['saved_sha256'] and sha(w / 'water-generator-reproduction/export/kits/water' / row['file']) == row['factory_sha256'], 'Factory evidence changed')
walks = {}
for mode, size in [('desktop', [1410, 600]), ('portrait', [540, 960])]:
    root = r / 'review-captures-resume1' / ('tour-' + mode)
    t = load(root / 'report.json')
    require(t['status'] == 'passed' and not t['error'] and not t['floor_failures'] and t['source_glb_sha256'] == expected, 'Tour failed: ' + mode)
    require(len(t['visited_rooms']) == 14 and len(t['legs']) == len(t['arrival_signals']) == len(t['settled_arrivals']) == 26 and len(t['captures']) == len(list(root.glob('*.png'))) == 139, 'Tour coverage')
    require(t['time_scale'] == 1 and t['maximum_practicals'] <= 4 and t['physics_ticks_per_second'] == 60 and t['legs'][-1]['to'] == 'terminal_room', 'Tour limits')
    for leg in t['legs']: require(leg['grounded_ray_samples'] > 0 and leg['supported_ray_samples'] == leg['grounded_ray_samples'] and not leg['centre_ray_misses'], 'Tour ground support')
    for c in t['captures']:
        p = root / c['file']
        require(sha(p) == c['sha256'] and list(struct.unpack('>II', p.read_bytes()[16:24])) == size, 'Tour original changed: ' + str(p))
    for key, rel in [('route_sha256', 'runtime/entry_route.gd'), ('test_sha256', 'tests/test_full_garden_traversal.gd'), ('render_test_sha256', 'tests/render_full_garden_traversal.gd')]: require(t[key] == sha(repo / 'godot' / rel), 'Tour code changed')
    walks[mode] = {'rooms': 14, 'legs': 26, 'supported_rays': sum(x['supported_ray_samples'] for x in t['legs']), 'misses': 0, 'captures': 139, 'image_size': size, 'report_sha256': sha(root / 'report.json')}
visual = load(r / 'preliminary-direct-original-review.json')
originals = visual['directly_reviewed_originals_sha256']
require(len(originals) == 34, 'Earlier direct review count')
for rel, h in originals.items(): require(sha(r / rel) == h, 'Earlier viewed original changed')
for mode in ['desktop', 'portrait']:
    for name in ['041-qinfang_ting-travel.png', '045-ouxiang_xie-travel.png', '047-ziling_zhou-settled.png', '048-ziling_zhou-travel.png']:
        rel = 'review-captures-resume1/tour-' + mode + '/' + name
        originals[rel] = sha(r / rel)
visual.update(status='incremental_bank_and_closed_lotus_source_accepted_final_site_art_open', updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), directly_reviewed_original_count=len(originals), directly_reviewed_originals_sha256=originals, scope='Six matched-lit water-edge views, all28 desktop/portrait arrivals and eight selected moving-tour originals directly viewed. All278 tour PNGs checked against their native hashes/dimensions; both14-room/26-leg tours pass. Incremental bank/lotus acceptance only; final all-site art, references, physical-phone budgets and services remain open.')
visual['observations'].append('Selected western travel frames retain the bridge, pavilion and above-water pads in both orientations. Dark bank faces and exposed island/set sides remain visible; no claim that those final-art tasks are complete.')
(r / 'direct-original-visual-review.json').write_text(json.dumps(visual, indent=2) + '\n')
final = {'status':'completed_water_edge_source_review_verified', 'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source_glb_sha256':expected, 'authoring_sha256':author, 'source_phases':6, 'native_review_phases':36, 'frozen_inputs':257, 'source_pngs':141, 'walks':walks, 'visual_review_sha256':sha(r / 'direct-original-visual-review.json'), 'prior_failed_runner_retained':True, 'directly_reviewed_originals':42, 'scope':'Technical and direct visual review for incremental source adoption. No final-site, reference, phone, release or service acceptance.'}
(w / 'completed-review-verification.json').write_text(json.dumps(final, indent=2) + '\n')
print(json.dumps(final, indent=2))
