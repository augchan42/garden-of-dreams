"""Paint the hilltop hall sign and warm its plaster terrace surfaces."""

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
site = bpy.data.collections["SITE_tubi-tang"]

for obj in list(site.objects):
    if obj.name.startswith(("KIT_props_inscription_凸碧堂", "HERO_tubi_title")):
        bpy.data.objects.remove(obj, do_unlink=True)

warm = bpy.data.materials.get("MAT_tubi_terrace_plaster")
if warm is None:
    warm = bpy.data.materials.new("MAT_tubi_terrace_plaster")
warm.use_nodes = True
warm.diffuse_color = (0.42, 0.28, 0.17, 1.0)
shader = next(node for node in warm.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
shader.inputs["Base Color"].default_value = (0.42, 0.28, 0.17, 1.0)
shader.inputs["Roughness"].default_value = 0.72

surfaces = ("TUBI_terrace", "TUBI_parapet", "TUBI_stair_tread", "TUBI_topic_table", "TUBI_topic_pedestal")
reassigned = 0
for obj in site.objects:
    if obj.type == "MESH" and obj.name.startswith(surfaces):
        assert obj.data.materials and obj.data.materials[0].name in ("MAT_plaster_rock", warm.name)
        obj.data.materials[0] = warm
        reassigned += 1
assert reassigned == 31, reassigned  # terrace, 4 parapets + caps, 20 treads, table + pedestal

old = bpy.data.materials.get("MAT_tubi_title_paint")
if old:
    bpy.data.materials.remove(old)
title = bpy.data.materials.new("MAT_tubi_title_paint")
title.use_nodes = True
nodes = title.node_tree.nodes
shader = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
shader.inputs["Roughness"].default_value = 0.9
image = bpy.data.images.load(str(ROOT / "textures/decals/hilltop/tubi-title.png"), check_existing=True)
image.pack()
texture = nodes.new("ShaderNodeTexImage")
texture.image = image
title.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
title.node_tree.links.new(texture.outputs["Alpha"], shader.inputs["Alpha"])
title.node_tree.links.new(texture.outputs["Color"], shader.inputs["Emission Color"])
shader.inputs["Emission Strength"].default_value = 0.55
method = title.bl_rna.properties.get("surface_render_method")
if method:
    title.surface_render_method = next(item.identifier for item in method.enum_items if item.identifier == "DITHERED")

mesh = bpy.data.meshes.new("HERO_tubi_title")
mesh.from_pydata(
    [(6.0, 31.912, 6.43), (8.0, 31.912, 6.43), (8.0, 31.912, 6.87), (6.0, 31.912, 6.87)],
    [],
    [(0, 1, 2, 3)],
)
mesh.update()
mesh.materials.append(title)
uv = mesh.uv_layers.new(name="UVMap")
for loop_index, coordinate in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
    uv.data[loop_index].uv = coordinate
obj = bpy.data.objects.new("HERO_tubi_title", mesh)
site.objects.link(obj)
obj["inscription_text"] = "凸碧堂"

assert not any(o.type == "FONT" and "凸碧堂" in o.name for o in site.objects)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender/authoring.blend"), compress=True)
bpy.data.libraries.write(
    str(ROOT / "blender/sites/SITE_tubi-tang.blend"),
    {site},
    fake_user=True,
    compress=True,
)
print("HILLTOP_ART_PASS: brush title and warm terrace, stair, parapet, table plaster saved")
