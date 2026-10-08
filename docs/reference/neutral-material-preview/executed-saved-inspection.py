import bpy,json
from pathlib import Path
rows={}
for m in bpy.data.materials:
 if not m.name.startswith('MAT_'):continue
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
 if p:
  rows[m.name]={'base':list(p.inputs['Base Color'].default_value),'emission':list(p.inputs['Emission Color'].default_value),'strength':p.inputs['Emission Strength'].default_value,'roughness':p.inputs['Roughness'].default_value,'base_linked':p.inputs['Base Color'].is_linked,'textures':[n.image.name if n.image else None for n in m.node_tree.nodes if n.type=='TEX_IMAGE']}
Path('/tmp/garden-saved-palette.json').write_text(json.dumps(rows,indent=2)+'\n')
for name in ['MAT_lattice_wood','MAT_whitewash','MAT_rooftile','MAT_plaster_rock','MAT_water','MAT_foliage_card']:
 print(name,json.dumps(rows.get(name)))
