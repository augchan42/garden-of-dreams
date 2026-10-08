"""Inspect a saved candidate in Blender and reproduce its default exports.

Run on an isolated authoring file with --source-root and --output-root.
This saves no Blender files and writes exports only under output-root.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

import bpy

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
from garden_material_palette import COMMON_BASE_COLORS
from nunnery_path_layout import COLLISION_SLABS, RENDER_SLABS


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inspect_path():
    collection = bpy.data.collections['SITE_stage']
    rows = []
    for prefix, slabs in [('LONGCUI_approach', RENDER_SLABS),
                          ('COL_longcui_approach', COLLISION_SLABS)]:
        objects = sorted((o for o in collection.objects if o.name.startswith(prefix)),
                         key=lambda o: o.name)
        assert len(objects) == len(slabs), (prefix, [o.name for o in objects])
        for obj, (center, dimensions) in zip(objects, slabs):
            assert obj.type == 'MESH' and len(obj.data.vertices) == 8 and len(obj.data.polygons) == 6
            points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
            bounds = [[min(p[i] for p in points) for i in range(3)],
                      [max(p[i] for p in points) for i in range(3)]]
            expected = [[center[i] - dimensions[i] / 2 for i in range(3)],
                        [center[i] + dimensions[i] / 2 for i in range(3)]]
            assert all(abs(a-b) < 1e-5 for row, wanted in zip(bounds, expected)
                       for a, b in zip(row, wanted)), (obj.name, bounds, expected)
            if prefix == 'LONGCUI_approach':
                assert [m.name for m in obj.data.materials] == ['MAT_plaster_rock']
            rows.append({'name': obj.name, 'bounds_z_up': bounds,
                         'materials': [m.name for m in obj.data.materials]})
    return rows


def inspect_palette(source):
    plain, atlases = {}, {}
    for name, rgb in COMMON_BASE_COLORS.items():
        material = bpy.data.materials[name]
        nodes = [n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED']
        assert len(nodes) == 1, name
        value = list(nodes[0].inputs['Base Color'].default_value)
        assert not nodes[0].inputs['Base Color'].is_linked, name
        assert all(abs(a-b) < 1e-7 for a, b in zip(value, [*rgb, 1])), (name, value)
        plain[name] = value
    for kind in ('pavilion', 'wall'):
        material = bpy.data.materials['MAT_' + kind + '_atlas']
        nodes = [n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED']
        assert len(nodes) == 1 and len(nodes[0].inputs['Base Color'].links) == 1
        image_node = nodes[0].inputs['Base Color'].links[0].from_node
        assert image_node.type == 'TEX_IMAGE' and image_node.image.packed_file
        image = image_node.image
        digest = hashlib.sha256(image.packed_file.data).hexdigest()
        assert digest == sha(source / 'textures/atlases' / kind / (kind + '_basecolor.png'))
        assert list(image.size) == [2048, 2048] and image.colorspace_settings.name == 'sRGB'
        atlases[material.name] = {'packed_png_sha256': digest, 'size': list(image.size),
                                 'colorspace': image.colorspace_settings.name}
    return {'plain_linear_rgba': plain, 'packed_color_atlases': atlases}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    source, output = args.source_root.resolve(), args.output_root.resolve()
    author = source / 'blender/authoring.blend'
    assert Path(bpy.data.filepath).resolve() == author
    assert output != source and not output.is_relative_to(source)
    author_hash = sha(author)
    path_rows = inspect_path()
    palette = inspect_palette(source)
    # Use the canonical exporter with its defaults, not the candidate's executed copy.
    sys.argv = [str(SCRIPT_ROOT / 'export_garden.py'), '--', '--output-root', str(output)]
    runpy.run_path(str(SCRIPT_ROOT / 'export_garden.py'), run_name='__main__')
    exports = {}
    for original in [source / 'export/garden-of-dreams.glb',
                     *sorted((source / 'export/sites').glob('*.glb'))]:
        relative = original.relative_to(source / 'export')
        reproduced = output / 'export' / relative
        assert original.read_bytes() == reproduced.read_bytes(), str(relative)
        exports[str(relative)] = sha(reproduced)
    assert len(exports) == 16
    bpy.ops.wm.open_mainfile(filepath=str(source / 'blender/sites/SITE_stage.blend'))
    library_rows = inspect_path()
    assert library_rows == path_rows
    assert sha(author) == author_hash
    report = {'status': 'saved_candidate_and_default_exports_verified',
              'authoring_sha256': author_hash, 'default_export_equality': exports,
              'saved_authoring_palette': palette, 'saved_path_ownership': path_rows,
              'stage_library_sha256': sha(source / 'blender/sites/SITE_stage.blend'),
              'scope': 'Read-only saved source/palette/path ownership and exact default reexport of all sixteen GLBs. No rendering, bake or adoption.'}
    (output / 'saved-source-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('SAVED_GARDEN_CANDIDATE_PASS', exports['garden-of-dreams.glb'])


if __name__ == '__main__':
    main()
