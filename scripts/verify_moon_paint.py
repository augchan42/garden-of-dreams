"""Verify saved native paint, UVs, shared image and calibrated moon factors."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from moon_paint_contract import check
parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
report=check();report.update(status='passed',scope='Native packed moon painting, projected UVs and calibrated source luminance; runtime, bakes and final art acceptance remain separate.')
args.report.write_text(json.dumps(report,indent=2)+'\n');print('MOON_PAINT_SOURCE_PASS',report)
