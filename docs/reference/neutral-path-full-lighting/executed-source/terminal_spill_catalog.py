"""Validate every native terminal spill artifact before engine installation."""
import hashlib
import json
import math
from pathlib import Path
import struct

from lightmap_catalog import eligible_meshes, glb_document


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_catalog(root: Path, source: Path) -> dict:
    manifest = json.loads((source / 'manifest.json').read_text())
    assert manifest['source_glb_sha256'] == sha(root / 'export/garden-of-dreams.glb'), 'Stale spill GLB'
    assert manifest['authoring_blend_sha256'] == sha(root / 'blender/authoring.blend'), 'Stale spill authoring'
    assert manifest['stage_blend_sha256'] == sha(root / 'blender/sites/SITE_stage.blend'), 'Stale spill stage'
    assert manifest['terminal_blend_sha256'] == sha(root / 'blender/sites/SITE_terminal-cells.blend'), 'Stale terminal source'
    assert len(manifest['site_blend_sha256']) == manifest['lights_baked'] == 12
    for slug, digest in manifest['site_blend_sha256'].items():
        assert sha(root / 'blender/sites' / ('SITE_' + slug + '.blend')) == digest, 'Stale exterior wash'
    assert len(manifest['lighting']['lights']) == 12 and manifest['lighting']['type'] == 'AREA'
    assert manifest['pass_filter'] == ['INDIRECT']
    assert manifest['adaptive_sampling'] is False and manifest['path_guiding'] is False
    assert manifest['samples'] >= 2048 and manifest['size'] >= 512
    assert manifest['point_lights_baked'] is False and manifest['emissive_geometry_baked'] is False
    assert set(manifest['controls']) == {'direct', 'window_only', 'sealed', 'washes_off'}
    for name, cells in manifest['controls'].items():
        assert len(cells) == 6
        for cell in cells:
            maximum = cell['linear_max']
            assert cell['pixels'] > 30 and math.isfinite(maximum)
            assert len(cell['linear_mean']) == 3 and all(math.isfinite(v) for v in cell['linear_mean'])
            if name == 'window_only':
                assert maximum > 1e-9
            else:
                assert maximum <= 1e-7
    expected = eligible_meshes(glb_document(root / 'export/sites/SITE_terminal-cells.glb'))
    assert len(expected) == 7 and set(manifest['records']) == expected
    records = {}
    provenance = ('source_glb_sha256', 'authoring_blend_sha256', 'stage_blend_sha256',
                  'terminal_blend_sha256', 'site_blend_sha256', 'samples', 'size',
                  'adaptive_sampling', 'path_guiding', 'pass_filter', 'point_lights_baked',
                  'emissive_geometry_baked', 'lights_baked')
    for name in sorted(expected):
        record = json.loads((source / (name + '.json')).read_text())
        assert record == manifest['records'][name] and record['mesh'] == name
        assert all(record[key] == manifest[key] for key in provenance), 'Map/manifest provenance differs'
        assert record['texture'] == name + '.png' and record['uv_channel'] == 1
        base = json.loads((root / 'export/lightmaps' / (name + '.json')).read_text())
        assert base['source_glb_sha256'] == manifest['source_glb_sha256']
        assert base['uv_sha256'] == record['uv_sha256'], 'Spill UVs differ from canonical base bake'
        scale, maximum = record['scale'], record['linear_max']
        assert math.isfinite(scale) and scale > 0 and math.isfinite(maximum) and maximum >= 0
        if maximum > 1e-12:
            assert abs(scale - maximum) <= 1e-10
        else:
            assert scale == 1
        assert math.isfinite(record['nonzero_fraction']) and 0 <= record['nonzero_fraction'] <= 1
        png = source / record['texture']
        assert sha(png) == record['png_sha256'], 'Spill PNG content changed'
        header = png.read_bytes()[:26]
        assert header[:8] == b'\x89PNG\r\n\x1a\n' and header[24] == 16
        assert struct.unpack('>II', header[16:24]) == (record['size'], record['size'])
        key = name.replace('.', '_')
        assert key not in records
        records[key] = {**record, 'texture': 'terminal-spill/' + record['texture'], 'engine_node': key}
    return records
