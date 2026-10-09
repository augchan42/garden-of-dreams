from pathlib import Path
import json,ast
w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root'])/'water-kit-parity';p=w/'executed-update_water_palette.py';old=p.read_text();(w/'first-prepared-color-only-unexecuted.py').write_text(old)
old=old.replace("color=(.25,.32,.4,1);material.diffuse_color=color;",'''atlas_material=bpy.data.materials['MAT_pavilion_atlas'];atlas_bsdf=next(n for n in atlas_material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');links=list(atlas_bsdf.inputs['Base Color'].links);assert len(links)==1 and links[0].from_node.type=='TEX_IMAGE'
node=links[0].from_node;original_image=node.image;assert original_image.packed_file and original_image.colorspace_settings.name=='sRGB' and list(original_image.size)==[2048,2048]
images_before={image.name:{'sha256':hashlib.sha256(image.packed_file.data).hexdigest(),'size':list(image.size),'colorspace':image.colorspace_settings.name,'fake_user':image.use_fake_user} for image in bpy.data.images if image.packed_file}
old_color_hash=hashlib.sha256(original_image.packed_file.data).hexdigest();assert old_color_hash=='8bb9434918c056be06886377de89e71ba721cf2b0e84dd3ce060137a693bbc5c'
uses=[(m.name,n.name) for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image==original_image];assert uses==[(atlas_material.name,node.name)]
image_name=original_image.name;fake_user=original_image.use_fake_user;color_path=r/'textures/atlases/pavilion/pavilion_basecolor.png';image=bpy.data.images.load(str(color_path),check_existing=False);image.colorspace_settings.name='sRGB';image.pack();node.image=image;assert original_image.users==int(fake_user);bpy.data.images.remove(original_image);image.name=image_name;image.use_fake_user=fake_user
color=(.25,.32,.4,1);material.diffuse_color=color;''')
old=old.replace("assert signature()==before\nmaterial=bpy.data.materials['MAT_water']", """assert signature()==before
images_after={image.name:{'sha256':hashlib.sha256(image.packed_file.data).hexdigest(),'size':list(image.size),'colorspace':image.colorspace_settings.name,'fake_user':image.use_fake_user} for image in bpy.data.images if image.packed_file};wanted=json.loads(json.dumps(images_before));wanted[image_name]['sha256']=sha(color_path);assert images_after==wanted
material=bpy.data.materials['MAT_water']""")
old=old.replace("'new_water_color':list(color)","'new_water_color':list(color),'images_before':images_before,'images_after':images_after")
old=old.replace('Only MAT_water diffuse/BSDF base/emission-color values change.','Only MAT_water diffuse/BSDF base/emission-color values and the packed pavilion basecolor image change. The atlas is the existing reviewed neutral PNG, copied without raster edits.')
old=old.replace('saved_water_source_color_only_reopened_exported','saved_water_source_palette_reopened_exported').replace('SAVED_WATER_COLOR_ONLY_PASS','SAVED_WATER_PALETTE_PASS');ast.parse(old);p.write_text(old)
p=Path('/tmp/garden_verify_water_kit_palette.py');s=p.read_text();(w/'first-prepared-verifier-unexecuted.py').write_text(s)
s=s.replace('saved_water_source_color_only_reopened_exported','saved_water_source_palette_reopened_exported').replace("['accessors','bufferViews','images','textures','samplers','scene','scenes']","['accessors','images','textures','samplers','scene','scenes']")
s=s.replace("  else:assert old==new,(p.name,m['name'])", """  elif m['name']=='MAT_pavilion_atlas':
   target=next(m for m in source.doc['materials'] if m['name']=='MAT_pavilion_atlas');assert new==source.material(target)
   old['pbrMetallicRoughness']['baseColorTexture']['index']['source']=new['pbrMetallicRoughness']['baseColorTexture']['index']['source'];assert old==new
  else:assert old==new,(p.name,m['name'])""")
s=s.replace(" for m,n in zip(a.doc.get('images',[]),b.doc.get('images',[])):assert a.image_hash(m)==b.image_hash(n)",""" for m,n in zip(a.doc.get('images',[]),b.doc.get('images',[])):
  ah,bh=a.image_hash(m),b.image_hash(n)
  if ah!=bh:assert ah=='8bb9434918c056be06886377de89e71ba721cf2b0e84dd3ce060137a693bbc5c' and bh==sha(r/'textures/atlases/pavilion/pavilion_basecolor.png')""")
s=s.replace("assert any(m['name']=='MAT_water' for m in a.doc['materials'])","assert any(m['name'] in ['MAT_water','MAT_pavilion_atlas'] for m in a.doc['materials'])").replace('len(changed)==4 and len(identical)==8','len(changed)==10 and len(identical)==2').replace('changed_color_only_exports','changed_palette_exports').replace('all other PBR/images/textures','all other PBR/images/textures').replace('Only four stream/pond base colors change to exact source material.','Four stream/pond base colors and six embedded architectural color images change to exact source palette; the two lotus exports stay byte-identical.')
ast.parse(s);p.write_text(s);(w/p.name).write_text(s);print('PREPARED_WATER_PALETTE_SYNC_10_EXPORTS_TWO_ALIASES')
