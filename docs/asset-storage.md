# Garden of Dreams asset storage

Migration is in progress under the approved 2026-10-24 spec and plan. Git LFS still manages asset pointers and revisions; the intended storage is the existing R2 bucket under the new root prefix `garden-of-dreams-lfs/`. Existing media objects and configuration are outside this migration's writes.

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
