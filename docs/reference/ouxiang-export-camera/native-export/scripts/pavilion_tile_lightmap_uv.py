"""Reserve enough UV2 texels for the pavilion's narrow raised tile strips."""
from pavilion_roof_geometry import components


def allocate_tile_charts(obj, size=1024):
    mesh=obj.data
    ridges=sorted([(sorted(vertices),faces) for vertices,faces in components(mesh)
                   if len(vertices)==15 and len(faces)==8],key=lambda item:item[0][0])
    assert len(ridges)==42, 'Expected the six-facet pavilion tile strips'
    assert len(mesh.uv_layers)==2
    positions=[tuple(v.co) for v in mesh.vertices]
    primary=[tuple(v.uv) for v in mesh.uv_layers[0].data]
    target_indices={p.index for _,faces in ridges for p in faces}
    reserved_height=144/size
    uv=mesh.uv_layers[1]
    for face in mesh.polygons:
        if face.index in target_indices:continue
        for loop in face.loop_indices:
            u,v=uv.data[loop].uv
            uv.data[loop].uv=(u,reserved_height+v*(1-reserved_height))
    for chart,(vertices,faces) in enumerate(ridges):
        lookup={index:offset for offset,index in enumerate(vertices)}
        column,row=chart%21,chart//21
        for face in faces:
            for loop in face.loop_indices:
                offset=lookup[mesh.loops[loop].vertex_index]
                across,along=offset%3,offset//3
                uv.data[loop].uv=((column*32+4+across*12)/size,
                                 (row*72+4+along*15)/size)
    assert positions==[tuple(v.co) for v in mesh.vertices]
    assert primary==[tuple(v.uv) for v in mesh.uv_layers[0].data]
    return {'strips':42,'faces':336,'reference_size':size,'cell_texels':[32,72],
            'tile_chart_texels':[24,60],'padding_texels':4,'reserved_height_texels':144,
            'scope':'UV2 only on the exported Qinfang atlas batch. Tile charts receive explicit pixel extent; all other charts fit above their reserved strip. Geometry/primary UVs are unchanged. Fresh matching bake and native filtering checks remain required.'}
