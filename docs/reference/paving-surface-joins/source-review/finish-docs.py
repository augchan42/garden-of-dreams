"""Publish the observed source checkpoint without closing the full art goal."""
from pathlib import Path
import json

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = Path(__file__).parent
application = json.loads((work / 'adoption-second/application.json').read_text())
assert application['status'] == 'working_paving_source_adopted_installed_checks_passed'
assert len(application['checks']) == 22
assert len(application['installed_arrival_originals_byte_exact']) == 28
assert len(application['installed_focused_originals_byte_exact']) == 57
section = '''

## Paving joins — 2026-10-10

Current source `ba40866e` / authoring `7eba169a` removes 84 positive coplanar paving overlaps by partitioning 26 render objects. The original floor footprint is retained within 10 micrometres; all collision geometry, 42 cameras, 71 markers, materials and runtime `7970380d` are preserved. Render geometry is 266,533 triangles. Eight other site exports remain byte-exact. The nunnery's black forecourt rectangle is replaced by continuous stone and plum shadows.

Six source phases regenerate 141 lighting PNGs. The 45-phase native review has 44 positive passes and one intended baseline-floor rejection. Both actual Mac tours visit 14 rooms over 26 legs with no unsupported floor samples and at most four practical lights. Three Ziling modes are repeated after a test-only real 250-millisecond foliage wait; runtime LOD remains enabled. All 28 arrivals, eight moving samples, eight matched floor controls and 35 repeated reed captures were directly inspected: 79 distinct original paths.

Twenty-two installed checks pass. All 85 installed camera/floor/arrival originals reproduce the reviewed files exactly. The first installation also passed all 22 native checks, then rolled back all 29 targets after a report-field comparison error; its 85 originals match independently. The corrected helper reads actual PNG dimensions. Failed source, native and installation attempts are retained in the evidence archive.

This closes the duplicate paving defect. Hengwu's arrival view is next: show its table and pierced stones while preserving the accepted detail actions. Final fourteen-site art, five missing references (37/42), current phones, 2020 Adreno and sustained budgets, release and authenticated reading/history/AI/presence/social remain open. Evidence: [paving checks and originals](reference/paving-surface-joins/README.md). The full goal remains active.
'''
for name in ['docs/scene-art-review.md', 'docs/build-status.md']:
    p = repo / name
    assert '## Paving joins — 2026-10-10' not in p.read_text()
    p.write_text(p.read_text() + section)
p = repo / 'docs/sites/README.md'
p.write_text(p.read_text() + section.replace('(reference/', '(../reference/'))
p = repo / 'docs/superpowers/plans/2026-09-23-garden-completion.md'
p.write_text(p.read_text() + section.replace('(reference/', '(../../reference/'))
slugs = sorted(set(json.loads((repo / 'export/manifest.json').read_text())['sites']) - {'stage'})
assert len(slugs) == 14
for slug in slugs:
    p = repo / 'docs/sites' / (slug + '.md')
    p.write_text(p.read_text() + '''

## Paving-source checkpoint — 2026-10-10

Current assembly is `ba40866e` with authoring `7eba169a`. Duplicate visible paving tops are partitioned while retaining the complete floor footprint, all 454 colliders, 42 cameras, 71 markers, materials and runtime `7970380d`. Complete matching 141 PNG lighting, both actual Mac 14-room/26-leg tours and 22 installed checks pass; all 85 installed originals reproduce the reviewed files. All 28 current arrival originals were directly inspected. This is focused paving acceptance; this site's final art is still open. References remain 37/42; current phone/sustained/release and authenticated services remain required. Evidence: [paving repair](../reference/paving-surface-joins/README.md).
''')
p = repo / 'docs/reference/paving-surface-joins/README.md'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text('''# Paving joins — 2026-10-10

The nunnery forecourt had a black rectangle where the shared approach and courtyard occupied the same plane. The saved assembly contained 84 positive overlap pairs across paving, platforms and terminal treads. Partitioning 26 render owners removes the duplicate tops while preserving the complete floor union within 10 micrometres. Existing side/bottom faces, collision geometry, object transforms, cameras, markers and materials are retained. Source is `ba40866e`, authoring `7eba169a`, runtime `7970380d`; 266,533 render triangles remain below the 300,000 source budget. This does not establish device performance.

The normalized independent audit covers 1,142 baseline and 1,241 candidate top faces and finds 84 versus zero positive overlaps. Earlier 69-pair and floating-coordinate/tread attempts are preserved under `source-review/`; they were not accepted. The saved source passes read-only floor and palette checks and reproduces all 16 default GLB exports exactly. Eight unchanged site exports remain byte-exact. Source bake logs show six fresh phases and all 141 PNGs match the engine files.

The 45 native phases pass 44 positive checks and one matched baseline rejection. Each desktop/portrait tour visits 14 rooms over 26 legs with zero unsupported samples: 17,582 desktop and 17,581 portrait supported samples. Both tours record 139 originals and at most four active practical lights. The native identity shader uses a measured 100-micrometre plane filter because the imported baseline nunnery top is 50 micrometres below its exported zero plane; the source footprint tolerance remains 10 micrometres. Four matched original controls per source prove that the retained court owns the repaired pixels. The earlier 10-micrometre native filter failure remains archived.

Ziling's exact island/bridge source vertex expectations change to 2,128/1,288, independently measured in exported and imported geometry. All original framing/action assertions remain. Twelve of thirteen first normal captures reproduce after the count-only correction; the return reeds differed because sixteen fast render frames could precede FloraLOD's 0.2-second update. A test-only real 250-millisecond wait and measured per-capture LOD checks repeat normal, touch and host-density modes. Their 35 original images were directly inspected. Of the preceding captures, 12/13 normal and 12/12 touch and 10/10 density reproduce; the changed normal return is preserved, not treated as identical. No runtime LOD or camera policy changes.

`native-review/direct-original-visual-review.json` names 79 directly inspected paths: all 28 arrivals, eight moving samples, eight matched floor controls and 35 final reed originals. Other raw captures are hashed and dimension-checked without claiming direct inspection. Fixed stationary comparisons use clock 3; Ziling uses clock 10 and tours retain moving clocks. Mac touch/density captures do not establish physical-phone acceptance.

The first installation passes all 22 native checks but restores all 29 targets after its comparison helper expects a `pixels` field absent from the floor report. `failed-installed-report-schema/rollback-verification.json` independently verifies every restored target and exact equality of all 85 captured originals. The corrected helper reads actual PNG headers. The second installation passes all 22 checks and all 85 originals match the reviewed candidate exactly. `installed/` retains those logs, reports and images. Recoverable staged source and backup binaries remain outside the archive.

Raw reports retain executed absolute scratch paths. Their matching contents are archived under corresponding phase folders. `export/paving-surface-joins-evidence.json` indexes archive and canonical hashes; `capture-inventory.json` records all raw original sizes and hashes. Source binaries are installed in the repository and are not duplicated in this archive.

Final fourteen-site art remains open: Hengwu's arrival composition is next, followed by the remaining material, foliage, signage, water/stage boundaries and action-view work. Five reference slots, current physical phones, 2020 Adreno/sustained budgets, release and authenticated services remain required. The full goal remains active. The user's open Blender and Godot editors were not reloaded, saved or closed.
''')
print('PAVING_CHECKPOINT_DOCUMENTED 14 site sheets')
