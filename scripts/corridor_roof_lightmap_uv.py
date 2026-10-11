"""Reserve continuous UV2 charts for the sixteen saved Qinfang corridor roofs."""
def key(point):
    return tuple(round(float(value),3) for value in point)

def allocate_corridor_roof_charts(obj, sources, size=1024):
    assert size==1024
    mesh=obj.data
    positions=[tuple(v.co) for v in mesh.vertices]
    primary=[tuple(v.uv) for v in mesh.uv_layers[0].data]
    registry=[]
    point_faces={}
    counts={}
    assert len(sources)==16
    for source in sources:
        direction=source['bay_direction']
        bay=int(source.name.rsplit('_',1)[1])
        chart=['north','south','east','west'].index(direction)*4+bay
        assert chart not in counts
        faces=[]
        for face in source.data.polygons:
            source_uv=source.data.uv_layers[0]
            if not all(.515624<source_uv.data[i].uv.x<.984376 and .515624<source_uv.data[i].uv.y<.984376 for i in face.loop_indices):continue
            world=[source.matrix_world@source.data.vertices[i].co for i in face.vertices]
            if not all(w.z>2.79 for w in world):continue
            points={key(w):(source.data.vertices[i].co.x,source.data.vertices[i].co.y) for w,i in zip(world,face.vertices)}
            faces.append(points)
        counts[chart]=len(faces)
        assert len(faces) in [24,28],(source.name,len(faces))
        bounds=[(min(p[a] for f in faces for p in f.values()),max(p[a] for f in faces for p in f.values())) for a in range(2)]
        for points in faces:
            i=len(registry)
            registry.append((chart,points,bounds))
            for p in points:point_faces.setdefault(p,set()).add(i)
    assert sum(counts.values())==392
    uv=mesh.uv_layers[1]
    targets={}
    used=set()
    for face in mesh.polygons:
        world=[obj.matrix_world@mesh.vertices[i].co for i in face.vertices]
        if not all(w.z>2.79 for w in world):continue
        if not all(.515624<mesh.uv_layers[0].data[i].uv.x<.984376 and .515624<mesh.uv_layers[0].data[i].uv.y<.984376 for i in face.loop_indices):continue
        keys=[key(w) for w in world]
        candidates=set.intersection(*(point_faces.get(p,set()) for p in keys))
        if not candidates:continue
        assert len(candidates)==1,(face.index,candidates)
        registered=next(iter(candidates))
        assert registered not in used
        used.add(registered)
        targets[face.index]=(registered,keys)
    assert len(targets)==len(registry)==392,(len(targets),len(registry))
    for face in mesh.polygons:
        if face.index in targets:
            registered,keys=targets[face.index]
            chart,points,bounds=registry[registered]
            x=(chart%8)*128+4
            y=144+(chart//8)*128+4
            for loop,p in zip(face.loop_indices,keys):
                local=points[p]
                uv.data[loop].uv=((x+(local[0]-bounds[0][0])/(bounds[0][1]-bounds[0][0])*120)/size,
                                 (y+(local[1]-bounds[1][0])/(bounds[1][1]-bounds[1][0])*120)/size)
        else:
            for loop in face.loop_indices:
                u,v=uv.data[loop].uv
                if v>=144/size:uv.data[loop].uv=(u,400/size+(v-144/size)*(624/880))
    assert positions==[tuple(v.co) for v in mesh.vertices]
    assert primary==[tuple(v.uv) for v in mesh.uv_layers[0].data]
    return {'corridor_charts':16,'corridor_faces':392,'corridor_cell_texels':[128,128],
            'corridor_padding_texels':4,'corridor_reserved_start':144,'reserved_height_texels':400,
            'scope':'UV2 only: sixteen continuous saved-source corridor roof charts; prior central tile strips retained; other charts fit above400. Fresh matching source lighting and native importer checks required.'}
