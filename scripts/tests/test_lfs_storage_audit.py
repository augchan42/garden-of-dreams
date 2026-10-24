"""Real Git histories exercise inventory completeness and recovery integrity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'audit_lfs_storage.py'
if MODULE.exists():
    spec = importlib.util.spec_from_file_location('audit', MODULE)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
else:
    audit = None


class GitFixture(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(audit, 'Storage inventory implementation is missing')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Storage tests')
        self.git('config', 'user.email', 'tests@localhost.invalid')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, stderr=subprocess.DEVNULL).decode().strip()

    def pointer(self, name, body=b'alpha'):
        oid = hashlib.sha256(body).hexdigest()
        (self.repo / name).write_text(f'version https://git-lfs.github.com/spec/v1\noid sha256:{oid}\nsize {len(body)}\n')
        cache = self.repo / '.git/lfs/objects' / oid[:2] / oid[2:4] / oid
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(body)
        self.git('add', name)
        self.git('commit', '-m', name)
        return oid, cache

class StorageAuditTests(GitFixture):
    def test_deduplicates_oids(self):
        oid, _ = self.pointer('one.bin')
        self.pointer('two.bin')
        report = audit.inventory(self.repo)
        self.assertEqual(report['objects'], [{'oid': oid, 'size': 5}])
        self.assertTrue(report['complete'])

    def test_retains_old_branch_object(self):
        oid, _ = self.pointer('old.bin')
        self.git('branch', 'old')
        self.git('checkout', '--orphan', 'replacement')
        self.git('rm', '-rf', '.')
        (self.repo / 'README').write_text('new root')
        self.git('add', 'README');self.git('commit', '-m', 'replacement')
        report = audit.inventory(self.repo)
        self.assertEqual(report['objects'], [{'oid': oid, 'size': 5}])
        self.assertIn('refs/heads/old', report['refs'])

    def test_retains_intermediate_commit_object(self):
        oid, _ = self.pointer('removed.bin')
        self.git('rm', 'removed.bin');self.git('commit', '-m', 'remove')
        self.assertEqual(audit.inventory(self.repo)['objects'], [{'oid': oid, 'size': 5}])

    def test_incomplete_inventory_fails(self):
        self.pointer('one.bin')
        report = audit.inventory(self.repo)
        report['complete'] = False
        with self.assertRaises(ValueError):audit.verify_local(report)

    def test_corrupt_local_object_fails(self):
        _, path = self.pointer('one.bin')
        report = audit.inventory(self.repo)
        path.write_bytes(b'wrong')
        checked = audit.verify_local(report)
        self.assertEqual(checked['status'], 'failed')
        self.assertEqual(checked['counts']['corrupt'], 1)

    def test_missing_local_object_fails(self):
        _, path = self.pointer('one.bin')
        report = audit.inventory(self.repo)
        path.unlink()
        self.assertEqual(audit.verify_local(report)['counts']['missing'], 1)

    def test_recovery_retains_detached_worktree_only_commit(self):
        self.pointer('one.bin')
        detached=self.root/'detached'
        self.git('worktree','add','--detach',str(detached),'HEAD')
        subprocess.run(['git','commit','--allow-empty','-m','detached only'],cwd=detached,check=True,capture_output=True)
        tip=subprocess.check_output(['git','rev-parse','HEAD'],cwd=detached).decode().strip()
        report=audit.inventory(self.repo)
        destination=self.root/'backup'
        audit.backup(report,destination)
        restored=self.root/'restored.git'
        subprocess.run(['git','clone','--mirror',str(destination/'refs.bundle'),str(restored)],check=True,capture_output=True)
        result=subprocess.run(['git','cat-file','-e',tip+'^{commit}'],cwd=restored,capture_output=True)
        self.assertEqual(result.returncode,0,'Recovery bundle omitted detached worktree commit')

    def test_backup_restores_refs_bytes_and_cache_only_object(self):
        oid, path = self.pointer('one.bin')
        spare = b'cache only'
        extra = hashlib.sha256(spare).hexdigest()
        cache = path.parents[2]
        target = cache / extra[:2] / extra[2:4] / extra
        target.parent.mkdir(parents=True);target.write_bytes(spare)
        report = audit.inventory(self.repo)
        destination = self.root / 'backup'
        result = audit.backup(report, destination)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['objects_copied'], 2)
        self.assertEqual((destination / 'objects' / oid[:2] / oid[2:4] / oid).read_bytes(), b'alpha')
        self.assertEqual((destination / 'objects' / extra[:2] / extra[2:4] / extra).read_bytes(), spare)
        restored = self.root / 'restored.git'
        subprocess.run(['git', 'clone', '--mirror', str(destination / 'refs.bundle'), str(restored)], check=True, capture_output=True)
        actual = subprocess.check_output(['git', '--git-dir', str(restored), 'rev-parse', 'refs/heads/main']).decode().strip()
        self.assertEqual(actual, report['refs']['refs/heads/main'])
        # Recovery bytes are independent copies; subsequent cache edits do not alter them.
        path.write_bytes(b'wrong')
        self.assertEqual((destination / 'objects' / oid[:2] / oid[2:4] / oid).read_bytes(), b'alpha')

    def test_backup_refuses_changed_refs(self):
        self.pointer('one.bin')
        report = audit.inventory(self.repo)
        self.pointer('two.bin', b'beta')
        with self.assertRaises(ValueError):audit.backup(report, self.root / 'backup')





class CopyAuditTests(GitFixture):
    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(audit,"copy_objects") and hasattr(audit,"verify_remote"), "Remote copy/verification implementation is missing")
    def store(self):
        import sys,shutil,os
        sys.path.insert(0,str(MODULE.parent))
        from lfs_r2_transfer import Store
        config=self.root/'rclone.conf';config.write_text('[fixture]\ntype = local\n')
        return Store(dict(os.environ,RCLONE_CONFIG=str(config),
                          R2_LFS_REMOTE='fixture:'+str(self.root/'remote/project'),
                          R2_LFS_RCLONE=shutil.which('rclone')))

    def test_partial_copy_retry_retains_correct_object(self):
        oid,_=self.pointer('first.bin')
        other,path=self.pointer('second.bin',b'beta')
        report=audit.inventory(self.repo);path.unlink()
        store=self.store()
        result=audit.copy_objects(report,store)
        self.assertEqual(result['status'],'failed')
        remote=self.root/'remote/project/objects/sha256'/oid[:2]/oid
        self.assertEqual(remote.read_bytes(),b'alpha')
        modified=remote.stat().st_mtime_ns
        path.write_bytes(b'beta')
        result=audit.copy_objects(report,store)
        self.assertEqual(result['status'],'passed')
        self.assertEqual(remote.stat().st_mtime_ns,modified)
        self.assertEqual(audit.verify_remote(report,store)['status'],'passed')

    def test_remote_corruption_fails_full_readback(self):
        oid,_=self.pointer('one.bin');report=audit.inventory(self.repo);store=self.store()
        self.assertEqual(audit.copy_objects(report,store)['status'],'passed')
        remote=self.root/'remote/project/objects/sha256'/oid[:2]/oid
        remote.write_bytes(b'wrong')
        result=audit.verify_remote(report,store)
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['counts']['error'],1)

    def test_copy_refuses_uncaptured_ref_delta(self):
        self.pointer('one.bin');report=audit.inventory(self.repo)
        self.pointer('two.bin',b'beta')
        with self.assertRaises(ValueError):audit.copy_objects(report,self.store())



class BulkAuditTests(GitFixture):
    store = CopyAuditTests.store
    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(audit,'bulk_copy_objects'),'Verified bulk transfer implementation is missing')

    def test_two_objects_bulk_full_readback(self):
        self.pointer('one.bin');self.pointer('two.bin',b'beta')
        report=audit.inventory(self.repo)
        result=audit.bulk_copy_objects(report,self.store(),self.root/'bulk')
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['counts'],{'ok':2,'error':0})
        self.assertTrue(all(x['readback_sha256_verified'] for x in result['objects']))
        for item in report['objects']:
            restored=self.store().fetch(item['oid'],item['size'])
            self.assertEqual(__import__('hashlib').sha256(restored.read_bytes()).hexdigest(),item['oid'])
            restored.unlink()

    def test_bulk_existing_wrong_bytes_never_overwritten(self):
        oid,_=self.pointer('one.bin');report=audit.inventory(self.repo)
        remote=self.root/'remote/project/objects/sha256'/oid[:2]/oid
        remote.parent.mkdir(parents=True);remote.write_bytes(b'WRONG')
        result=audit.bulk_copy_objects(report,self.store(),self.root/'bulk')
        self.assertEqual(result['status'],'failed')
        self.assertEqual(remote.read_bytes(),b'WRONG')

    def test_bulk_rejects_corrupt_source_before_upload(self):
        oid,path=self.pointer('one.bin');report=audit.inventory(self.repo);path.write_bytes(b'WRONG')
        result=audit.bulk_copy_objects(report,self.store(),self.root/'bulk')
        self.assertEqual(result['status'],'failed')
        self.assertFalse((self.root/'remote/project/objects/sha256'/oid[:2]/oid).exists())


class DeltaAuditTests(GitFixture):
    store=CopyAuditTests.store

    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(audit,'delta_inventory'),'Explicit verified delta processing is missing')

    def baseline(self):
        self.pointer('first.bin');before=audit.inventory(self.repo)
        proof=audit.copy_objects(before,self.store())
        self.assertEqual(proof['status'],'passed')
        return before,proof

    def test_delta_copies_only_new_oids(self):
        before,proof=self.baseline()
        oid,_=self.pointer('second.bin',b'beta');current=audit.inventory(self.repo)
        delta=audit.delta_inventory(before,current,proof)
        self.assertEqual(delta['objects'],[{'oid':oid,'size':4}])
        self.assertEqual(delta['verified_baseline']['object_count'],1)
        changed=audit.copy_objects(delta,self.store())
        self.assertEqual(changed['status'],'passed')
        merged=audit.reconcile_verification(before,current,proof,changed)
        self.assertEqual(merged['status'],'passed')
        self.assertEqual(merged['counts'],{'ok':2,'error':0})
        self.assertEqual(merged['source_refs'],current['refs'])
        self.assertEqual(merged['verification_kind'],'composed_full_readback')
        changed['objects'][0]['readback_sha256_verified']=False
        with self.assertRaises(ValueError):audit.reconcile_verification(before,current,proof,changed)
        self.assertEqual(audit.verify_remote(current,self.store())['counts'],{'ok':2,'error':0})

    def test_code_only_delta_needs_no_asset_transfer(self):
        before,proof=self.baseline()
        self.git('commit','--allow-empty','-m','code only')
        delta=audit.delta_inventory(before,audit.inventory(self.repo),proof)
        self.assertEqual(delta['objects'],[])
        self.assertEqual(delta['refs']['HEAD'],self.git('rev-parse','HEAD'))
        self.assertEqual(audit.copy_objects(delta,self.store())['counts'],{'ok':0,'error':0})
        merged=audit.reconcile_verification(before,audit.inventory(self.repo),proof)
        self.assertEqual(merged['counts'],{'ok':1,'error':0})

    def test_unverified_baseline_cannot_support_delta(self):
        before,proof=self.baseline()
        proof['objects'][0]['readback_sha256_verified']=False
        with self.assertRaises(ValueError):audit.delta_inventory(before,before,proof)

    def test_delta_cannot_switch_storage_provider(self):
        before,proof=self.baseline();self.pointer('second.bin',b'beta')
        delta=audit.delta_inventory(before,audit.inventory(self.repo),proof)
        other=self.store();other.remote+='-other'
        with self.assertRaises(ValueError):audit.copy_objects(delta,other)
        with self.assertRaises(ValueError):audit.bulk_copy_objects(delta,other,self.root/'bulk')

    def test_delta_subset_cannot_be_mistaken_for_full_recovery_inventory(self):
        before,proof=self.baseline();self.pointer('second.bin',b'beta');current=audit.inventory(self.repo)
        delta=audit.delta_inventory(before,current,proof)
        copied=audit.copy_objects(delta,self.store())
        with self.assertRaises(ValueError):audit.backup(delta,self.root/'incomplete-recovery')
        with self.assertRaises(ValueError):audit.delta_inventory(delta,current,copied)

    def test_removed_ref_objects_remain_in_verified_baseline(self):
        before,proof=self.baseline()
        self.git('checkout','--orphan','replacement');self.git('rm','-rf','.')
        self.git('commit','--allow-empty','-m','replacement');self.git('branch','-D','main')
        delta=audit.delta_inventory(before,audit.inventory(self.repo),proof)
        self.assertEqual(delta['object_count'],0)
        self.assertEqual(delta['verified_baseline']['object_count'],1)
        self.assertEqual(delta['baseline_only_oids'],[before['objects'][0]['oid']])


if __name__ == '__main__':unittest.main()
