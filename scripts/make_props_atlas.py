"""Original procedural prop surfaces and ink-style scroll/screen atlas."""
import math,random,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
CELLS={'wood':0,'stone':1,'bronze':2,'paper_lit':3,'coals':4,'linen':5,'calligraphy':6,'screen':7,'lacquer':8,'ash':9}
def build():
 from PIL import Image,ImageDraw,ImageFont
 random.seed(149)
 images={key:Image.new('RGB',(2048,2048)) for key in ['basecolor','orm','emission']}
 palette={'wood':(86,58,45),'stone':(174,171,157),'bronze':(126,97,60),'paper_lit':(230,177,102),'coals':(49,32,28),'linen':(204,189,162),'calligraphy':(221,207,177),'screen':(210,200,175),'lacquer':(131,64,43),'ash':(117,107,95)}
 for name,index in CELLS.items():
  tile=Image.new('RGB',(512,512),palette[name]);draw=ImageDraw.Draw(tile)
  for i in range(1500):
   x=random.randrange(512);y=random.randrange(512);shift=random.randrange(-12,13);c=tuple(max(0,min(255,v+shift)) for v in palette[name])
   draw.line((x,y,x+(2 if name!='wood' else 0),y+(25 if name=='wood' else 2)),fill=c,width=1)
  if name=='paper_lit':
   for y in range(512):
    strength=.72+.28*math.sin(math.pi*y/512);draw.line((0,y,512,y),fill=tuple(int(v*strength) for v in palette[name]))
   for x in range(0,512,64):draw.line((x,0,x,512),fill=(186,133,74),width=3)
  if name=='calligraphy':
   font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',94,index=2)
   assert all(font.getmask(ch).getbbox() for ch in '清風明月')
   for i,ch in enumerate('清風明月'):
    box=draw.textbbox((0,0),ch,font=font);draw.text((256-(box[2]-box[0])/2,20+i*113-box[1]),ch,font=font,fill=(44,38,32))
   draw.rectangle((328,412,350,454),outline=(138,57,42),width=5)
   draw.line((332,420,346,448),fill=(138,57,42),width=5)
  if name=='screen':
   for j in range(5):
    x=145+j*46;top=45+j%3*25
    draw.line((x,460,x-20,top),fill=(89,94,72),width=7)
    for y in range(top+45,450,65):
     draw.line((x-6,y,x+9,y),fill=(69,77,60),width=3)
     for side in [-1,1]:draw.polygon([(x,y),(x+side*70,y-42),(x+side*24,y-8)],fill=(96,103,77))
  if name=='coals':
   for j in range(65):
    x=random.randrange(512);y=random.randrange(512);draw.ellipse((x,y,x+35,y+17),fill=(158,68,28))
  rough={'bronze':120,'lacquer':135,'stone':180}.get(name,225);metal=190 if name=='bronze' else 0
  orm=Image.new('RGB',(512,512),(255,rough,metal));emission=Image.new('RGB',(512,512))
  if name=='paper_lit':emission=tile.copy()
  elif name=='coals':emission=tile.point(lambda v:int(v*.8))
  pos=((index%4)*512,(index//4)*512)
  for key,t in [('basecolor',tile),('orm',orm),('emission',emission)]:images[key].paste(t,pos)
 folder=R/'textures/kits/props';folder.mkdir(parents=True,exist_ok=True)
 for key,img in images.items():img.save(folder/f'props-{key}.png')
 (folder/'atlas.json').write_text(json.dumps({'size':2048,'cells':CELLS,'calligraphy_text':'清風明月','calligraphy_method':'Songti TC Bold typesetting on original procedural paper; not a historical calligraphy image'},indent=2,ensure_ascii=False)+'\n')
 print('PROPS_ATLAS_PASS')
if __name__=='__main__':build()
