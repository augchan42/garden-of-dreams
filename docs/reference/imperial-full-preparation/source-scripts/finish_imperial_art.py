"""Finish the imperial title and distinguish its closed lacquer door bays."""

from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
site = bpy.data.collections["SITE_daguan-lou"]

for obj in list(site.objects):
    if obj.name.startswith(("KIT_props_inscription_大觀樓", "HERO_daguan_title")):
        bpy.data.objects.remove(obj, do_unlink=True)

def surface(name, rgb, roughness):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*rgb, 1)
    shader = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = roughness
    return material

lacquer = surface("MAT_daguan_lacquer", (0.20, 0.055, 0.035), 0.42)
recess = surface("MAT_daguan_recess", (0.060, 0.018, 0.012), 0.62)
doors = panels = 0
for obj in site.objects:
    if obj.type != "MESH":
        continue
    if obj.name.startswith("DAGUAN_closed_door"):
        obj.data.materials[0] = lacquer
        doors += 1
    elif obj.name.startswith("DAGUAN_recessed_panel"):
        obj.data.materials[0] = recess
        panels += 1
assert doors == 10 and panels == 20, (doors, panels)

title = surface("MAT_daguan_title_paint", (1, 1, 1), 0.9)
nodes = title.node_tree.nodes
shader = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
for node in list(nodes):
    if node.type == "TEX_IMAGE":
        nodes.remove(node)
image = bpy.data.images.load(str(ROOT / "textures/decals/imperial/daguan-title.png"), check_existing=True)
image.pack()
texture = nodes.new("ShaderNodeTexImage")
texture.image = image
title.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
title.node_tree.links.new(texture.outputs["Alpha"], shader.inputs["Alpha"])
title.node_tree.links.new(texture.outputs["Color"], shader.inputs["Emission Color"])
shader.inputs["Emission Strength"].default_value = 0.55
title.surface_render_method = "DITHERED"

mesh = bpy.data.meshes.new("HERO_daguan_title")
mesh.from_pydata([(-0.9, 21.912, 2.77), (0.9, 21.912, 2.77), (0.9, 21.912, 3.33), (-0.9, 21.912, 3.33)], [], [(0, 1, 2, 3)])
mesh.update()
mesh.materials.append(title)
uv = mesh.uv_layers.new(name="UVMap")
for index, coordinate in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
    uv.data[index].uv = coordinate
obj = bpy.data.objects.new("HERO_daguan_title", mesh)
site.objects.link(obj)
obj["inscription_text"] = "大觀樓"

key = bpy.data.objects["LGT_daguan-lou_key"]
key.data.color = (0.86, 0.76, 0.60)
key.location = (5, 18, 2.8)
key.rotation_euler = (Vector((0, 22.8, 1.55)) - key.location).to_track_quat("-Z", "Y").to_euler()
camera = bpy.data.objects["CAM_daguan-lou_wide"]
camera.location = (5.5, 13, 2.5)
camera.rotation_euler = (Vector((0, 23, 2.7)) - camera.location).to_track_quat("-Z", "Y").to_euler()

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender/authoring.blend"), compress=True)
bpy.data.libraries.write(str(ROOT / "blender/sites/SITE_daguan-lou.blend"), {site}, fake_user=True, compress=True)
print("IMPERIAL_ART_PASS: painted title, ten lacquer doors, twenty recesses, warm-neutral key")
