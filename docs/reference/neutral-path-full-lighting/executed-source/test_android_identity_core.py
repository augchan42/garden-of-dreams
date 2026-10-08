"""Exercise cancellation races and independent request-signature vectors on JVM."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--java-home', type=Path, default=Path('/Applications/Android Studio.app/Contents/jbr/Contents/Home'))
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args()
fixture = Path(tempfile.mkdtemp(prefix='garden-identity-core-'))
package = ROOT / 'native/android/identity/src/main/java/ai/eightbitoracle/garden/identity'
tests = ROOT / 'native/android/identity/src/test/java/ai/eightbitoracle/garden/identity'
sources = [package / 'AttemptGate.java', package / 'RequestSigner.java', *sorted(tests.glob('*.java'))]
commands = [[str(args.java_home / 'bin/javac'), '--release', '17', '-d', str(fixture), *map(str, sources)]]
commands += [[str(args.java_home / 'bin/java'), '-cp', str(fixture), 'ai.eightbitoracle.garden.identity.' + name]
             for name in ['IdentityCoreTest', 'RequestSignerTest']]
report = {'scope': 'JVM callback race/signing core only; Android Keystore, provider UI, Godot registration, server exchange and history untested.',
          'source_files_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, 'phases': []}
for command in commands:
    result = subprocess.run(command, capture_output=True, text=True)
    report['phases'].append({'command': command, 'exit_code': result.returncode, 'output': result.stdout + result.stderr})
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    if result.returncode: raise SystemExit(result.returncode)
report['status'] = 'passed'
args.report.write_text(json.dumps(report, indent=2) + '\n')
print('ANDROID_IDENTITY_CORE_PASS: 8 cancellation/publication assertions, 4 independent signing assertions')
