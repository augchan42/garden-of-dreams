"""Compare a painted-flat export with its preceding physical scene.

Expand indexed triangles before comparison: a new UV seam may duplicate vertices
without changing the physical geometry or the second lightmap UV channel.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PAINT_MATERIALS = {'MAT_painted_mountains_' + str(i) for i in range(3)}
PAINT_NODES = {'SITE_stage_' + name for name in PAINT_MATERIALS}
DTYPES = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5122: '<i2', 5121: 'u1', 5120: 'i1'}
COLUMNS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


class Glb:
    def __init__(self, path):
        self.path = Path(path)
        self.bytes = self.path.read_bytes()
        magic, version, size = struct.unpack_from('<III', self.bytes)
        assert magic == 0x46546C67 and version == 2 and size == len(self.bytes)
        length, kind = struct.unpack_from('<II', self.bytes, 12)
        assert kind == 0x4E4F534A
        self.doc = json.loads(self.bytes[20:20 + length])
        bin_length, bin_kind = struct.unpack_from('<II', self.bytes, 20 + length)
        assert bin_kind == 0x004E4942
        self.binary = self.bytes[28 + length:28 + length + bin_length]

    def accessor(self, index):
        a = self.doc['accessors'][index]
        assert 'sparse' not in a
        view = self.doc['bufferViews'][a['bufferView']]
        dtype = np.dtype(DTYPES[a['componentType']])
        columns = COLUMNS[a['type']]
        return np.ndarray((a['count'], columns), dtype=dtype, buffer=self.binary,
                          offset=view.get('byteOffset', 0) + a.get('byteOffset', 0),
                          strides=(view.get('byteStride', dtype.itemsize * columns), dtype.itemsize)).copy()

    def image_hash(self, image):
        view = self.doc['bufferViews'][image['bufferView']]
        start = view.get('byteOffset', 0)
        return hashlib.sha256(self.binary[start:start + view['byteLength']]).hexdigest()

    def texture(self, index):
        texture = copy.deepcopy(self.doc['textures'][index])
        texture['source'] = self.image_hash(self.doc['images'][texture['source']])
        if 'sampler' in texture:
            texture['sampler'] = self.doc['samplers'][texture['sampler']]
        return texture

    def material(self, material):
        def resolve(value):
            if isinstance(value, list):
                return [resolve(v) for v in value]
            if not isinstance(value, dict):
                return value
            result = {}
            for key, item in value.items():
                if key.endswith('Texture') and isinstance(item, dict) and 'index' in item:
                    item = copy.deepcopy(item)
                    item['index'] = self.texture(item['index'])
                result[key] = resolve(item)
            return result
        return resolve(material)


def compare(before_path, after_path, paint_hash):
    old, new = Glb(before_path), Glb(after_path)
    atlas = json.loads((ROOT / 'textures/backdrops/mountain-paint/atlas.json').read_text())
    for key in ('asset', 'extensionsUsed', 'extensionsRequired', 'extensions', 'scene', 'scenes', 'cameras'):
        assert old.doc.get(key) == new.doc.get(key), ('Scene or light/camera contract changed', key)
    assert len(old.doc['nodes']) == len(new.doc['nodes'])
    targets = []
    triangle_count = 0
    for previous, current in zip(old.doc['nodes'], new.doc['nodes']):
        name = previous.get('name')
        contract = copy.deepcopy(current)
        if name in PAINT_NODES:
            assert contract.pop('extras') == {'paint_source': 'textures/backdrops/mountain-paint/atlas.json'}
            targets.append(name)
        assert previous == contract, ('Node identity/transform/collision changed', name)
        if 'mesh' not in previous:
            continue
        a = old.doc['meshes'][previous['mesh']]
        b = new.doc['meshes'][current['mesh']]
        assert {k: v for k, v in a.items() if k != 'primitives'} == {k: v for k, v in b.items() if k != 'primitives'}
        assert len(a['primitives']) == len(b['primitives'])
        for pa, pb in zip(a['primitives'], b['primitives']):
            assert {k: v for k, v in pa.items() if k not in ('attributes', 'indices')} == {
                k: v for k, v in pb.items() if k not in ('attributes', 'indices')}, ('Primitive contract', name)
            assert set(pa['attributes']) == set(pb['attributes']), ('Attribute set', name)
            ia, ib = old.accessor(pa['indices']).ravel(), new.accessor(pb['indices']).ravel()
            assert len(ia) == len(ib) and len(ia) % 3 == 0
            triangle_count += len(ia) // 3
            for attr in pa['attributes']:
                va, vb = old.accessor(pa['attributes'][attr])[ia], new.accessor(pb['attributes'][attr])[ib]
                if name in PAINT_NODES and attr == 'TEXCOORD_0':
                    assert np.isfinite(vb).all() and vb.min() >= -1e-5 and vb.max() <= 1.00001
                    x, y, width, height = atlas['uv_regions'][name.removeprefix('SITE_stage_')]
                    # glTF's top-origin image coordinates invert the Blender V.
                    assert vb[:, 0].min() >= x - 1e-5 and vb[:, 0].max() <= x + width + 1e-5
                    assert vb[:, 1].min() >= 1 - y - height - 1e-5 and vb[:, 1].max() <= 1 - y + 1e-5, ('Wrong paint band', name)
                    assert np.ptp(vb[:, 0]) > width * .99 and np.ptp(vb[:, 1]) > height * .99
                    assert not np.array_equal(va, vb), ('Paint UV unchanged', name)
                else:
                    assert np.array_equal(va, vb), ('Physical geometry or preserved UV changed', name, attr)
    assert set(targets) == PAINT_NODES
    old_materials = {m['name']: m for m in old.doc['materials']}
    new_materials = {m['name']: m for m in new.doc['materials']}
    assert old_materials.keys() == new_materials.keys()
    for name, material in new_materials.items():
        if name not in PAINT_MATERIALS:
            assert old.material(old_materials[name]) == new.material(material), ('Unrelated material changed', name)
            continue
        assert material['doubleSided'] and material['pbrMetallicRoughness']['metallicFactor'] == 0
        assert 'baseColorFactor' not in material['pbrMetallicRoughness']
        assert np.allclose(material['emissiveFactor'], [.6] * 3, atol=1e-7, rtol=0)
        for slot in (material['emissiveTexture'], material['pbrMetallicRoughness']['baseColorTexture']):
            assert slot.get('texCoord', 0) == 0
            assert new.texture(slot['index'])['source'] == paint_hash, ('Wrong exported paint', name)
    old_images = {i['name']: old.image_hash(i) for i in old.doc['images']}
    new_images = {i['name']: new.image_hash(i) for i in new.doc['images']}
    assert set(new_images) == set(old_images) | {'mountain-paint'}
    assert all(new_images[name] == digest for name, digest in old_images.items()), 'Unrelated image changed'
    assert new_images['mountain-paint'] == paint_hash
    return {'before_sha256': hashlib.sha256(old.bytes).hexdigest(),
            'after_sha256': hashlib.sha256(new.bytes).hexdigest(),
            'nodes': len(new.doc['nodes']), 'indexed_triangles_checked': triangle_count,
            'painted_nodes': sorted(targets), 'unchanged_materials': len(old_materials) - 3,
            'unchanged_images': len(old_images)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--before-sites', type=Path, required=True)
    parser.add_argument('--after-sites', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'export/mountain-export-preservation.json')
    args = parser.parse_args()
    paint_hash = hashlib.sha256((ROOT / 'textures/backdrops/mountain-paint/mountain-paint.png').read_bytes()).hexdigest()
    report = {'scope': 'Exported physical scene, all indexed attributes except three new paint UVs, lights/cameras/collisions, material/image preservation.',
              'paint_sha256': paint_hash, 'master': compare(args.before, args.after, paint_hash), 'sites': {}}
    old_sites = {p.name: p for p in args.before_sites.glob('*.glb')}
    new_sites = {p.name: p for p in args.after_sites.glob('*.glb')}
    assert old_sites.keys() == new_sites.keys() and len(old_sites) == 15
    for name, before in old_sites.items():
        after = new_sites[name]
        if name == 'SITE_stage.glb':
            report['sites'][name] = compare(before, after, paint_hash)
        else:
            assert before.read_bytes() == after.read_bytes(), ('Unrelated site changed', name)
            report['sites'][name] = {'byte_identical': True, 'sha256': hashlib.sha256(after.read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('MOUNTAIN_EXPORT_PRESERVATION_PASS: master/stage scene and fourteen unrelated site exports')


if __name__ == '__main__':
    main()
