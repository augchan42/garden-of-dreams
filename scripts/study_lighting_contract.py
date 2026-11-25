"""Inspect the saved spotlight cone against actual CRT phosphor quads.

This measures cone coverage only, not exposure, shadows or final lighting.
"""
import bpy,math
from mathutils import Vector

def inspect():
    site=bpy.data.collections['SITE_qiushuang-zhai']
    lights=[o for o in site.objects if o.type=='LIGHT' and o.name=='LGT_qiushuang-zhai_key']
    assert len(lights)==1
    key=lights[0]
    assert key.data.type=='SPOT' and key.data.energy>0
    assert key.data.shadow_soft_size==0 and key.data.use_shadow
    axis=(key.matrix_world.to_quaternion()@Vector((0,0,-1))).normalized()
    limit=math.cos(key.data.spot_size/2)
    banks=sorted([o for o in site.objects if o.get('tech_variant')=='monitor_bank'],key=lambda o:o.location.x)
    assert len(banks)==3
    rows=[]
    for bank in banks:
        uv=bank.data.uv_layers[0];points=[]
        for face in bank.data.polygons:
            center=sum((uv.data[i].uv for i in face.loop_indices),Vector((0.,0.)))/len(face.loop_indices)
            if .006<center.x<.244 and .506<center.y<.744:points.append(bank.matrix_world@face.center)
        assert len(points)==192
        angles=[math.degrees(math.acos(max(-1.,min(1.,axis.dot((p-key.matrix_world.translation).normalized()))))) for p in points]
        inside=sum(axis.dot((p-key.matrix_world.translation).normalized())>limit for p in points)
        rows.append({'bank':bank.name,'samples':len(points),'inside_cone':inside,'maximum_angle_degrees':max(angles),'minimum_distance':min((p-key.matrix_world.translation).length for p in points)})
    return {'status':'passed' if all(r['inside_cone']==r['samples'] for r in rows) else 'failed_key_misses_screen_banks','banks':rows,'samples':sum(r['samples'] for r in rows),'inside_cone':sum(r['inside_cone'] for r in rows),'light':{'location':list(key.location),'rotation':list(key.rotation_euler),'power':key.data.energy,'color':list(key.data.color),'cone_degrees':math.degrees(key.data.spot_size),'blend':key.data.spot_blend,'source_radius':key.data.shadow_soft_size},'scope':'Actual source phosphor quad centres and spotlight cone; not occlusion, exposure, legibility or final lighting acceptance.'}
