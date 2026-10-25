# Garden of Dreams R2 Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for execution in this chat. Steps use checkbox syntax for tracking. The user assigns the goal separately; this document does not start execution.

**Goal:** Switch asset storage to owner-approved public R2 with random folder names, preserve exact history and asset bytes, and prove clean builds, publishing and recovery.

**Architecture:** Keep Git LFS pointers and filters. Install a versioned Python/rclone standalone adapter outside each checkout, with clone-local configuration and a committed external-provider identifier. Inventory, transfer and readback verification precede switching writers.

**Tech Stack:** Python, pinned rclone/S3 transport, installed Git LFS 3.8.0 baseline, GitHub Actions, existing Blender/Godot build checks.

**Spec:** `docs/superpowers/specs/2026-10-24-lfs-r2-migration.md` is authoritative. The 2026-10-23 proposal is historical context. This plan supersedes its unproven pilot status, boto3 implementation choice and requirement to demonstrate rollback through the currently quota-blocked GitHub backend.

## Current destination gate

The owner approved public storage conditional on difficult-to-guess URLs. Generate a cryptographically random 256-bit subfolder in the existing migration folder, keep it only in private configuration and the reader secret, and require explicit prefix configuration. Resume copy and complete all verification gates. Earlier predictable-prefix migration copies may be removed only after their replacements pass full hash verification; this specific cleanup is authorized. Preserve existing media and all GitHub/recovery bytes.
## Global constraints

- Preserve Git history, pointers, working paths, asset bytes and frozen reference evidence.
- User-directed existing bucket with a random migration subfolder configured privately; preserve existing media data/configuration.
- No credentials in Git or diagnostics; `.env` remains ignored.
- No delete command, completed-object expiration, global Git config changes or automatic GitHub fallback.
- Four concurrent objects maximum; multipart above 64 MiB, 16 MiB parts, two parts per object.
- Verify every retained object by complete GET and SHA-256, plus a recovery copy of refs and bytes outside the production bucket.
- Keep the current provider until migration verification passes. Record and verify the final ref delta.
- Preserve user edits, open editors, `output/`, existing security holds and PR14's independent scope.
- Finish at verified switch/handoff; GitHub asset retirement and the 30-day retention interval are later work.

## Review focus

- S3 missing keys can appear as empty successful cat output or virtual directories: explicit object detection and integrity verification (Task 2).
- New objects introduced and removed between commits must still be retained and checked (Tasks 1, 5).
- Old revisions lack the bootstrap files: installed executable and clone settings must survive switching revisions (Tasks 2, 4).
- Dirty Blender/PNG files must keep Git's overwrite protection (Task 4).
- Recovery cannot depend on spare GitHub LFS quota or live production R2 access (Tasks 1, 6).

## Files and interfaces

| Path | Responsibility |
| --- | --- |
| `scripts/audit_lfs_storage.py` | Inventory refs/OIDs, local hashes, backup/copy/readback reports |
| `scripts/lfs_r2_transfer.py` | Validated JSON-lines protocol and immutable transport |
| `scripts/bootstrap_lfs_r2.py` | Versioned installation outside checkout; local config, hooks, rollback snapshot |
| `scripts/check_asset_checkout.py` | Offline active/all preflight, optional strict hashes |
| `scripts/tests/test_lfs_storage_audit.py` | Enumeration, historical coverage and resumable-copy failures |
| `scripts/tests/test_lfs_r2_transfer.py` | Protocol, integrity, S3 edge cases and actual Git integration |
| `scripts/tests/test_asset_checkout.py` | Pointers, missing/dirty assets and strict verification |
| `.lfsconfig`, `.gitignore` | Nonsecret provider identity and credential-file exclusion |
| `.github/workflows/asset-integrity.yml` | Trusted, read-only checks of newly introduced history |
| `docs/asset-storage.md`, `README.md`, `docs/godot-import.md` | Setup, profile selection, diagnostics and recovery |
| Existing build entry points | Call preflight without weakening provenance checks |

