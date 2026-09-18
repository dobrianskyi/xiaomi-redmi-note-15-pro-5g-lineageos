"""Regression coverage for overlapping patches and repeat build invocations."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/apply-build-patches.py'


class BuildPatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'source/example'
        self.repo.mkdir(parents=True)
        (self.root / 'scripts').mkdir()
        (self.root / 'patches').mkdir()
        shutil.copy2(SCRIPT, self.root / 'scripts')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Patch Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.repo / 'base').write_text('base\n')
        self.commit('base')
        self.base = self.git('rev-parse', 'HEAD').strip()
        entries = []
        self.commits = []
        for index, content in enumerate(('original\n', 'updated\n'), 1):
            (self.repo / 'feature').write_text(content)
            self.commit(f'patch {index}')
            self.commits.append(self.git('rev-parse', 'HEAD').strip())
            name = f'{index}.patch'
            (self.root / 'patches' / name).write_text(self.git('format-patch', '-1', '--stdout'))
            entries.append({'project': 'example', 'base': self.base, 'patch': name})
        (self.root / 'patches/series.json').write_text(json.dumps(entries))

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-qm', message)

    def run_patches(self, success=True):
        result = subprocess.run([sys.executable, str(self.root / 'scripts' / SCRIPT.name)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_clean_and_partial_checkouts_then_repeat(self):
        for start in (self.base, self.commits[0]):
            with self.subTest(start=start):
                self.git('reset', '--hard', start)
                self.run_patches()
                self.assertEqual((self.repo / 'feature').read_text(), 'updated\n')
                head = self.git('rev-parse', 'HEAD')
                self.run_patches()
                self.assertEqual(self.git('rev-parse', 'HEAD'), head)
                self.assertEqual(self.git('status', '--porcelain'), '')

    def test_reverted_patch_is_applied_again(self):
        self.git('revert', '--no-edit', self.commits[1])
        self.run_patches()
        self.assertEqual((self.repo / 'feature').read_text(), 'updated\n')

    def test_dirty_and_unreviewed_trees_rejected_without_changes(self):
        (self.repo / 'feature').write_text('unexpected\n')
        result = self.run_patches(False)
        self.assertIn('Dirty project', result.stderr)
        self.commit('unreviewed change')
        head = self.git('rev-parse', 'HEAD')
        result = self.run_patches(False)
        self.assertIn('Unexpected source tree', result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual((self.repo / 'feature').read_text(), 'unexpected\n')


if __name__ == '__main__':
    unittest.main()
