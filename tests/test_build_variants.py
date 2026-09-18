"""Exercise the real launcher/archive code without compiling Android."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class BuildVariantsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='build variants ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for path in ('scripts', 'cache', 'source/.repo', 'source/build', 'research', 'patches'):
            (self.root / path).mkdir(parents=True, exist_ok=True)
        for name in ('build.sh', 'scripts/archive-image.py', 'scripts/inspect-image.py'):
            shutil.copy2(ROOT / name, self.root / name)
        (self.root / 'scripts/env.sh').write_text(
            f'export PATH="{ROOT}/tools/host/usr/bin:$PATH"\n')
        (self.root / 'source/build/envsetup.sh').touch()
        (self.root / 'research/resolved-manifest.xml').write_text('<manifest/>')
        (self.root / 'research/gapps-source.json').write_text('{"revision":"fixture"}')
        (self.root / 'patches/series.json').write_text('[]')
        (self.root / 'scripts/prepare-gapps.py').write_text('print("GApps check fixture")\n')
        for arch in ('arm', 'arm64'):
            directory = self.root / f'source/external/chromium-webview/prebuilt/{arch}'
            directory.mkdir(parents=True)
            with zipfile.ZipFile(directory / 'webview.apk', 'w') as z:
                z.writestr('fixture', 'fixture')
        (self.root / 'scripts/build-baseline.sh').write_text('''set -e
printf '%s:%s:%s' "$LAPIS_GAPPS" "$BUILD_JOBS" "$OUT_DIR" > invoked
cd source
[ "${TEST_FAIL:-0}" != 1 ] || exit 42
mkdir -p "$OUT_DIR/target/product/tdgsi_arm64_ab"
printf '%032s%s' "$LAPIS_GAPPS" "${TEST_CONTENT:-initial}" > "$OUT_DIR/target/product/tdgsi_arm64_ab/system.img"
''')

    def run_build(self, *args, expected=0, **env):
        result = subprocess.run(['bash', str(self.root / 'build.sh'), *args],
                                env={**os.environ, **env}, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_variants_archive_and_selected_clean(self):
        archives = {}
        for choice, variant, work in [('none', 'vanilla', 'out'),
                                     ('minimal', 'gapps-minimal', 'out-gapps-minimal'),
                                     ('full', 'gapps-full', 'out-gapps-full')]:
            self.run_build('--gapps', choice, '--jobs', '3', OUT_DIR='/ignored')
            image = self.root / 'out' / variant / 'latest/system.img'
            archives[variant] = (image.resolve(), image.read_bytes())
            self.assertIn(f'{choice}:3:{work}',
                          (self.root / 'invoked').read_text())
            (self.root / 'source' / work / 'cache-marker').touch()
        self.run_build('--gapps', 'minimal', '--clean', TEST_CONTENT='new')
        self.assertFalse((self.root / 'source/out-gapps-minimal/cache-marker').exists())
        self.assertTrue((self.root / 'source/out/cache-marker').exists())
        self.assertTrue((self.root / 'source/out-gapps-full/cache-marker').exists())
        for path, content in archives.values():
            self.assertEqual(path.read_bytes(), content)
        latest = self.root / 'out/gapps-minimal/latest/system.img'
        self.assertNotEqual(latest.resolve(), archives['gapps-minimal'][0])
        report = json.loads((latest.parent / 'system.img.inspection.json').read_text())
        manifest = json.loads((latest.parent / 'manifest.json').read_text())
        self.assertEqual(report['sha256'], manifest['sha256'])

    def test_preflight_failure_and_resume(self):
        self.run_build('--gapps', 'minimal', '--check')
        self.assertFalse((self.root / 'invoked').exists())
        self.run_build('--gapps', 'invalid', expected=2)
        self.run_build('--clean', '--check', expected=2)
        self.run_build('--gapps', 'full')
        old = (self.root / 'out/gapps-full/latest').resolve()
        (self.root / 'source/out-gapps-full/target/product/tdgsi_arm64_ab/system.img').write_bytes(b'partial previous output')
        self.run_build('--gapps', 'full', expected=42, TEST_FAIL='1')
        self.assertEqual((self.root / 'out/gapps-full/latest').resolve(), old)
        self.run_build('--gapps', 'full')
        self.assertEqual((self.root / 'out/gapps-full/latest').resolve(), old)

    def test_clean_refuses_symlink(self):
        protected = self.root / 'protected'
        protected.mkdir()
        (protected / 'keep').touch()
        (self.root / 'source/out-gapps-full').symlink_to(protected)
        self.run_build('--gapps', 'full', '--clean', expected=1)
        self.assertTrue((protected / 'keep').exists())


if __name__ == '__main__':
    unittest.main()
