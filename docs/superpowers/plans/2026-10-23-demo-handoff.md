# Four-minute demo handoff

User-approved scope (2026-10-23): deliver a current-source offline desktop demo,
terminal → gate → Qinfang Pavilion → local hexagram → finale → replay, with a
fresh playable build, short video and accurate run guide. Merge release changes
after required checks pass. Stop at the handoff.

The earlier full-garden plan remains the future roadmap. Fourteen-site final
art, broad phone/performance certification and authenticated services are not
requirements for this handoff. Their unfinished state must remain explicit.

## 1. Inspect the current demo

Use a separate Godot project copy. Inspect native desktop arrival, reading and
finale images, then the existing packaged interaction tests. Reuse current
source/bake evidence. Do not repeat full-garden bakes or tours without a relevant
change. Preserve unrelated output and the R2 migration plan.

## 2. Finish route defects

Fix visible or functional defects that prevent this demo's handoff. Prefer the
smallest source-correct change; check the affected behavior and appearance.
Record scope decisions and any remaining limitations. Leave user editors and
phones alone. Do not resume unrelated site work.

## 3. Package and capture

Export the demo as the package's startup scene from current reviewed sources.
Run native packaged mouse/keyboard start → travel → cast → close → finale →
replay acceptance, with a resizable-window check. Produce a short native video
with the project's audio. Verify the archive and a clean extracted launch.
Write a concise guide with actual launch requirements and offline limitations.

## 4. Review and handoff

Review the final changes once with a fresh reviewer. Fix material findings,
commit/push and create/attach a PR. Check the existing dependency stack and merge
release changes with merge commits only after required checks clear. GitGuardian
findings remain user-owned and PR14 retains its independent hold. Supply the
playable build, video, guide and a short account of remaining roadmap work.

## Execution decisions

- Existing passing checks are reused unless changed inputs or unresolved
  failures invalidate their coverage. No new tests for documentation-only work.
- Read-only exploration can be delegated; implementation and native GPU jobs
  stay coordinated to avoid conflicting edits and measurements.
- Current baseline: 147a01b6 (Aojing ground infill), source GLB 09910fba.

## Progress

- Goal created and active with the user-approved demo scope.
- Current native baseline inspected at terminal, gate, pavilion, reading, table and finale.
- Startup check rejects the repository full-garden default; staged export will set the demo entry.
- Bank coverage baseline fails at 0.00785 texels/triangle. Candidate passes at 3.0828 minimum, covering 3240 visible bank triangles in unused atlas space.
- Preserved all 770 other resolved nodes, all non-bank UV2 and all fourteen other site GLBs. One fresh atlas bake; 280 other source/engine PNG copies retained with explicit compatibility provenance.
- Native candidate pavilion, gate and table reviewed: stream edges now show masonry rather than black strips. The 1024px lossless map also improves existing atlas filtering; no pixel equality claim for those surfaces.
- Python suite: 30 tests pass. Full lighting check requires the existing imperial/Ouxiang flags; first invocation omitted them and correctly rejected their 512px maps.
- GitGuardian still fails on PR22 and PR35; user retains incident resolution. No merge bypass.
- Ruling: use a single receiver bake after strict UV-only preservation rather than rebake unchanged receivers. Cost: existing bake provenance must be retained and compatibility documented.
- Ruling: retain the bank atlas at lossless1024 for this desktop demo. Cost: increased texture memory; mobile budget acceptance remains future work.

- Confirmed the lighting regression in the actual release executable: assertions skipped backdrop and terminal-spill installation. Calls now run outside assertions with explicit failure handling.
- Godot release disables script and path overrides. Release acceptance therefore uses an opt-in child on the actual default scene and the embedded PCK; ordinary startup is unchanged.

- Final packaged checks pass without warnings/errors: configured startup, local cast, route/replay, reading/recast, release pointer/keyboard in desktop and portrait.
- Reviewed release startup and twelve native capture frames. Video: 1290 frames, 43 seconds, H.264/AAC with six original cues; complete decode passes.
- Archive, clean extracted hashes/signature and normal extracted startup pass. Final evidence: build/demo-handoff-final/handoff.json.
- Fresh independent code review found no material issues. Conditional merge remains held by existing dependency GitGuardian failures; full-garden roadmap remains open.
