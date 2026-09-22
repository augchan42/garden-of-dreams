"""Map a pavilion mesh's stock materials into the shared PBR atlas."""
import bpy, json, hashlib

def apply_atlas(model,root,atlas='pavilion'):
 folder=root/'textures/atlases'/atlas
 config=json.loads((folder/'atlas.json').read_text())
 material=bpy.data.materials.get('MAT_'+atlas+'_atlas')
 if material is None:
  material=bpy.data.materials.new('MAT_'+atlas+'_atlas');material.use_nodes=True
  nodes=material.node_tree.nodes;links=material.node_tree.links
  bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
  textures={}
  for key in ['basecolor','orm','normal']:
   node=nodes.new('ShaderNodeTexImage')
   node.image=bpy.data.images.load(str(folder/f'{atlas}_{key}.png'),check_existing=True)
   if key!='basecolor':node.image.colorspace_settings.name='Non-Color'
   node.image.pack();textures[key]=node
  links.new(textures['basecolor'].outputs['Color'],bsdf.inputs['Base Color'])
  channels=nodes.new('ShaderNodeSeparateColor')
  links.new(textures['orm'].outputs['Color'],channels.inputs['Color'])
  links.new(channels.outputs['Green'],bsdf.inputs['Roughness'])
  links.new(channels.outputs['Blue'],bsdf.inputs['Metallic'])
  bump=nodes.new('ShaderNodeNormalMap');bump.inputs['Strength'].default_value=.4
  links.new(textures['normal'].outputs['Color'],bump.inputs['Color'])
  links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
  material['atlas_resolution']=2048
  material['atlas_source']=f'textures/atlases/{atlas}/atlas.json'
 mesh=model.data
 uv=mesh.uv_layers[0]
 original_lightmap=[tuple(v.uv) for v in mesh.uv_layers[1].data]
 for poly in mesh.polygons:
  name=mesh.materials[poly.material_index].name.split('.')[0]
  x,y,w,h=config['uv_regions'][name]
  for loop in poly.loop_indices:
   u,v=uv.data[loop].uv
   uv.data[loop].uv=(x+u*w,y+v*h)
 mesh.materials.clear();mesh.materials.append(material)
 for poly in mesh.polygons:poly.material_index=0
 assert original_lightmap==[tuple(v.uv) for v in mesh.uv_layers[1].data]
 mesh.uv_layers.active_index=0
 model['atlas_source']=atlas+'_2048'
