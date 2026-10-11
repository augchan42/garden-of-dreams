import sys,json
from pathlib import Path
root=Path('/tmp/garden-qiushuang-lattice-20261010');sys.path.insert(0,str(root))
from lattice_contract import inspect
name=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'baseline-rays.json'
report=inspect();(root/name).write_text(json.dumps(report,indent=2)+'\n')
print('LATTICE_SCREEN_RAYS',report['status'],report['blocked_samples'],'/',report['total_samples'],flush=True)
assert report['status']=='passed', 'Lattice blocks actual CRT phosphor quads'
