"""Place the completed flora kit in existing authored beds and embankments."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
variants=['bamboo_small','bamboo_medium','bamboo_large','banana','plum','willow','reed']
with bpy.data.libraries.load(str(R/'blender/kits/KIT_flora.blend'),link=False) as (src,dst):
 dst.collections=['KIT_flora_'+v for v in variants]
models={v:next(o for o in c.objects if o.type=='MESH' and not o.name.startswith('COL_')) for v,c in zip(variants,dst.collections)}
records=[]
def plant(slug,variant,position,angle=0,scale=1):
 col=bpy.data.collections['SITE_'+slug];source=models[variant];o=source.copy();o.data=source.data
 o.name='HERO_flora_'+slug.replace('-','_')+'_'+str(len(records));o.location=position;o.rotation_euler=(0,0,angle);o.scale=(scale,)*3
 o.hide_render=False;o.hide_viewport=False;o['flora_variant']=variant;o['flora_placement']=True;o['lod_distance']=14.0;col.objects.link(o)
 records.append({'name':o.name,'site':slug,'variant':variant,'position_blender':list(position),'rotation_z':angle,'scale':scale})
def remove(slug,prefixes):
 for o in list(bpy.data.collections['SITE_'+slug].objects):
  if o.name.startswith(prefixes) and not o.name.startswith('COL_'):bpy.data.objects.remove(o,do_unlink=True)
# Idempotent placements. Existing planters, beds and route colliders stay authored.
for slug in ['xiaoxiang-guan','yihong-yuan','longcui-an','ziling-zhou','qinfang-ting']:remove(slug,('HERO_flora_',))
remove('xiaoxiang-guan',('XIAOXIANG_bamboo_stem','XIAOXIANG_bamboo_node','XIAOXIANG_bamboo_branch','XIAOXIANG_bamboo_leaf'))
for i,(cx,cy) in enumerate([(-2.15,-1.3),(2.4,-1.1),(-2.3,-3.3),(2.5,-3.3)]):
 plant('xiaoxiang-guan',['bamboo_large','bamboo_medium','bamboo_small','bamboo_large'][i],(-9-cy,-13+cx,.08),math.pi/2+i*.5)
remove('yihong-yuan',('YIHONG_banana_trunk','YIHONG_banana_leaf','YIHONG_banana_midrib'))
for cx,cy,size in [(-2.45,-1.35,1.3),(2.7,-2.35,1.05)]:plant('yihong-yuan','banana',(25+cy,-1-cx,.4),-math.pi/2,size)
remove('longcui-an',('LONGCUI_plum_trunk','LONGCUI_plum_branch','LONGCUI_plum_twig','LONGCUI_plum_blossom'))
for cx,cy,angle in [(-2.45,-1.8,0),(2.5,-2.5,.6)]:plant('longcui-an','plum',(-25-cx,-13-cy,0),angle,1.12)
remove('ziling-zhou',('KIT_flora_ziling_reed','KIT_flora_ziling_seedhead'))
for i in range(16):
 a=i*math.tau/16;y=1.9*math.sin(a)
 if abs(y)<1.2:continue
 plant('ziling-zhou','reed',(-34+2.8*math.cos(a),y,-.08),a,.85+(i%3)*.08)
# Replace original bamboo and leaf cards while retaining lotus leaves in the water.
remove('qinfang-ting',('KIT_flora_bamboo','KIT_flora_leaf_card'))
for x,size in [(-7,'bamboo_large'),(7,'bamboo_large'),(-10,'bamboo_small')]:plant('qinfang-ting',size,(x,-7,-.4),x*.17)
for obj in list(bpy.data.collections['SITE_qinfang-ting'].objects):
 if obj.name.startswith('COL_flora_willow_'):bpy.data.objects.remove(obj,do_unlink=True)
for x in [-12,12]:
 plant('qinfang-ting','willow',(x,-5.9,-.4),x*.08)
 # New trunks alone need collision; do not place a canopy-sized volume on the route.
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-5.9,.8));o=bpy.context.object;o.name='COL_flora_willow_'+str(x);o.scale=(.32,.32,2.4)
 for old in list(o.users_collection):old.objects.unlink(o)
 bpy.data.collections['SITE_qinfang-ting'].objects.link(o)
# Keep every authored route marker and plant bed collider unchanged.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in sorted({r['site'] for r in records}):
 col=bpy.data.collections['SITE_'+slug];bpy.data.libraries.write(str(R/f'blender/sites/SITE_{slug}.blend'),{col},fake_user=True,compress=True)
(R/'export/flora-placements.json').write_text(json.dumps({'placements':records,'count':len(records)},indent=2)+'\n')
print('FLORA_PLACEMENTS_PASS',len(records))
