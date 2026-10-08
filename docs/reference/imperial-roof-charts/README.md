# Imperial roof chart experiment — 2026-10-08

Production remains authoring `9356f6ec` and GLB `b540496a`. The separate
candidate GLB is `361a67c7`. No source, production lighting or import setting
was installed by this experiment.

The exact saved Daguan roof consists of two broad shells and 576 closed,
eight-sided cylinders of 22 mm radius. All cylinder faces point outward.
Matching exported triangle vertices back to these saved objects distinguishes
52 shell triangles, 9,216 cylinder-side triangles and 6,912 end-cap triangles.
This avoids interpreting unrelated batch parts as roof caps.

All original cylinder-side charts are narrower than 0.1 source pixel at the
actual 1024px bake size. Native RGB16 centroid sampling finds zero irradiance
on 4,065 of 4,520 upward-facing side triangles (89.9%). The candidate gives
each cylinder a 16×24px unfolded side chart and two radius-4px cap charts,
with separate shell packing. Every exported triangle has minimum altitude
above one source pixel; the smallest is 1.172px. Expanded triangle comparisons
preserve positions, normals, primary UVs and winding exactly. All 716 other
resolved nodes and fourteen other site GLBs preserve their contracts/bytes.

A fresh 128-sample 1024px Cycles roof bake, in the complete candidate scene's
shadow context, reduces zero upward-side centroids to 15/4,520 (0.3%). End-cap
zeros remain 1,543/3,456; these samples alone do not distinguish physically
occluded ends from raster/filter artifacts. Shell zeros also remain. None of
these centroid measurements proves camera visibility or final lighting.

Four separate native Godot comparison runs cover portrait, desktop and a roof
close-up, with fixed clocks and twelve byte-identical baseline/restored pairs.
All ninety capture PNGs have verified report hashes. Only the target roof mesh
and its matching fresh map are swapped; all other parts retain production
inputs. This is not a complete candidate lighting or traversal acceptance run.

Directly inspected originals: first run's close baseline/import256/native,
portrait baseline/import256 and desktop import256; filtering run's close
lossless256/lossless512 and portrait/desktop lossless512; actual lossless256
import close/portrait/desktop; actual lossless512 import close/portrait/desktop.
The broad black stripes become lit, narrow ribs. The actual 256px imports
retain patchy shading even though the manually resized lossless preview is
smoother. The actual 512px lossless import improves this in the inspected
views and is selected for the next complete-source validation. Its decoded
RGB8 image is 786,432 bytes; this is not a renderer allocation or phone budget
measurement. Native-resolution controls retain fine shading variation.

Remaining checks include chart gutters at engine filtering sizes, bake noise,
material colour, eave joins, complete matching lighting, moving-camera and
all-room appearance, renderer memory and actual phone performance. Roof-only
comparison success does not accept the whole site or authorize relabelling
old lighting maps against a new GLB hash.

Raw failed attempts are retained: the scratch component iterator was consumed
twice in the first two exports; a later scratch export exited with SIGBUS
while retaining polygon references across edit-mode reconstruction. Storing
polygon indices before that reconstruction allowed the subsequent export to
complete. This does not establish Blender's internal crash cause. The first
lossless report script used an unavailable PackedByteArray hash method and
failed to parse; the corrected script uses HashingContext. None was adopted.

Executed scripts, complete candidate and target-site GLBs, source vertex
inventory, matching roof map, import parameters, reports, original captures
and native logs are archived here. Other candidate site GLBs remain in the
scratch tree; their byte equality is recorded by the preservation verifier.
All native and CPU jobs from this experiment exited before this checkpoint.
