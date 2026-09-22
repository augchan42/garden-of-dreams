"""Use the existing water shader and compressed architectural maps for water-kit imports."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
folder=R/'godot/assets/kits/water'
for part in ['stream','pond']:
 for suffix in ['','_LOD1']:
  p=folder/f'KIT_water_{part}{suffix}.glb.import'
  s,n=re.subn(r'^import_script/path=.*$','import_script/path="res://garden_import.gd"',p.read_text(),flags=re.M)
  assert n==1;p.write_text(s)
for p in folder.glob('*_pavilion_*.png.import'):
 s,n=re.subn(r'^compress/mode=.*$','compress/mode=2',p.read_text(),flags=re.M)
 assert n==1;p.write_text(s)
print('WATER_IMPORTS_CONFIGURED')
