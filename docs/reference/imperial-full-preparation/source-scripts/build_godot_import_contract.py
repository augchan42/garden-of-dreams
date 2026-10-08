"""Extract independent camera, collider and marker expectations from canonical glTF."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from verify_mountain_export import Glb

ROOT = Path(__file__).resolve().parents[1]


def local_matrix(node):
    if 'matrix' in node:
        return np.asarray(node['matrix']).reshape(4, 4).T
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    matrix = np.eye(4)
    matrix[:3, :3] = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    matrix[:3, :3] *= node.get('scale', [1, 1, 1])
    matrix[:3, 3] = node.get('translation', [0, 0, 0])
    return matrix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT / 'export/garden-of-dreams.glb')
    parser.add_argument('--output', type=Path, default=ROOT / 'export/godot-import-source-contract.json')
    args = parser.parse_args()
    glb = Glb(args.source)
    nodes = glb.doc['nodes']
    parents = {child: parent for parent, node in enumerate(nodes) for child in node.get('children', [])}
    def world(index):
        matrix = local_matrix(nodes[index])
        return world(parents[index]) @ matrix if index in parents else matrix
    report = {'source_glb_sha256': hashlib.sha256(glb.bytes).hexdigest(),
              'scope': 'Expected transforms, camera projections, collision triangle positions and room-marker metadata read directly from exported glTF.',
              'cameras': {}, 'colliders': {}, 'markers': {}, 'render_meshes': 0}
    for index, node in enumerate(nodes):
        name = node.get('name', '')
        engine_name = name.replace('-colonly', '').replace('.', '_')
        transform = world(index).T.ravel().tolist()
        if 'camera' in node:
            camera = glb.doc['cameras'][node['camera']]
            assert camera['type'] == 'perspective'
            report['cameras'][engine_name] = {'transform': transform, **camera['perspective']}
        if name.startswith('COL_'):
            assert 'mesh' in node and '-colonly' in name
            faces = []
            for primitive in glb.doc['meshes'][node['mesh']]['primitives']:
                assert primitive.get('mode', 4) == 4
                positions = glb.accessor(primitive['attributes']['POSITION'])
                faces.extend(positions[glb.accessor(primitive['indices']).ravel()].tolist())
            assert len(faces) % 3 == 0 and len(faces) > 0
            report['colliders'][engine_name] = {'transform': transform, 'faces': faces}
        elif 'mesh' in node:
            report['render_meshes'] += 1
        if name.startswith('TRG_'):
            report['markers'][engine_name] = {'transform': transform, 'extras': node.get('extras', {})}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, separators=(',', ':'), ensure_ascii=False) + '\n')
    print('GODOT_IMPORT_SOURCE_CONTRACT', len(report['cameras']), 'cameras', len(report['colliders']),
          'colliders', len(report['markers']), 'markers', report['render_meshes'], 'render meshes')


if __name__ == '__main__':
    main()
