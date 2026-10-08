# Ouxiang roof native comparison — 2026-10-08

The baseline is the fully baked imperial candidate 361a67c7. The isolated
Ouxiang UV2 proposal be80374c swaps only the target roof mesh and its fresh
matching 128-sample 1024² Cycles map. Complete candidate lighting is not adopted.
The earlier CPU diagnosis/proposal is recorded in `../ouxiang-roof-proposal/`.

Read-only saved Blender inspection identifies 168 closed eight-sided tile
cylinders of 18 mm radius and one roof shell. All 169 saved vertex sets and triangle
counts match unique export components within 30 µm. Cylinder face normals point
outward. Saved authoring is unchanged; this does not establish a default
Blender allocator for the proposed UVs.

Matching RGB16 upward-side zero centroids fall from 117/1344 to 0/1344. Upward cap
zeros rise from 218/1008 to 229/1008; shell samples remain nonzero. These samples
do not prove camera visibility, all-pixel coverage, gutters or cap cause.
The original diagnosis PNG equals the fresh 361a baseline PNG byte for byte.

Three native comparison runs cover desktop, 390×844 portrait, roof close-up and
an alternative portrait framing. All 96 capture hashes and twelve exact
baseline/restored pairs verify. The three ordinary-view baselines also match
between runs. Two different portrait-water poses are clearly separated.

Actual lossless 512 import is 512² RGB8/786,432bytes. Actual lossless 256 is RGB8/
196,608bytes; actual compressed 256 is DXT1/32,768bytes. These are decoded image
bytes, not renderer or phone allocations. The 512 setting looks cleanest in
inspected originals. Both actual 256 imports retain patchy alternating shading,
despite the smoother manual-resize preview; 512 is selected for the next full
candidate validation.

The lower/further portrait pose exposes more platform and water, but final
framing still needs a 512 render and moving-camera/full-route verification.
Materials, eave joins, backdrop, water treatment and full-site acceptance are
open. No production Ouxiang source, map or camera is installed by these runs.

Exact scripts, source ownership, fresh map, all original captures, import
parameters and native logs are retained. Reproducible default export, complete
matching lighting, final art, memory and actual device checks remain required.
