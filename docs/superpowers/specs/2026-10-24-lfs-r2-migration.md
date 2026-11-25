# Garden of Dreams asset storage migration


**Owner ruling (2026-10-24):** Public storage in the existing bucket is approved if URLs are difficult to guess. Use a cryptographically random 256-bit subfolder within the migration folder. Keep its value in private configuration and the Actions reader secret, never Git or public logs. After full replacement verification, remove only the earlier predictable-prefix migration copies, as explicitly authorized. Preserve GitHub assets, recovery copies and all existing media.
**Owner reconfirmation (2026-10-25):** Public asset uploads are authorized. The random-folder and private-configuration requirements remain in effect; a private-bucket access gate is no longer applicable.

Status: migration functional acceptance verified on 2026-10-26. The migration PR is merged, the demo source is published, and live CI, publishing and offline recovery passed. See `docs/asset-storage.md` and the public acceptance summary for results; original contracts and baseline evidence below are retained.

## Outcome

Move development asset storage from GitHub LFS to Cloudflare R2 with owner-approved public storage through a standalone Git LFS transfer adapter. Preserve existing Git commits, LFS pointers, authoring assets, generated assets, provenance records and working-tree paths. A fresh checkout must recover its correct assets and build the offline desktop demo without downloading asset bytes from GitHub LFS.

GitHub continues to host ordinary Git data. Git LFS continues to manage revisions, filters and upload hooks. Packaged games continue to contain local files.

## Established evidence

At local demo commit `3d4e4fe96108c1ec3f948767c7f14fc6a16171ce`, the captured locally reachable inventory contains 12,104 LFS objects, 21,538,909,700 bytes. Every object passed full local size/SHA-256 validation. This is a baseline, not a final inventory of refreshed remote refs or an independent backup.

Evidence: `build/asset-storage-migration-baseline/inventory.json` and `local-sha256-validation.json`.

The live pilot passed a new synthetic R2-only upload, normal GitHub push, fresh GitHub clone with empty LFS cache and byte-identical recovery, and rejection of an ordinary push when upload fails. Eleven prototype protocol tests pass. Evidence is in `build/r2-adapter-smoke/status.json`, `live-status.json` and their per-command logs. Published pilot branch: `codex/r2-adapter-smoke-96bdb521b4e7`.

Both `.env` credential sets (`CF_*`, `R2_MEDIA_*`) verify as active account API tokens and passed S3 upload/readback/delete probes in the configured media bucket. Account-level bucket listing and automatic bucket creation are not authorized by those observed permissions. The rclone transport needs `no_check_bucket=true`. Credentials must be loaded privately; no secret values belong in source, configuration committed to Git, reports or logs.

The pilot uses a reserved `.invalid` external URL and a small object. It does not establish production onboarding, bucket privacy, multipart recovery, full-history coverage or full builds. Do not rerun the successful small pilot without changed inputs; validate those remaining cases directly.

## Storage and transfer contract

- Use the existing R2 bucket with a random 256-bit subfolder inside the migration folder. Keep the exact configured prefix out of Git/public output and refuse missing configuration. This is public storage with unguessable names, not authenticated confidentiality. Preserve existing media objects/configuration. Earlier403 probes did not establish privacy; a browser-agent full GET established public accessibility. The owner approved it with the random-folder condition.
- Use keys `objects/sha256/<first-two-hex>/<full-oid>` under one explicit configured project prefix. Completed objects are immutable. No adapter delete command or completed-object expiration.
- Base production code on the proven Python/rclone prototype. Pin the supported Python and rclone versions. Use bounded transfers: at most four objects concurrently, multipart above 64 MiB with 16 MiB parts and two parts concurrently per object.
- Validate OID syntax and expected size; hash uploads before transfer, hash existing objects before treating them as present, and hash downloads/readbacks before reporting success. ETags are not content hashes.
- Distinguish absent S3 keys, virtual directories, authorization failures and corruption. Download into temporary files; a failure must never leave usable partial bytes in the LFS cache. Failed multipart uploads must be aborted or covered by an explicitly verified abandoned-upload cleanup policy.
- Report only JSON-lines protocol messages on stdout. Redact private configuration and credentials from diagnostics. Provide no automatic fallback to GitHub LFS.
- Install the versioned adapter outside the checkout. Configure each clone locally, preserving existing hooks and settings. Do not silently change global Git configuration.
- Commit a stable owned HTTPS external-provider identifier with setup instructions. Verify the final URL/configuration through GitHub, including an unconfigured clone; the pilot's `.invalid` URL is not the production configuration.

## Migration and backup contract

Refresh and capture all retained remote/local branches, tags, relevant PR refs and worktree/unpushed commits. Enumerate each distinct OID with its expected size. Preserve cache-only objects in recovery storage until their ownership is resolved. Exclude unrelated `output/` files from migration unless separately requested.

Create and verify a recovery copy containing Git refs and asset bytes outside the production R2 bucket. Record its location and failure domain; the live cache and a Git bundle alone are insufficient. Restore a sample before changing the default provider. Ask for a backup destination if none suitable is available.

Copy objects without changing the current provider, then GET every retained object from R2 and recompute its size and SHA-256. Capture a final ref delta before switching writers. Every retained OID must have explicit verified coverage; zero unexplained gaps.

Before every publishing session during the recovery period, back up new refs/OIDs and verify their recovery copies. Keep GitHub history and recovery copies for at least 30 days and two successful build/recovery cycles. Retirement is a later decision; do not keep this execution goal running for that retention interval.

## Authoring, builds and publication

Support `active` (blender/export/godot/textures) and `all` asset profiles. Preflight must identify unresolved pointers and missing files without overwriting locally edited assets. Strict mode additionally hashes materialized bytes against the selected revision.

Test clean current/demo, main and an older revision using empty caches and R2 only. Test branch switches, revisions without bootstrap files, dirty asset protection, read-only credentials, missing/corrupt objects and a failed upload blocking normal Git push. Verify linked Blender assets, existing provenance checks, cold Godot import, and an offline desktop demo build/launch in disposable processes/checkouts. Leave the user's open editors alone.

Add a read-only CI integrity check for OIDs introduced anywhere in new history, including assets introduced then removed in the same PR. Run trusted checker code with bucket-scoped reader credentials; untrusted PR code must not execute with secrets. Document preview/archive limitations for externally stored assets.

Publish the migration changes, update actively publishing clones/branches, and publish the currently local demo handoff commit using the R2 workflow. Existing GitGuardian findings remain user-owned and PR14 retains its independent hold; migration must not bypass those checks or require their unrelated resolution to pass its own acceptance.

## Recovery and completion

Prove recovery of a new post-switch object and its Git refs while the production R2 destination is unavailable. Restore into a disposable recovery backend/clone and verify exact bytes. Document restoration to GitHub as an option requiring available GitHub LFS capacity; the current quota must not make recovery testing circular or require a new purchase.

Complete when production storage/configuration is switched, all retained assets are verified in R2 and recovery storage, clean authoring/build/new-push workflows pass, the demo source is published, CI/setup/recovery documentation is delivered, and the migration PR has passed its own required checks and merged. Report any external access blocker precisely; never substitute a pilot result for full migration acceptance.

## Outside this goal

Removing the Git LFS client; rewriting Git history; deleting GitHub assets/repository; requesting a purge; full-garden art/performance work; broad platform certification; notarization; and waiting 30 days to retire old storage.
