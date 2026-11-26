"""Check lightmap coverage of the stream-facing masonry and coping tops."""
import argparse
import json
from pathlib import Path
import numpy as np
from verify_mountain_export import Glb


def matrix(node):
    if 'matrix' in node:
        return np.array(node['matrix']).reshape(4, 4).T
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    m = np.eye(4)
    m[:3, :3] = np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)],
    ]) @ np.diag(node.get('scale', [1, 1, 1]))
    m[:3, 3] = node.get('translation', [0, 0, 0])
    return m


def measure(path, details=False):
    g = Glb(path)
    nodes = g.doc['nodes']
    index = next(i for i, n in enumerate(nodes) if n.get('name') == 'SITE_qinfang-ting_MAT_pavilion_atlas')
    parents = {c: i for i, n in enumerate(nodes) for c in n.get('children', [])}
    transform = matrix(nodes[index])
    parent = index
    while parent in parents:
        parent = parents[parent]
        transform = matrix(nodes[parent]) @ transform
    p = g.doc['meshes'][nodes[index]['mesh']]['primitives'][0]
    positions = g.accessor(p['attributes']['POSITION'])
    positions = (np.c_[positions, np.ones(len(positions))] @ transform.T)[:, :3]
    normals = g.accessor(p['attributes']['NORMAL']) @ np.linalg.inv(transform[:3, :3])
    indices = g.accessor(p['indices']).ravel().reshape(-1, 3)
    points = positions[indices]
    n = normals[indices].mean(axis=1)
    center = points.mean(axis=1)
    bounds = (np.abs(points[:, :, 2]).min(axis=1) >= 4.999) & (np.abs(points[:, :, 2]).max(axis=1) <= 5.681)
    bounds &= (points[:, :, 1].min(axis=1) >= -.984) & (points[:, :, 1].max(axis=1) <= -.014)
    front = (center[:, 2] * n[:, 2] < 0) & (np.abs(n[:, 2]) > .99)
    top = (n[:, 1] > .99) & (points[:, :, 1].min(axis=1) > -.016)
    selected = bounds & (front | top)
    uv = g.accessor(p['attributes']['TEXCOORD_1'])[indices[selected]] * 1024
    a, b = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
    area = np.abs(a[:, 0]*b[:, 1]-a[:, 1]*b[:, 0]) / 2
    report = {'triangles': int(selected.sum()), 'front_triangles': int((bounds & front).sum()),
              'top_triangles': int((bounds & top).sum()), 'reference_size': 1024,
              'minimum_triangle_texels': float(area.min()), 'median_triangle_texels': float(np.median(area))}
    return (report, selected, indices, g) if details else report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('glb', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = measure(args.glb)
    if args.report:
        args.report.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    assert result['front_triangles'] == 2592 and result['top_triangles'] == 648, 'Unexpected bank surface coverage'
    assert result['minimum_triangle_texels'] >= 3, 'Visible bank faces have less than three source texels per triangle'
    print('STREAM_BANK_UV_PASS')
