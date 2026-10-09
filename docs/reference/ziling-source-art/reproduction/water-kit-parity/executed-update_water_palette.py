import bpy,json,hashlib,math,sys
from pathlib import Path
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root'])/'water-kit-parity'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (w/'baseline').exists();(w/'baseline').mkdir();(w/'candidate').mkdir()
variants=['stream','pond','embankment','lotus','wood_bridge','stone_bridge']
def export_all(folder):
 for variant in variants:
  for suffix in ['', '_LOD1']:
   name='Water '+variant+(' LOD1' if suffix else '');bpy.context.window.scene=bpy.data.scenes[name]
   bpy.ops.export_scene.gltf(filepath=str(folder/('KIT_water_'+variant+suffix+'.glb')),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
def signature():
 data={'objects':{},'scenes':{},'worlds':{}}
 for o in bpy.data.objects:
  row={'type':o.type,'matrix':[list(x) for x in o.matrix_world],'extras':{k:str(v) for k,v in o.items()},'visibility':[o.hide_render,o.hide_viewport],'instance_collection':o.instance_collection.name if o.instance_collection else None}
  if o.type=='MESH':
   row.update(vertices=[list(x.co) for x in o.data.vertices],polygons=[list(x.vertices) for x in o.data.polygons],material_slots=[x.name if x else None for x in o.data.materials],indices=[x.material_index for x in o.data.polygons],uv={l.name:[list(x.uv) for x in l.data] for l in o.data.uv_layers},modifiers=[{'type':m.type,'ratio':m.ratio if m.type=='DECIMATE' else None} for m in o.modifiers])
  elif o.type=='LIGHT':row['light']={'type':o.data.type,'color':list(o.data.color),'energy':o.data.energy}
  elif o.type=='CAMERA':row['camera']={'type':o.data.type,'lens':o.data.lens,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end}
  data['objects'][o.name]=row
 for s in bpy.data.scenes:data['scenes'][s.name]={'objects':sorted(o.name for o in s.objects),'camera':s.camera.name if s.camera else None,'world':s.world.name if s.world else None,'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage]}
 for world in bpy.data.worlds:
  data['worlds'][world.name]={'color':list(world.color),'nodes':{n.name: {'type':n.type,'color':list(n.inputs[0].default_value),'strength':n.inputs[1].default_value} for n in world.node_tree.nodes if n.type=='BACKGROUND'} if world.node_tree else {}}
 return data
bpy.ops.wm.open_mainfile(filepath=str(r/'blender/kits/KIT_water.blend'));before=signature();source_hash=sha(r/'blender/kits/KIT_water.blend');material=bpy.data.materials['MAT_water'];bsdf=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');old={'diffuse':list(material.diffuse_color),'base':list(bsdf.inputs['Base Color'].default_value),'emission':list(bsdf.inputs['Emission Color'].default_value),'strength':bsdf.inputs['Emission Strength'].default_value,'roughness':bsdf.inputs['Roughness'].default_value,'metallic':bsdf.inputs['Metallic'].default_value,'alpha':bsdf.inputs['Alpha'].default_value}
export_all(w/'baseline')
for file in sorted((w/'baseline').glob('*.glb')):assert file.read_bytes()==(r/'export/kits/water'/file.name).read_bytes(),('Saved water source baseline does not reproduce',file.name)
atlas_material=bpy.data.materials['MAT_pavilion_atlas'];atlas_bsdf=next(n for n in atlas_material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');links=list(atlas_bsdf.inputs['Base Color'].links);assert len(links)==1 and links[0].from_node.type=='TEX_IMAGE'
node=links[0].from_node;original_image=node.image;assert original_image.packed_file and original_image.colorspace_settings.name=='sRGB' and list(original_image.size)==[2048,2048]
images_before={image.name:{'sha256':hashlib.sha256(image.packed_file.data).hexdigest(),'size':list(image.size),'colorspace':image.colorspace_settings.name,'fake_user':image.use_fake_user} for image in bpy.data.images if image.packed_file}
old_color_hash=hashlib.sha256(original_image.packed_file.data).hexdigest();assert old_color_hash=='8bb9434918c056be06886377de89e71ba721cf2b0e84dd3ce060137a693bbc5c'
uses=[(m.name,n.name) for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image==original_image];assert uses==[(atlas_material.name,node.name)]
image_name=original_image.name;fake_user=original_image.use_fake_user;color_path=r/'textures/atlases/pavilion/pavilion_basecolor.png';image=bpy.data.images.load(str(color_path),check_existing=False);image.colorspace_settings.name='sRGB';image.pack();node.image=image;assert original_image.users==int(fake_user);bpy.data.images.remove(original_image);image.name=image_name;image.use_fake_user=fake_user
color=(.25,.32,.4,1);material.diffuse_color=color;bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Emission Color'].default_value=color
assert signature()==before
bpy.context.window.scene=bpy.data.scenes['Water kit showroom'];bpy.ops.wm.save_as_mainfile(filepath=str(w/'KIT_water.blend'),compress=True);bpy.ops.wm.open_mainfile(filepath=str(w/'KIT_water.blend'));assert signature()==before
images_after={image.name:{'sha256':hashlib.sha256(image.packed_file.data).hexdigest(),'size':list(image.size),'colorspace':image.colorspace_settings.name,'fake_user':image.use_fake_user} for image in bpy.data.images if image.packed_file};wanted=json.loads(json.dumps(images_before));wanted[image_name]['sha256']=sha(color_path);assert images_after==wanted
material=bpy.data.materials['MAT_water'];bsdf=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
assert all(abs(a-b)<1e-7 for a,b in zip(bsdf.inputs['Base Color'].default_value,color))
for key,input_name in [('strength','Emission Strength'),('roughness','Roughness'),('metallic','Metallic'),('alpha','Alpha')]:assert bsdf.inputs[input_name].default_value==old[key]
export_all(w/'candidate');assert sha(r/'blender/kits/KIT_water.blend')==source_hash
(w/'source-review.json').write_text(json.dumps({'status':'saved_water_source_palette_reopened_exported','baseline_saved_source_sha256':source_hash,'candidate_saved_source_sha256':sha(w/'KIT_water.blend'),'before_water_material':old,'new_water_color':list(color),'images_before':images_before,'images_after':images_after,'unchanged_source_snapshot_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'baseline_exports_byte_identical':12,'candidate_exports':12,'scope':'Only MAT_water diffuse/BSDF base/emission-color values and the packed pavilion basecolor image change. The atlas is the existing reviewed neutral PNG, copied without raster edits. Saved/reopened object geometry, UVs, transforms, collision/ports, all scenes/cameras/lights/worlds are identical. Roughness/metal/alpha/emission strength retained. Source assembly and in-progress bake are untouched; native exported material validation and kit adoption pending.'},indent=2)+'\n');print('SAVED_WATER_PALETTE_PASS',w)
