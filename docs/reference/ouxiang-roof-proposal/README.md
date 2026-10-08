# Ouxiang roof UV proposal — 2026-10-08

This is an isolated CPU proposal. Production remains GLB `b540496a` and
saved authoring `9356f6ec`. The proposal starts from imperial candidate
`361a67c7` and produces `be80374c`; no old lightmaps are installed against it.

Position-welded export topology identifies 168 closed eight-sided cylinders
and one 26-triangle roof surface. All 2,688 cylinder-side triangles and all
2,016 cap triangles have minimum UV2 altitude below one pixel in the matching
1024px source map. RGB16 centroid samples find zero irradiance on 117/1,344
upward side triangles and 218/1,008 upward cap triangles. These counts do not
prove saved Blender object ownership, camera visibility or the cause of every
visible stripe.

The proposal gives each cylinder a 32×48px side chart and two radius-8px cap
charts in a 64px cell. The main roof projects into the remaining upper strip.
All 4,730 target triangles have minimum altitude 2.342 source pixels at 1024,
or 1.171 pixels at 512. Within-component geometric intersection checks find
no positive chart overlaps. Nominal gaps do not prove filtered/dilated gutters.

Independent expanded-triangle comparison checks 241,810 triangles across the
complete GLB: positions, normals, primary UVs and other attributes are unchanged;
only the target secondary UVs change. Scene metadata, cameras, materials,
textures and collision triangles are preserved.

Saved-source ownership, a reproducible Blender exporter, fresh native lighting,
import filtering, camera comparisons, memory and device acceptance remain
pending. This is not a scene adoption or final visual acceptance.

Exact executed CPU scripts, reports, logs, candidate and source-matched
baseline roof PNG/record are retained. The helper is archived for provenance;
these scripts still use the original scratch/repository paths.
