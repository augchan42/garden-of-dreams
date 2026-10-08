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


def orient_tile_ridges(obj):
    """Orient the open raised tile strips above the shell without moving them."""
    mesh = obj.data
    shell = outer_shell(mesh)
    sides = (len(shell) - 1) // 4
    assert sides in (4, 6)
    x, y, width, height = json.loads(
        (ROOT / 'textures/atlases/pavilion/atlas.json').read_text()
    )['uv_regions']['MAT_rooftile']
    ridges = [faces for vertices, faces in components(mesh)
              if len(vertices) == 15 and len(faces) == 8]
    assert len(ridges) == sides * 7, 'Raised tile strips must be unambiguous'
    faces = [face for ridge in ridges for face in ridge]
    assert all(x <= mesh.uv_layers[0].data[i].uv.x <= x + width and
               y <= mesh.uv_layers[0].data[i].uv.y <= y + height
               for face in faces for i in face.loop_indices), 'Tile strip leaves roof atlas cell'
    positions = [tuple(v.co) for v in mesh.vertices]
    uv = face_uv_signature(mesh)
    materials = [p.material_index for p in mesh.polygons]
    originals = {p.index: tuple(p.vertices) for p in mesh.polygons}
    target_indices = {p.index for p in faces}
    changed = []
    for face in faces:
        assert abs(face.normal.z) > .25, 'Unexpected tile-strip slope'
        if face.normal.z < 0:
            changed.append(face.index)
            face.flip()
    mesh.update()
    assert all(face.normal.z > .25 for face in faces)
    assert positions == [tuple(v.co) for v in mesh.vertices]
    assert uv == face_uv_signature(mesh)
    assert materials == [p.material_index for p in mesh.polygons]
    assert all(tuple(p.vertices) == originals[p.index] for p in mesh.polygons
               if p.index not in target_indices), 'Unrelated roof faces changed'
    return {'object': obj.name, 'tile_strips': len(ridges), 'tile_faces': len(faces),
            'flipped_faces': changed, 'positions_uv_materials_other_faces_preserved': True}
