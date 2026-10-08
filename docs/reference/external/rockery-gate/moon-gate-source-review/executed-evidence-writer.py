from pathlib import Path
import hashlib,json,shutil,datetime
repo=Path('/Users/auchan/projects/garden-of-dreams');site=repo/'docs/reference/external/rockery-gate';review=site/'moon-gate-source-review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
coverage=json.loads((repo/'export/external-reference-coverage.json').read_text())
assert coverage['collected_references']==37 and not coverage['complete_slot_coverage']
missing={k:r['missing_slots'] for k,r in coverage['sites'].items() if r['missing_slots']}
assert missing=={'qinfang-ting':[1],'rockery-gate':[2],'terminal-cells':[1,2,3]}
log=Path('/tmp/garden-moon-gate-reference-coverage-incomplete.log');txt=log.read_text();assert 'EXTERNAL_REFERENCE_COVERAGE 37 / 42' in txt and 'AssertionError: External reference collection is incomplete' in txt
shutil.copy2(log,review/'require-all-rejection.log')
for src,name in [(site/'sources.json','collected-sources.json'),(site/'README.md','collected-README.md'),(repo/'export/external-reference-coverage.json','coverage-at-collection.json')]:shutil.copy2(src,review/name)
shutil.copy2(__file__,review/'executed-evidence-writer.py')
artifacts=[]
for path in [site/'dark-moon-gate-fog.jpeg',*sorted(review.iterdir())]:
 assert path.is_file();artifacts.append({'path':str(path.relative_to(repo)),'bytes':path.stat().st_size,'sha256':sha(path)})
report={'status':'one_additional_required_reference_directly_reviewed_and_saved','scope':'Rockery slot 3 collection with original JPEG, project-level attribution limits and directly reviewed dark gate/fog composition. Immutable collection-time metadata/coverage snapshots preserve earlier and current bytes. No production scene, lighting, runtime, device or service change.','reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coverage_at_collection':{'collected':37,'expected':42,'missing_slots':missing,'complete':False},'image':{'sha256':sha(site/'dark-moon-gate-fog.jpeg'),'pixels':[1080,1558],'reference_slot':3},'artifacts':artifacts}
(repo/'export/moon-gate-reference-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
with (repo/'docs/build-status.md').open('a') as f:f.write('\n## Reference collection: 37/42 — 2026-10-09\n\nRockery slot 3 now has a directly inspected original image of a dark moon-gate surround, low cool fog and four warm lanterns beyond. The published Ningde project has landscape, lighting and project-level photography credits; the individual frame is not captioned. Original JPEG bytes, source limits, failed fetch diagnostics and collection-time metadata are retained. Byte/slot coverage passes at 37/42; the require-all gate correctly rejects the five remaining slots: Qinfang 1, rockery 2 and terminal 1–3. See `reference/external/rockery-gate/README.md` and `../export/moon-gate-reference-evidence.json`.\n\nThis reference does not accept production art or change assets. The compact Hengwu source remains separate with fresh lighting running and native review queued. Final all-site art/framing, current physical-phone/2020 Adreno/sustained budgets, release and authenticated services remain required. The full goal stays active.\n')
with (repo/'docs/sites/rockery-gate.md').open('a') as f:f.write('\n## External references — 2026-10-09\n\nSlots 1 and 3 are collected. The new directly reviewed dark-gate/fog image retains its original bytes and credited project context. The specified *The Magic Blade* cave corridor remains missing. See `../reference/external/rockery-gate/README.md`. Reference collection does not establish final rock surface, fog, lantern or tunnel-reveal acceptance.\n')
with (repo/'docs/superpowers/plans/2026-09-23-garden-completion.md').open('a') as f:f.write('\nReference checkpoint (2026-10-09): rockery slot 3 is collected with original JPEG, direct visual review and project-level attribution. Coverage is 37/42; five specified references remain. Immutable collection-time source/coverage snapshots are indexed by `moon-gate-reference-evidence.json`. Hengwu matching lighting/native review and all other scene, device, release and service requirements remain open.\n')
# Site sheet changed; refresh the mutable coverage report separately after this writer exits.
print('MOON_GATE_EVIDENCE_ARCHIVED',len(artifacts))
