#!/usr/bin/env python3
"""Run the actual boot script with isolated property commands, never against a phone."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / "rom/bluetooth-fix"


class DefaultsTest(unittest.TestCase):
    def run_script(self, initial, twice=False, script='post-fs-data.sh',
                   expected=0, bootmode='true', flags=()):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            module = temp / 'module'
            shutil.copytree(ROOT / 'module', module)
            for flag in flags:
                (module / flag).touch()
            state = temp / 'props.json'
            state.write_text(json.dumps(initial))
            helper = temp / 'property-tool'
            helper.write_text('''#!/usr/bin/env python3
import os, json, sys
from pathlib import Path
p=Path(os.environ['LAPIS_BT_TEST_PROPS'])
data=json.loads(p.read_text())
if Path(sys.argv[0]).name=='getprop':
 print(data.get(sys.argv[1],''))
else:
 assert sys.argv[1]=='-n'
 key,value=sys.argv[2:]
 data[key]=value
 p.write_text(json.dumps(data))
''')
            helper.chmod(0o755)
            (temp / 'getprop').symlink_to(helper)
            (temp / 'resetprop').symlink_to(helper)
            env = dict(os.environ, PATH=str(temp) + os.pathsep + os.environ['PATH'],
                       LAPIS_BT_TEST_PROPS=str(state), MODPATH=str(module), BOOTMODE=bootmode)
            for _ in range(2 if twice else 1):
                command = ['bash', str(module / script)]
                if script == 'customize.sh':
                    command = ['bash', '-c', '''abort() { echo "$*" >&2; exit 1; }
set_perm_recursive() { :; }
set_perm() { :; }
ui_print() { :; }
. "$1"
''', 'installer-test', str(module / script)]
                result = subprocess.run(command, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            return json.loads(state.read_text())

    def test_stock_explicit_values_win_and_repeated_boot_is_idempotent(self):
        initial = {'ro.build.version.sdk': '36',
                   'ro.vendor.build.version.incremental': 'OS3.0.307.0.WPPMIXM',
                   'ro.product.vendor.device': 'lapis',
                   'ro.lineage.version': '23.2-20260918-UNOFFICIAL-gsi_lapis',
                   'bluetooth.profile.sap.server.enabled': 'false',
                   'bluetooth.profile.bap.unicast.client.enabled': 'false',
                   'bluetooth.profile.a2dp.source.enabled': 'false',
                   'bluetooth.device.class_of_device': 'existing'}
        after = self.run_script(initial, twice=True)
        for key, value in initial.items():
            self.assertEqual(after[key], value)
        self.assertEqual(after['bluetooth.profile.hfp.ag.enabled'], 'true')
        self.assertEqual(after['bluetooth.profile.hid.host.enabled'], 'true')
        self.assertNotIn('bluetooth.profile.bap.broadcast.source.enabled', after)

    def test_other_device_and_other_rom_are_untouched(self):
        for device, rom in [('other', '23.2-test-gsi_lapis'), ('lapis', 'HyperOS')]:
            initial = {'ro.product.vendor.device': device, 'ro.lineage.version': rom}
            self.assertEqual(self.run_script(initial), initial)

    def test_disable_and_remove_flags_prevent_changes(self):
        initial = {'ro.build.version.sdk': '36',
                   'ro.vendor.build.version.incremental': 'OS3.0.307.0.WPPMIXM',
                   'ro.product.vendor.device': 'lapis',
                   'ro.lineage.version': '23.2-20260918-UNOFFICIAL-gsi_lapis'}
        for flag in ('disable', 'remove'):
            self.assertEqual(self.run_script(initial, flags=(flag,)), initial)

    def test_installer_accepts_other_dates_but_checks_device_android_vendor_and_magisk(self):
        initial = {'ro.build.version.sdk': '36',
                   'ro.vendor.build.version.incremental': 'OS3.0.307.0.WPPMIXM',
                   'ro.product.vendor.device': 'lapis',
                   'ro.lineage.version': '23.2-20260918-UNOFFICIAL-gsi_lapis'}
        self.assertEqual(self.run_script(initial, script='customize.sh'), initial)
        other_date = {**initial, 'ro.lineage.version': '23.2-another-gsi_lapis'}
        self.assertEqual(self.run_script(other_date, script='customize.sh'), other_date)
        for key, value in [('ro.product.vendor.device', 'other'),
                           ('ro.lineage.version', '24.0-another-gsi_lapis'),
                           ('ro.build.version.sdk', '37'),
                           ('ro.vendor.build.version.incremental', 'other-vendor')]:
            with self.subTest(key=key):
                changed = {**initial, key: value}
                self.assertEqual(self.run_script(changed, script='customize.sh', expected=1), changed)
        self.assertEqual(self.run_script(initial, script='customize.sh', expected=1,
                                         bootmode='false'), initial)

    def test_build_defaults_match_runtime_payload_and_are_inherited(self):
        product = ROOT.parents[1] / 'local/device/local/gsi'
        result = subprocess.run(['make', '--no-print-directory', '-f',
                                 str(product / 'bluetooth-defaults.mk'), '-f', '-', 'all'],
                                input='$(info PROPS:$(PRODUCT_SYSTEM_PROPERTIES))\nall:;\n',
                                text=True, capture_output=True, check=True)
        line = next(line for line in result.stdout.splitlines() if line.startswith('PROPS:'))
        actual = dict(item.replace('?=', '=').split('=', 1) for item in line[6:].split())
        expected = dict(line.split('=', 1) for line in (ROOT / 'module/profiles.prop').read_text().splitlines()
                        if line and not line.startswith('#'))
        self.assertEqual(actual, expected)
        self.assertIn('$(call inherit-product, device/local/gsi/bluetooth-defaults.mk)',
                      (product / 'lapis-base.mk').read_text())


if __name__ == '__main__':
    unittest.main()
