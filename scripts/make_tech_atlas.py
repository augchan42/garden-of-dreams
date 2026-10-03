"""Original CRT phosphor lettering, casing, timber and metal atlas maps."""
from pathlib import Path
import json,math
CELLS={'case':0,'black':1,'bronze':2,'wood':3,'amber':4,'green':5,'keyboard':6,'cable':7,'steel':8,'label':9}
def build():
 from PIL import Image,ImageDraw,ImageFont
 import numpy as np
 R=Path(__file__).resolve().parents[1];out=R/'textures/kits/tech';out.mkdir(parents=True,exist_ok=True)
 base=Image.new('RGB',(2048,2048),(35,32,29));orm=Image.new('RGB',(2048,2048),(255,200,0));emission=Image.new('RGB',(2048,2048),(0,0,0))
 colors={'case':(156,148,130),'black':(19,21,23),'bronze':(121,86,47),'wood':(69,43,32),'amber':(15,10,3),'green':(4,12,7),'keyboard':(102,99,90),'cable':(25,25,27),'steel':(65,66,65),'label':(202,190,158)}
 yy,xx=np.mgrid[0:512,0:512];noise=np.random.default_rng(1978).normal(0,1,(512,512))
 for key,index in CELLS.items():
  x=index%4*512;y=index//4*512
  grain=noise*1.5
  if key=='wood':grain+=4*np.sin(xx*.12+np.sin(yy*.01)*2)
  if key=='cable':grain+=2*np.sin((xx+yy)*.25)
  tile=np.clip(np.array(colors[key])[None,None,:]+grain[:,:,None],0,255).astype('uint8');base.paste(Image.fromarray(tile),(x,y))
  rough={'case':175,'black':200,'bronze':110,'wood':195,'steel':135}.get(key,190);metal=220 if key in ['bronze','steel'] else 0
  ImageDraw.Draw(orm).rectangle((x,y,x+511,y+511),fill=(255,rough,metal))
 font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',44,index=1);small=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',36,index=1)
 for key,color,lines in [('amber',(255,172,45),['GARDEN NOTICE','--------------','PUBLIC BOARD','','NEWS  /  TOPICS','> READY']),('green',(78,225,122),['GARDEN TERMINAL','--------------','PERSONAL CELL','','ENTER THE GARDEN','> _'])]:
  index=CELLS[key];x=index%4*512;y=index//4*512
  for line,row in zip(lines,[55,115,175,235,295,355]):
   face=small if len(line)>14 else font
   assert face.getlength(line)<444,line
   ImageDraw.Draw(emission).text((x+34,y+row),line,font=face,fill=color)
  # Dark lines in emission fake the CRT scanline mask without cutting holes.
  e=np.asarray(emission).copy();e[y:y+512:4,x:x+512]=e[y:y+512:4,x:x+512]//3;emission=Image.fromarray(e)
  ImageDraw.Draw(base).rounded_rectangle((x+18,y+24,x+493,y+487),radius=35,outline=tuple(v//5 for v in color),width=10)
 index=CELLS['label'];x=index%4*512;y=index//4*512
 ImageDraw.Draw(base).text((x+55,y+210),'GARDEN / 1978',font=font,fill=(43,36,29))
 for key,img in [('basecolor',base),('orm',orm),('emission',emission)]:img.save(out/f'tech-{key}.png')
 (out/'atlas.json').write_text(json.dumps({'size':2048,'cells':CELLS,'art':'Original procedural textures and typeset CRT dressing. Static screen art, not service state.','font':'System Menlo; no font file redistributed.'},indent=2)+'\n')
 print('TECH_ATLAS_PASS',2048)
if __name__=='__main__':build()
