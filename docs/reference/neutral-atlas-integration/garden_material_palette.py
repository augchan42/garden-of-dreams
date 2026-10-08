"""Linear RGB for the four plain shared garden materials."""

COMMON_BASE_COLORS = {
    'MAT_lattice_wood': (.085, .045, .022),
    'MAT_whitewash': (.36, .335, .29),
    'MAT_rooftile': (.045, .055, .065),
    'MAT_plaster_rock': (.21, .205, .19),
}

# Baseline checked by the saved-source applicator. Atlas, foliage, CRT and
# emissive practical materials have separate contracts and are not changed.
PREVIOUS_BASE_COLORS = {
    'MAT_lattice_wood': (.045, .07, .025),
    'MAT_whitewash': (.3, .39, .23),
    'MAT_rooftile': (.025, .06, .035),
    'MAT_plaster_rock': (.15, .24, .12),
}
