# Site sheet: rockery gate (曲徑通幽)

Slug `rockery-gate`. Priority 1. Function: transition from cell to garden (design doc
"garden transition"). Room id `rockery_gate`.

## Stage direction

In the novel the first thing inside the garden gate is a screen of rockery so that nothing
is seen at once. Here it is a plaster Taihu tunnel, 12 m long, bending twice, 2.2 m wide,
floor fog to the knee. The corridor from the cells ends at its mouth. The tunnel is dark
except for one amber lantern at each bend. At the far end it opens without warning onto the
沁芳 stream and the bridge pavilion, full width, fully lit. The reveal is the shot.

## References

1. The rockery tunnels in the Beijing 大觀園 park reconstruction (1980s), which are
   themselves a film set.
2. The cave corridors in Shaw Brothers *The Magic Blade* (1976): plaster rock, hard side
   light, dry ice.
3. A moon gate in fog, seen from the dark side.

## Light

- Key: none in the tunnel. At the exit, the 沁芳亭 site key (green) spills back 3 m.
- Wash: none.
- Practicals: two hanging lanterns (`#FFA500`), one at each bend, realtime, radius 0.1 m,
  range 4 m.
- Fog: floor fog plane at 0.6 m, density high, `#2EBD2E`. The engine height fog is at
  its maximum here and eases to normal at the tunnel mouth.

## Practicals and dressing

- Lantern ×2, hanging from iron hooks set in the plaster.
- Carved characters 曲徑通幽 above the entrance, in the plaster, catching the lantern.
- Water drip decal at the second bend.
- A single potted banana plant at the exit, silhouetted against the bright garden.

## Assets

| From | Piece |
| --- | --- |
| `KIT_rockery` | Tunnel segment ×4, arch ×2 (entrance and exit), cliff face ×2 (flanking the exit) |
| `KIT_props` | Hanging lantern ×2 |
| `KIT_flora` | Banana leaf clump ×1 |
| `KIT_stage` | Fog plane ×3, studio wall behind the rock |

No hero object. The 曲徑通幽 carving is a decal on the arch.

## Trigger empties

| Name | `room_id` | Position |
| --- | --- | --- |
| `TRG_gate_mouth` | `rockery_gate` | Tunnel entrance. Entering fires the tunnel text and drops the camera to `CAM_shawscope`. |
| `TRG_gate_bend_2` | `rockery_gate` | Second bend. Optional `look` beat: the drip, the carved characters. |
| `TRG_gate_exit` | `qinfang_ting` | Tunnel exit. Entering fires the reveal and hands over to 沁芳亭. |

## Cameras

- `CAM_shawscope` rail: enters low behind the player, tightens through the bends, and at the
  exit pulls back to the stage-wide frame of the pavilion. This is the one scripted move in
  the priority-1 slice.
- `CAM_stage_wide`: from inside the tunnel mouth looking out, the pavilion framed by rock.

## Current build and remaining acceptance

Four tunnel-kit segments now span twelve metres along the entrance axis, fitted to a centreline with two bends. Two arches frame the ends, and two cliff faces flank the exit. Separate matching collision shells and a continuous paving slab follow the bends. The two lanterns have moved to the bend positions. Three trigger markers and the existing fog layers remain. Source: `scripts/integrate_gate_rockery.py`.

The entrance-to-exit centre sightline is blocked by the tunnel, while the exit-to-approach centre sightline is clear. The low exit view is still framed by the south covered corridor. The runtime now performs the reveal after the visitor clears the arch: slide through the corridor’s open west side, rise above the roof, and move to the wide pavilion view. All sixteen corridor bays remain. The four-second shot holds the visitor still and hides the command panel, then restores the panel and resumes travel. Return travel does not trigger it.

The return-to-cell turn needed more clearance from the entrance arch; its horizontal approach now runs half a metre farther out before reaching the gate marker. Remaining site work includes final fog/lighting, sourced references and final lighting/color acceptance for the reveal shot. The kit placement is not final site acceptance.

The authored rail is stored as `CAM_rail_gate_reveal`, with `CAM_gate_reveal_slide`, `CAM_gate_reveal_lift` and `CAM_gate_reveal_wide` in the Blender site. Godot owns timing and visitor state. The cameras use a 55-degree vertical field of view; portrait runtime keeps horizontal width during the shot. `test_gate_reveal.gd` checks trigger direction, visitor pause, camera endpoint, panel restoration and movement resumption. The full entry-route test passes with the shot enabled. Intermediate desktop and portrait frames are generated from actual route movement by `render_gate_reveal.gd`.

The old exit bamboo is replaced by one potted banana with seven curved leaves. Its narrow planter sits inside the east edge of the approach, clear of the tested walking route; the leaves silhouette against the garden. A transparent 512² original water-stain texture is projected onto the uneven inside wall at the second bend. Sources: `scripts/dress_rockery_gate.py` and `scripts/generate_gate_drip.py`. Blender source and desktop/portrait Godot captures were inspected; final lighting/composition acceptance remains open. The complete entry route passes in both directions with the final planter position.

