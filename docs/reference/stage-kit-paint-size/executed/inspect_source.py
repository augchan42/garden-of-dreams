from pathlib import Path
import bpy,hashlib,json
r=Path('/tmp/garden-stage-kit-atlas-20261011');reports={}
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for label,path in [('current',Path('/Users/auchan/projects/garden-of-dreams/blender/kits/KIT_stage.blend')),('baseline',r/'baseline/blender/kits/KIT_stage.blend'),('candidate',r/'candidate/blender/kits/KIT_stage.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path))
 objects={};meshes={};paints={}
 for obj in bpy.data.objects:
  objects[obj.name]={'type':obj.type,'matrix':[list(v) for v in obj.matrix_local],'data':obj.data.name if obj.data else None,'collections':sorted(c.name for c in obj.users_collection),'properties':dict(obj.items())}
 for mesh in bpy.data.meshes:
  meshes[mesh.name]=digest({'vertices':[list(v.co) for v in mesh.vertices],'faces':[list(p.vertices) for p in mesh.polygons],'materials':[m.name if m else None for m in mesh.materials],'material_indexes':[p.material_index for p in mesh.polygons],'uv':{uv.name:[list(v.uv) for v in uv.data] for uv in mesh.uv_layers}})
 for material in bpy.data.materials:
  if not material.name.startswith('MAT_stage_cyclorama_'):continue
  nodes=[n for n in material.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(nodes)==1
  image=nodes[0].image;assert tuple(image.size)==(4096,4096);assert image.packed_file is not None
  paints[material.name]={'image_name':image.name,'size':list(image.size),'packed_sha256':hashlib.sha256(image.packed_file.data).hexdigest()}
 assert len(paints)==3 and not any('.export2048' in i.name for i in bpy.data.images)
 reports[label]={'objects':objects,'meshes':meshes,'paints':paints}
assert reports['baseline']==reports['candidate'],'Editable source was altered'
assert reports['current']==reports['baseline'],'Baseline source inventory differs'
(r/'source-preservation.json').write_text(json.dumps({'status':'passed','source_inventory':reports['candidate'],'scope':'All actual editable objects/transforms/custom properties/collections, mesh positions/faces/material indexes/UVs and three4096packed original paints exact across installed source and both reproduced files.'},indent=2)+'\n');print('STAGE_EDITABLE_SOURCE_PRESERVATION_PASS',len(reports['candidate']['objects']),len(reports['candidate']['meshes']))
