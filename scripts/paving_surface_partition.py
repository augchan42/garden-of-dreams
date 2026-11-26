"""Remove duplicate paving top faces while retaining existing floor owners.

Only visible upward surfaces close to walking height are partitioned. Collision
objects, walking heights and the union of the existing paving are unchanged.
Run after site construction; final exports require fresh matching lightmaps.
"""
import math

PREFIXES = ('KIT_water_stone_walk', 'STUDY_approach', 'STUDY_front_walk',
            'TUBI_approach', 'HENGWU_approach', 'LONGCUI_approach',
            'AOJING_approach', 'DAOXIANG_approach', 'KIT_water_bridge_crosswalk',
            'QINFANG_corridor_', 'KIT_floor_joint_', 'GATE_paving',
            'KIT_stage_entry_corridor', 'KIT_stage_entry_walk',
            'SITE_qiushuang-zhai_platform', 'DAGUAN_platform', 'SITE_ouxiang_deck',
            'KIT_water_pavilion_approach', 'SITE_hengwu-yuan_platform',
            'HENGWU_court_paving', 'YIHONG_paving', 'XIAOXIANG_paving',
            'LONGCUI_paving', 'DAOXIANG_court', 'SITE_ziling_stone_landing',
            'WESTERN_kit_wood_bridge')


def signed_area(points):
    return sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(points, points[1:]+points[:1])) / 2


def clean(points):
    result = []
    for point in points:
        if not result or math.dist(result[-1], point) > 1e-8:
            result.append(point)
    if len(result) > 1 and math.dist(result[0], result[-1]) < 1e-8:
        result.pop()
    if len(result) < 3 or abs(signed_area(result)) < 1e-8:
        return []
    return result if signed_area(result) > 0 else list(reversed(result))


