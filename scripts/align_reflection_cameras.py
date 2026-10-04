"""Store reviewed runtime shots in the editable hall, including portrait framing."""
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
collection = scene.collection.children['SITE_aojing-guan']

def source_point(point):
    x, y, z = point
    return Vector((x, -z, y))

shots = [
    ('wide', (26, 4, 24), (26, -2.5, 14), 70, 'height', (1410, 600)),
    ('reflection', (26, -.5, 20.7), (26, -1.7, 14), 70, 'height', (1410, 600)),
    ('reflection_portrait', (26, -.5, 20.7), (26, -2.5, 14), 68, 'width', (390, 844)),
    ('portrait', (26, 4, 23), (26, -4.5, 14), 55, 'width', (390, 844)),
]
report = []
for suffix, position, target, fov, fit, viewport in shots:
    name = 'CAM_aojing-guan_' + suffix
    camera = next((o for o in collection.objects if o.name == name), None)
    if camera is None:
        camera = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        collection.objects.link(camera)
    camera.location = source_point(position)
    camera.rotation_euler = (source_point(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    data = camera.data
    data.sensor_fit = next(i.identifier for i in data.bl_rna.properties['sensor_fit'].enum_items
                           if i.identifier == fit.upper().replace('HEIGHT', 'VERTICAL').replace('WIDTH', 'HORIZONTAL'))
    data.sensor_width = 36
    data.sensor_height = 24
    sensor = data.sensor_height if fit == 'height' else data.sensor_width
    data.lens = sensor / (2 * math.tan(math.radians(fov) / 2))
    data.clip_start = .06
    data.clip_end = 160
    camera['runtime_camera_fov'] = fov
    camera['runtime_camera_fit'] = fit
    camera['runtime_camera_viewport'] = list(viewport)
    report.append({'name': name, 'position': position, 'target': target,
                   'fov_degrees': fov, 'fit': fit, 'viewport': viewport})

scene.render.resolution_x = 1410
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'blender/authoring.blend'), compress=True)
path = ROOT / 'blender/sites/SITE_aojing-guan.blend'
bpy.data.libraries.write(str(path), {collection}, fake_user=True, compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(path), link=False) as (source, destination):
    destination.collections = ['SITE_aojing-guan']
collection = destination.collections[0]
wide = bpy.context.scene
wide.name = 'SITE_aojing-guan'
wide.collection.children.link(collection)
wide.unit_settings.system = 'METRIC'
wide.render.resolution_x, wide.render.resolution_y = 1410, 600
wide.render.resolution_percentage = 100
wide.camera = next(o for o in collection.objects if o.name.endswith('_wide'))
portrait = bpy.data.scenes.new('SITE_aojing-guan portrait')
portrait.collection.children.link(collection)
portrait.unit_settings.system = 'METRIC'
portrait.render.resolution_x, portrait.render.resolution_y = 390, 844
portrait.render.resolution_percentage = 100
portrait.camera = next(o for o in collection.objects if o.name == 'CAM_aojing-guan_portrait')
for suffix, size in [('reflection', (1410, 600)), ('reflection_portrait', (390, 844))]:
    view = bpy.data.scenes.new('SITE_aojing-guan ' + suffix)
    view.collection.children.link(collection)
    view.unit_settings.system = 'METRIC'
    view.render.resolution_x, view.render.resolution_y = size
    view.render.resolution_percentage = 100
    view.camera = next(o for o in collection.objects if o.name == 'CAM_aojing-guan_' + suffix)
temporary = path.with_name(path.stem + '-packaged.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
os.replace(temporary, path)
print('REFLECTION_SOURCE_CAMERAS_SAVED', report)
