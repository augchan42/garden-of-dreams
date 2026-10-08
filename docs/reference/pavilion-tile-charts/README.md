# Pavilion tile lighting charts — 2026-10-08

The current saved Qinfang roof contains 42 raised tile strips. All 336 strip
faces point inward, while the upper shell already points outward. The production
regression log records this failure. Separate saved candidates correct the face
winding while preserving primary paint UV ownership and all unrelated objects.

Normal correction alone still renders broad black stripes. Reducing cap height
to 9 mm and increasing width to 76 mm also leaves stripes. Rays from most of
those corrected faces can reach the Sun lights; this is a geometric visibility
probe, not a Cycles radiometric or light-linking acceptance test.

The shallow candidate's 672 exported tile triangles have minimum UV2 altitudes
of 0.113–0.130 pixels in a 1024px source map. Every triangle is narrower than
one source texel; 76.8% of sampled centroid texels are black. These are chart
geometry and native-float centroid measurements, not full raster coverage.

Explicit 24×60px tile charts with 4px padding give every tile triangle 90 square
source texels and a minimum altitude of 9.370px. Other charts fit above the
reserved 144px strip. Geometry and primary paint UVs remain unchanged by this
export operation. With these charts, black centroid samples fall to 7.14% for
the shallow caps and 1.79% for the original cap shape.

The selected candidate retains the original 26 mm rise and 46 mm width. Only
336 inward faces reverse winding in its saved source. Its complete GLB is
`b540496a9129879389a96f5fff0cf59c04c0ff116fa44f2a2389fee3f643f4f1`.
All 716 other resolved nodes and fourteen other site exports preserve their
production contracts/bytes. An additional exact triangle comparison against
the preceding normal-only export preserves positions, normals and primary UVs;
UV2 is the only new delta. Tangents are absent in these primitives.

Each of four candidates retains a fresh 128-sample, 1024px roof-only bake and
three Godot comparison views: portrait, desktop and roof close-up. Each view
has baseline, baseline lossless 256px, candidate imported 256px, candidate full
native lossless, and baseline restored. All twelve before/after baseline PNG
pairs are byte identical. Only the target atlas mesh and its matching fresh
map are swapped; the rest of the scene stays on the production 8d source.

Directly reviewed originals: normal-only six views as recorded in the earlier
ledger; shallow close imported/native and portrait imported; shallow-charts
close baseline/imported/native plus portrait/desktop imported; original-shape
charts close imported/native and portrait imported. The explicit charts remove
the broad black rib pattern in these views, including the 256px import.
Remaining hip shadows, green roof colour, joins and other buildings still need
art work. This selects a roof correction for whole-source validation; it does
not accept every site or target-device performance.

Blender exports retain shared image-sampler warnings in their raw logs; the
resolved target material and all unrelated nodes are checked for preservation.
The initial normal-only render emitted raw res-path image warnings. It is kept
under `first-run-res-readback`; repaired runs use absolute hash-checked PNGs.
The shallow probe's rounded-point classifier failed to identify all triangles;
its rejected script/log is retained separately. The accepted classifier matches
positions within 10 micrometres and checks exactly 672 triangles. An attempted
UV comparison incorrectly assumed exported tangents; the corrected comparator
checks the actual non-UV2 attribute set. No tangents are claimed as verified.

Each earlier candidate archives its saved source, target site GLB, roof map,
reports, logs and images. The selected candidate also archives the complete
GLB. Unchanged other site GLBs are established by the export-preservation
reports and remain in the separate temporary candidates; they are not copied
here. The shallow executed preparer/helper copies are exact. The general
preparer was extended after the normal-only run, so its current bytes are not
claimed as that earlier run's exact script.

Matching fifteen candidate site libraries and a portable master have now been
saved, with twelve Areas sharing six visible stage receivers. A full sequential
ordinary/wash/terminal-spill refresh is running in the separate candidate tree.
These frozen roof comparisons precede that refresh. Production authoring, GLBs,
lighting maps and imports are unchanged. Full matching lighting, native engine
validation and atomic installation remain required.
