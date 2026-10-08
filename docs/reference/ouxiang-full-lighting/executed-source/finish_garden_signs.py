"""Fit seven painted titles to the existing boards, preserving all structural objects."""
import hashlib
import json
import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
TITLES = {'qinfang-ting': '沁芳', 'hengwu-yuan': '蘅蕪苑', 'yihong-yuan': '怡紅院',
          'xiaoxiang-guan': '瀟湘館', 'longcui-an': '櫳翠庵', 'aojing-guan': '凹晶館',
          'daoxiang-cun': '稻香村'}
# The original boards intersect these deep eaves or the pavilion front post. Move their wood and lettering together.
EAVE_OFFSETS = {'qinfang-ting': .50, 'yihong-yuan': .52, 'longcui-an': .55,
                'aojing-guan': .60, 'daoxiang-cun': .58}
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene


def structure():
    return {o.name: {'matrix': [float(v) for row in o.matrix_world for v in row],
                     'room_id': o.get('room_id')}
            for o in scene.objects if o.name.startswith(('COL_', 'TRG_', 'LGT_', 'CAM_'))}


before = structure()
records = []
for slug, title in TITLES.items():
    site = bpy.data.collections['SITE_' + slug]
    boards = [o for o in site.objects if o.name.startswith('KIT_props_calligraphy_board')]
    assert len(boards) == 1, (slug, [o.name for o in boards])
    board = boards[0]
    offset = EAVE_OFFSETS.get(slug, 0)
    prior_offset = board.get('painted_sign_eave_offset', 0.0)
    original_matrix = board.matrix_world.copy()
    original_matrix.translation += original_matrix.to_3x3() @ Vector((0, prior_offset, 0))
    board.matrix_world.translation += board.matrix_world.to_3x3() @ Vector((0, prior_offset-offset, 0))
    board['painted_sign_eave_offset'] = offset
    for obj in list(site.objects):
        if (obj.type == 'FONT' and obj.data.body == title) or obj.name.startswith('HERO_' + slug + '_title'):
            bpy.data.objects.remove(obj, do_unlink=True)
    image_path = ROOT / 'textures/decals/garden-signs' / (slug + '-title.png')
    image = bpy.data.images.load(str(image_path), check_existing=True)
    image.pack()
    material_name = 'MAT_' + slug + '_title_paint'
    old = bpy.data.materials.get(material_name)
    if old:
        bpy.data.materials.remove(old)
    material = bpy.data.materials.new(material_name)
    material.use_nodes = True
    shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Roughness'].default_value = .9
    texture = material.node_tree.nodes.new('ShaderNodeTexImage')
    texture.image = image
    for output, socket in [('Color', 'Base Color'), ('Alpha', 'Alpha'), ('Color', 'Emission Color')]:
        material.node_tree.links.new(texture.outputs[output], shader.inputs[socket])
    shader.inputs['Emission Strength'].default_value = .55
    methods = [i.identifier for i in material.bl_rna.properties['surface_render_method'].enum_items]
    assert 'DITHERED' in methods
    material.surface_render_method = 'DITHERED'
    # Work in the board's local coordinates so rotated court signs keep their orientation.
    bounds = [Vector(p) for p in board.bound_box]
    low = Vector(tuple(min(p[a] for p in bounds) for a in range(3)))
    high = Vector(tuple(max(p[a] for p in bounds) for a in range(3)))
    aspect = image.size[0] / image.size[1]
    height = min((high.z-low.z) * .84, (high.x-low.x) * .92 / aspect)
    width = height * aspect
    cx = (low.x+high.x)/2
    cz = (low.z+high.z)/2
    y = low.y - .008
    vertices = [board.matrix_world @ Vector(p) for p in
                [(cx-width/2, y, cz-height/2), (cx+width/2, y, cz-height/2),
                 (cx+width/2, y, cz+height/2), (cx-width/2, y, cz+height/2)]]
    mesh = bpy.data.meshes.new('HERO_' + slug + '_title')
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()
    mesh.materials.append(material)
    uv = mesh.uv_layers.new(name='UVMap')
    for loop, coordinate in zip(mesh.polygons[0].loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[loop].uv = coordinate
    obj = bpy.data.objects.new('HERO_' + slug + '_title', mesh)
    site.objects.link(obj)
    obj['inscription_text'] = title
    obj['finish'] = 'Original hand-brushed gold lettering texture on retained wood board'
    obj['sign_board'] = board.name
    # Two short wood brackets attach each projected board to the original wall/eave mount.
    if offset:
        for index, fraction in enumerate([.2, .8]):
            name = 'KIT_sign_' + slug + '_bracket_' + str(index)
            old_bracket = bpy.data.objects.get(name)
            if old_bracket:
                bpy.data.objects.remove(old_bracket, do_unlink=True)
            x = low.x + (high.x-low.x)*fraction
            z = high.z-.10
            old_y = (low.y+high.y)/2
            bracket_vertices = [original_matrix @ Vector((x+dx, y, z+dz))
                                for dx, y, dz in [(-.035,old_y-offset,-.035),(.035,old_y-offset,-.035),
                                    (.035,old_y,-.035),(-.035,old_y,-.035),(-.035,old_y-offset,.035),
                                    (.035,old_y-offset,.035),(.035,old_y,.035),(-.035,old_y,.035)]]
            bracket_mesh = bpy.data.meshes.new(name)
            bracket_mesh.from_pydata(bracket_vertices, [], [(0,3,2,1),(4,5,6,7),(0,1,5,4),
                                                           (1,2,6,5),(2,3,7,6),(3,0,4,7)])
            bracket_mesh.materials.append(board.data.materials[0])
            bracket = bpy.data.objects.new(name, bracket_mesh)
            site.objects.link(bracket)
    assert not any(o.type == 'FONT' for o in site.objects), slug
    records.append({'site': slug, 'text': title, 'object': obj.name, 'board': board.name,
                    'texture': str(image_path.relative_to(ROOT)),
                    'texture_sha256': hashlib.sha256(image_path.read_bytes()).hexdigest(),
                    'world_vertices': [list(v) for v in vertices], 'local_width': width,
                    'local_height': height, 'eave_mount_offset_m': offset})
assert structure() == before
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/authoring.blend'), compress=True)
for slug in TITLES:
    bpy.data.libraries.write(str(ROOT/'blender/sites'/('SITE_'+slug+'.blend')),
                             {bpy.data.collections['SITE_'+slug]}, fake_user=True, compress=True)
# Package each library as a directly openable scene without touching the live Blender app.
for slug in TITLES:
    path = ROOT/'blender/sites'/('SITE_'+slug+'.blend')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(path), link=False) as (source, destination):
        destination.collections = [path.stem]
    saved_scene = bpy.context.scene
    saved_scene.name = path.stem
    saved_scene.collection.children.link(destination.collections[0])
    saved_scene.unit_settings.system = 'METRIC'
    saved_scene.render.resolution_x = 1410
    saved_scene.render.resolution_y = 600
    saved_scene.camera = next(o for o in saved_scene.objects if o.type == 'CAMERA' and 'wide' in o.name)
    temp = path.with_name(path.stem+'-packaged.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(temp), compress=True)
    os.replace(temp, path)
(ROOT/'export/painted-signs.json').write_text(json.dumps({
    'structural_objects_preserved': len(before), 'placements': records}, indent=2, ensure_ascii=False)+'\n')
print('PAINTED_SIGNS_SAVED', len(records), 'structural objects preserved', len(before))
