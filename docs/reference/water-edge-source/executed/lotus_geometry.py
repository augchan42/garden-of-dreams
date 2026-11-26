"""Shallow circular lotus pads, with a continuous peltate leaf edge.

Stock geometry for the stylized garden; source/native acceptance is separate.
"""
import math
LAYOUT = [(-.6,-.3,.34),(.05,-.45,.3),(.55,-.1,.36),(-.4,.4,.4),(.35,.45,.38),(0,.05,.25)]
def leaf(radius, segments, phase=0):
    if not radius>0 or segments<9:raise ValueError('Positive radius and at least nine rim segments required')
    angles=[j*math.tau/segments for j in range(segments)]
    vertices=[(0,0,.005)]
    vertices.extend((radius*.5*math.cos(a),radius*.5*math.sin(a),.012+.001*math.sin(2*a+phase)) for a in angles)
    outer=[]
    for a in angles:
        r=radius*(1+.025*math.sin(3*a+phase))
        outer.append((r*math.cos(a),r*math.sin(a),.020+.007*math.sin(a+phase)**2))
    vertices.extend(outer);vertices.extend((x,y,z-.006) for x,y,z in outer)
    bottom=len(vertices);vertices.append((0,0,-.001))
    inner=1;rim=1+segments;under=1+2*segments;faces=[]
    for j in range(segments):
        k=(j+1)%segments
        faces.extend([(0,inner+j,inner+k),(inner+j,rim+j,rim+k),(inner+j,rim+k,inner+k),
                      (rim+j,under+j,under+k),(rim+j,under+k,rim+k),(bottom,under+k,under+j)])
    return vertices,faces

def cluster(segments):
    vertices=[];faces=[]
    for i,(x,y,r) in enumerate(LAYOUT):
        vs,fs=leaf(r,segments,i*.7);offset=len(vertices);a=i*.71;c=math.cos(a);s=math.sin(a)
        vertices.extend((x+c*u-s*v,y+s*u+c*v,z) for u,v,z in vs)
        faces.extend(tuple(offset+k for k in f) for f in fs)
    return vertices,faces
