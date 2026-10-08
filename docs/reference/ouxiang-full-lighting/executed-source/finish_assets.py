import bpy, math, json, numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('/Users/auchan/projects/garden-of-dreams');s=next(q for q in bpy.data.scenes if q.name.startswith('Garden of Dreams'))
bpy.context.window.scene=s
s.view_layers.update()
stage=bpy.data.collections['SITE_stage']
# Raster fog mask: deterministic soft turbulence with edge falloff.
n=512;yy,xx=np.mgrid[0:n,0:n]/n
mask=(np.sin(xx*27+np.sin(yy*12)*2)+np.sin(yy*31+xx*6)+3)/5
mask*=np.sin(xx*np.pi)**2*np.sin(yy*np.pi)**2
pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=(.08,.25,.09);pix[:,:,3]=mask*.18
im=bpy.data.images.new('fog-mask',width=n,height=n,alpha=True);im.pixels.foreach_set(pix.ravel());im.filepath_raw=str(R/'export/textures/fog-mask.png');im.file_format='PNG';im.save();im.pack()
m=bpy.data.materials.new('MAT_fog_plane');m.use_nodes=True
p=next(q for q in m.node_tree.nodes if q.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.08,.25,.09,1);p.inputs['Emission Color'].default_value=(.08,.25,.09,1);p.inputs['Emission Strength'].default_value=.3
tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha'])
# select surface method from RNA, rather than assuming a version enum
prop=m.bl_rna.properties.get('surface_render_method')
if prop:
 opts=[i.identifier for i in prop.enum_items]
 m.surface_render_method=next((i for i in opts if 'BLEND' in i),opts[0])
for i,(x,y,w,d) in enumerate([(0,0,76,10),(0,-11,12,14),(0,12,14,14),(-22,0,14,9),(22,0,14,9),(0,-26,5,12),(0,-39,17,2)]):
 c=stage if i<5 else bpy.data.collections['SITE_'+('rockery-gate' if i==5 else 'terminal-cells')]
 for level in range(3):
  z=.3+level*.17;me=bpy.data.meshes.new('fog_card');me.from_pydata([(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z)],[],[(0,1,2,3)]);me.materials.append(m)
  uv=me.uv_layers.new(name='UVMap')
  for j,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[j].uv=co
  o=bpy.data.objects.new('KIT_stage_fog_plane',me);c.objects.link(o);o['godot_scroll_speed']=[.008,.003]
# Preserve honest backdrop painting with a raster brush-grain texture at required resolution.
n=4096;yy,xx=np.mgrid[0:n,0:n].astype(np.float32)/n
brush=.92+.05*np.sin(xx*650+np.sin(yy*35)*8)+.025*np.sin(yy*1300+xx*60)
pix=np.empty((n,n,4),dtype=np.float32)
for k,v in enumerate([.019,.055,.025]):pix[:,:,k]=v*brush*(.65+.55*yy)
pix[:,:,3]=1
im=bpy.data.images.new('cyclorama-painted',width=n,height=n);im.pixels.foreach_set(pix.ravel());im.filepath_raw=str(R/'export/textures/cyclorama-painted.png');im.file_format='PNG';im.save();im.pack()
m=bpy.data.materials['MAT_cyclorama'];p=next(q for q in m.node_tree.nodes if q.type=='BSDF_PRINCIPLED');tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color'])
o=bpy.data.objects['KIT_stage_cyclorama'];uv=o.data.uv_layers.new(name='UVMap')
for poly in o.data.polygons:
 for li in poly.loop_indices:
  co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(math.atan2(co.y,co.x)/math.tau%1,(co.z+2)/22)
# Six screen lights retained as authored choices, but only occupied cell enabled in reference.
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith('LGT_CRT_cell_') and not o.name.endswith('_2'):o.data.energy=0
# Camera rail metadata; no character or gameplay scripts.
for slug,c in [(c.name.removeprefix('SITE_'),c) for c in s.collection.children]:
 cams=[o for o in c.objects if o.type=='CAMERA']
 if not cams:continue
 cam=cams[0];me=bpy.data.meshes.new('rail_path');loc=cam.location
 me.from_pydata([tuple(loc+Vector((d,0,0))) for d in [-1.5,0,1.5]],[(0,1),(1,2)],[])
 o=bpy.data.objects.new('CAM_rail_'+slug,me);c.objects.link(o);o.hide_render=True;o['camera']=cam.name;o['rail_only']=True
# Show more sky and the full moon in the establishing shot.
cam=s.camera;cam.location=(18,-30,10);cam.rotation_euler=(Vector((0,5,3.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=32
# Remove shadow from the disc so the painted moon is visibly part of a flat.
moon=bpy.data.objects['KIT_stage_painted_moon'];moon.visible_shadow=False
# Per-site editable blend files, retaining absolute assembly coordinates.
for c in list(s.collection.children):
 slug=c.name.removeprefix('SITE_')
 bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{c},fake_user=True,compress=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
# Share linked per-site collections in the master.
master=bpy.data.scenes.new('Garden of Dreams | master');master.world=s.world;master.unit_settings.system='METRIC';master.render.engine=s.render.engine
master.render.resolution_x=1410;master.render.resolution_y=600;master.render.resolution_percentage=100
for file in sorted((R/'blender/sites').glob('*.blend')):
 with bpy.data.libraries.load(str(file),link=True) as (src,dst):dst.collections=[n for n in src.collections if n==file.stem]
 for c in dst.collections:
  master.collection.children.link(c)
  if c.name=='SITE_qinfang-ting':master.camera=next(o for o in c.objects if o.type=='CAMERA' and o.name=='CAM_stage_wide')
bpy.context.window.scene=master
master.view_layers.update()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/master.blend'),compress=True)
# Color grading LUT uses green mids, amber highlights, crushed blacks; red-fastest .cube ordering.
def grade(rgb):
 lum=rgb[...,0]*.2126+rgb[...,1]*.7152+rgb[...,2]*.0722
 lum=np.clip((lum-.025)/.975,0,1)**.9
 warm=np.clip((rgb[...,0]-rgb[...,1]*.85)*2.3,0,1)
 g=np.stack([lum*.16,lum*.86,lum*.16],axis=-1)
 a=np.stack([lum*1.5,lum*.70,lum*.015],axis=-1)
 return np.clip(g*(1-warm[...,None])+a*warm[...,None],0,1)
with (R/'grade/tech-noir.cube').open('w') as f:
 f.write('TITLE "Garden of Dreams tech-noir"\nLUT_3D_SIZE 32\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
 for b in range(32):
  for g in range(32):
   for r in range(32):f.write('%.6f %.6f %.6f\n'%tuple(grade(np.array([r,g,b])/31)))
# Save helper for rendering exactly this grade, used for every reference image.
bpy.app.driver_namespace['garden_grade']=grade
print('Saved authoring file, linked master, 15 site files, fog and backdrop textures, LUT')