def split(points, a, b):
    """Split a convex polygon at a directed line, retaining both sides."""
    inside, outside = [], []
    side = lambda p: (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    for p, q in zip(points, points[1:]+points[:1]):
        sp, sq = side(p), side(q)
        (inside if sp >= 0 else outside).append(p)
        if (sp > 1e-10 and sq < -1e-10) or (sp < -1e-10 and sq > 1e-10):
            t = sp/(sp-sq)
            intersection = [p[k]+t*(q[k]-p[k]) for k in (0, 1)]
            inside.append(intersection)
            outside.append(intersection)
        elif abs(sp) <= 1e-10:
            (outside if sp >= 0 else inside).append(p)
    return clean(inside), clean(outside)


def subtract(subject, clip):
    """Return convex pieces of subject outside the convex clip polygon."""
    remainder, pieces = subject, []
    for a, b in zip(clip, clip[1:]+clip[:1]):
        if not remainder:
            break
        remainder, outside = split(remainder, a, b)
        if outside:
            pieces.append(outside)
    return pieces


def tops(scene):
    rows = []
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.hide_render or obj.name.startswith('COL_'):
            continue
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        for poly in obj.data.polygons:
            points = [obj.matrix_world @ obj.data.vertices[i].co for i in poly.vertices]
            if len(points) < 3 or max(p.z for p in points)-min(p.z for p in points) > 1e-5:
                continue
            if abs(points[0].z) > .006 or (normal_matrix @ poly.normal).normalized().z < .99:
                continue
            material = obj.data.materials[poly.material_index].name
            # Keep constructed timber walkways/decks, then each site's forecourt.
            # Plain connecting stone slabs yield at their shared joints.
            priority = 300 if material == 'MAT_pavilion_atlas' else 200 if material == 'MAT_lattice_wood' else 0
            if any(s in obj.name for s in ('_paving', '_court', '_deck', '_landing')):
                priority += 100
            elif '_platform' in obj.name:
                priority += 60
            elif '_approach' in obj.name:
                priority += 20
            mutable = obj.name.startswith(PREFIXES)
            if not mutable:
                # Stair treads and other constructed surfaces retain their
                # geometry. Connecting paving yields to these floor owners.
                priority += 1000
            rows.append({'object': obj, 'face': poly.index, 'height': points[0].z,
                         'polygon': clean([[p.x, p.y] for p in points]),
                         'priority': priority, 'mutable': mutable})
    return rows


def partition(scene):
    import bpy
    from mathutils import Vector, geometry
    originals = tops(scene)
    accepted = []
    replacements = {}
    for row in sorted(originals, key=lambda r: (-r['priority'], r['object'].name, r['face'])):
        pieces = [row['polygon']]
        if not row['mutable']:
            accepted.append({'height': row['height'], 'polygon': row['polygon']})
            continue
        for earlier in accepted:
            if abs(row['height']-earlier['height']) > 1e-5:
                continue
            clip = earlier['polygon']
            # Bounding boxes avoid unnecessary splits at distant set pieces.
            if max(p[0] for p in row['polygon']) <= min(p[0] for p in clip)+1e-8 or min(p[0] for p in row['polygon']) >= max(p[0] for p in clip)-1e-8 or max(p[1] for p in row['polygon']) <= min(p[1] for p in clip)+1e-8 or min(p[1] for p in row['polygon']) >= max(p[1] for p in clip)-1e-8:
                continue
            pieces = [part for piece in pieces for part in subtract(piece, clip)]
        old_area = abs(signed_area(row['polygon']))
        new_area = sum(abs(signed_area(p)) for p in pieces)
        if abs(old_area-new_area) > 1e-7:
            replacements.setdefault(row['object'], {})[row['face']] = pieces
        for piece in pieces:
            accepted.append({'height': row['height'], 'polygon': piece})
    changes = []
    for obj, faces in replacements.items():
        original = obj.data
        vertices = [tuple(v.co) for v in original.vertices]
        polygons, attrs, uv_data = [], [], {layer.name: [] for layer in original.uv_layers}
        inverse = obj.matrix_world.inverted()
        original.calc_loop_triangles()
        for poly in original.polygons:
            if poly.index not in faces:
                polygons.append(list(poly.vertices)); attrs.append((poly.material_index, poly.use_smooth))
                for layer in original.uv_layers:
                    uv_data[layer.name].append([tuple(layer.data[i].uv) for i in poly.loop_indices])
                continue
            world = [obj.matrix_world @ original.vertices[i].co for i in poly.vertices]
            triangles = [tuple(obj.matrix_world @ original.vertices[i].co for i in triangle.vertices) for triangle in original.loop_triangles if triangle.polygon_index == poly.index]
            for piece in faces[poly.index]:
                indices = []
                values = {layer.name: [] for layer in original.uv_layers}
                for xy in piece:
                    point = Vector((xy[0], xy[1], world[0].z))
                    local = inverse @ point
                    # Reconcile the new cut vertex with Blender's stored float coordinates.
                    best = local.copy();error = (obj.matrix_world @ best-point).length_squared
                    for attempt in range(16):
                        local += inverse.to_3x3() @ (point-obj.matrix_world @ local)
                        candidate_error = (obj.matrix_world @ local-point).length_squared
                        if candidate_error < error:
                            best = local.copy();error = candidate_error
                        if error == 0:break
                    indices.append(len(vertices));vertices.append(tuple(best))
                    # Preserve the original primary texture mapping by interpolation.
                    def contains(t):
                        a, b, c = [[v.x, v.y] for v in t]
                        sides = [(q[0]-p[0])*(xy[1]-p[1])-(q[1]-p[1])*(xy[0]-p[0]) for p, q in ((a,b),(b,c),(c,a))]
                        return min(sides) >= -1e-5 or max(sides) <= 1e-5
                    triangle = next(t for t in triangles if contains(t))
                    offsets = [min(range(len(world)), key=lambda i: (world[i]-v).length_squared) for v in triangle]
                    for layer in original.uv_layers:
                        coords = [layer.data[poly.loop_indices[i]].uv for i in offsets]
                        mapped = geometry.barycentric_transform(point, *triangle, *[Vector((uv.x, uv.y, 0)) for uv in coords])
                        values[layer.name].append((mapped.x, mapped.y))
                polygons.append(indices);attrs.append((poly.material_index, poly.use_smooth))
                for name in uv_data:
                    uv_data[name].append(values[name])
        mesh = bpy.data.meshes.new(original.name + '_partitioned')
        mesh.from_pydata(vertices, [], polygons)
        for material in original.materials:
            mesh.materials.append(material)
        for poly, (material, smooth) in zip(mesh.polygons, attrs):
            poly.material_index = material;poly.use_smooth = smooth
        for name, values in uv_data.items():
            layer = mesh.uv_layers.new(name=name)
            for poly, coords in zip(mesh.polygons, values):
                for index, value in zip(poly.loop_indices, coords):
                    layer.data[index].uv = value
        mesh.update()
        obj.data = mesh
        changes.append({'object': obj.name, 'changed_top_faces': sorted(faces),
                        'before_faces': len(original.polygons), 'after_faces': len(mesh.polygons)})
    return changes
