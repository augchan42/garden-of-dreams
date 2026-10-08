"""Non-overlapping render slabs and the original continuous collision footprint."""

COLLISION_SLABS = (
    ((-19.2, -2.5, -.12), (1.8, 5.0, .24)),
    ((-22.1, -5.0, -.12), (7.6, 1.8, .24)),
    ((-25.0, -7.9, -.12), (1.8, 7.6, .24)),
)

# Butt each longitudinal slab against the crosspiece. Its two corner patches
# previously had two coplanar top faces, causing self-shadowed lightmaps.
RENDER_SLABS = (
    ((-19.2, -2.05, -.12), (1.8, 4.1, .24)),
    COLLISION_SLABS[1],
    ((-25.0, -8.8, -.12), (1.8, 5.8, .24)),
)
