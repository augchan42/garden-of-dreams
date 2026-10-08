"""Replace only packed architectural color images in a separate Blender source."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--baseline-root', type=Path, required=True)
parser.add_argument('--candidate-root', type=Path, required=True)
parser.add_argument('--output-root', type=Path, required=True)
parser.add_argument('--before-export', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = args.output_root.resolve()
production = Path('/Users/auchan/projects/garden-of-dreams')
source = Path(bpy.data.filepath).resolve()
assert root != production and production not in root.parents, 'Separate source candidate required'
assert source != (production/'blender/authoring.blend').resolve(), 'Use the isolated neutral source'
assert source != root/'blender/authoring.blend', 'Do not overwrite the input source'
assert not (root/'blender/authoring.blend').exists(), 'Do not replace an existing source candidate'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_hash = sha(source)
pending = []
for kind in ('pavilion', 'wall'):
    old_folder = args.baseline_root/'textures/atlases'/kind
    new_folder = args.candidate_root/'textures/atlases'/kind
    old_config = json.loads((old_folder/'atlas.json').read_text())
    new_config = json.loads((new_folder/'atlas.json').read_text())
    for key in ('size', 'uv_regions', 'padding_pixels', 'orm_channels'):
        assert old_config[key] == new_config[key], ('Atlas layout changed', kind, key)
    assert new_config['size'] == [2048, 2048]
    assert all(sha(new_folder/name) == digest for name,digest in new_config['files'].items())
    for channel in ('normal', 'orm'):
        assert (old_folder/f'{kind}_{channel}.png').read_bytes() == (new_folder/f'{kind}_{channel}.png').read_bytes()
    material = bpy.data.materials['MAT_'+kind+'_atlas']
    nodes = material.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    links = list(bsdf.inputs['Base Color'].links)
    assert len(links) == 1 and links[0].from_node.type == 'TEX_IMAGE'
    node = links[0].from_node
    image = node.image
    assert image.packed_file and tuple(image.size) == (2048, 2048)
    assert image.colorspace_settings.name == 'sRGB'
    old_hash = hashlib.sha256(bytes(image.packed_file.data)).hexdigest()
    assert old_hash == sha(old_folder/f'{kind}_basecolor.png'), ('Unexpected packed input image', kind)
    uses = [(m.name, n.name) for m in bpy.data.materials if m.use_nodes
            for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image == image]
    assert uses == [(material.name, node.name)], ('Color image has other material users', uses)
    pending.append((kind, node, image, new_folder/f'{kind}_basecolor.png', old_hash))
changes = {}
for kind, node, old, file, old_hash in pending:
    previous_name = old.name
    previous_fake_user = old.use_fake_user
    image = bpy.data.images.load(str(file.resolve()), check_existing=False)
    image.colorspace_settings.name = 'sRGB'
    image.pack()
    assert tuple(image.size) == (2048, 2048)
    assert hashlib.sha256(bytes(image.packed_file.data)).hexdigest() == sha(file)
    node.image = image
    assert old.users == int(previous_fake_user), ('Image has an unreviewed user', old.name, old.users)
    bpy.data.images.remove(old)
    image.name = previous_name
    image.use_fake_user = previous_fake_user
    assert image.name == previous_name
    changes[kind] = {'image_name':image.name, 'before_sha256':old_hash, 'after_sha256':sha(file)}
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
(root/'blender/sites').mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/authoring.blend'), compress=True)
assert sha(source) == source_hash
report = {'status':'saved_architecture_atlas_candidate_export_pending',
          'input_authoring_sha256':source_hash,
          'candidate_authoring_sha256':sha(root/'blender/authoring.blend'), 'changed_images':changes,
          'scope':'Only packed wall and pavilion color images replaced. Full fresh lighting and native scene acceptance required before adoption.'}
(root/'architecture-atlas-application.json').write_text(json.dumps(report, indent=2)+'\n')
sys.argv = ['export_garden.py', '--', '--output-root', str(root)]
runpy.run_path(str(Path(__file__).resolve().parent/'export_garden.py'), run_name='__main__')
report['candidate_glb_sha256'] = sha(root/'export/garden-of-dreams.glb')
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_garden_atlas_export import compare
preservation = compare(args.before_export, root/'export/garden-of-dreams.glb',
                       args.baseline_root, args.candidate_root)
(root/'export/atlas-export-preservation.json').write_text(json.dumps(preservation, indent=2)+'\n')
report['status'] = 'saved_architecture_atlas_candidate_exported_not_adopted'
(root/'architecture-atlas-application.json').write_text(json.dumps(report, indent=2)+'\n')
print('GARDEN_ARCHITECTURE_ATLAS_SOURCE_PASS', report['candidate_glb_sha256'])
