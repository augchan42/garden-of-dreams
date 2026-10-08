"""Replace the bulletin hall's temporary type and block marks with painted art."""

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
site = bpy.data.collections["SITE_qiushuang-zhai"]

for obj in list(site.objects):
    if obj.name.startswith(("KIT_props_inscription_秋爽齋", "STUDY_scroll_ink", "HERO_study_")):
        bpy.data.objects.remove(obj, do_unlink=True)


def painted_material(name: str, image_name: str, alpha: bool = False) -> bpy.types.Material:
    old = bpy.data.materials.get(name)
    if old:
        bpy.data.materials.remove(old)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    shader = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    shader.inputs["Roughness"].default_value = 0.9
    image = bpy.data.images.load(str(ROOT / "textures/decals/study" / image_name), check_existing=True)
    image.pack()
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    material.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
    if alpha:
        material.node_tree.links.new(texture.outputs["Alpha"], shader.inputs["Alpha"])
        material.node_tree.links.new(texture.outputs["Color"], shader.inputs["Emission Color"])
        shader.inputs["Emission Strength"].default_value = 0.55
        property_info = material.bl_rna.properties.get("surface_render_method")
        if property_info:
            material.surface_render_method = next(
                item.identifier for item in property_info.enum_items if item.identifier == "DITHERED"
            )
    return material


def painted_plane(name: str, x_min: float, x_max: float, y: float,
                  z_min: float, z_max: float, material: bpy.types.Material) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(
        [(x_min, y, z_min), (x_max, y, z_min), (x_max, y, z_max), (x_min, y, z_max)],
        [],
        [(0, 1, 2, 3)],
    )
    mesh.update()
    mesh.materials.append(material)
    uv = mesh.uv_layers.new(name="UVMap")
    for loop_index, coordinate in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[loop_index].uv = coordinate
    obj = bpy.data.objects.new(name, mesh)
    site.objects.link(obj)
    return obj


title = painted_material("MAT_study_title_paint", "hall-title.png", alpha=True)
bamboo = painted_material("MAT_study_scroll_bamboo", "bamboo-scroll.png")
plum = painted_material("MAT_study_scroll_plum", "plum-scroll.png")
painted_plane("HERO_study_title", 20.9, 23.1, 14.912, 2.43, 2.88, title)
painted_plane("HERO_study_scroll_bamboo", 20.7, 21.1, 15.76, 1.1, 2.4, bamboo)
painted_plane("HERO_study_scroll_plum", 22.9, 23.3, 15.76, 1.1, 2.4, plum)

assert not any(obj.type == "FONT" and "秋爽齋" in obj.name for obj in site.objects)
assert len([obj for obj in site.objects if obj.name.startswith("HERO_study_")]) == 3
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender/authoring.blend"), compress=True)
bpy.data.libraries.write(
    str(ROOT / "blender/sites/SITE_qiushuang-zhai.blend"),
    {site},
    fake_user=True,
    compress=True,
)
print("STUDY_ART_PASS: painted title and bamboo/plum scrolls saved")
