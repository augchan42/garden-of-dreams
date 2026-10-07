# Site sheet: 秋爽齋

Slug `qiushuang-zhai`. Priority 2. Function: Bulletin board. Room id `qiushuang_zhai`.

## Stage direction

A long study hall faces a shallow courtyard. Three banks of amber screens sit behind repeated lattice panels. Keep the centre aisle clear so a visitor can approach a screen without crossing furniture.

## Dimensions and access

9 m wide, 2 m deep facade; 1.8 m clear front walk; eaves at 3.1 m. Maintain a continuous collision-tested approach. Future rooms remain closed rather than exposing unfinished interiors.

## Assets

12 amber monitors in three groups of four; lattice screen fronts; three desks; two scrolls; closed side doors. Reuse stock corridor, wall, roof, lantern and stage materials where their silhouettes fit this site; do not force every site into the same hall mesh.

## Lighting and atmosphere

Warm-neutral hard key across the frontage; amber screens and the two lanterns are the dominant warm sources. The site key was changed from green to reduce the garden's overall green cast while keeping the stage-wide green wash. Exterior floor fog stays between 0.3 and 0.8 m. Keep the walking surface and interactable furniture readable. Unfinished backs use MAT_backstage.

## Room markers

Board entrance; left, centre and right screen banks; return to the central walk. Each marker is a named `TRG_` empty carrying the room id. The existing `TRG_qiushuang_zhai_entry` is the initial marker; add specific action markers during the site pass. Game actions belong in Godot.

## Camera contract

A frontal medium view must show the individual monitors rather than merge them into one lit window. Ship a 2.35:1 establishing camera and a constrained visitor rail. Check both approach and return views for exposed backs or intersections.

## References to collect

1. A sourced Shaw Brothers night-set still for the lighting and built-set treatment.
2. A sourced architectural reference specific to this site's structure.
3. A sourced close view of its distinguishing material or foliage.

These are collection requirements, not claims that reference stills have been collected.

Sourced leads reviewed: [Hong Kong Memory’s Shaw Brothers set collection](https://www.hkmemory.hk/en/collections-shaw_brothers_movies-behind_the_screen-introduction.html) shows daylight studio construction, not the required night-set still. The [National Museum’s *Grand View Garden* painting record](https://www.chnmuseum.cn/zp/zpml/ysp/202101/t20210112_248877.shtml) names the begonia gathering at 秋爽齋 but is not an exterior photograph. Its [*Orchid and Bamboo* painting record](https://www.chnmuseum.cn/zp/zpml/ysp/202101/t20210113_248883.shtml) is a close ink-art reference for the scroll treatment. A site-specific architectural photograph and Shaw night-set still remain to be collected.

## Current build and acceptance

The hall now has twelve screens, three desks with keyboards, two scrolls, closed side doors, five room markers, three bank cameras and a frontal camera. A stone approach connects the east covered walk to the courtyard. A warm frontal key makes the centre sign and screen bank readable; two existing lanterns cast amber light at the ends. The temporary typeset title and block marks are replaced by painted 秋爽齋 lettering and separate bamboo/plum scroll textures, embedded in the Blender source and glTF. Ten opaque hall meshes have current Cycles lightmaps applied in the normal Godot exploration route; the transparent painted title retains its source material. Desktop and portrait arrival and screen-bank views were inspected after the bake, and the four-practical light limit and return route still pass. The images are original production art, documented in `textures/decals/study/README.md`, not historical reference stills. The shared painted backdrop has an authored linked Area wash and a backdrop-only Godot substitute. Live bulletin content, final material acceptance and the site-specific architectural photograph and Shaw night-set still remain unfinished.

Acceptance: distinct site silhouette, complete specified props, named markers, traversable approach, no exposed unfinished backs on the camera rail, and one graded reference render matching this sheet. The stage-wide first pass is not evidence of completion for this site.


## Shared prop placement — 2026-10-04

The existing dressing now uses fitted prop-library meshes with a shared PBR atlas. Mount positions, seat/table heights, collision, lights and triggers are retained. The site’s props export as one material batch and stop drawing beyond 28 metres. Desktop and portrait views were reviewed; source-hash-checked bakes apply where this site belongs to the demo or priority-2 catalog. Further art, sourced references and final lighting remain open. Details: `../kits/props.md`.


## Shared tech placement — 2026-10-04

Three fitted four-monitor banks, three timber desks with keyboards and three cable drops now use the shared tech library. The twelve-screen layout, lattice fronts, painted scrolls, bank actions, lights and approach collision remain in place. Desktop and portrait arrival and all three bank views were inspected. Current Cycles coverage is nine opaque hall batches; static CRT artwork does not report live bulletin state. Source-matched bakes and route checks pass. Details: `../kits/tech.md`.

The runtime bake adapter now corrects Cycles diffuse transfer for Compatibility and isolates baked receivers from static keys while preserving shadow-caster masks. Desktop and portrait views are refreshed; final material, bake noise and texel-density acceptance remain open. See `../baked-lighting.md`.


## Owned backdrop wash — 2026-10-06

`LGT_qiushuang_zhai_backdrop_wash` is saved in authoring and `SITE_qiushuang-zhai.blend`: a 150 W, 15 × 10 m Area light, neutral gray-blue (linear RGB 0.72, 0.78, 0.84), aimed at the painted enclosure along `CAM_qiushuang-zhai_wide`. The reduced-green direction follows the user’s palette revision. It links only to the five shared stage backdrop objects. The directly openable library links those receiver IDs from `SITE_stage.blend`; all twelve lights resolve to the visible stage objects in the linked master.

The combined native Cycles direct pass uses 128 samples and nine 512² front/back maps, imported at compressed 256px. Current desktop and portrait arrival views are refreshed. The canonical site/master GLBs are unchanged byte for byte. This establishes the authored wash and its engine transfer; final palette, material, noise/filtering and moving-camera acceptance remain open. Details: `../baked-lighting.md`.


## Collected reference — 2026-10-08

Slot 2: [original photograph](../reference/external/qiushuang-zhai/qiushuang-entrance-plaque.jpg), by 朱華龍 - Zhu Hua Long, CC BY 2.0. The visible plaque reads 秋爽齋 from right to left. The close entrance view shows a red structural frame, green rectangular return-pattern door lattices and a blue/turquoise/yellow painted upper beam and open fretwork. It supports the study hall frontage and patterned screen treatment; the cropped view does not establish the complete roof, plan, dimensions or the required night lighting. Attribution, license and original-byte integrity are saved beside the image. Other reference slots remain open.
