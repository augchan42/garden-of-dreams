"""Generate the flora kit's original 2048px RGBA atlas from vector shapes."""
import math, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CELLS = {'bamboo':0, 'willow':1, 'banana':2, 'plum':3, 'reed':4,
         'blossom':5, 'bark':6, 'culm':7, 'pot':8, 'soil':9, 'reed_stem':10}

def build():
    from PIL import Image, ImageDraw
    random.seed(83)
    atlas = Image.new('RGBA', (2048,2048))
    colors = [(139,157,114), (153,163,137), (130,147,103), (156,164,126), (166,164,123)]
    for name,index in CELLS.items():
        tile = Image.new('RGBA',(512,512)); d=ImageDraw.Draw(tile)
        if index < 5:
            points=[]
            for side in (1,-1):
                for j in (range(65) if side==1 else range(64,-1,-1)):
                    t=j/64
                    width=185*math.sin(math.pi*t)**(.72 if name in ('banana','plum') else 1.4)
                    if name=='banana': width *= 1-.08*(j%7==0)
                    points.append((256+side*width,478-t*444))
            color=colors[index]
            d.polygon(points,fill=(*color,255))
            d.line([(256,475),(250,250),(256,34)],fill=(*(min(255,c+28) for c in color),255),width=5)
            for j in range(1,12):
                t=j/13; y=478-t*444; width=170*math.sin(math.pi*t)**.9
                for side in (-1,1):d.line([(254,y+25),(256+side*width,y-17)],fill=(*(max(0,c-16) for c in color),255),width=2)
        elif name=='blossom':
            for j in range(5):
                a=j*math.tau/5-math.pi/2; x=256+math.cos(a)*91;y=256+math.sin(a)*91
                d.ellipse((x-90,y-90,x+90,y+90),fill=(232,196,193,255))
                d.ellipse((x-65,y-65,x+65,y+65),fill=(245,218,208,255))
            d.ellipse((228,228,284,284),fill=(173,123,80,255))
            for j in range(13):
                a=j*math.tau/13; x=256+math.cos(a)*38;y=256+math.sin(a)*38
                d.line((256,256,x,y),fill=(202,153,85,255),width=3)
                d.ellipse((x-4,y-4,x+4,y+4),fill=(243,215,142,255))
        else:
            color={'bark':(111,94,77),'culm':(157,149,111),'pot':(167,110,86),'soil':(88,72,60),'reed_stem':(159,148,103)}[name]
            d.rectangle((0,0,512,512),fill=(*color,255))
            for j in range(180):
                x=random.randrange(512);y=random.randrange(512);delta=random.randint(-13,13)
                c=tuple(max(0,min(255,v+delta)) for v in color)
                d.line((x,y,x+random.randint(-3,3),y+random.randint(5,70)),fill=(*c,255),width=random.randint(1,3))
        atlas.alpha_composite(tile,((index%4)*512,(index//4)*512))
    path=ROOT/'textures/kits/flora/flora-basecolor.png';path.parent.mkdir(parents=True,exist_ok=True)
    atlas.save(path)
    print(path)
if __name__=='__main__':build()
