"""Experimental UV2-only allocation for the actual 576 imperial cylinders."""
import math
from mathutils import Vector
import bpy
from pavilion_roof_geometry import components

def allocate_imperial_charts(obj,size=1024):
    mesh=obj.data
    groups=list(components(mesh))
    cylinders=sorted([(sorted(v),[p.index for p in f]) for v,f in groups if len(v)==16 and len(f)==28],key=lambda item:item[0][0])
    shells=[(v,f) for v,f in groups if len(v)==16 and len(f)==26]
    from collections import Counter
    print('IMPERIAL_JOINED_TOPOLOGY',dict(Counter((len(v),len(f)) for v,f in groups)),flush=True)
    assert len(cylinders)==576 and len(shells)==2 and len(groups)==578
    positions=[tuple(v.co) for v in mesh.vertices]
    primary=[tuple(v.uv) for v in mesh.uv_layers[0].data]
    assert len(mesh.uv_layers)==2
    shell_faces={p.index for _,faces in shells for p in faces}
    # Reproject the shells independently instead of shrinking their already
    # tiny whole-batch charts a second time.
    bpy.context.tool_settings.mesh_select_mode=(False,False,True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT');bpy.ops.object.mode_set(mode='OBJECT')
    for face in mesh.polygons:face.select=face.index in shell_faces
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(30),island_margin=.015)
    bpy.ops.object.mode_set(mode='OBJECT')
    uv=mesh.uv_layers[1]
    reserved=756/size
    for face in mesh.polygons:
        if face.index not in shell_faces:continue
        for loop in face.loop_indices:
            u,v=uv.data[loop].uv
            uv.data[loop].uv=(u,reserved+v*(1-reserved))
    for chart,(vertices,faces) in enumerate(cylinders):
        lookup={index:offset for offset,index in enumerate(vertices)}
        rings=[[mesh.vertices[i].co for i in vertices[:8]],[mesh.vertices[i].co for i in vertices[8:]]]
        centers=[sum(r,Vector())/8 for r in rings]
        axis=(centers[1]-centers[0]).normalized()
        radii=[(p-centers[ring]).length for ring,r in enumerate(rings) for p in r]
        assert max(radii)-min(radii)<1e-5 and abs(sum(radii)/16-.022)<1e-5
        assert all(abs((p-centers[ring]).dot(axis))<1e-5 for ring,r in enumerate(rings) for p in r)
        ox,oy=(chart%28)*36,(chart//28)*36
        for face_index in faces:
            face=mesh.polygons[face_index]
            offsets=[lookup[v] for v in face.vertices]
            face_rings={v//8 for v in offsets}
            angular={v%8 for v in offsets}
            cap=len(face_rings)==1
            for loop in face.loop_indices:
                offset=lookup[mesh.loops[loop].vertex_index]
                ring,index=divmod(offset,8)
                if cap:
                    angle=index*math.tau/8
                    u=28+4*math.cos(angle)
                    v=(8 if ring==0 else 26)+4*math.sin(angle)
                else:
                    # The closing seam belongs to facet seven, not facet zero.
                    across=8 if index==0 and 7 in angular else index
                    u=4+across*2;v=4+ring*24
                uv.data[loop].uv=((ox+u)/size,(oy+v)/size)
    assert positions==[tuple(v.co) for v in mesh.vertices]
    assert primary==[tuple(v.uv) for v in mesh.uv_layers[0].data]
    return {'status':'isolated_uv2_experiment','cylinders':576,'shell_components':2,
            'reference_size':size,'cell_pixels':[36,36],'cylinder_grid':[28,21],
            'side_chart_pixels':[16,24],'cap_chart_radius_pixels':4,
            'reserved_height_pixels':756,
            'scope':'UV2-only experimental export allocation. Side/cap charts use four source-pixel separation inside each cell; cross-cell charts remain separated. Fresh source lighting, native filtering and gutter/appearance review required before adoption.'}
