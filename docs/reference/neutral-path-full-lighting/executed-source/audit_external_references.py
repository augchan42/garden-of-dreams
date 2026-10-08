"""Record collected reference slot and byte coverage for the fourteen site sheets.

This checks saved metadata and hashes; source attribution and visual relevance
still require direct review. Production painting is not an external reference.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--require-all', action='store_true')
args = parser.parse_args()
slugs = set(json.loads((ROOT / 'export/manifest.json').read_text())['sites']) - {'stage'}
sheets = [ROOT / 'docs/sites' / (slug + '.md') for slug in sorted(slugs)]
assert len(sheets) == 14
report = {'scope': 'Saved external reference metadata, unique slots and original-byte integrity; direct attribution/relevance review remains separate.',
          'expected_sites': 14, 'expected_references': 42, 'collected_references': 0, 'sites': {}}
for sheet in sheets:
    folder = ROOT / 'docs/reference/external' / sheet.stem
    index = folder / 'sources.json'
    records = json.loads(index.read_text()) if index.exists() else []
    slots, digests, sources = set(), set(), set()
    for record in records:
        slot = record['reference_slot']
        assert slot in (1, 2, 3) and slot not in slots, ('Duplicate or invalid slot', sheet.stem, slot)
        path = folder / record['local_file']
        assert path.resolve().parent == folder.resolve()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == record['sha256'] and digest not in digests
        if 'commons_sha1' in record:
            assert hashlib.sha1(data).hexdigest() == record['commons_sha1']
        assert record['source_page'].startswith('https://') and record['source_page'] not in sources
        assert record['photographer'] and record['license'] and record['license_url'].startswith('https://')
        assert record['visual_review'] and record['changes']
        slots.add(slot)
        digests.add(digest)
        sources.add(record['source_page'])
    report['collected_references'] += len(records)
    report['sites'][sheet.stem] = {'site_sheet_sha256': hashlib.sha256(sheet.read_bytes()).hexdigest(),
        'collected_slots': sorted(slots), 'missing_slots': sorted({1, 2, 3} - slots),
        'sources_sha256': hashlib.sha256(index.read_bytes()).hexdigest() if index.exists() else None}
report['complete_slot_coverage'] = report['collected_references'] == 42
(ROOT / 'export/external-reference-coverage.json').write_text(json.dumps(report, indent=2) + '\n')
print('EXTERNAL_REFERENCE_COVERAGE', report['collected_references'], '/', report['expected_references'])
if args.require_all:
    assert report['complete_slot_coverage'], 'External reference collection is incomplete'
