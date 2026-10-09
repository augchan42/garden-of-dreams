from pathlib import Path
import json
p=Path(json.loads(Path('/tmp/garden-ziling-framing.json').read_text())['folder']);s=(p/'godot/tests/compare_ziling_roof.gd').read_text();start=s.index('   for position in [');end=s.index('\n    for x in',start)
s=s[:start]+'''   for position in [Vector3(-40,2.4,2),Vector3(-41,2.4,2),Vector3(-42,2.4,2),Vector3(-40,3.2,2),Vector3(-41,3.2,2),Vector3(-42,3.2,2),Vector3(-40,2.4,3),Vector3(-41,2.4,3),Vector3(-42,2.4,3),Vector3(-40,3.2,3),Vector3(-41,3.2,3),Vector3(-42,3.2,3),Vector3(-40,2.4,4),Vector3(-41,2.4,4),Vector3(-42,2.4,4),Vector3(-40,3.2,4),Vector3(-41,3.2,4),Vector3(-42,3.2,4)]:''' +s[end:]
s=s.replace('var value:float=island.width_fraction+.4*(island.high[1]-island.low[1])/root.get_visible_rect().size.y+.3*(reeds.high[1]-reeds.low[1])/root.get_visible_rect().size.y+.12*roof.width_fraction','var value:float=island.width_fraction+.5*(island.high[1]-roof.low[1])/root.get_visible_rect().size.y+.15*island.high[1]/root.get_visible_rect().size.y')
s=s.replace('compare_ziling_roof.gd','compare_ziling_axis.gd');(p/'godot/tests/compare_ziling_axis.gd').write_text(s)
folder=p/'axis-comparison';assert not folder.exists();folder.mkdir()
d=json.loads((p/'roof-command.json').read_text());d['command']=[v.replace('compare_ziling_roof.gd','compare_ziling_axis.gd').replace('roof-comparison','axis-comparison') for v in d['command']];d['status']='prepared';d.pop('exit_code');d.pop('log_sha256');(p/'axis-command.json').write_text(json.dumps(d,indent=2)+'\n')
