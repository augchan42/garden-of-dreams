"""Update isolated saved kits, preserving their export and source contracts.

Run in a fresh background Blender with --baseline-root and --candidate-root.
Only packed color images change. Baseline exports must first reproduce exactly.
"""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import shutil
import sys

import bpy

KITS = ('pavilion', 'corridor', 'wall', 'rockery')
ALIASES = {'pavilion': 'roof_hex', 'corridor': 'straight', 'wall': 'bay', 'rockery': 'medium'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def values(value):
    if isinstance(value, bpy.types.ID):
        return {'id': value.name, 'type': type(value).__name__}
    if isinstance(value, (str, bool, int, float)) or value is None:
        return value
    if hasattr(value, 'items'):
        return {k: values(v) for k, v in value.items()}
    return [values(v) for v in value]


def properties(block):
    return {key: values(value) for key, value in block.items()}


def floats(items, field, width):
    data = array('f', [0]) * (len(items) * width)
    items.foreach_get(field, data)
    return hashlib.sha256(data.tobytes()).hexdigest()


def snapshot():
    objects = {}
    for obj in bpy.data.objects:
        row = {'type': obj.type, 'matrix': values(obj.matrix_world), 'parent': values(obj.parent),
               'props': properties(obj), 'hide_render': obj.hide_render,
               'hide_viewport': obj.hide_viewport, 'data': values(obj.data),
               'instance_collection': values(obj.instance_collection),
               'modifiers': []}
        for modifier in obj.modifiers:
            row['modifiers'].append({p.identifier: values(getattr(modifier, p.identifier))
                                     for p in modifier.bl_rna.properties
                                     if not p.is_readonly and p.type in ('BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM', 'POINTER')})
        if obj.type == 'MESH':
            mesh = obj.data
            row['mesh'] = {'vertices': floats(mesh.vertices, 'co', 3),
                           'faces': [list(p.vertices) for p in mesh.polygons],
                           'material_indices': [p.material_index for p in mesh.polygons],
                           'smooth': [p.use_smooth for p in mesh.polygons],
                           'materials': [m.name for m in mesh.materials],
                           'uv': {uv.name: floats(uv.data, 'uv', 2) for uv in mesh.uv_layers}}
        if obj.type == 'CAMERA':
            row['camera'] = {k: values(getattr(obj.data, k)) for k in ('type', 'lens', 'sensor_fit', 'sensor_width', 'clip_start', 'clip_end')}
        if obj.type == 'LIGHT':
            row['light'] = {k: values(getattr(obj.data, k)) for k in ('type', 'color', 'energy')}
        objects[obj.name] = row
    return {'objects': objects,
            'collections': {c.name: {'objects': sorted(o.name for o in c.objects),
                                     'children': sorted(x.name for x in c.children), 'props': properties(c)}
                            for c in bpy.data.collections},
            'scenes': {s.name: {'collections': sorted(c.name for c in s.collection.children),
                                'camera': values(s.camera), 'world': values(s.world), 'props': properties(s)}
                       for s in bpy.data.scenes}}


def images():
    return {image.name: {'sha256': hashlib.sha256(image.packed_file.data).hexdigest(),
                         'size': list(image.size), 'colorspace': image.colorspace_settings.name,
                         'fake_user': image.use_fake_user}
            for image in bpy.data.images if image.packed_file}


def export_modules(kit, baseline, destination):
    manifest = json.loads((baseline / 'export/kits' / kit / 'manifest.json').read_text())
    directory = destination / 'export/kits' / kit
    directory.mkdir(parents=True, exist_ok=True)
    rows = {}
    for variant in manifest['variants']:
        for suffix in ('', '_LOD1'):
            scene_name = kit.capitalize() + ' ' + variant + (' LOD1' if suffix else '')
            bpy.context.window.scene = bpy.data.scenes[scene_name]
            bpy.context.view_layer.update()
            name = f'KIT_{kit}_{variant}{suffix}.glb'
            path = directory / name
            bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_active_scene=True,
                                     export_apply=True, export_extras=True, export_animations=False, export_loglevel=-1)
            rows[name] = sha(path)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline-root', type=Path, required=True)
    parser.add_argument('--candidate-root', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    baseline, candidate = args.baseline_root.resolve(), args.candidate_root.resolve()
    production = Path(__file__).resolve().parents[1]
    assert baseline != candidate and not candidate.is_relative_to(production)
    assert not baseline.is_relative_to(production), 'Use isolated input copies'
    reports = {}
    for kit in KITS:
        source = baseline / f'blender/kits/KIT_{kit}.blend'
        output = candidate / f'blender/kits/KIT_{kit}.blend'
        assert not output.exists(), 'Do not overwrite a previous candidate'
        source_hash = sha(source)
        bpy.ops.wm.open_mainfile(filepath=str(source))
        original_scene = bpy.context.scene.name
        original = snapshot()
        before_images = images()
        reproduced = export_modules(kit, baseline, candidate.parent / 'baseline-reexports')
        for name, digest in reproduced.items():
            assert digest == sha(baseline / 'export/kits' / kit / name), ('Saved source did not reproduce existing export', kit, name)
        bpy.context.window.scene = bpy.data.scenes[original_scene]
        kind = 'wall' if kit == 'wall' else 'pavilion'
        material = bpy.data.materials['MAT_' + kind + '_atlas']
        bsdf = [n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED']
        assert len(bsdf) == 1
        links = list(bsdf[0].inputs['Base Color'].links)
        assert len(links) == 1 and links[0].from_node.type == 'TEX_IMAGE'
        node, old = links[0].from_node, links[0].from_node.image
        assert old.packed_file and old.colorspace_settings.name == 'sRGB' and list(old.size) == [2048, 2048]
        expected_old = sha(baseline / f'textures/atlases/{kind}/{kind}_basecolor.png')
        assert before_images[old.name]['sha256'] == expected_old
        uses = [(m.name, n.name) for m in bpy.data.materials if m.use_nodes
                for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image == old]
        assert uses == [(material.name, node.name)], ('Unexpected color image users', uses)
        name, fake_user = old.name, old.use_fake_user
        color_path = candidate / f'textures/atlases/{kind}/{kind}_basecolor.png'
        image = bpy.data.images.load(str(color_path), check_existing=False)
        image.colorspace_settings.name = 'sRGB'
        image.pack()
        node.image = image
        assert old.users == int(fake_user)
        bpy.data.images.remove(old)
        image.name, image.use_fake_user = name, fake_user
        assert image.name == name
        output.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(output))
        assert snapshot() == original, 'Saved native geometry, UV, metadata or scene contract changed'
        after_images = images()
        wanted = json.loads(json.dumps(before_images))
        wanted[name]['sha256'] = sha(color_path)
        assert after_images == wanted, 'Unrelated packed image or color configuration changed'
        assert expected_old != sha(color_path)
        exports = export_modules(kit, baseline, candidate)
        for suffix in ('', '_LOD1'):
            alias = candidate / f'export/kits/KIT_{kit}{suffix}.glb'
            original_alias = baseline / alias.relative_to(candidate)
            original_variant = baseline / f'export/kits/{kit}/KIT_{kit}_{ALIASES[kit]}{suffix}.glb'
            assert original_alias.read_bytes() == original_variant.read_bytes(), 'Legacy alias is not the expected module'
            shutil.copyfile(candidate / f'export/kits/{kit}/KIT_{kit}_{ALIASES[kit]}{suffix}.glb', alias)
        assert sha(source) == source_hash
        reports[kit] = {'source_sha256': source_hash, 'candidate_sha256': sha(output),
                        'native_snapshot_sha256': hashlib.sha256(json.dumps(original, sort_keys=True).encode()).hexdigest(),
                        'baseline_exports_reproduced': reproduced, 'candidate_exports': exports,
                        'images_before': before_images, 'images_after': after_images,
                        'saved_native_contract_equal': True}
        (candidate.parent / 'source-update.json').write_text(json.dumps({'status': 'partial', 'kits': reports}, indent=2)+'\n')
        print('SAVED_KIT_PALETTE_PASS', kit, len(exports), flush=True)
    (candidate.parent / 'source-update.json').write_text(json.dumps({'status': 'four_saved_kits_updated_exported_preserved', 'kits': reports}, indent=2)+'\n')


if __name__ == '__main__':
    main()
