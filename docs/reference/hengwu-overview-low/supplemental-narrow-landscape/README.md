# Narrow landscape follow-up

Final runtime `bde86917` keeps the full description and command input beside horizontally scrollable actions in Hengwu landscape views below 580 pixels high or 1000 pixels wide. Below 820 pixels wide, the title wraps and shares header width 1:2 with the description. Camera aim and field of view blend between 390 and 480 pixels high so taller narrow windows keep larger furniture and less foreground wall. Ordinary layout flags are restored on exit. Hengwu recomputes its scroll reserve after reflow, making returned portrait pixels exactly match initial portrait pixels.

The unmodified original framing/state assertions now cover 640×360 and 720×360,819/820 and999/1000 width boundaries,579/580 height boundaries, and six intermediate390–480 heights. Normal/touch overview runs have 41 originals each; desktop-clamped density has 10. Detail runs contribute 30, native region visibility 16 and all fourteen arrivals in two sizes 28. All 12 final isolated checks and 12 installed checks pass. All 166 installed originals reproduce their isolated counterparts exactly. Nine final isolated originals were directly viewed; their exact paths/hashes are recorded, without claiming visual review of every file.

Of 120 prior fixed-clock originals,113 are byte-identical. Seven differ only where the portrait panel now uses its initial-arrival height instead of a height inherited from the previous window width. All their row fields except panel_top remain identical, and scene pixels above the interface match exactly at actual physical/logical density scaling. Both sets of fourteen arrivals, including all 26 other-room arrivals, are byte-identical to the preceding installed version. The earlier30-phase/two-tour proof belongs to runtime 56813eb7; it is retained as historical broad evidence rather than relabelled as a new full tour of this runtime.

- [Final isolated commands, frozen inputs and comparisons](review/pipeline.json)
- [Installed checks, backups and 166 exact originals](installed/application.json)
- [Precisely nine direct original reviews](direct-original-review.json)
- [Rejected and intermediate runs](rejected-notes.json)

Only the runtime and overview regression test were installed by this follow-up. Authoring 7eba169a, complete source ba40866e, matching 141 imported maps and other runtime files are unchanged. The original and intermediate helpers, source snapshots, logs and raw pixels are retained. Native region masks establish neither source-owner segmentation nor through-hole visibility. Final site art, all fourteen scenes, five missing references, current physical devices/2020 Adreno/sustained budgets, release and authenticated services remain open. Protected Blender/Godot editors were not saved, restarted or reloaded.
