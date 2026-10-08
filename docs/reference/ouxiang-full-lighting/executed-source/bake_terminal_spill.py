"""Bake native cyclorama-wash indirect light into the seven terminal batches.

Keep the ordinary maps independent. Fixed sampling is required for the rare
window paths; normalized PNGs retain their faint physical energy through scale.
Run in a separate Blender process with --python-exit-code 1.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from native_wash_scene import isolated_wash_scene
from lightmap_catalog import eligible_meshes, glb_document

parser = argparse.ArgumentParser()
parser.add_argument('--samples', type=int, default=2048)
parser.add_argument('--size', type=int, default=512)
parser.add_argument('--output', type=Path, default=ROOT / 'export/lightmaps/terminal-spill')
parser.add_argument('--controls-only', action='store_true')
options = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
assert options.samples >= 2048 and options.size >= 512
rig = isolated_wash_scene(ROOT, options.samples)
scene = rig['scene']
scene.cycles.use_adaptive_sampling = False
scene.cycles.use_guiding = False
scene.cycles.diffuse_bounces = 4
scene.cycles.seed = 0
bpy.context.view_layer.update()
terminal = ROOT / 'blender/sites/SITE_terminal-cells.blend'
terminal_hash = hashlib.sha256(terminal.read_bytes()).hexdigest()
windows = sorted([o for o in scene.objects if o.name.startswith('TRG_cell_window')],
                 key=lambda o: o.matrix_world.translation.x)
doors = sorted([o for o in scene.objects if o.name.startswith('TRG_cell_door')],
               key=lambda o: o.matrix_world.translation.x)
assert len(windows) == len(doors) == 6
assert all(abs(w.matrix_world.translation.x - d.matrix_world.translation.x) < 1e-4
           for w, d in zip(windows, doors))
centres = [float(o.matrix_world.translation.x) for o in windows]
window_y = float(windows[0].matrix_world.translation.y) + .5
door_y = float(doors[0].matrix_world.translation.y)
assert all(abs(o.matrix_world.translation.y + .5 - window_y) < 1e-4 for o in windows)
assert all(abs(o.matrix_world.translation.y - door_y) < 1e-4 for o in doors)


def floor_masks(obj, size):
    """Rasterize top-face UV pixel centers into world-space cell interiors."""
    obj.data.update()
    matrix = obj.matrix_world.copy()
    normal_matrix = matrix.to_3x3().inverted().transposed()
    masks = [np.zeros((size, size), bool) for _ in centres]
    for polygon in obj.data.polygons:
        if (normal_matrix @ polygon.normal).normalized().z < .9:
            continue
        uv = np.array([list(obj.data.uv_layers[1].data[i].uv) for i in polygon.loop_indices])
        world = np.array([list(matrix @ obj.data.vertices[obj.data.loops[i].vertex_index].co)
                          for i in polygon.loop_indices])
        assert len(uv) == 3
        if np.max(np.abs(world[:, 2])) > .02:
            continue
        lo = np.maximum(0, np.floor(uv.min(axis=0) * size - .5).astype(int))
        hi = np.minimum(size - 1, np.ceil(uv.max(axis=0) * size - .5).astype(int))
        if np.any(hi < lo):
            continue
        xx, yy = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1))
        points = np.stack([(xx + .5) / size, (yy + .5) / size], axis=-1)
        a, b, c = uv
        v0, v1 = b - a, c - a
        denominator = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(denominator) < 1e-12:
            continue
        delta = points - a
        u = (delta[..., 0] * v1[1] - v1[0] * delta[..., 1]) / denominator
        v = (v0[0] * delta[..., 1] - delta[..., 0] * v0[1]) / denominator
        inside = (u >= 0) & (v >= 0) & (u + v <= 1)
        positions = world[0] + u[..., None] * (world[1] - world[0]) + v[..., None] * (world[2] - world[0])
        region = inside & (positions[..., 1] > door_y + .1) & (positions[..., 1] < window_y - .1)
        for index, x in enumerate(centres):
            masks[index][yy, xx] |= region & (positions[..., 0] > x - 1.1) & (positions[..., 0] < x + 1.1)
    assert all(mask.sum() > 30 for mask in masks)
    return masks


def block_openings(windows_blocked=False, doors_blocked=False):
    for obj in [o for o in scene.objects if o.name.startswith('CONTROL_spill_blocker_')]:
        bpy.data.objects.remove(obj, do_unlink=True)
    openings = ([('window', window_y, 1.65, 1.2)] if windows_blocked else [])
    openings += ([('door', door_y, 1.1, 2.2)] if doors_blocked else [])
    for kind, y, z, height in openings:
        for index, x in enumerate(centres):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
            obj = bpy.context.object
            obj.name = 'CONTROL_spill_blocker_' + kind + '_' + str(index)
            obj.dimensions = (1.3, .18, height)
            material = bpy.data.materials.new('Spill control black')
            material.use_nodes = True
            bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
            obj.data.materials.append(material)
    bpy.context.view_layer.update()


def bake(obj, passes):
    image = bpy.data.images.new('SPILL_' + obj.name, width=options.size, height=options.size,
                                alpha=False, float_buffer=True)
    image.colorspace_settings.name = 'Non-Color'
    for index, original in enumerate(list(obj.data.materials)):
        material = original.copy()
        obj.data.materials[index] = material
        node = material.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = image
        material.node_tree.nodes.active = node
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.data.uv_layers.active_index = 1
    bpy.ops.object.bake(type='DIFFUSE', pass_filter=set(passes),
                       uv_layer=obj.data.uv_layers[1].name, margin=4, use_clear=True)
    pixels = np.empty(options.size * options.size * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    pixels = pixels.reshape(options.size, options.size, 4)
    assert np.isfinite(pixels).all()
    return image, pixels


floor = bpy.data.objects['SITE_terminal-cells_MAT_stage_atlas']
masks = floor_masks(floor, options.size)
controls = {}
for name, windows_blocked, doors_blocked, off, direct in (
        ('direct', False, False, False, True),
        ('window_only', False, True, False, False),
        ('sealed', True, True, False, False),
        ('washes_off', False, False, True, False)):
    block_openings(windows_blocked, doors_blocked)
    for light in scene.objects:
        if light.type == 'LIGHT' and light.data.type == 'AREA':
            light.hide_render = off
    image, pixels = bake(floor, ['DIRECT'] if direct else ['INDIRECT'])
    cells = []
    for mask in masks:
        values = pixels[..., :3][mask]
        cells.append({'pixels': int(mask.sum()), 'linear_max': float(values.max()),
                      'linear_mean': values.mean(axis=0).tolist()})
    controls[name] = cells
    bpy.data.images.remove(image)
    print('TERMINAL_SPILL_CONTROL', name, cells, flush=True)
assert all(c['linear_max'] > 1e-9 for c in controls['window_only']), 'Missing window bounce in a cell'
for name in ('direct', 'sealed', 'washes_off'):
    assert all(c['linear_max'] <= 1e-7 for c in controls[name]), (name, controls[name])
block_openings()
for light in scene.objects:
    if light.type == 'LIGHT' and light.data.type == 'AREA':
        light.hide_render = False

provenance = {key: rig[key] for key in ('source_hash', 'stage_hash', 'authoring_hash', 'site_hashes')}
report = {'source_glb_sha256': provenance['source_hash'], 'stage_blend_sha256': provenance['stage_hash'],
          'authoring_blend_sha256': provenance['authoring_hash'], 'site_blend_sha256': provenance['site_hashes'],
          'terminal_blend_sha256': terminal_hash, 'samples': options.samples,
          'adaptive_sampling': False, 'path_guiding': False, 'size': options.size,
          'pass_filter': ['INDIRECT'], 'point_lights_baked': False, 'emissive_geometry_baked': False,
          'lights_baked': 12, 'lighting': {**rig['lighting'], 'pass_filter': ['INDIRECT']}, 'shadow_intent':rig['shadow_intent']['explicit_meshes'], 'controls': controls,
          'scope': 'Native indirect diffuse from saved linked exterior washes; actual production openings retained.',
          'engine_installed': False, 'records': {}}
options.output.mkdir(parents=True, exist_ok=True)
if not options.controls_only:
    names = eligible_meshes(glb_document(ROOT / 'export/sites/SITE_terminal-cells.glb'))
    assert len(names) == 7
    for name in sorted(names):
        obj = bpy.data.objects[name]
        image, pixels = bake(obj, ['INDIRECT'])
        maximum = float(pixels[..., :3].max())
        scale = maximum if maximum > 1e-12 else 1.0
        nonzero = float((pixels[..., :3].max(axis=2) > 1e-9).mean())
        pixels[..., :3] /= scale
        pixels[..., 3] = 1
        image.pixels.foreach_set(pixels.ravel())
        filename = name + '.png'
        image.file_format = 'PNG'
        image.filepath_raw = str(options.output / filename)
        image.save()
        uv = np.empty(len(obj.data.uv_layers[1].data) * 2, dtype=np.float32)
        obj.data.uv_layers[1].data.foreach_get('uv', uv)
        record = {key: report[key] for key in ('source_glb_sha256', 'stage_blend_sha256',
                  'authoring_blend_sha256', 'site_blend_sha256', 'terminal_blend_sha256',
                  'samples', 'adaptive_sampling', 'path_guiding', 'size', 'pass_filter',
                  'point_lights_baked', 'emissive_geometry_baked', 'lights_baked')}
        record.update(mesh=name, texture=filename, scale=scale, linear_max=maximum,
                      nonzero_fraction=nonzero, uv_channel=1,
                      uv_sha256=hashlib.sha256(uv.tobytes()).hexdigest(),
                      png_sha256=hashlib.sha256((options.output / filename).read_bytes()).hexdigest())
        (options.output / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        report['records'][name] = record
        bpy.data.images.remove(image)
        print('TERMINAL_SPILL_BAKED', name, maximum, nonzero, flush=True)
assert hashlib.sha256(rig['source'].read_bytes()).hexdigest() == rig['source_hash']
assert hashlib.sha256(rig['authoring'].read_bytes()).hexdigest() == rig['authoring_hash']
assert hashlib.sha256(rig['stage'].read_bytes()).hexdigest() == rig['stage_hash']
assert hashlib.sha256(terminal.read_bytes()).hexdigest() == terminal_hash
for slug, digest in rig['site_hashes'].items():
    assert hashlib.sha256((ROOT / 'blender/sites' / ('SITE_' + slug + '.blend')).read_bytes()).hexdigest() == digest
(options.output / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
print('NATIVE_TERMINAL_SPILL_PASS', len(report['records']), 'source files unchanged', flush=True)
