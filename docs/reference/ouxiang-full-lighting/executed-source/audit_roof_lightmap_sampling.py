"""Measure exported roof-batch UV2 triangle sizes against their actual bake maps.

A batch also contains posts or beams. This is a chart diagnostic, not proof that
every small triangle causes a visible artifact or that the roof art is accepted.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'export/garden-of-dreams.glb')
    parser.add_argument('--maps', type=Path, default=ROOT / 'export/lightmaps')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = args.source.read_bytes()
    magic, version, total = struct.unpack_from('<III', data)
    assert magic == 0x46546c67 and version == 2 and total == len(data)
    json_size, json_type = struct.unpack_from('<II', data, 12)
    assert json_type == 0x4e4f534a
    doc = json.loads(data[20:20 + json_size])
    binary_size, binary_type = struct.unpack_from('<II', data, 20 + json_size)
    assert binary_type == 0x004e4942
    binary = data[28 + json_size:28 + json_size + binary_size]
    source_hash = hashlib.sha256(data).hexdigest()

    def values(index):
        accessor = doc['accessors'][index]
        assert 'sparse' not in accessor
        view = doc['bufferViews'][accessor['bufferView']]
        assert view['buffer'] == 0
        code = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}[accessor['componentType']]
        count = {'SCALAR': 1, 'VEC2': 2}[accessor['type']]
        format_string = '<' + code * count
        stride = view.get('byteStride', struct.calcsize(format_string))
        offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        return [struct.unpack_from(format_string, binary, offset + i * stride)
                for i in range(accessor['count'])]

    batches = {}
    for node in doc['nodes']:
        name = node.get('name', '')
        if 'mesh' not in node or not name.startswith('SITE_'):
            continue
        if not name.endswith(('_MAT_rooftile', '_MAT_pavilion_atlas', '_MAT_thatch')):
            continue
        record_path = args.maps / (name + '.json')
        record = json.loads(record_path.read_text())
        assert record['source_glb_sha256'] == source_hash and record['uv_channel'] == 1
        size = record['size']
        altitudes = []
        areas = []
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            assert primitive.get('mode', 4) == 4
            uv = values(primitive['attributes']['TEXCOORD_1'])
            indices = [row[0] for row in values(primitive['indices'])]
            assert len(indices) % 3 == 0
            for i in range(0, len(indices), 3):
                a, b, c = [tuple(v * size for v in uv[index]) for index in indices[i:i + 3]]
                assert all(math.isfinite(v) for point in (a, b, c) for v in point)
                area = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2
                longest = max(math.dist(a, b), math.dist(b, c), math.dist(c, a))
                areas.append(area)
                altitudes.append(2 * area / longest if longest else 0)
        ordered = sorted(altitudes)
        batches[name] = {
            'source_map_size': size, 'triangles': len(altitudes),
            'degenerate_uv_triangles': sum(area < 1e-8 for area in areas),
            'source_triangles_under_one_pixel_altitude': sum(value < 1 for value in altitudes),
            'minimum_altitude_source_pixels': {str(q): ordered[round((len(ordered) - 1) * q)] for q in [0, .25, .5, .75, 1]},
            'source_map_sha256': hashlib.sha256((args.maps / record['texture']).read_bytes()).hexdigest(),
        }
    assert batches
    report = {
        'status': 'chart_sampling_measured', 'source_glb_sha256': source_hash,
        'scope': 'UV2 chart geometry of whole roof material batches at actual source map sizes. Includes non-roof parts sharing these batches; not isolated cap coverage, overlap/gutter proof, baked irradiance, rendered artifact diagnosis, import-filter quality or final art acceptance.',
        'batches': batches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('ROOF_CHART_SAMPLING_MEASURED', len(batches), 'source-matched batches')
    for name, row in batches.items():
        print(name, row['source_triangles_under_one_pixel_altitude'], '/', row['triangles'], 'below one source pixel')


if __name__ == '__main__':
    main()
