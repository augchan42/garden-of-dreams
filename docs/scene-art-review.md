# Scene art review — 2026-10-09

All fourteen arrival views were inspected at desktop and portrait sizes using the original native captures for the `5ae484f9` paving/plain-material candidate. These are arrival inspections, not acceptance of every action camera, travelling shot, prop, reference, device budget or service. The images remain in `reference/neutral-path-native-review/native-captures/`. The newer `59de1ca2` architectural-color candidate has the same geometry and cameras, with separate fresh lighting; its final visual review is still pending.

| Site | Visible result | Remaining art or composition issue |
| --- | --- | --- |
| Personal terminal | CRT and desk read against the dark cell; barred window shows the gate and moon. | Inspect seat/window actions and corridor view; retain the restricted green key. |
| Rockery gate | Inscription, dark entry and amber bend are visible. | Entrance has a broad, angular plaster silhouette; rock surface and tunnel reveal need final inspection. |
| Qinfang | Pavilion, lanterns and moon read in both aspects. | Table/supports sit near the command panel; surrounding paths and stage remain broad. New atlas colors need their own inspection. |
| Ouxiang | Slate roof, brown timber and repaired foreground paving read in both aspects. | Water-edge treatment, backdrop and final roof filtering remain open. |
| Ziling | Reed landing and connection to Ouxiang are recognizable. | Portrait clips much of the bridge; reeds and island edge remain angular. |
| Hengwu | Hall title, warm windows, table and pierced stones are visible. | Near stone/wall-cap geometry dominates the right of the desktop shot; portrait loses the court's side details. Preserve the required clear skyline without adding trees. |
| Daoxiang | Thatch, door, fence and painted paddy flat distinguish the farmhouse. | Portrait house is small and off-center beneath a large ceiling area. The painted flat's rectangular edge is conspicuous. |
| Daguan | Two roof tiers, title and closed door bays read as one facade. | Portrait roof extends beyond the right edge; excessive ceiling and mottled facade shading remain. |
| Yihong | Red walls, paired doors, banana leaves and one amber window distinguish the court. | Portrait court is small beneath the ceiling; inspect leaf silhouettes and door/window lighting. |
| Xiaoxiang | Bamboo frames the closed gate and amber window. | Leaf/stem repetition and ceiling exposure remain; inspect aisle and bamboo detail views. |
| Longcui | Plum branches frame the timber gate and incense bowl. | Portrait gate is small beneath the ceiling; blossoms and branches remain coarse. |
| Aojing | Window and roof appear in the pond reflection. | Arrival reveals adjoining stage/path geometry; the separate water-dominant action and reflection performance need final review. |
| Qiushuang | Three desk/screen groups and title read in both aspects. | Portrait shows excessive ceiling; inspect all three screen-bank actions and lattice readability. |
| Tubi | Terrace, stairs, hall and amber windows read clearly. | Portrait moon is clipped at the left edge; inspect the garden-overlook action and background closure. |

The next camera comparisons target Daoxiang, Daguan and Longcui. CPU projections use actual exported vertices and both 390×844 and 360×800 viewports. They identify Daguan's current roof clipping and constrain proposals, but do not establish occlusion or rendered quality. Camera proposals remain outside production until native comparison and interaction checks pass.

A CPU ray diagnosis of the desktop Hengwu foreground intersects its plaster-rock batch at two sampled pixels, and its wall-atlas batch at another. This narrows the source inspection to those objects. It does not replace a native surface-ID control or prove every foreground pixel belongs to the same object.

The primary color revision is separate: neutral brown wood, warm plaster/stone and slate roofs, with amber practicals and selective green CRT/gel accents. The combined candidate's completed fresh bake and in-progress native review are recorded in `build-status.md`.

Later in this run, the combined color source passed all 42 review phases and exact saved-source reexport verification, then was installed with ten production checks. Twelve actual native camera-only comparisons now cover the three proposed portrait views at both sizes. All six proposed architecture bounds fit above the interface. The farmhouse is larger and centered; Daguan fits the roof but still shows broad ceiling/ground areas; Longcui is larger but a plum branch partly crosses its title. Those camera proposals remain uninstalled pending further composition and action/resize/authored-camera checks. Evidence: `../export/portrait-framing-comparison-evidence.json`.


Hengwu detail update (2026-10-09): actual public stone/book actions now fit in normal, touch-size and desktop density-scaled portrait views, preserve selection on resize, restore original desktop poses on rotation and clear selection with Look. Eight final originals were inspected. The closest stone's three holes/base and complete book/tabletop are visible above the panel. The earlier eight baseline failures, two touch failures and two density/header failures are preserved with all 174 comparison/regression originals. Three final focused modes and ten adjacent regressions pass; source geometry and lighting remain unchanged. Evidence: `reference/hengwu-detail-framing/README.md`. Hengwu arrival wall cap, roof crop and facade lighting still need work. This is incremental camera/UI acceptance, not final all-site art or physical-device acceptance.


Tubi framing update (2026-10-09): the complete moon, hall/title and staircase clear the portrait panel in three final graphical modes. The higher overlook reveals the bridge pavilion beyond the nearer roof. Public resize/rotation/Look behavior, stable scroll reserve, 48-unit touch targets and final-action reachability pass. Seven final originals were inspected. The original 29 failed assertions and two later density/wrapping failures remain preserved. Source geometry and lighting are unchanged. Evidence: `reference/tubi-portrait-framing/README.md`. Small ceiling strips, stage/backdrop/ground edges and coarse surfaces remain for final site art; physical-device acceptance is separate.


Qiushuang framing update (2026-10-09): the full facade and all three groups of four monitors now fit in portrait; all three public bank close-ups show distinct monitors. Resize/rotation/Look and touch scrolling pass in three graphical modes, with fourteen adjacent regressions. Eight final originals were directly inspected. All 273 originals, including four comparison attempts and the 22 failed baseline assertions, are retained. Source geometry and lighting remain unchanged. Evidence: `reference/qiushuang-screen-framing/README.md`. Lattice crosses screen text; central plaster remains bright/mottled; broad ceiling/ground and stage/background closure remain final art tasks. This is incremental camera/UI acceptance; phone, live content and final all-site art remain separate.
