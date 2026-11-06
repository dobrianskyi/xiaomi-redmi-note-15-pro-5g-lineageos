"""Exercise installer eligibility and boot guards without running hardware payloads."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('display-fix', 'fingerprint-fix', 'call-audio-fix', 'dolby-fix')
BASE = {'ro.product.vendor.device': 'lapis', 'ro.lineage.version': '23.2-another-GSI',
        'ro.build.version.sdk': '36',
        'ro.vendor.build.version.incremental': 'OS3.0.307.0.WPPMIXM'}


class CompatibilityTest(unittest.TestCase):
    def run_script(self, name, props, script='customize.sh', integrated=False, bootmode='true'):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            module = temp / 'module'
            shutil.copytree(ROOT / 'rom' / name / 'module', module)
            marker = temp / 'lapis.rc'
            if integrated:
                marker.touch()
            # Only remap the Android filesystem location into the fixture.
            target = module / script
            target.write_text(target.read_text().replace('/system/etc/ueventd/lapis.rc', str(marker)))
            getprop = temp / 'getprop'
            getprop.write_text('#!/bin/sh\ncase "$1" in\n' + ''.join(
                f"{key}) printf '%s\\n' '{value}';;\n" for key, value in props.items()) + 'esac\n')
            getprop.chmod(0o755)
            env = dict(os.environ, PATH=str(temp) + os.pathsep + os.environ['PATH'],
                       MODPATH=str(module), BOOTMODE=bootmode)
            harness = '''abort() { echo "$*" >&2; exit 1; }
set_perm_recursive() { :; }
set_perm() { :; }
ui_print() { :; }
. "$1"
'''
            return subprocess.run(['sh', '-c', harness, 'module-test', str(target)],
                                  env=env, capture_output=True, text=True)

    def test_other_build_dates_are_allowed(self):
        for name in MODULES:
            for version in ('23.2-20260524-GAPPS-EXT4-GSI', '23.2-another-GSI'):
                with self.subTest(module=name, version=version):
                    result = self.run_script(name, {**BASE, 'ro.lineage.version': version})
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_incompatible_installations_are_rejected(self):
        for name in MODULES:
            for key, value in [('ro.product.vendor.device', 'other'),
                               ('ro.lineage.version', '24.0-test-GSI'),
                               ('ro.lineage.version', '23.2-test-gsi_lapis'),
                               ('ro.lineage.version', 'HyperOS'),
                               ('ro.build.version.sdk', '37'),
                               ('ro.vendor.build.version.incremental', 'other')]:
                with self.subTest(module=name, key=key, value=value):
                    result = self.run_script(name, {**BASE, key: value})
                    self.assertEqual(result.returncode, 1, result.stderr)
            for kwargs in ({'integrated': True}, {'bootmode': 'false'}):
                result = self.run_script(name, BASE, **kwargs)
                self.assertEqual(result.returncode, 1, result.stderr)

    def test_installed_modules_stop_after_incompatible_rom_upgrade(self):
        for name in MODULES:
            script = 'device-node.sh' if name == 'fingerprint-fix' else 'service.sh'
            for props, integrated in [({**BASE, 'ro.lineage.version': '24.0-test'}, False),
                                      ({**BASE, 'ro.lineage.version': '23.2-test-gsi_lapis'}, False),
                                      (BASE, True)]:
                with self.subTest(module=name, props=props, integrated=integrated):
                    result = self.run_script(name, props, script, integrated=integrated)
                    self.assertEqual(result.returncode, 1, result.stderr)


if __name__ == '__main__':
    unittest.main()