Evidence reports use schema version 1, captured ref→commit mappings, unique `{oid,size}` objects and per-OID status/errors. Consumers must reject incomplete reports or changed refs without explicit delta processing.

## Task 1: Inventory and recovery baseline

**Consumes:** existing local inventory/hash reports. **Produces:** refreshed inventory, full local verification, verified recovery location/report.

- [x] Write failing `test_deduplicates_oids`, `test_retains_old_branch_object`, `test_retains_intermediate_commit_object`, `test_incomplete_inventory_fails` and `test_corrupt_local_object_fails`.
- [x] Run `python3 -m unittest discover -s scripts/tests -p 'test_lfs_storage_audit.py'`; observe failures before implementation.
- [x] Implement `audit_lfs_storage.py inventory --refs all --output REPORT` and `verify-local --report REPORT`; capture retained branches/tags/PR/worktree refs and separately list cache-only objects. Refresh ordinary remote refs without overwriting local work.
- [x] Run tests to green, capture a complete hashed inventory, and compare with the verified 12,104-object/21,538,909,700-byte baseline. Explain every delta.
- [x] Create the recovery copy of refs and asset bytes outside production R2, record its failure domain and restore a sample. Identify an unavailable backup destination as an access blocker before switching storage.
- [x] Commit inventory tooling/tests/documentation; keep large reports and backup payloads out of ordinary Git.

**Acceptance:** every retained OID is accounted for; backup sample recovery verifies exact bytes.

## Task 2: Production adapter and installation

**Consumes:** prototype and live evidence under `build/r2-adapter-smoke/`. **Produces:** installed adapter/bootstrap, tested versions and local settings snapshot.

- [x] Add failing tests for malformed requests, zero-byte objects, virtual directories, missing/corrupt/read-only objects, interrupted transfers, duplicate/concurrent uploads, failed readback, multipart failure cleanup and redacted errors.
- [x] Run `python3 -m unittest discover -s scripts/tests -p 'test_lfs_r2_transfer.py'`; observe the relevant failures.
- [x] Implement the spec's protocol/integrity contract using Python/rclone. Configure existing-bucket access with `no_check_bucket=true`; map missing keys explicitly and stream hashes. Pin actual supported versions and transfer settings.
- [x] Implement `bootstrap_lfs_r2.py --profile active|all` with versioned installation outside checkout, private credential loading, clone-local settings and preserved hooks/core.hooksPath. Existing hooks must be chained or left intact with an actionable setup error.
- [x] Use existing R2_MEDIA object credentials for the privately configured random prefix. Account admin permission/bucket creation is unnecessary. Record public access and random-folder configuration without publishing its value.
- [ ] Test the final owned HTTPS provider identifier and installation with a new R2-only object, normal GitHub push and fresh empty-cache clone. Exercise a file above 64 MiB and interrupted upload. Reuse the passing synthetic pilot for unchanged basic cases.
- [x] Run tests to green and commit adapter/bootstrap/setup changes.

**Acceptance:** final configuration, large-object integrity, failed-upload blocking and old-revision executable availability all pass; no production default switched yet.

## Task 3: Copy and verify retained history

**Consumes:** Task 1 inventory and Task 2 transport. **Produces:** per-OID full remote verification and recovery coverage reports.

- [x] Add failing tests for partial copy/resume, shared OIDs, absent source bytes, remote corruption and refs changing during copying; run the audit test command and observe failures.
- [x] Implement `copy --report REPORT`, `verify-remote --report REPORT` and delta processing in `audit_lfs_storage.py`, using the same validated transfer functions as the adapter.
- [x] Run tests to green. Copy all retained OIDs into the approved existing bucket/random folder without changing production settings; bound object concurrency to four.
- [x] GET every migrated object, hash all bytes and compare size/OID. Retain explicit failures; no HEAD-only success counts.
- [ ] Capture refs again, copy/readback-verify every delta and update recovery copies. Record uploaded/read-back byte totals and zero unexplained gaps.
- [ ] Commit the tooling and a concise nonsecret evidence summary, preserving original reports.

