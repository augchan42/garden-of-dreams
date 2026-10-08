"""Compare actual GLB data, resolving indices before checking preservation."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Document:
    def __init__(self, path):
        self.blob = path.read_bytes()
        length = struct.unpack_from('<I', self.blob, 12)[0]
        self.data = json.loads(self.blob[20:20 + length])
        offset = 20 + length
        self.binary = self.blob[offset + 8:offset + 8 + struct.unpack_from('<I', self.blob, offset)[0]]
        self.nodes = {n['name']: n for n in self.data['nodes']}

    def view(self, index):
        view = self.data['bufferViews'][index]
        start = view.get('byteOffset', 0)
        return self.binary[start:start + view['byteLength']]

    def accessor(self, index):
        accessor = self.data['accessors'][index]
        assert 'sparse' not in accessor
        view = self.data['bufferViews'][accessor['bufferView']]
        sizes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
        widths = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
        size = sizes[accessor['componentType']] * widths[accessor['type']]
        stride = view.get('byteStride', size)
        start = accessor.get('byteOffset', 0)
        data = self.view(accessor['bufferView'])
        values = b''.join(data[start + i * stride:start + i * stride + size]
                          for i in range(accessor['count']))
        return {k: v for k, v in accessor.items() if k not in ('bufferView', 'byteOffset')} | {'values_sha256': digest(values)}

    def texture(self, index):
        texture = self.data['textures'][index]
        image = self.data['images'][texture['source']]
        assert 'bufferView' in image
        return {'image_sha256': digest(self.view(image['bufferView'])),
                'mime': image['mimeType'],
                'sampler': self.data['samplers'][texture['sampler']] if 'sampler' in texture else None}

    def material(self, index):
        def resolve(value):
            if isinstance(value, list):
                return [resolve(v) for v in value]
            if not isinstance(value, dict):
                return value
            return {k: (v | {'index': self.texture(v['index'])}) if k.endswith('Texture') and isinstance(v, dict) and 'index' in v else resolve(v)
                    for k, v in value.items()}
        return resolve(self.data['materials'][index])

    def node(self, name):
        source = self.nodes[name]
        value = {k: v for k, v in source.items() if k not in ('mesh', 'camera', 'children', 'extensions')}
        if 'children' in source:
            value['children'] = [self.data['nodes'][i]['name'] for i in source['children']]
        if 'camera' in source:
            value['camera'] = self.data['cameras'][source['camera']]
        extensions = dict(source.get('extensions', {}))
        if 'KHR_lights_punctual' in extensions:
            index = extensions['KHR_lights_punctual']['light']
            extensions['KHR_lights_punctual'] = self.data['extensions']['KHR_lights_punctual']['lights'][index]
        if extensions:
            value['extensions'] = extensions
        if 'mesh' in source:
            mesh = self.data['meshes'][source['mesh']]
            primitives = []
            for primitive in mesh['primitives']:
                item = {k: v for k, v in primitive.items() if k not in ('attributes', 'indices', 'material')}
                item['attributes'] = {k: self.accessor(v) for k, v in primitive['attributes'].items()}
                if 'indices' in primitive:
                    item['indices'] = self.accessor(primitive['indices'])
                if 'material' in primitive:
                    item['material'] = self.material(primitive['material'])
                primitives.append(item)
            value['mesh'] = primitives
        return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-root', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    candidate = args.candidate_root.resolve()
    original = Document(root / 'export/garden-of-dreams.glb')
    prepared = Document(candidate / 'export/garden-of-dreams.glb')
    added = set(prepared.nodes) - set(original.nodes)
    assert added == {'SITE_stage_MAT_stage_canopy_paint'}, added
    assert set(original.nodes) <= set(prepared.nodes)
    for name in original.nodes:
        assert original.node(name) == prepared.node(name), ('Existing GLB contract differs', name)
    canopy = prepared.node(next(iter(added)))
    assert canopy['extras']['godot_cast_shadow'] is False
    primitive = canopy['mesh'][0]
    assert primitive['indices']['count'] == 2240 * 3
    assert {'TEXCOORD_0', 'TEXCOORD_1'} <= set(primitive['attributes'])
    identical = []
    for path in sorted((root / 'export/sites').glob('*.glb')):
        if path.name == 'SITE_stage.glb':
            continue
        assert path.read_bytes() == (candidate / 'export/sites' / path.name).read_bytes(), path.name
        identical.append(path.name)
    report = {'status': 'scratch_export_verified', 'source_glb_sha256': digest(original.blob),
              'candidate_glb_sha256': digest(prepared.blob),
              'existing_complete_node_contracts_preserved': len(original.nodes),
              'byte_identical_site_exports': identical, 'canopy_triangles': 2240,
              'canopy_node': canopy,
              'scope': 'Actual separate export preserves existing mesh data including both UV channels, embedded paint bytes/material factors, cameras, lights, transforms, extras and node children. New canopy carries no-shadow intent. Not Godot importer/baker shadow behavior, fresh lighting, adoption or final paint acceptance.'}
    (candidate / 'export-preservation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('CANOPY_EXPORT_PRESERVATION_PASS', report['candidate_glb_sha256'], len(original.nodes), len(identical))


if __name__ == "__main__":
    main()
