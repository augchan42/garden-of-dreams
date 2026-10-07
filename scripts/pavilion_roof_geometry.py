"""Identify the original painted five-ring pavilion roof shell."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def components(mesh):
    adjacency = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining = set(range(len(mesh.vertices)))
    while remaining:
        pending = [next(iter(remaining))]
        vertices = set()
        while pending:
            index = pending.pop()
            if index in vertices:
                continue
            vertices.add(index)
            pending.extend(adjacency[index] - vertices)
        remaining -= vertices
        yield vertices, [p for p in mesh.polygons if p.vertices[0] in vertices]


def outer_shell(mesh):
    # The upper shell uses the roof atlas cell; the lower uses timber.
    x, y, width, height = json.loads(
        (ROOT / 'textures/atlases/pavilion/atlas.json').read_text()
    )['uv_regions']['MAT_rooftile']
    candidates = []
    for vertices, faces in components(mesh):
        if len(vertices) not in (20, 30) or len(faces) != len(vertices) * 4 // 5 + 1:
            continue
        z = [mesh.vertices[i].co.z for i in vertices]
        if abs(min(z)) > 1e-5 or abs(max(z) - 1.5) > 1e-5:
            continue
        uv = [mesh.uv_layers[0].data[i].uv for p in faces for i in p.loop_indices]
        if all(x <= p.x <= x + width and y <= p.y <= y + height for p in uv):
            candidates.append(faces)
    assert len(candidates) == 1, ('Outer roof shell must be unambiguous', len(candidates))
    return candidates[0]


def face_uv_signature(mesh):
    return [sorted((mesh.loops[i].vertex_index,
                    tuple(tuple(layer.data[i].uv) for layer in mesh.uv_layers))
                   for i in p.loop_indices) for p in mesh.polygons]


def orient_outer_shell(obj):
    """Flip only inward shell polygons; preserve positions and UV ownership."""
    mesh = obj.data
    faces = outer_shell(mesh)
    positions = [tuple(v.co) for v in mesh.vertices]
    uv = face_uv_signature(mesh)
    materials = [p.material_index for p in mesh.polygons]
    transform = [list(row) for row in obj.matrix_world]
    changed = []
    for face in faces:
        if face.normal.z < 0:
            changed.append(face.index)
            face.flip()
    mesh.update()
    assert all(p.normal.z > .25 for p in faces)
    assert positions == [tuple(v.co) for v in mesh.vertices]
    assert uv == face_uv_signature(mesh)
    assert materials == [p.material_index for p in mesh.polygons]
    assert transform == [list(row) for row in obj.matrix_world]
    return {'object': obj.name, 'outer_shell_faces': len(faces),
            'flipped_faces': changed, 'positions_uv_materials_transform_preserved': True}