**Acceptance:** complete retained history is verified in R2 and recovery storage.

## Task 4: Clean authoring and offline builds

**Consumes:** verified R2 inventory and installed adapter. **Produces:** cold-checkout/build acceptance.

- [x] Write failing `test_missing_asset`, `test_pointer_stub`, `test_dirty_asset_allowed`, `test_strict_hash_mismatch` and `test_selective_checkout`; run `python3 -m unittest discover -s scripts/tests -p 'test_asset_checkout.py'`.
- [x] Implement `check_asset_checkout.py --profile active|all [--strict]` as a read-only offline check; integrate with `verify_assets.py`, `verify_godot_reimport.py`, `build_android_profile.py` and `build_demo_handoff.py` without removing existing provenance checks.
- [x] Run tests to green. Restore main, the local demo commit and an older source/bake revision into disposable checkouts with empty caches and R2-only asset downloads. Verify strict hashes; test dirty branch switching, selective/full profiles and missing credentials.
- [ ] Run existing asset/provenance checks, linked Blender loading, cold Godot imports, offline desktop demo build/launch and existing Android export/payload checks where supported. Record unrelated portability failures separately; do not expand into full-garden certification.
- [ ] Commit preflight integration and accurate setup/build limitations.

**Acceptance:** correct revision bytes, protected local edits and a working offline demo from R2-only hydration.

## Task 5: CI and switch active publishing

**Consumes:** complete verified history and clean-build evidence. **Produces:** final provider configuration, trusted CI and normal new publishing through R2.

- [x] Add a test where an asset exists in an intermediate new commit but is removed at the tip, plus missing/corrupt OID failures. Observe failures, then implement full newly introduced history enumeration and readback checks.
- [x] Add `.github/workflows/asset-integrity.yml` with trusted checker code and reader credentials. Untrusted PR code must not execute with secrets; provide a maintainer-run path for forks.
- [ ] Verify valid and deliberately missing objects against the actual workflow. Configure the required check where permissions permit; document any unavailable repository setting.
- [ ] Coordinate the final asset-write pause, capture and verify deltas, then apply the final `.lfsconfig` and clone-local setup. Update actively publishing branches/clones without overwriting dirty assets.
- [ ] Publish the currently local demo handoff source through R2. Keep dependency GitGuardian findings user-owned and PR14 independent; create/attach the appropriate PR without bypassing checks.
- [ ] Commit/push the migration PR with concrete acceptance evidence and merge when its own checks pass. Use merge commits as previously requested.

**Acceptance:** ordinary new upload/push, empty-cache clone and trusted CI work with the production provider.

## Task 6: Recovery, review and handoff

**Consumes:** a new post-switch object/ref and independent recovery bytes. **Produces:** verified recovery and final handoff.

- [ ] Make production R2 unavailable only to a disposable recovery clone, restore the new object and refs from recovery storage into a separate test backend, and verify exact bytes. Restore settings snapshots in that clone and demonstrate its Git workflow.
- [ ] Document GitHub restoration as conditional on available LFS capacity. Do not require increasing quota to pass recovery acceptance.
- [ ] Perform one independent final code/evidence review, fix material issues and run affected checks. Confirm all spec acceptance conditions against actual reports.
- [ ] Deliver setup, bootstrap, profile selection, evidence and recovery instructions. Record the 30-day/two-cycle retention rule and backup responsibility; GitHub purge/retirement remains a later user decision.

**Acceptance:** storage migration is complete, the demo source is publishable, recovery is demonstrated, and remaining retirement/access limitations are explicit.

## Self-review

Spec coverage: Tasks 1/3 cover inventory and backup; Task 2 covers transfer/bootstrap and final identity; Task 4 covers authoring/builds; Task 5 covers CI/publication; Task 6 covers recovery/retention/handoff. Reports and CLI names are shared consistently. Review-focus cases have explicit tests in their owning task. No production migration task is marked complete from the small pilot alone.
