"""Shared native checks for the physical moon painting; no source edits."""
import hashlib
import json
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'textures/backdrops/moon-paint'
OBJECT='KIT_stage_painted_moon'
MATERIAL='MAT_painted_moon'

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def properties(data):
 result={}
 for prop in data.bl_rna.properties:
  if prop.is_readonly or prop.type not in ('BOOLEAN','INT','FLOAT','STRING','ENUM'):continue
  value=getattr(data,prop.identifier)
  result[prop.identifier]=sorted(value) if isinstance(value,set) else list(value) if getattr(prop,'is_array',False) else value
 return result

def fingerprint(mesh,skip_uv=False):
 return digest({'vertices':[list(v.co) for v in mesh.vertices],
                'faces':[[list(p.vertices),p.material_index,p.use_smooth] for p in mesh.polygons],
                'materials':[m.name if m else None for m in mesh.materials],
                'uv':None if skip_uv else [[u.name,[list(v.uv) for v in u.data]] for u in mesh.uv_layers]})

def serial(value):
 if hasattr(value,'to_dict'):return {k:serial(v) for k,v in value.to_dict().items()}
 if hasattr(value,'to_list'):return [serial(v) for v in value.to_list()]
 if isinstance(value,bpy.types.ID):return [value.__class__.__name__,value.name]
 if isinstance(value,(str,int,float,bool)) or value is None:return value
 return [serial(v) for v in value]

def snapshot():
 objects={}
 for obj in bpy.data.objects:
  record={'type':obj.type,'matrix':list(map(list,obj.matrix_world)),
          'hidden':[obj.hide_viewport,obj.hide_render],'modifiers':[properties(m) for m in obj.modifiers],
          'extras':{k:serial(v) for k,v in obj.items() if not (obj.name==OBJECT and k=='paint_source')}}
  if obj.type=='MESH':record['mesh']=fingerprint(obj.data,obj.name==OBJECT)
  elif obj.type=='LIGHT':
   record['light']=properties(obj.data)
   receivers=obj.light_linking.receiver_collection
   record['receivers']=sorted(o.name for o in receivers.objects) if receivers else None
  elif obj.type=='CAMERA':record['camera']=properties(obj.data)
  objects[obj.name]=record
 materials={}
 for mat in bpy.data.materials:
  if mat.name==MATERIAL:continue
  nodes=list(mat.node_tree.nodes) if mat.use_nodes else []
  def value(v):
   try:return list(v)
   except TypeError:return v if isinstance(v,(float,int,bool,str)) else str(v)
  materials[mat.name]={'settings':properties(mat),'nodes':[[n.type,properties(n),[(s.identifier,value(s.default_value)) for s in n.inputs if hasattr(s,'default_value')],n.image.name if n.type=='TEX_IMAGE' and n.image else None] for n in nodes],
                       'links':[[nodes.index(l.from_node),l.from_socket.identifier,nodes.index(l.to_node),l.to_socket.identifier] for l in mat.node_tree.links] if mat.use_nodes else []}
 return {'objects':objects,'materials':materials}

def check(atlas_path=None):
 atlas=json.loads((Path(atlas_path) if atlas_path else FOLDER/'atlas.json').read_text());obj=bpy.data.objects[OBJECT];mat=bpy.data.materials[MATERIAL]
 bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 assert bsdf.inputs['Base Color'].is_linked,'Moon still has no paint texture'
 assert bsdf.inputs['Emission Color'].is_linked,'Moon retains constant green emission'
 images=[];factors={}
 for key,expected in [('Base Color',atlas['base_factor']),('Emission Color',atlas['emission_factor'])]:
  node=bsdf.inputs[key].links[0].from_node
  assert node.type=='MIX' and node.data_type=='RGBA' and node.blend_type=='MULTIPLY'
  fac=next(s for s in node.inputs if s.name=='Factor' and s.type=='VALUE');a=next(s for s in node.inputs if s.name=='A' and s.type=='RGBA');b=next(s for s in node.inputs if s.name=='B' and s.type=='RGBA')
  assert fac.default_value==1 and a.is_linked and not b.is_linked
  image=a.links[0].from_node
  assert image.type=='TEX_IMAGE' and image.image.packed_file
  assert image.image.colorspace_settings.name=='sRGB'
  assert hashlib.sha256(image.image.packed_file.data).hexdigest()==atlas['png_sha256']
  assert tuple(image.image.size)==tuple(atlas['image_size'])
  assert max(abs(float(v)-expected) for v in b.default_value[:3])<1e-6
  images.append(image);factors[key]=expected
 assert images[0]==images[1],'Base/emission must share the original painting'
 assert abs(bsdf.inputs['Emission Strength'].default_value-.8)<1e-6
 assert len(obj.data.uv_layers)==1
 uv=obj.data.uv_layers[0]
 for loop in obj.data.loops:
  point=obj.data.vertices[loop.vertex_index].co
  expected=(.5+point.x/5.4,.5+point.y/5.4)
  assert max(abs(uv.data[loop.index].uv[i]-expected[i]) for i in range(2))<1e-6
 mean=np.array(atlas['mean_linear_rgb']);weights=np.array([.2126,.7152,.0722])
 ratios={k:float(mean@weights)*factor/float(np.array(atlas['preceding_base_linear_rgb' if k=='Base Color' else 'preceding_emission_linear_rgb'])@weights) for k,factor in factors.items()}
 target=atlas.get('target_mean_luminance_ratio',1.0)
 assert type(target) in (int,float) and np.isfinite(target) and target>0, 'Invalid intended moon luminance ratio'
 assert all(abs(v-target)<1e-6 for v in ratios.values()), 'Moon factors differ from intended source luminance'
 assert mean[0]>mean[1]>mean[2] and mean[1]<.5*(mean[0]+mean[2])+.05
 return {'texture_sha256':atlas['png_sha256'],'image_size':atlas['image_size'],'uv_layer':uv.name,'base_factor':factors['Base Color'],'emission_factor':factors['Emission Color'],'emission_strength':.8,'mean_base_luminance_ratio':ratios['Base Color'],'mean_emission_luminance_ratio':ratios['Emission Color'],'target_mean_luminance_ratio':target,'mean_linear_paint_rgb':mean.tolist()}
