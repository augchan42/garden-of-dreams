"""Original painted-set skies and timber/metal atlas; no external image sources."""
from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1];out=R/'textures/kits/stage';out.mkdir(parents=True,exist_ok=True)
CELLS={'wood':0,'steel':1,'black':2,'brass':3}
def build():
 from PIL import Image,ImageDraw
 import numpy as np
 rng=np.random.default_rng(1978);yy,xx=np.mgrid[:512,:512]
 atlas=Image.new('RGB',(2048,2048),(10,10,12));orm=Image.new('RGB',(2048,2048),(255,210,0))
 for name,index,color,rough,metal in [('wood',0,(91,64,43),205,0),('steel',1,(47,48,53),170,220),('black',2,(4,4,6),255,0),('brass',3,(137,99,53),115,210)]:
  grain=rng.normal(0,1.5,(512,512))
  if name=='wood':grain+=6*np.sin(yy*.14+np.sin(xx*.015)*3)
  tile=Image.fromarray(np.clip(np.array(color)[None,None,:]+grain[:,:,None],0,255).astype('uint8'));atlas.paste(tile,((index%4)*512,(index//4)*512))
  ImageDraw.Draw(orm).rectangle((index*512,0,index*512+511,511),fill=(255,rough,metal))
 atlas.save(out/'stage-basecolor.png');orm.save(out/'stage-orm.png')
 palettes={
  'moonlit':{'sky':(76,87,109),'horizon':(161,145,139),'mountains':[(112,112,130),(86,89,108),(61,71,89)],'moon':(237,227,199)},
  'dusk':{'sky':(89,65,88),'horizon':(197,151,122),'mountains':[(148,116,126),(107,84,110),(68,61,85)],'moon':(247,217,180)},
  'mist':{'sky':(132,141,151),'horizon':(214,203,180),'mountains':[(169,170,171),(130,146,155),(91,118,132)],'moon':(244,235,208)}}
 # Work in a 2048px canvas, then retain a 4096px source with visible brush grain.
 n=2048;y,x=np.mgrid[:n,:n];texture_noise=rng.normal(0,1.5,(n,n)).astype('float32')
 for index,(name,palette) in enumerate(palettes.items()):
  t=(y/n)**1.3;sky=np.array(palette['sky']);horizon=np.array(palette['horizon'])
  pixels=sky[None,None,:]*(1-t[:,:,None])+horizon[None,None,:]*t[:,:,None]+texture_noise[:,:,None]
  canvas=Image.fromarray(np.clip(pixels,0,255).astype('uint8'));draw=ImageDraw.Draw(canvas)
  moon=(1540,240,1608,408);draw.ellipse(moon,fill=palette['moon'])
  for layer,color in enumerate(palette['mountains']):
   points=[]
   for px in range(0,n+1,12):
    wave=math.sin(px*.005+index*.9+layer)*.55+math.sin(px*.012+layer*.6)*.27+math.sin(px*.027+index)*.11
    py=int(1000+layer*210-wave*(170-layer*30));points.append((px,py))
   draw.polygon(points+[(n,n),(0,n)],fill=color)
   # Short directional strokes along ridges and slopes keep the set visibly painted.
   for j in range(1100):
    px=int(rng.integers(0,n));ridge=points[min(px//12,len(points)-1)][1];py=int(rng.integers(ridge,min(n,ridge+330)))
    ink=tuple(max(0,min(255,c+int(rng.integers(-9,10)))) for c in color)
    draw.line((px,py,px+int(rng.integers(5,40)),py+int(rng.integers(-9,10))),fill=ink,width=int(rng.integers(1,4)))
  canvas=canvas.resize((4096,4096),Image.Resampling.LANCZOS)
  canvas.save(out/f'cyclorama-{name}.png')
 (out/'atlas.json').write_text(json.dumps({'size':2048,'cells':CELLS,'cyclorama_size':4096,'variants':palettes,'provenance':'Original seeded brushwork, mountains and moon; no external source images.','seed':1978},indent=2)+'\n')
 print('STAGE_ART_PASS: 2048px atlas, three 4096px painted skies')
if __name__=='__main__':build()
