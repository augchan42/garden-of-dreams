# Tech kit

All six inventory variants have editable Blender sources and independent lower-detail companions. The showroom and twelve module scenes are in `blender/kits/KIT_tech.blend`; the modules export to `export/kits/tech/`. Legacy `KIT_tech.glb` and its LOD1 companion now represent the amber CRT.

| Variant | Base triangles | LOD1 triangles | Ratio | Colliders per detail level |
|---|---:|---:|---:|---:|
| crt_amber | 536 | 208 | 39% | 1 |
| crt_green | 536 | 208 | 39% | 1 |
| monitor_bank | 1820 | 788 | 43% | 1 |
| cable_run | 952 | 372 | 39% | 0 |
| cell_door | 572 | 228 | 40% | 3 |
| terminal_desk | 652 | 276 | 42% | 1 |

The CRTs have rounded warm gray cases, curved phosphor screens, three bronze controls, side vents and cable sockets. The stock monitor bank groups four amber CRTs in a two-by-two steel rack; the bulletin hall uses three fitted banks to retain its twelve-screen layout. The three-metre cable run has clamps and connector endpoints. The cell door is an open steel frame with a 1.08-metre clear width and no door leaf, as the terminal site sheet requires. The desk has timber drawers, a keyboard, steel legs and braces.

LOD1 uses fewer screen subdivisions, case bevel segments, cable segments and keyboard keys. The screen artwork, controls, cabinet outlines, door opening and functional heights remain in place. Colliders and connector transforms match exactly between detail levels. The cable is nonblocking dressing; all other modules use separate simplified collision meshes.

## Atlas and material

One original 2048px atlas layout supplies base color, ORM and emission. Cases are warm gray, wood is red-brown, controls are bronze and steel/cables are charcoal. Phosphor color stays on the screens. The CRT text is original static dressing: it does not report service state. The font is system Menlo Bold; no font file is distributed. Scanline modulation is baked into the emission RGB rather than cutting holes through the screen mesh. Source and Godot emission strength are four.

Godot imports the RGB maps with compression and mipmaps at 512px for color/emission and 256px for ORM. All twelve models share `materials/tech_atlas.tres`. The post-import script replaces both mesh surface materials and overrides and discards redundant extracted maps. Automatic extra LOD generation is disabled. No realtime lights ship in the modules; placement must use the existing four-practical pool.

## Connectors and verification

All modules have `PORT_ground`. CRTs add `screen` and `cable`; the monitor bank adds `screen`, `cable` and `stack`; the cable adds `start` and `end`; the open door adds `threshold` and `opening`; the desk adds `top`, `screen` and `cable`. Coordinates in the manifest use Blender metres. Godot maps `(x,y,z)` to `(x,z,-y)`.

`verify_tech_kit.py` checks actual GLB triangle counts, UV0/UV1, PBR maps, emission strength, opaque culling, connector positions and collider parity. Each of the twelve models passes the 512-square sampled UV1 overlap check. `test_tech_kit.gd` checks shared resource identity, runtime texture sizes, silhouette bounds, collision counts, and rays through the clear door opening and solid frame posts. Blender MCP confirms twelve module collections and the showroom in the saved library.

[Base overview](../reference/tech-kit.png) · [LOD1 overview](../reference/tech-kit-lod1.png) · [CRT detail](../reference/tech-crt-detail.png)

## Integration status

The main garden now contains 33 placed modules: six green CRTs, six desks, six open frames and six cable drops in the cells, plus three four-monitor banks, three desks and three cable drops in the bulletin hall. Two shared-material export batches contain 26,544 triangles. Existing lights, triggers and unrelated collision transforms remain unchanged; 33 simplified kit colliders are added. Cell frames fit the existing 1.12 m clear width and 2.1 m clear height. The interactive table, hall lattice and painted scrolls remain in place.

The current source is `db2e84a9c6f72dfc6686421b07f0ea1e8334b1f0f9e2818fe02d1b0adfa4c2dd`. Fresh bakes cover 31 demo and 29 priority-2 opaque meshes. `test_tech_placements.gd` verifies both underlying and active material sharing, UV2, triangle and collision counts, and clear passage through all six doors. Entry, study, hilltop and demo replay checks pass. Desktop and portrait cell/hall views were inspected; Blender MCP confirms both saved site libraries are directly openable without changing the user’s open scene. The playable pack and 43.7-second capture are refreshed. Stationary desktop demo views use 101–143 draw calls, 63.80 MiB of textures and at most four practical lights. Full-traversal and phone GPU acceptance remain open. The terminal site’s folding chair is now built and placed in all six cells; its current source, bakes and verification are recorded in `props.md`. Stage variants, further site art and sourced references, final lighting, services and phone acceptance remain open.
