"""Export the corrected saved roof/LOD sources without regenerating their UVs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output-root', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
sys.path.insert(0, str(ROOT / 'scripts'))
from pavilion_roof_geometry import outer_shell

output = args.output_root / 'export/kits/pavilion'
output.mkdir(parents=True, exist_ok=True)
format = next(item[0] for item in io_scene_gltf2.get_format_items(None, bpy.context) if item[0] == 'GLB')
report = {'source_blend_sha256': hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
          'scope': 'Saved corrected roof sources and existing LOD modifiers; no source regeneration or UV repacking.',
          'exports': {}}
for variant in ('roof_hex', 'roof_square'):
    for suffix in ('', '_LOD1'):
        bpy.context.window.scene = bpy.data.scenes['Pavilion ' + variant + (' LOD1' if suffix else '')]
        collection = bpy.data.collections['KIT_pavilion_' + variant + suffix]
        render = [o for o in collection.objects if o.type == 'MESH' and not o.name.startswith('COL_')]
        assert len(render) == 1
        assert all(p.normal.z > .25 for p in outer_shell(render[0].data))
        path = output / ('KIT_pavilion_' + variant + suffix + '.glb')
        bpy.ops.export_scene.gltf(filepath=str(path), export_format=format, use_active_scene=True,
                                 export_apply=True, export_extras=True, export_animations=False,
                                 export_loglevel=-1)
        report['exports'][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if variant == 'roof_hex':
            legacy = output.parent / ('KIT_pavilion' + suffix + '.glb')
            shutil.copy2(path, legacy)
report_path = args.output_root / 'export/pavilion-roof-saved-export.json'
report_path.write_text(json.dumps(report, indent=2) + '\n')
print('SAVED_PAVILION_ROOFS_EXPORT_PASS', len(report['exports']), flush=True)
