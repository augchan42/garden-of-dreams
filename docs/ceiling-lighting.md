# Ceiling lighting and combined scene checks

The lighting pipeline now validates the exact five painted backdrop surfaces
in the installed source and all six in the ceiling candidate. The ceiling is
required whenever its mesh exists in the export. Missing, duplicate, substituted
or additional painted receivers fail validation. Source and map shadow flags
must agree. Thirteen rejection cases pass on the actual five/six-surface exports.

The unshaded ceiling follows the existing cyclorama's ordinary-bake exclusion.
There are still 124 ordinary targets. Native Godot checks preserve the current
normal/demo maps and linked receiver layers; the actual candidate has six wash
receivers while 161 other rendered meshes retain their layers.

All fifteen separate Blender candidate libraries were regenerated from the
combined saved authoring file and packaged for direct inspection. Twelve
exterior washes reference the same six visible objects in the linked master.
The candidate master uses relative library paths. Fourteen library audits match
authoring structure and signage. The full saved review source remains
`blender/candidates/floor-canopy/authoring.blend`; packaged scratch-library hashes
and their location are retained in `reference/ceiling-lighting/candidate-source-files.json`.

Fresh native Cycles wash maps use the actual twelve saved Areas at 128 samples
and 512 pixels. All six receivers and ten front/back PNGs retain current source,
authoring and library hashes. The ceiling's direct maximum is 0.1037; the building
control is exactly zero. Its false shadow flag is applied and recorded. The
shared native rig used by indirect-spill baking separately passes geometry/UV,
Area transform/property and receiver-identity inspection. These checks do not
prove freshly baked ordinary or indirect lighting. The actual new wash catalog
combined with the old ordinary catalog is rejected before materials or layers
change; old maps are never relabelled for the new geometry.

The combined export `33b20efadae58c5eb137eda3e21236211a5fb9a1047a1ba41d6338cb48fefbce`
passes the actual continuous command-driven walk: fourteen rooms, twenty-six
legs and 17,581 grounded rays without a miss. The isolated route disables old
site/wash maps; it does not add test floor shapes or reset the visitor.

Twenty-eight native portrait comparisons use the actual production import
material and shadow settings without paint, shadow or layer overrides. Each
arrival has twenty-seven upper-image rays; the 201 baseline misses become
ceiling hits, and all fourteen ceiling views have zero sampled misses. The
native views retain the current cameras and UI. Direct inspection still finds
the wall/ceiling paint join and overall site art unfinished. This is sampled
arrival coverage, not every pixel or rendered traversal acceptance.

Seven material counterfactuals in the currently installed, genuinely baked
garden diagnose the flat moon. Its ungraded interior is clipped to white;
the graded interior is one constant cream value. Removing emission or ordinary
lighting restores detail. Scaling base color in linear space and emission by
0.45 restores the brush texture in this diagnostic view. Disabling the wash
alone leaves most of the disc flat. Captures and display-RGB statistics are
retained; they are not linear radiometry, a new authored material or final art
acceptance. Adjust the authored moon before committing to a full lighting
rebuild, then inspect it with the resulting new maps.

Canonical authoring/export, the installed GLB and previous packaged release are
unchanged. Current runtime source supports the candidate, so the previous
package's runtime provenance must not be described as current. Exact source
and native evidence is indexed by `export/ceiling-lighting-evidence.json`.
Earlier indexed documents/tools keep their original hashes under historical
snapshot paths.

The full goal remains active: final paint and site art, thirty missing external
references, fresh ordinary/wash/spill lighting for the final source, production
walk and transition renders, texture/performance/device/package acceptance,
and authenticated room services remain unfinished.