The temporary typeset signboard has been replaced by original brush lettering, 曲徑通幽, mapped onto the plaster above the entrance. The transparent decal has a derived recessed normal map, and every projection vertex lands on the arch. Native Blender and desktop/portrait Godot views were inspected. Provenance and the exact generation prompt are in `textures/decals/gate-inscription-provenance.md`.


## Shared prop placement — 2026-10-04

The existing dressing now uses fitted prop-library meshes with a shared PBR atlas. Mount positions, seat/table heights, collision, lights and triggers are retained. The site’s props export as one material batch and stop drawing beyond 28 metres. Desktop and portrait views were reviewed; source-hash-checked bakes apply where this site belongs to the demo or priority-2 catalog. Further art, sourced references and final lighting remain open. Details: `../kits/props.md`.


## Lighting exception — 2026-10-06

The tunnel retains its explicit no-key/no-wash contract and two amber practicals. The twelve exterior backdrop washes have no tunnel receivers. Qinfang’s missing owned key and its specified three-metre exit spill remain lighting work; existing ordinary maps still use the shared stage rig. Current desktop/portrait views are refreshed.


## Inscription runtime size — 2026-10-08

The original brush lettering and recessed-normal source images are retained. Their aligned Godot imports now cap the longest edge at 1024px, with lossless pixels and mipmaps. Actual native allocation drops by 10.9 MiB in both demo and normal exploration at installed source b4. Fixed-clock desktop/portrait arrival and diagnostic close comparisons pass; both arrivals retain all four characters. Diagnostic portrait close-up edge clipping and final camera/art acceptance remain open. The corrected roof source90 has not yet finished lighting installation. Evidence: `../runtime-texture-audit.md`.


## Beijing reconstruction reference — 2026-10-08

Slot 1 is collected and directly reviewed in `../reference/external/rockery-gate/README.md`. The original photograph shows a dry narrow path concealed by piled stone and overhangs, with irregular openings, vines and pine branches. It guides the entry's obstructed view and rock treatment, rather than measured clearance or lighting. This daytime frame does not establish the full twelve-metre/two-bend route, amber lanterns or fog. The Sipa copyright/watermark and primary article attribution are retained. The Shaw cave and moon-gate-in-fog slots remain missing.

## External references — 2026-10-09

Slots 1 and 3 are collected. The new directly reviewed dark-gate/fog image retains its original bytes and credited project context. The specified *The Magic Blade* cave corridor remains missing. See `../reference/external/rockery-gate/README.md`. Reference collection does not establish final rock surface, fog, lantern or tunnel-reveal acceptance.

## Waterline and reed source checkpoint — 2026-10-09

The combined Blender source is now `0d3e84e3`; export and Godot use `1380ceca`. The complete fresh lighting set covers 124 ordinary receivers and 141 source PNGs, with matching wash/spill catalogs. Both native Mac tours visit all fourteen sites over twenty-six public-command legs and return to the cell, with no floor misses and at most four practical lights. All 42 camera, 400 collider and 71 marker contracts are preserved. This is an incremental working-source checkpoint; final site art, references, phone/sustained performance and authenticated services remain open. Evidence: `../reference/ziling-source-art/README.md`.


## Stream bank and lotus checkpoint — 2026-10-09

The current complete source is `7a9fc523` with authoring `074ab201`. The shared stream has 54 bank modules and 54 added colliders; all 42 cameras,400 earlier colliders and 71 markers are preserved. Closed circular lotus pads sit above the water, with a muted shared leaf material and matching saved kit/generator. Fresh lighting covers 124 receivers and 141 source PNGs. Both native Mac tours pass 14 locations and 26 travel legs;15 installed checks pass. This is an incremental source checkpoint. Final site art, five remaining reference slots, current phone/sustained performance, release and authenticated services remain open. Evidence: `../reference/water-edge-source/README.md`.


## Island exterior winding checkpoint — 2026-10-09

Current assembly `73267e2b` / authoring `2b07ce48` repairs the reed island’s exterior face winding. All other exported mesh attributes and fourteen other site GLBs are preserved; cameras, colliders, markers and runtime are unchanged. Complete matching lighting, twenty-five focused native checks and thirteen installed checks pass. This site is not declared final by the island repair. Five references, current phone/sustained budgets, release and authenticated services remain open. Evidence: [island source review](../reference/island-exterior-winding/README.md).


## Neutral stage-floor checkpoint — 2026-10-09

Current complete source is `c9d4fb30`; authoring is `43d7e33e`. The five broad canvas floor pieces use muted warm gray (.065,.060,.055 linear RGB). Other materials, geometry, cameras, collisions, markers and runtime are preserved. All 141 fresh lightmaps, six source phases, 38 positive native checks plus two intended rejection controls, both 14-room/26-leg tours and 15 installed checks pass. All 47 installed lit/Ziling/arrival originals reproduce the reviewed candidate exactly. References remain 37/42; this is palette repair acceptance, not final site or phone acceptance. Evidence: [neutral stage floor](../reference/stage-floor-palette/README.md).
