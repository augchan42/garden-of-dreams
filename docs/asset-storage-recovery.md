# Recovering Garden of Dreams assets

Use a separate recovery directory and the preserved snapshot; the production bucket and GitHub LFS capacity are unnecessary. Keep the original snapshots unchanged. The local handoff names the latest asset snapshot and any later code-only refs bundle.

First verify the snapshot using its own `verification.json`, which contains expected object sizes/hashes and the original bundle hash. This check uses no live cache or credentials:

```sh
export GARDEN_RECOVERY_SNAPSHOT=/absolute/path/to/asset-snapshot
python3 - <<'PYTHON'
import hashlib, json, os
from pathlib import Path
snapshot = Path(os.environ['GARDEN_RECOVERY_SNAPSHOT'])
manifest = json.loads((snapshot / 'verification.json').read_text())
assert manifest['status'] == 'passed'
def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()
assert digest(snapshot / 'refs.bundle') == manifest['bundle_sha256']
for item in manifest['objects']:
    oid = item['oid']
    path = snapshot / 'objects' / oid[:2] / oid[2:4] / oid
    assert path.stat().st_size == item['size'] and digest(path) == oid
print('Recovery snapshot verified:', len(manifest['objects']), 'objects')
PYTHON
```

Restore the latest refs bundle into a fresh mirror, run full Git integrity verification, then create a working clone. The published demo commit is preserved as `refs/migration/demo-handoff-r2` in the captured bundle:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --mirror /absolute/path/to/latest/refs.bundle /absolute/path/to/recovery.git
git --git-dir=/absolute/path/to/recovery.git fsck --full
GIT_LFS_SKIP_SMUDGE=1 git clone /absolute/path/to/recovery.git /absolute/path/to/recovered
GIT_LFS_SKIP_SMUDGE=1 git -C /absolute/path/to/recovered fetch origin refs/migration/demo-handoff-r2
GIT_LFS_SKIP_SMUDGE=1 git -C /absolute/path/to/recovered checkout --detach FETCH_HEAD
```

Copy the verified snapshot objects into that clone's LFS cache, preserving the `objects/<aa>/<bb>/<oid>` layout. Verify each copied file against the manifest before running `git lfs checkout`. An existing mismatched cache file is a failure: use a fresh recovery clone rather than overwriting evidence. Run the recovered source's `scripts/check_asset_checkout.py --profile active --strict` after materialization. Git LFS checkout uses local cached bytes and needs no remote download.

For temporary adapter-based recovery, configure an explicit separate local rclone backend and install the adapter only in the disposable clone. This path was tested with all network denied: both new post-switch objects restored from the independent snapshot, normal LFS fetch/checkout, a normal push of a backed-up local-only test object to a local bare Git origin, and exact settings restoration. The test object was never sent to GitHub or production R2.

Restore temporary settings with `bootstrap_lfs_r2.py --restore /absolute/settings-snapshot.json`. It refuses later configuration/hook edits so those edits can be reconciled explicitly. Restoring GitHub as the online provider requires sufficient GitHub LFS capacity. The stored copies share the workstation filesystem; a separate-device copy is needed for disk-loss protection.
