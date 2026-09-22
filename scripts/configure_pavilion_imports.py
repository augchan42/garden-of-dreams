"""Enable GPU compression for extracted pavilion atlas textures at full resolution."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
paths=list((R/'godot/assets/kits/pavilion').glob('*_pavilion_*.png.import'))+list((R/'godot/assets/kits/corridor').glob('*_pavilion_*.png.import'))+list((R/'godot/assets').glob('garden-of-dreams_pavilion_*.png.import'))
assert len(paths)>=39,len(paths)
for p in paths:
 s=p.read_text()
 for key,value in {'compress/mode':'2','compress/high_quality':'false','process/size_limit':'0','mipmaps/generate':'true'}.items():
  s,count=re.subn('^'+re.escape(key)+'=.*$',key+'='+value,s,flags=re.M)
  assert count==1,(p,key)
 p.write_text(s)
print('PAVILION_GPU_COMPRESSION_CONFIGURED',len(paths))
