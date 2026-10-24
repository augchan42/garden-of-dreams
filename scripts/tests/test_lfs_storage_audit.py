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


class StorageAuditTests(unittest.TestCase):
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


if __name__ == '__main__':unittest.main()
