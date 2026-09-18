"""Pinned fetch, offline check, and refusal to overwrite GApps changes."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrepareGappsTest(unittest.TestCase):
    def test_pinned_download_and_modified_checkout(self):
        with tempfile.TemporaryDirectory(prefix='gapps-fetch-') as name:
            root = Path(name)
            origin = root / 'origin'
            origin.mkdir()
            def git(directory, *args):
                return subprocess.run(['git', '-C', str(directory), *args], check=True,
                                      capture_output=True, text=True).stdout.strip()
            git(origin, 'init', '-q')
            git(origin, 'config', 'user.name', 'Test')
            git(origin, 'config', 'user.email', 'test@example.invalid')
            (origin / 'fixture').write_text('pinned')
            git(origin, 'add', '.')
            git(origin, 'commit', '-qm', 'pinned input')
            revision = git(origin, 'rev-parse', 'HEAD')
            for path in ('scripts', 'research', 'source/vendor'):
                (root / path).mkdir(parents=True)
            shutil.copy2(ROOT / 'scripts/prepare-gapps.py', root / 'scripts')
            (root / 'research/gapps-source.json').write_text(
                json.dumps({'url': str(origin), 'revision': revision}))
            def run(*args):
                return subprocess.run([sys.executable, str(root / 'scripts/prepare-gapps.py'),
                                       *args], capture_output=True, text=True)
            self.assertEqual(run('--variant', 'none', '--check').returncode, 0)
            self.assertNotEqual(run('--variant', 'minimal', '--check').returncode, 0)
            self.assertFalse((root / 'source/vendor/gapps').exists())
            result = run('--variant', 'full')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(git(root / 'source/vendor/gapps', 'rev-parse', 'HEAD'), revision)
            self.assertEqual(run('--variant', 'minimal', '--check').returncode, 0)
            target = root / 'source/vendor/gapps/fixture'
            target.write_text('local change')
            self.assertNotEqual(run('--variant', 'full').returncode, 0)
            self.assertEqual(target.read_text(), 'local change')


if __name__ == '__main__':
    unittest.main()
