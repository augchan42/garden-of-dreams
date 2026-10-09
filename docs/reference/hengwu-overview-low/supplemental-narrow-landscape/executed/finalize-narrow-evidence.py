"""Archive terminal installed proof and update the current checkpoint."""
from pathlib import Path
import hashlib,json,shutil
repo=Path('/Users/auchan/projects/garden-of-dreams');work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview';archive=repo/'docs/reference/hengwu-overview-low';supp=archive/'supplemental-narrow-landscape'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
application=json.loads((work/'adoption-narrow/application.json').read_text());assert application['status']=='supplemental_installed_checks_passed' and application['installed_original_count']==166 and len(application['checks'])==12 and all(x['status']=='passed' for x in application['checks'])
assert sha(repo/'godot/runtime/entry_route.gd')=='bde869171ad37d520ce34d10aa1ca825a327a6c6c6ce13e3dfafbeca6be5ba95'
proof=json.loads((supp/'review/pipeline.json').read_text());assert proof['status']=='supplemental_native_checks_passed' and proof['unchanged_original_count']==113 and len(proof['ui_only_changes'])==7
assert not (supp/'installed').exists();shutil.copytree(work/'adoption-narrow',supp/'installed')
for p in (supp/'review').rglob('*.png'):
 assert sha(p)==sha(supp/'installed'/p.relative_to(supp/'review'))
shutil.copyfile(archive/'README.md',supp/'executed/overview-readme-v6.md');shutil.copyfile(archive/'evidence-index.json',supp/'executed/evidence-index-v6.json')
(supp/'README.md').write_text('''# Narrow landscape follow-up

Final runtime `bde86917` keeps the full description and command input beside horizontally scrollable actions in Hengwu landscape views below 580 pixels high or 1000 pixels wide. Below 820 pixels wide, the title wraps and shares header width 1:2 with the description. Camera aim and field of view blend between 390 and 480 pixels high so taller narrow windows keep larger furniture and less foreground wall. Ordinary layout flags are restored on exit. Hengwu recomputes its scroll reserve after reflow, making returned portrait pixels exactly match initial portrait pixels.

The unmodified original framing/state assertions now cover 640×360 and 720×360,819/820 and999/1000 width boundaries,579/580 height boundaries, and six intermediate390–480 heights. Normal/touch overview runs have 41 originals each; desktop-clamped density has 10. Detail runs contribute 30, native region visibility 16 and all fourteen arrivals in two sizes 28. All 12 final isolated checks and 12 installed checks pass. All 166 installed originals reproduce their isolated counterparts exactly. Nine final isolated originals were directly viewed; their exact paths/hashes are recorded, without claiming visual review of every file.

Of 120 prior fixed-clock originals,113 are byte-identical. Seven differ only where the portrait panel now uses its initial-arrival height instead of a height inherited from the previous window width. All their row fields except panel_top remain identical, and scene pixels above the interface match exactly at actual physical/logical density scaling. Both sets of fourteen arrivals, including all 26 other-room arrivals, are byte-identical to the preceding installed version. The earlier30-phase/two-tour proof belongs to runtime 56813eb7; it is retained as historical broad evidence rather than relabelled as a new full tour of this runtime.

- [Final isolated commands, frozen inputs and comparisons](review/pipeline.json)
- [Installed checks, backups and 166 exact originals](installed/application.json)
- [Precisely nine direct original reviews](direct-original-review.json)
- [Rejected and intermediate runs](rejected-notes.json)

Only the runtime and overview regression test were installed by this follow-up. Authoring 7eba169a, complete source ba40866e, matching 141 imported maps and other runtime files are unchanged. The original and intermediate helpers, source snapshots, logs and raw pixels are retained. Native region masks establish neither source-owner segmentation nor through-hole visibility. Final site art, all fourteen scenes, five missing references, current physical devices/2020 Adreno/sustained budgets, release and authenticated services remain open. Protected Blender/Godot editors were not saved, restarted or reloaded.
''')
summary='''\n\n## Narrow landscape follow-up — 2026-10-10

Current runtime `bde86917` also handles 640×360 and 720×360. Hengwu uses compact landscape controls below 580 pixels high or 1000 pixels wide; narrow titles wrap beside the complete description. Camera aim/field of view ease as height increases, and returning to portrait now reproduces initial portrait pixels exactly. Twelve final isolated checks and 12 installed checks pass, with 166 byte-exact installed originals. Of 120 prior captures, 113 are byte-identical; seven change only the portrait interface, with identical scene pixels above it at actual density scaling. All 28 stationary arrivals remain byte-identical. Geometry, authoring and matching 141 maps are unchanged. The preceding 30-phase/two-tour results remain historical evidence for runtime 56813eb7. Final art, references, current device/sustained budgets, release and authenticated services remain open. See [supplemental evidence](LINK).
'''
for name,link in [('docs/build-status.md','reference/hengwu-overview-low/supplemental-narrow-landscape/README.md'),('docs/scene-art-review.md','reference/hengwu-overview-low/supplemental-narrow-landscape/README.md'),('docs/scene-work-plan.md','reference/hengwu-overview-low/supplemental-narrow-landscape/README.md'),('docs/sites/hengwu-yuan.md','../reference/hengwu-overview-low/supplemental-narrow-landscape/README.md')]:
 p=repo/name;p.write_text(p.read_text()+summary.replace('LINK',link))
p=repo/'docs/scene-work-plan.md';p.write_text(p.read_text()+'\nNext scene inspection: Xiaoxiang’s repeated bamboo silhouettes and exposed upper enclosure, using the current source and retained public arrival/action views. The full goal remains active.\n')
p=archive/'README.md';p.write_text(p.read_text()+'\n## Current narrow landscape follow-up\n\nRuntime `bde86917` supersedes 56813eb7 for the additional small landscape cases and consistent portrait panel height. All 12 final isolated and 12 installed checks pass, with 166 exact installed originals. All 28 arrivals remain byte-identical. The earlier broad/tour and installation records above retain their original runtime identity. See [the supplemental proof and limits](supplemental-narrow-landscape/README.md).\n')
shutil.copyfile(work/'finalize-narrow-evidence.py',supp/'executed/finalize-narrow-evidence.py')
index=json.loads((archive/'evidence-index.json').read_text());index['runtime_sha256']=sha(repo/'godot/runtime/entry_route.gd');index['files']={str(p.relative_to(archive)):sha(p) for p in sorted(archive.rglob('*')) if p.is_file() and p!=archive/'evidence-index.json'};index['native_originals']=len(list(archive.rglob('*.png')));index['scope']='Index excludes itself. Original, intermediate, rejected, final and installed raw files retain their bytes. Current narrow proof is runtimebde86917; earlier broad/tour proof retains runtime 56813eb7. Saved prior README/index are historical. Counts include duplicate archived originals.';(archive/'evidence-index.json').write_text(json.dumps(index,indent=2)+'\n')
assert all(sha(archive/n)==h for n,h in index['files'].items());print('FINAL_NARROW_EVIDENCE_PASS',len(index['files']),'hashes;',index['native_originals'],'archived PNGs')
