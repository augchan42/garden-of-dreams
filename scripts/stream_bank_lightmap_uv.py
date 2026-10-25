"""Use the unused right end of the pavilion tile strip for visible bank faces.

Fifty-four 32x28 cells fit in x=672..1024, y=0..140. Each contains a
28x10 stream-facing chart and a 28x10 coping-top chart with two-pixel padding.
Other UV2 coordinates, primary UVs and physical geometry remain unchanged.
"""


def allocate_stream_bank_charts(obj, sources, size=1024):
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    assert size == 1024 and len(sources) == 54
    mesh = obj.data
    registry = []
    for cell, source in enumerate(sorted(sources, key=lambda o: o.name)):
        points = [source.matrix_world @ v.co for v in source.data.vertices]
        bounds = [(min(p[a] for p in points), max(p[a] for p in points)) for a in range(3)]
        side = -1 if sum(bounds[1]) > 0 else 1
        for face in source.data.polygons:
            world = [points[i] for i in face.vertices]
            normal = source.matrix_world.to_3x3().inverted().transposed() @ face.normal
            normal.normalize()
            front = normal.y * side > .99
            top = normal.z > .99 and min(p.z for p in world) > bounds[2][1] - .001
            if not (front or top):
                continue
            registry.append((world, cell, top, bounds))
    assert len(registry) == 1620, len(registry)
    centers = KDTree(len(registry))
    for i, (points, _, _, _) in enumerate(registry):
        centers.insert(sum(points, Vector()) / len(points), i)
    centers.balance()
    used = set()
    changed = 0
    for face in mesh.polygons:
        world = [obj.matrix_world @ mesh.vertices[i].co for i in face.vertices]
        _, index, distance = centers.find(sum(world, Vector()) / len(world))
        if distance > .0001:
            continue
        saved, cell, top, bounds = registry[index]
        assert len(saved) == len(world) and max(min((p - q).length for q in saved) for p in world) < .0001
        assert index not in used
        used.add(index)
        column, row = cell % 11, cell // 11
        for loop, point in zip(face.loop_indices, world):
            u = (point.x - bounds[0][0]) / (bounds[0][1] - bounds[0][0])
            axis = 1 if top else 2
            v = (point[axis] - bounds[axis][0]) / (bounds[axis][1] - bounds[axis][0])
            mesh.uv_layers[1].data[loop].uv = (
                (672 + column * 32 + 2 + 28 * u) / size,
                (row * 28 + (16 if top else 2) + 10 * v) / size)
        changed += 1
    assert len(used) == changed == 1620, (changed, len(used))
    return {'stream_bank_modules': 54, 'stream_bank_faces': changed,
            'stream_bank_chart_texels': [28, 10], 'stream_bank_padding_texels': 2,
            'stream_bank_reserved_rect': [672, 0, 352, 140]}
