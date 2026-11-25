# Garden of Dreams asset storage

R2 asset storage is active and verified under the approved migration spec and plan. Git LFS still manages asset pointers and revisions. Storage uses the existing R2 bucket and a random subfolder inside the migration folder. Existing media objects and configuration are outside this migration's writes.

## Public storage and folder configuration

The owner approved public storage and reconfirmed permission for public asset uploads on 2026-10-25, conditional on URLs being difficult to guess. The migration uses a cryptographically random 256-bit folder component, saved only in private `R2_LFS_PREFIX` configuration and the Actions reader secret. The actual prefix and public object URLs must not appear in Git, public reports or workflow output. Collaborators receive the configuration separately. Both the adapter and reader issuer refuse a missing explicit prefix.

Anyone with an exact public object URL can read it. Random names prevent practical guessing; they do not provide authentication. R2's public endpoint does not provide root bucket listing ([Cloudflare documentation](https://developers.cloudflare.com/r2/buckets/public-buckets/)). No full public-route policy audit is claimed. Asset transport still uses authenticated S3 requests.

All 12,098 retained objects (21,519,155,652 bytes) completed upload and full GET/SHA-256 verification on 2026-10-24. The owner-authorized cleanup then removed exactly 4,893 earlier predictable-prefix copies (8,491,152,876 bytes); the old origin listing is empty and the previously public sample returns HTTP 404. GitHub assets, independent recovery copies and existing bucket media remain preserved. Publishing and final recovery acceptance subsequently passed, as recorded below.

## Verified recovery baseline

After refreshing remote branches, tags and all 36 PR heads, retained history contains 12,098 distinct LFS objects totaling 21,519,155,652 bytes. All local size/SHA-256 checks pass. Seven objects from the earlier 12,104-object baseline were reachable only through transient app checkpoint refs; all remain in the recovery copy. The published synthetic pilot adds one 4,151-byte object, recovered from its verified pilot checkout.

The recovery snapshot contains 12,882 objects (23,755,847,182 verified bytes), including 784 cache-only objects, plus a Git bundle. It is stored locally at `build/asset-storage-recovery/2026-10-24-baseline` in the primary project checkout. The restored bundle passed full Git fsck and all captured named refs match. `blender/authoring.blend` was restored from the copied LFS bytes and its SHA-256 matches.

This is a separate byte copy outside production R2 and the live LFS cache. It shares the workstation filesystem with the source, so it protects recovery from R2/account failure but does not provide an independent copy against workstation disk loss. No GitHub asset deletion or history rewriting is authorized by this migration.

The ignored worktree evidence directory `build/r2-migration/` contains the inventory, local verification, exact inventory delta, recovery summary and restore results. The auditor excludes transient `refs/codex/` app checkpoint names from retained ref stability checks; corresponding cache-only objects are preserved. Publishing refs, PR refs, tags and worktree heads remain in scope.

## Audit commands

```sh
python3 scripts/audit_lfs_storage.py inventory --refs all --output build/r2-migration/inventory.json
python3 scripts/audit_lfs_storage.py verify-local --report build/r2-migration/inventory.json --output build/r2-migration/local-verification.json
```

Every command writes an explicit report; verification never replaces the inventory. Incomplete inventories, changed refs and missing/corrupt objects prevent acceptance. The setup, profiles, publishing, CI and recovery instructions below describe the verified provider.

## Final ref and asset deltas

Capture a new full inventory whenever publishing refs change. A prior full readback report can support the next capture only when it contains a successful size/SHA-256 GET proof for every old OID. Delta planning identifies new bytes and records the baseline provider identity; copying that delta to another prefix/backend is refused.

```sh
python3 scripts/audit_lfs_storage.py inventory --refs all --output build/current-inventory.json
python3 scripts/audit_lfs_storage.py delta --report build/current-inventory.json --previous-inventory build/previous-inventory.json --verification build/previous-readback.json --output build/delta-inventory.json
python3 scripts/audit_lfs_storage.py copy --report build/delta-inventory.json --env-file /absolute/private/r2.env --output build/delta-readback.json
python3 scripts/audit_lfs_storage.py reconcile --report build/current-inventory.json --previous-inventory build/previous-inventory.json --verification build/previous-readback.json --delta-verification build/delta-readback.json --output build/current-readback.json
```

For code-only changes, the delta has zero objects: skip copying and omit `--delta-verification` when reconciling. Reconciliation composes the earlier full-GET evidence with actual full-GET proofs for new objects; it does not claim to download unchanged bytes again. The report records both source captures and proof fingerprints. A later ref change still returns `needs_delta`, so capture and reconcile again before cutover.

Delta inventories are explicitly partial. Recovery backup and further delta planning require a full retained-history inventory, so they cannot silently omit the previously verified history. Keep the original inventory, readback proof and recovery snapshot, including any objects no longer reachable from a later ref capture. No delta command deletes remote objects.

## Clone setup

