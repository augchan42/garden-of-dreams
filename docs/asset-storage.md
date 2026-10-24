# Garden of Dreams asset storage

Migration is in progress under the approved 2026-10-24 spec and plan. Git LFS still manages asset pointers and revisions; the intended storage is the existing R2 bucket under the new root prefix `garden-of-dreams-lfs/`. Existing media objects and configuration are outside this migration's writes.

## Destination access gate — unresolved

The configured media endpoint exposes `garden-of-dreams-lfs/` publicly. An unauthenticated GET with a browser user agent returned the full 2,129-byte retained object with its exact SHA-256. Earlier HTTP403 probes using Python's default user agent did not prove privacy. No public response body or credentials are stored in the evidence.

The historical writer and queued cold builds were stopped before provider cutover. Completed objects remain in the existing bucket; interrupted multipart work was aborted and the follow-up listing found zero incomplete uploads. Existing media settings and the active Git provider are unchanged. The full historical readback and R2-only build gates have not passed.

The user must resolve the destination: provide a private bucket/object access, restrict and verify every public route to the new prefix, or explicitly approve public asset storage. A new folder alone has not provided privacy on this endpoint. The current object credentials also return403 when reading managed/custom-domain settings, so no full bucket-policy audit is claimed. The configured endpoint is not a managed `r2.dev` hostname; its exact serving policy is outside the available management permissions.

For a separate private bucket, add `R2_ASSETS_ACCOUNT_ID`, `R2_ASSETS_BUCKET`, `R2_ASSETS_ACCESS_KEY_ID` and `R2_ASSETS_SECRET_ACCESS_KEY` to the private configuration file. Keep the existing media fields for their existing purpose. Validate the destination before restarting the copy; never infer privacy from one user agent's403 response.

Evidence: `build/r2-migration/public-asset-full-hash-proof.json`, `public-destination-stop.json`, `multipart-after-stop.json` and `bucket-privacy-evidence.json` in the migration checkout. The active goal remains incomplete.

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

Every command writes an explicit report; verification never replaces the inventory. Incomplete inventories, changed refs and missing/corrupt objects prevent acceptance. Build/profile/bootstrap and final provider instructions will be added with their implementation and actual verification.

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

Before downloading private assets:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/augchan42/garden-of-dreams.git
cd garden-of-dreams
python3 scripts/bootstrap_lfs_r2.py --env-file /absolute/private/r2.env --profile active
# Run after the migration cutover is recorded below:
git lfs pull
python3 scripts/check_asset_checkout.py --profile active --strict
```

A fresh clone initially contains small pointer files. Bootstrap installs a content-versioned adapter under `~/.local/share/garden-lfs/` and records a private settings snapshot there. It changes only this clone's configuration and standard LFS hooks. Existing custom hooks or `core.hooksPath` cause an actionable refusal before settings change; integrate those hooks manually. The tool refuses linked worktrees because their configuration is shared: install once in their primary checkout at cutover. A user-owned hook must keep calling `git lfs pre-push` for upload failures to prevent publishing.

The private file is parsed as data, never executed as shell code. Supply `R2_ASSETS_ACCOUNT_ID`, `R2_ASSETS_BUCKET`, `R2_ASSETS_ACCESS_KEY_ID`, `R2_ASSETS_SECRET_ACCESS_KEY` and, for temporary credentials, `R2_ASSETS_SESSION_TOKEN`. Existing maintainer machines can use the equivalent `R2_MEDIA_*` fields. `R2_LFS_PREFIX=garden-of-dreams-lfs` selects the new root namespace; media key-prefix/public-URL settings are ignored by this adapter. Keep credential files outside Git; `.env` and `.env.*` are ignored. No credentials are stored in Git configuration or committed provider settings.

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

Same-repository PRs run automatically. For forks, a maintainer runs **Asset integrity** from **main** with the PR number. The workflow reports the `R2 asset integrity` status directly on the PR head. Private asset verification is not provided to arbitrary fork code, GitHub archive downloads, or GitHub's asset previews; collaborators need reader access and the adapter.

The current CI reader is scoped to `garden-of-dreams-lfs/` and expires after 30 days. A maintainer must renew it before expiry (or after parent-token rotation):

```sh
python3 scripts/mint_r2_reader.py --env-file /absolute/private/r2.env --ttl-seconds 2592000 --github-repository augchan42/garden-of-dreams
```

The helper derives a temporary reader locally and sends only that reader to the repository's `R2_LFS_READER` secret through stdin. It never sends the parent writer secret or prints credential values. For a private local reader file, use `--output /absolute/new-reader.json` instead; creation is exclusive with mode `0600`. The 30-day reader was accepted by the actual R2 endpoint. Its derivation follows [Cloudflare's temporary-credential protocol](https://developers.cloudflare.com/r2/api/s3/temporary-credentials/). Expired readers fail closed, so a missed renewal blocks integrity checks and requires maintainer action.

## Transfer and recovery rules

Objects are keyed by SHA-256 under `garden-of-dreams-lfs/objects/sha256/<first-two-hex>/<oid>`. Upload source bytes and every completed download are checked against size and SHA-256. Existing mismatched remote data causes failure. There is no automatic GitHub fallback, delete operation or completed-object expiration. Transfers allow four objects per client, with 16 MiB multipart parts and two parts per object above 64 MiB. Interrupted multipart work is aborted; the large-file and interruption acceptance reports record actual endpoint behavior.

Preserve the independent recovery copy, its inventory and Git bundle. A recovery procedure must first restore the bundle into a separate clone, verify it with `git fsck --full`, and copy each required OID from `objects/<aa>/<bb>/<oid>` into that clone's LFS cache. Verify all copied hashes before `git lfs checkout`. This path works with production R2 disabled and does not require GitHub quota. A separately configured test backend can also be populated from these bytes through the same adapter. Verify settings snapshots and restore them only in the recovery clone.

Keep GitHub assets and the recovery copy for at least 30 days **and** two successful authoring/build/publishing cycles after cutover. Retirement is a later decision; this migration does not delete them or rewrite history. The project owner is responsible for keeping the recovery snapshot and should place another copy on independent storage to cover workstation disk loss. Restoring GitHub as the asset backend is conditional on sufficient LFS capacity.

## Acceptance status

Migration is still in progress. Full historical upload/readback, clean revision builds, production provider cutover, actual workflow acceptance and final recovery evidence remain gates. The passing small pilot is not the migration completion report.