Use Git LFS (tested 3.8.0), Python 3.11–3.14 and **rclone v1.75.0**. Obtain that rclone release from [the official release](https://github.com/rclone/rclone/releases/tag/v1.75.0), verify its archive checksum, and keep the executable outside the checkout. Bootstrap configures Git; it does not install these dependencies. The adapter rejects a different rclone version.

Before downloading assets:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/augchan42/garden-of-dreams.git
cd garden-of-dreams
python3 scripts/bootstrap_lfs_r2.py --env-file /absolute/private/r2.env --profile active
git lfs pull
python3 scripts/check_asset_checkout.py --profile active --strict
```

A fresh clone initially contains small pointer files. Bootstrap installs a content-versioned adapter under `~/.local/share/garden-lfs/` and records a private settings snapshot there. It changes only this clone's configuration and standard LFS hooks. Existing custom hooks or `core.hooksPath` cause an actionable refusal before settings change; integrate those hooks manually. The tool refuses linked worktrees because their configuration is shared: install once in their primary checkout at cutover. A user-owned hook must keep calling `git lfs pre-push` for upload failures to prevent publishing.

The private file accepts `.env` assignments or the reader JSON emitted by `mint_r2_reader.py`; both are parsed as data and never executed as shell code. Process environment values take precedence. Supply `R2_ASSETS_ACCOUNT_ID`, `R2_ASSETS_BUCKET`, `R2_ASSETS_ACCESS_KEY_ID`, `R2_ASSETS_SECRET_ACCESS_KEY` and, for temporary credentials, `R2_ASSETS_SESSION_TOKEN`. Existing maintainer machines can use the equivalent `R2_MEDIA_*` fields. `R2_LFS_PREFIX` must contain the exact privately supplied random project prefix; there is no default. Never copy its value into Git or public logs. The media key-prefix/public-URL settings are ignored by this adapter. Keep credential files outside Git; `.env` and `.env.*` are ignored. No credentials are stored in Git configuration or committed provider settings.

The `active` profile downloads `blender/**`, `export/**`, `godot/**` and `textures/**`; other historical reference assets can remain pointers. For all current-revision assets, rerun bootstrap with `--profile all`, then `git lfs pull`. This fetches the selected revision, not every historical version. The installed executable and clone-local settings survive checking out older commits that lack these scripts. Keep a current tooling checkout for offline preflight against such revisions:

```sh
python3 /absolute/tooling/scripts/check_asset_checkout.py --repo /absolute/older-clone --profile active --strict
```

The ordinary preflight permits edited asset bytes but rejects missing files and pointers. `--strict` additionally compares every selected file with its committed SHA-256 and size; it will intentionally reject local edits. Neither mode writes assets. Git retains its usual protection against switching branches over edited Blender/PNG files.

Bootstrap prints its settings snapshot path. To restore that clone's previous configuration/hooks:

```sh
python3 /absolute/tooling/scripts/bootstrap_lfs_r2.py --restore /absolute/settings-snapshot.json
```

Restore refuses later configuration or hook edits. Reconcile those edits manually; do not overwrite them. Restoring a GitHub provider setting does not restore GitHub LFS capacity.

## CI reader and integrity check

`asset-integrity.yml` runs checker code from the trusted base revision. It fetches PR Git objects without checking out or executing PR files, and fully downloads/hashes newly introduced historical pointer blobs, including intermediate assets removed before the PR tip. Secrets are available only to that verification step. No writer credential is sent to GitHub Actions.

Same-repository PRs run automatically through the registered workflow. A maintainer can also run **Asset integrity** from **main** with the PR number for forks, older stacked branches, or a missing status. Both automatic and manual runs for the demo source were verified to check out trusted main code. The workflow reports the `R2 asset integrity` status directly on the PR head. Authenticated asset verification is not provided to arbitrary fork code, GitHub archive downloads, or GitHub's asset previews; collaborators need reader access and the adapter.

Main requires `R2 asset integrity` from the GitHub Actions app, including for administrators. No human-review requirement was added.

The CI reader is scoped to the configured random project prefix and expires after 30 days. Renew the current reader before **23 November 2026, 10:11 Hong Kong time (02:11 UTC)**. A maintainer must renew it before expiry (or after parent-token rotation):

```sh
python3 scripts/mint_r2_reader.py --env-file /absolute/private/r2.env --ttl-seconds 2592000 --github-repository augchan42/garden-of-dreams
```

The helper derives a temporary reader locally and sends only that reader to the repository's `R2_LFS_READER` secret through stdin. It never sends the parent writer secret or prints credential values. For a private local reader file, use `--output /absolute/new-reader.json` instead; creation is exclusive with mode `0600`. That JSON file can be passed directly to bootstrap with `--env-file /absolute/new-reader.json`; its reader can hydrate assets but cannot publish new ones. The 30-day reader was accepted by the actual R2 endpoint. Its derivation follows [Cloudflare's temporary-credential protocol](https://developers.cloudflare.com/r2/api/s3/temporary-credentials/). Expired readers fail closed, so a missed renewal blocks integrity checks and requires maintainer action.

## Transfer and recovery rules

Objects are keyed by SHA-256 under `<privately-configured-prefix>/objects/sha256/<first-two-hex>/<oid>`. Upload source bytes and every completed download are checked against size and SHA-256. Existing mismatched remote data causes failure. There is no automatic GitHub fallback, delete operation or completed-object expiration. Transfers allow four objects per client, with 16 MiB multipart parts and two parts per object above 64 MiB. Interrupted multipart work is aborted; the large-file and interruption acceptance reports record actual endpoint behavior.

Preserve the independent recovery copy, its inventory and Git bundle. A recovery procedure must first restore the bundle into a separate clone, verify it with `git fsck --full`, and copy each required OID from `objects/<aa>/<bb>/<oid>` into that clone's LFS cache. Verify all copied hashes before `git lfs checkout`. This path works with production R2 disabled and does not require GitHub quota. A separately configured test backend can also be populated from these bytes through the same adapter. Verify settings snapshots and restore them only in the recovery clone.

Keep GitHub assets and the recovery copy for at least 30 days **and** two successful authoring/build/publishing cycles after cutover. Retirement is a later decision; this migration does not delete them or rewrite history. The project owner is responsible for keeping the recovery snapshot and should place another copy on independent storage to cover workstation disk loss. Restoring GitHub as the asset backend is conditional on sufficient LFS capacity.

## Published demo source

The four-minute demo source is published in [PR #39](https://github.com/augchan42/garden-of-dreams/pull/39), on `codex/demo-handoff-r2`. Its original local commit remains in history. The source PR stays stacked on the existing scene branch; earlier owner-managed security holds and PR #14 remain separate. The storage migration merged in [PR #37](https://github.com/augchan42/garden-of-dreams/pull/37).

For a fresh demo source checkout, clone that branch with smudging skipped, then use the setup steps above:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --branch codex/demo-handoff-r2 https://github.com/augchan42/garden-of-dreams.git
```

Before each publishing session, commit the intended source, capture its full inventory and create a new verified recovery snapshot with `audit_lfs_storage.py backup`. Then use ordinary `git push`; the installed LFS pre-push hook uploads through R2 and blocks the push on failure. Keep new refs and asset bytes backed up during the recovery period.

## Recovery and retention

The latest full asset snapshot is `build/asset-storage-recovery/2026-10-26-pre-source-publication` in the primary checkout: **12,884 objects / 23,755,850,913 verified bytes**, including 784 cache-only objects. Its `verification.json`, `inventory.json`, `refs.bundle` and `objects/` form the recovery package. Later code-only publishing refs are preserved in additional verified bundles; the final local handoff identifies the latest one.

[Recovery instructions](asset-storage-recovery.md) cover full hash verification, restoring Git refs and materializing assets without R2 or GitHub LFS capacity. The actual disaster test denied all network access, removed production credentials, restored both post-switch objects and the demo source ref, exercised normal Git LFS fetch/checkout and a local push, and restored the temporary settings snapshot.

Keep GitHub assets and every recovery snapshot for at least 30 days **and** two successful authoring/build/publishing cycles after cutover. Keep them through at least **25 November 2026**, and longer until the cycle condition is met. Retirement needs a later owner decision. Recovery copies share the workstation disk; copy the recovery package to independent storage for disk-loss protection. Keep private provider configuration separately in secure storage.

## Acceptance status

All **12,100 retained objects / 21,519,159,383 bytes** have full GET/SHA-256 evidence: the initial 12,098-object readback plus the two verified publishing-test objects. Fresh R2-only main/demo/older checkouts, strict hashes, provenance checks, six linked Blender loads, cold Godot imports, older all-profile hydration and the offline desktop demo passed. The final main preflight also passed offline.

The demo Android staging fix passed native export and exact finalized payload verification: an 86,957,124-byte diagnostic APK and 177 bound texture imports. The accepted graphical inventory contains 167 meshes and 178 textures. The earlier empty inventory is rejected evidence. Subsequent changes added preflight guards and storage integration while preserving runtime and asset bytes; no target-phone certification is claimed.

One independent review found two important issues, both fixed with failing regressions followed by passing suites. The migration suite passed 73 tests; the combined source suite passed 97. Completion-audit regressions also cover both official legacy headers and accepted ASCII/Unicode outer whitespace, using the installed Git LFS parser to validate every fixture. Inventory, history CI and ordinary preflight share the same read-only framing logic. No critical or deferred minor findings remain.

Live CI rejected the intentionally missing object, then passed both historical objects after normal publishing. A read-only normal push failed without changing the GitHub ref or creating the object. A fresh GitHub clone failed closed before setup, then retrieved both revisions using only the scoped reader. The source PR's trusted CI verified all ten introduced asset objects. Workflow logs were checked for private prefix/credential disclosure.

The [public acceptance summary](reference/r2-migration-20261025/acceptance.json) records these results and workflow links. Detailed reports and original failures remain in the tooling checkout's ignored `build/r2-migration/`; the local handoff contains the selected nonsecret evidence and final ref receipt. Existing media settings, GitHub asset bytes, user edits and security holds remain preserved. No further asset deletion or history rewrite was performed.
